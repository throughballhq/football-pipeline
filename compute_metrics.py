"""Compute derived layers: player_metrics, team_form, fixture_difficulty.

Cold-start design (pre-season / GW1-3): with fewer than MIN_GWS_FOR_MODEL
finished gameweeks of our own data, team strengths are seeded from FPL's
bootstrap strength ratings and marked source='fpl_prior'. Once enough of
our own per-GW xG data exists, the model switches to rolling xG
(source='model') automatically.

Runs daily after the snapshot. Idempotent (upserts keyed by date/GW).
"""

import os
import sys
from datetime import date, timedelta

import requests
from supabase import create_client

FPL_BASE = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "throughball-pipeline/1.0"}
MIN_GWS_FOR_MODEL = 3
ROLLING_WINDOW = 6           # matches, team form
PLAYER_WINDOW = 5            # gameweeks, player form
DIFFICULTY_HORIZON = 10      # upcoming gameweeks to score


def sb():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        sys.exit("Missing SUPABASE_URL / SUPABASE_SERVICE_KEY env vars.")
    return create_client(url, key)


def get_json(path: str):
    r = requests.get(f"{FPL_BASE}/{path}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all(query, page_size: int = 1000):
    """Paginate around PostgREST's 1000-row cap."""
    rows, start = [], 0
    while True:
        res = query.range(start, start + page_size - 1).execute()
        rows.extend(res.data)
        if len(res.data) < page_size:
            return rows
        start += page_size


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_0_100(values: dict) -> dict:
    """Min-max normalize a {key: value} dict to 0-100 within the league."""
    vals = [v for v in values.values() if v is not None]
    if not vals or max(vals) == min(vals):
        return {k: 50.0 for k in values}
    lo, hi = min(vals), max(vals)
    return {k: round((v - lo) / (hi - lo) * 100, 1) if v is not None else 50.0
            for k, v in values.items()}


def quintile(value, sorted_values) -> int:
    """Rank value into 1..5 within the league distribution."""
    if not sorted_values or len(set(sorted_values)) <= 1:
        return 3  # degenerate distribution -> honest neutral, never a fake 1
    below = sum(1 for v in sorted_values if v < value)
    return min(5, max(1, int(below / len(sorted_values) * 5) + 1))


def slope(points: list) -> float | None:
    """Least-squares slope of points over their index (no numpy)."""
    n = len(points)
    if n < 3:
        return None
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(points) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return None
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, points)) / denom, 2)


# ---------------------------------------------------------------- player layer

def compute_player_metrics(client, elements, finished: list[int]):
    today = date.today()

    # price 7 days ago from our own snapshots
    week_ago = (today - timedelta(days=7)).isoformat()
    old_prices = {
        r["player_id"]: num(r["price"])
        for r in fetch_all(
            client.table("daily_snapshots")
            .select("player_id, price")
            .eq("snapshot_date", week_ago)
        )
    }

    # last-N-GW stats from our own per-GW table
    recent: dict[int, list] = {}
    if finished:
        window = finished[-PLAYER_WINDOW:]
        for r in fetch_all(
            client.table("player_gw_stats")
            .select("player_id, gw, minutes, total_points, xgi")
            .in_("gw", window)
        ):
            recent.setdefault(r["player_id"], []).append(r)

    rows = []
    for el in elements:
        pid = el["id"]
        price = el["now_cost"] / 10 if el.get("now_cost") is not None else None
        pts = el.get("total_points") or 0
        goals = el.get("goals_scored") or 0
        xg_season = num(el.get("expected_goals"))

        gw_rows = sorted(recent.get(pid, []), key=lambda r: r["gw"])
        minutes_l5 = sum(r.get("minutes") or 0 for r in gw_rows) or None
        xgi_l5 = sum(num(r.get("xgi")) or 0 for r in gw_rows)
        xgi_per90 = (
            round(xgi_l5 / minutes_l5 * 90, 2)
            if minutes_l5 and minutes_l5 >= 180
            else None
        )

        old = old_prices.get(pid)
        rows.append(
            {
                "player_id": pid,
                "computed_date": today.isoformat(),
                "price": price,
                "total_points": pts,
                "value_ppm": round(pts / price, 2) if price else None,
                "minutes_l5": minutes_l5,
                "xgi_per90_l5": xgi_per90,
                "overperformance": (
                    round(goals - xg_season, 2) if xg_season is not None else None
                ),
                "form_slope": slope([r.get("total_points") or 0 for r in gw_rows]),
                "price_7d_delta": (
                    round(price - old, 1) if price is not None and old is not None else None
                ),
                "net_transfers_event": (
                    (el.get("transfers_in_event") or 0)
                    - (el.get("transfers_out_event") or 0)
                ),
            }
        )

    for i in range(0, len(rows), 500):
        client.table("player_metrics").upsert(
            rows[i : i + 500], on_conflict="player_id,computed_date"
        ).execute()
    print(f"  player_metrics: {len(rows)} rows for {today.isoformat()}")


# ------------------------------------------------------------------ team layer

def team_xg_from_own_data(client, teams_by_player):
    """Aggregate our per-GW player xG into team xG for/against per fixture."""
    stats = fetch_all(
        client.table("player_gw_stats").select("player_id, fixture_id, xg")
    )
    fixtures = {
        f["id"]: f
        for f in fetch_all(
            client.table("fixtures").select("id, home_team_id, away_team_id, finished")
        )
        if f["finished"]
    }
    # team attacking xG per fixture
    xg_for: dict[tuple, float] = {}
    for r in stats:
        fx = fixtures.get(r["fixture_id"])
        team = teams_by_player.get(r["player_id"])
        if fx is None or team is None:
            continue
        xg_for[(team, r["fixture_id"])] = xg_for.get((team, r["fixture_id"]), 0) + (
            num(r["xg"]) or 0
        )

    per_team: dict[int, list] = {}
    for (team, fixture_id), xg in xg_for.items():
        fx = fixtures[fixture_id]
        opponent = fx["away_team_id"] if fx["home_team_id"] == team else fx["home_team_id"]
        against = xg_for.get((opponent, fixture_id), 0)
        per_team.setdefault(team, []).append((fixture_id, xg, against))
    return per_team


def compute_team_form(client, bootstrap, finished: list[int], next_gw: int):
    teams = bootstrap["teams"]

    use_model = len(finished) >= MIN_GWS_FOR_MODEL
    if use_model:
        teams_by_player = {
            p["id"]: p["team_id"]
            for p in fetch_all(client.table("players").select("id, team_id"))
        }
        per_team = team_xg_from_own_data(client, teams_by_player)

        raw_att, raw_def, meta = {}, {}, {}
        for t in teams:
            matches = sorted(per_team.get(t["id"], []))[-ROLLING_WINDOW:]
            n = len(matches)
            xf = round(sum(m[1] for m in matches) / n, 2) if n else None
            xa = round(sum(m[2] for m in matches) / n, 2) if n else None
            raw_att[t["id"]] = xf
            raw_def[t["id"]] = -xa if xa is not None else None  # fewer conceded = better
            meta[t["id"]] = (n, xf, xa)
        source = "model"
    else:
        # FPL leaves strength_attack_*/strength_defence_* at 0 until the season
        # settles; strength_overall_* is populated pre-season. Fallback chain:
        # specific fields -> overall fields -> flat neutral.
        def pick_prior(key_a, key_b):
            raw = {
                t["id"]: ((t.get(key_a) or 0) + (t.get(key_b) or 0)) / 2
                for t in teams
            }
            return raw if len(set(raw.values())) > 1 else None

        overall = pick_prior("strength_overall_home", "strength_overall_away")
        raw_att = pick_prior("strength_attack_home", "strength_attack_away") or overall             or {t["id"]: 1 for t in teams}
        raw_def = pick_prior("strength_defence_home", "strength_defence_away") or overall             or {t["id"]: 1 for t in teams}
        meta = {t["id"]: (0, None, None) for t in teams}
        source = "fpl_prior"

    att_n = normalize_0_100(raw_att)
    def_n = normalize_0_100(raw_def)

    rows = [
        {
            "team_id": t["id"],
            "gw": next_gw,
            "matches_played_l6": meta[t["id"]][0],
            "xg_for_l6": meta[t["id"]][1],
            "xg_against_l6": meta[t["id"]][2],
            "attack_strength": att_n[t["id"]],
            "defense_strength": def_n[t["id"]],
            "source": source,
        }
        for t in teams
    ]
    client.table("team_form").upsert(rows, on_conflict="team_id,gw").execute()
    print(f"  team_form: {len(rows)} teams as of GW{next_gw} (source={source})")
    return att_n, def_n


def compute_fixture_difficulty(client, att_n, def_n, next_gw: int):
    horizon = list(range(next_gw, next_gw + DIFFICULTY_HORIZON))
    fixtures = fetch_all(
        client.table("fixtures")
        .select("id, gw, home_team_id, away_team_id")
        .in_("gw", horizon)
    )
    att_sorted = sorted(att_n.values())
    def_sorted = sorted(def_n.values())

    rows = []
    for f in fixtures:
        for team, opp in (
            (f["home_team_id"], f["away_team_id"]),
            (f["away_team_id"], f["home_team_id"]),
        ):
            rows.append(
                {
                    "fixture_id": f["id"],
                    "team_id": team,
                    # hard to score against a good defense
                    "att_difficulty": quintile(def_n.get(opp, 50), def_sorted),
                    # hard to keep a clean sheet against a good attack
                    "def_difficulty": quintile(att_n.get(opp, 50), att_sorted),
                }
            )

    for i in range(0, len(rows), 500):
        client.table("fixture_difficulty").upsert(
            rows[i : i + 500], on_conflict="fixture_id,team_id"
        ).execute()
    print(f"  fixture_difficulty: {len(rows)} team-fixture rows (GW{horizon[0]}-{horizon[-1]})")


# ------------------------------------------------------------------------ main

def main():
    client = sb()
    bootstrap = get_json("bootstrap-static/")
    elements = bootstrap.get("elements", [])
    if not elements:
        sys.exit("Empty bootstrap — aborting compute.")

    events = bootstrap.get("events", [])
    finished = sorted(e["id"] for e in events if e.get("finished"))
    upcoming = [e["id"] for e in events if not e.get("finished")]
    next_gw = min(upcoming) if upcoming else (max(finished) if finished else 1)

    print(f"compute_metrics: {len(finished)} finished GWs, next GW = {next_gw}")
    compute_player_metrics(client, elements, finished)
    att_n, def_n = compute_team_form(client, bootstrap, finished, next_gw)
    compute_fixture_difficulty(client, att_n, def_n, next_gw)
    print("compute_metrics: done")


if __name__ == "__main__":
    main()

"""Newsletter pack: charts (PNG) + brief.json from real pipeline data.

Output: pack_out/gw_XX/ with fixture heatmaps (att/def), market scatter,
price movers (once 7 days of snapshots exist) and brief.json — the data
grounding for the newsletter draft.

Pre-season aware: with no finished GWs it produces the Issue #0 package
(fixture outlook + market state). Post-GW1, value/form content activates.

Runs via GitHub Actions (newsletter-pack workflow) or locally.
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

import requests
from supabase import create_client

import charts

FPL_BASE = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "throughball-pipeline/1.0"}
HORIZON = 6  # gameweeks shown in fixture outlook


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


# ------------------------------------------------------------ data loading

def load(client):
    bootstrap = get_json("bootstrap-static/")
    events = bootstrap["events"]
    upcoming = [e for e in events if not e.get("finished")]
    next_gw = min(e["id"] for e in upcoming) if upcoming else max(e["id"] for e in events)
    deadline = next((e.get("deadline_time") for e in events if e["id"] == next_gw), None)

    teams = {t["id"]: t for t in bootstrap["teams"]}

    fixtures = fetch_all(
        client.table("fixtures")
        .select("id, gw, home_team_id, away_team_id")
        .gte("gw", next_gw)
        .lt("gw", next_gw + HORIZON)
    )
    difficulty = fetch_all(
        client.table("fixture_difficulty").select("fixture_id, team_id, att_difficulty, def_difficulty")
    )
    diff_by_key = {(d["fixture_id"], d["team_id"]): d for d in difficulty}

    snap_dates = client.table("daily_snapshots").select("snapshot_date").order(
        "snapshot_date", desc=True).limit(1).execute().data
    latest_date = snap_dates[0]["snapshot_date"] if snap_dates else None
    snapshots = fetch_all(
        client.table("daily_snapshots")
        .select("player_id, price, ownership_pct")
        .eq("snapshot_date", latest_date)
    ) if latest_date else []

    week_ago = (date.fromisoformat(latest_date) - timedelta(days=7)).isoformat() if latest_date else None
    old_snaps = fetch_all(
        client.table("daily_snapshots").select("player_id, price").eq("snapshot_date", week_ago)
    ) if week_ago else []

    return bootstrap, teams, next_gw, deadline, fixtures, diff_by_key, snapshots, old_snaps, latest_date


# ---------------------------------------------------------------- builders

def fixture_matrices(teams, fixtures, diff_by_key, next_gw):
    gw_labels = [f"GW{g}" for g in range(next_gw, next_gw + HORIZON)]
    order = sorted(teams.values(), key=lambda t: t["name"])
    att, deff = [], []
    for t in order:
        att_row, def_row = [], []
        for g in range(next_gw, next_gw + HORIZON):
            cells = [
                diff_by_key.get((f["id"], t["id"]))
                for f in fixtures
                if f["gw"] == g and t["id"] in (f["home_team_id"], f["away_team_id"])
            ]
            cells = [c for c in cells if c]
            att_row.append(round(sum(c["att_difficulty"] for c in cells) / len(cells)) if cells else None)
            def_row.append(round(sum(c["def_difficulty"] for c in cells) / len(cells)) if cells else None)
        att.append(att_row)
        deff.append(def_row)
    names = [t["name"] for t in order]
    return names, gw_labels, att, deff


def avg_run(matrix_row):
    vals = [v for v in matrix_row if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None


def build(client, out_dir: str):
    (bootstrap, teams, next_gw, deadline, fixtures,
     diff_by_key, snapshots, old_snaps, latest_date) = load(client)

    gw_dir = os.path.join(out_dir, f"gw_{next_gw:02d}")
    os.makedirs(gw_dir, exist_ok=True)

    players = {el["id"]: el for el in bootstrap["elements"]}
    finished_gws = [e["id"] for e in bootstrap["events"] if e.get("finished")]

    # 1) fixture outlook heatmaps (att + def)
    names, gw_labels, att, deff = fixture_matrices(teams, fixtures, diff_by_key, next_gw)
    charts.fixture_heatmap(
        "Who has the kind run-in?",
        f"Attacking fixture difficulty, GW{next_gw}-{next_gw + HORIZON - 1} — our model, not the official FDR",
        names, gw_labels, att, os.path.join(gw_dir, "fixtures_attack.png"),
    )
    charts.fixture_heatmap(
        "Clean sheets live here",
        f"Defensive fixture difficulty, GW{next_gw}-{next_gw + HORIZON - 1} — our model, not the official FDR",
        names, gw_labels, deff, os.path.join(gw_dir, "fixtures_defense.png"),
    )

    # 2) market scatter: price vs ownership (works pre-season)
    pts = []
    for s in snapshots:
        el = players.get(s["player_id"])
        own, price = num(s["ownership_pct"]), num(s["price"])
        if el and own is not None and price is not None and own >= 1:
            pts.append((price, own, el["web_name"]))
    if pts:
        charts.market_scatter(
            "Where the template money sits",
            f"Price vs. ownership, all players above 1% — snapshot {latest_date}",
            pts, os.path.join(gw_dir, "market_scatter.png"),
            xlabel="Price (£m)", ylabel="Ownership %",
        )

    # 3) price movers (needs 7 days of history)
    movers = []
    if old_snaps:
        old_price = {s["player_id"]: num(s["price"]) for s in old_snaps}
        for s in snapshots:
            old = old_price.get(s["player_id"])
            new = num(s["price"])
            if old is not None and new is not None and abs(new - old) >= 0.1:
                movers.append((players[s["player_id"]]["web_name"], round(new - old, 1)))
        movers = sorted(movers, key=lambda m: m[1], reverse=True)
        movers = movers[:7] + movers[-7:] if len(movers) > 14 else movers
        if movers:
            charts.movers_bar(
                "The market moved",
                "Biggest price changes over the last 7 days",
                movers, os.path.join(gw_dir, "price_movers.png"),
            )

    # 4) brief.json — the grounding document for the draft
    team_runs = [
        {"team": n, "att_run_avg": avg_run(a), "def_run_avg": avg_run(d)}
        for n, a, d in zip(names, att, deff)
    ]
    by_pos = {}
    for s in sorted(snapshots, key=lambda s: num(s["ownership_pct"]) or 0, reverse=True):
        el = players.get(s["player_id"])
        if not el:
            continue
        pos = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}.get(el["element_type"], "?")
        by_pos.setdefault(pos, [])
        if len(by_pos[pos]) < 5:
            by_pos[pos].append({
                "name": el["web_name"],
                "team": teams.get(el["team"], {}).get("short_name"),
                "price": num(s["price"]),
                "ownership_pct": num(s["ownership_pct"]),
            })

    brief = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "next_gw": next_gw,
        "deadline_utc": deadline,
        "finished_gws": len(finished_gws),
        "mode": "pre-season" if not finished_gws else "in-season",
        "snapshot_date": latest_date,
        "fixture_outlook": {
            "easiest_attacking_runs": sorted(
                [t for t in team_runs if t["att_run_avg"]], key=lambda t: t["att_run_avg"])[:5],
            "hardest_attacking_runs": sorted(
                [t for t in team_runs if t["att_run_avg"]], key=lambda t: t["att_run_avg"], reverse=True)[:5],
            "best_clean_sheet_runs": sorted(
                [t for t in team_runs if t["def_run_avg"]], key=lambda t: t["def_run_avg"])[:5],
        },
        "template": {"top_owned_by_position": by_pos},
        "price_movers_7d": [{"name": n, "delta": d} for n, d in movers],
        "charts": sorted(f for f in os.listdir(gw_dir) if f.endswith(".png")),
        "todo_post_gw1": ["value_ppm content", "xgi_per90 trends", "form slopes",
                          "team_form switches to source=model at 3 finished GWs"],
    }
    with open(os.path.join(gw_dir, "brief.json"), "w") as f:
        json.dump(brief, f, indent=2)

    print(f"newsletter_pack: {gw_dir} ready — {len(brief['charts'])} charts + brief.json")


if __name__ == "__main__":
    build(sb(), os.environ.get("PACK_OUT", "pack_out"))

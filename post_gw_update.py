"""Post-gameweek update: per-player stats (incl. xG) for finished gameweeks.

Uses /api/event/{gw}/live/ — one request per GW covering all players.
Idempotent: checks which finished GWs are missing rows and fills only those,
so it can safely run on the daily schedule (does nothing until GW1 finishes).

Note on double gameweeks (v1 simplification): the live endpoint aggregates
stats across a player's fixtures within the GW; we store one aggregated row
keyed to the player's first fixture of that GW. Per-fixture xG split can be
added later via element-summary if ever needed.
"""

import os
import sys

import requests
from supabase import create_client

FPL_BASE = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "throughball-pipeline/1.0"}


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


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def finished_gws(client) -> list[int]:
    res = client.table("gameweeks").select("id").eq("is_finished", True).execute()
    return sorted(row["id"] for row in res.data)


def gw_row_count(client, gw: int) -> int:
    res = (
        client.table("player_gw_stats")
        .select("player_id", count="exact")
        .eq("gw", gw)
        .limit(1)
        .execute()
    )
    return res.count or 0


def process_gw(client, gw: int):
    live = get_json(f"event/{gw}/live/")
    rows = []
    for el in live.get("elements", []):
        stats = el.get("stats", {})
        explain = el.get("explain", [])
        if not explain:
            continue  # player had no fixture this GW
        fixture_id = explain[0].get("fixture")
        if fixture_id is None:
            continue
        rows.append(
            {
                "player_id": el["id"],
                "gw": gw,
                "fixture_id": fixture_id,
                "minutes": stats.get("minutes"),
                "goals": stats.get("goals_scored"),
                "assists": stats.get("assists"),
                "clean_sheet": (stats.get("clean_sheets") or 0) > 0,
                "goals_conceded": stats.get("goals_conceded"),
                "bonus": stats.get("bonus"),
                "bps": stats.get("bps"),
                "total_points": stats.get("total_points"),
                "xg": num(stats.get("expected_goals")),
                "xa": num(stats.get("expected_assists")),
                "xgi": num(stats.get("expected_goal_involvements")),
                "xgc": num(stats.get("expected_goals_conceded")),
            }
        )

    for i in range(0, len(rows), 500):
        client.table("player_gw_stats").upsert(
            rows[i : i + 500], on_conflict="player_id,gw,fixture_id"
        ).execute()
    print(f"  GW{gw}: upserted {len(rows)} player rows")


def main():
    client = sb()
    gws = finished_gws(client)
    if not gws:
        print("post_gw_update: no finished gameweeks yet — nothing to do.")
        return

    todo = [gw for gw in gws if gw_row_count(client, gw) == 0]
    if not todo:
        print(f"post_gw_update: all {len(gws)} finished GWs already stored.")
        return

    for gw in todo:
        process_gw(client, gw)
    print("post_gw_update: done")


if __name__ == "__main__":
    main()

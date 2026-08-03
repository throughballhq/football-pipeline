"""Fetch FPL bootstrap data and upsert base entities into Supabase.

Tables: teams, gameweeks, players, fixtures.
Safe to run repeatedly (idempotent upserts). Run before daily_snapshot.py.
"""

import os
import sys

import requests
from supabase import create_client

FPL_BASE = "https://fantasy.premierleague.com/api"
POSITIONS = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
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


def chunked_upsert(client, table: str, rows: list, on_conflict: str, size: int = 500):
    for i in range(0, len(rows), size):
        client.table(table).upsert(rows[i : i + size], on_conflict=on_conflict).execute()
    print(f"  {table}: upserted {len(rows)} rows")


def main():
    client = sb()
    data = get_json("bootstrap-static/")

    # Sanity check: is the 2026/27 game live? (task 0.5)
    n_events = len(data.get("events", []))
    n_players = len(data.get("elements", []))
    print(f"bootstrap-static OK: {n_events} gameweeks, {n_players} players")
    if n_events == 0 or n_players == 0:
        sys.exit("FPL API returned empty data — game for the new season may not be live yet.")

    teams = [
        {
            "id": t["id"],
            "code": t.get("code"),
            "name": t["name"],
            "short_name": t["short_name"],
        }
        for t in data["teams"]
    ]
    chunked_upsert(client, "teams", teams, on_conflict="id")

    gameweeks = [
        {
            "id": e["id"],
            "deadline_utc": e.get("deadline_time"),
            "is_finished": e.get("finished", False),
        }
        for e in data["events"]
    ]
    chunked_upsert(client, "gameweeks", gameweeks, on_conflict="id")

    players = [
        {
            "id": el["id"],
            "code": el.get("code"),
            "team_id": el.get("team"),
            "web_name": el.get("web_name"),
            "full_name": f"{el.get('first_name', '')} {el.get('second_name', '')}".strip(),
            "position": POSITIONS.get(el.get("element_type")),
            "status": el.get("status"),
            "team_join_date": el.get("team_join_date"),
        }
        for el in data["elements"]
    ]
    chunked_upsert(client, "players", players, on_conflict="id")

    fixtures_raw = get_json("fixtures/")
    fixtures = [
        {
            "id": f["id"],
            "gw": f.get("event"),  # can be null until rescheduled fixtures get a GW
            "home_team_id": f.get("team_h"),
            "away_team_id": f.get("team_a"),
            "kickoff_utc": f.get("kickoff_time"),
            "home_score": f.get("team_h_score"),
            "away_score": f.get("team_a_score"),
            "finished": f.get("finished", False),
        }
        for f in fixtures_raw
    ]
    chunked_upsert(client, "fixtures", fixtures, on_conflict="id")

    print("fetch_bootstrap: done")


if __name__ == "__main__":
    main()

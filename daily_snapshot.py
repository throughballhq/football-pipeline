"""Daily market snapshot: price, ownership, transfers, availability per player.

FPL provides NO historical prices/ownership — this table only exists
if we collect it every day. This is the single most time-critical job
in the whole pipeline. Runs daily via GitHub Actions (06:00 UTC).

Run fetch_bootstrap.py first (players must exist for the FK).
"""

import os
import sys
from datetime import date, datetime, timezone

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


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    client = sb()
    r = requests.get(f"{FPL_BASE}/bootstrap-static/", headers=HEADERS, timeout=30)
    r.raise_for_status()
    elements = r.json().get("elements", [])
    if not elements:
        sys.exit("Empty elements — aborting snapshot.")

    today = date.today().isoformat()
    rows = [
        {
            "snapshot_date": today,
            "player_id": el["id"],
            "price": (el["now_cost"] / 10) if el.get("now_cost") is not None else None,
            "ownership_pct": to_float(el.get("selected_by_percent")),
            "transfers_in_event": el.get("transfers_in_event"),
            "transfers_out_event": el.get("transfers_out_event"),
            "status": el.get("status"),
            "chance_of_playing": el.get("chance_of_playing_next_round"),
            "news": (el.get("news") or None),
        }
        for el in elements
    ]

    for i in range(0, len(rows), 500):
        client.table("daily_snapshots").upsert(
            rows[i : i + 500], on_conflict="snapshot_date,player_id"
        ).execute()

    print(
        f"daily_snapshot: {len(rows)} players snapshotted for {today} "
        f"at {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    )


if __name__ == "__main__":
    main()

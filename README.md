# throughball-pipeline

Data pipeline for **The Throughball** — daily FPL market snapshots and base entities
(teams, players, gameweeks, fixtures) stored in Supabase. Runs on GitHub Actions,
zero servers.

> Why the snapshot job matters: FPL exposes **no historical prices or ownership**.
> The `daily_snapshots` table only exists if we collect it every day — it is the
> single dataset nobody can backfill later.

## Setup (one-time, ~15 min)

1. **Supabase project**
   - Create a project at supabase.com (Free tier, region: EU/Frankfurt).
   - SQL Editor → New query → paste the contents of `schema.sql` → Run.
   - Table Editor should now show 6 tables.

2. **Repo secrets** (GitHub → repo → Settings → Secrets and variables → Actions):
   - `SUPABASE_URL` — Supabase → Project Settings → API → Project URL
   - `SUPABASE_SERVICE_KEY` — same page → `service_role` key
   - The service key bypasses RLS — it lives **only** in GitHub Secrets.
     Never commit it, never paste it into chats or docs.

3. **First run**
   - Push this repo (org `throughball`, private).
   - Actions tab → `daily-pipeline` → **Run workflow** (manual trigger).
   - Green run → check Supabase Table Editor: `players` ~700 rows,
     `daily_snapshots` has today's date.

4. **Done.** The cron now runs daily at 06:00 UTC. Check the Actions tab
   once every few days for red runs (GitHub also emails on failure).

## Jobs

| Script | What it does | Schedule |
|---|---|---|
| `fetch_bootstrap.py` | Upserts teams, players, gameweeks, fixtures | daily, before snapshot |
| `daily_snapshot.py` | Price, ownership, transfers, availability per player | daily 06:00 UTC |

## Roadmap (per masterplan)

- Phase 1: `compute_metrics.py` (player_metrics, team_form, fixture_difficulty),
  chart module (`brand.py`), `newsletter_pack.py`
- Phase 2: `post_gw_update.py` (per-GW stats incl. xG into `player_gw_stats`),
  `weekly_signals.py` (signal engine)

## Troubleshooting

- **Empty data / exit "game may not be live yet"**: the 2026/27 FPL game hasn't
  launched or is being reset. Re-run the next day.
- **FK errors on snapshot**: run `fetch_bootstrap.py` first (workflow already
  orders them correctly).
- **FPL API schema change**: scripts fail loudly rather than writing bad data —
  open the Actions log and fix the field mapping.

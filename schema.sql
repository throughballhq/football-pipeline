-- The Throughball — pipeline schema v1 (base entities + facts)
-- Run this in Supabase: SQL Editor -> New query -> paste -> Run.
-- Design note: we use FPL ids directly as primary keys (stable within a season).
-- A `season` column is included as cheap insurance for future archiving.

-- ============ 2.1 Base entities ============

create table if not exists teams (
  id          int primary key,          -- FPL team id
  season      text not null default '2026-27',
  code        int,                      -- FPL team code (stable across seasons)
  name        text not null,
  short_name  text not null
);

create table if not exists players (
  id            int primary key,        -- FPL element id
  season        text not null default '2026-27',
  code          int,                    -- FPL player code (stable across seasons)
  team_id       int references teams(id),
  web_name      text not null,
  full_name     text,
  position      text check (position in ('GKP','DEF','MID','FWD')),
  status        text                    -- a/d/i/s/u/n
);

create table if not exists gameweeks (
  id            int primary key,        -- GW number
  season        text not null default '2026-27',
  deadline_utc  timestamptz,
  is_finished   boolean default false
);

create table if not exists fixtures (
  id            int primary key,        -- FPL fixture id
  season        text not null default '2026-27',
  gw            int references gameweeks(id),
  home_team_id  int references teams(id),
  away_team_id  int references teams(id),
  kickoff_utc   timestamptz,
  home_score    int,
  away_score    int,
  finished      boolean default false
);

-- ============ 2.2 Facts ============

-- One row per player per day. FPL gives no historical prices/ownership,
-- so this table is the asset we build from day one.
create table if not exists daily_snapshots (
  snapshot_date       date not null,
  player_id           int not null references players(id),
  price               numeric(5,1),     -- in millions, e.g. 7.5
  ownership_pct       numeric(6,2),
  transfers_in_event  int,
  transfers_out_event int,
  status              text,
  chance_of_playing   int,
  news                text,
  primary key (snapshot_date, player_id)
);

-- One row per player per fixture (handles double gameweeks).
-- Filled by post_gw_update job (Phase 1/2).
create table if not exists player_gw_stats (
  player_id       int not null references players(id),
  gw              int not null references gameweeks(id),
  fixture_id      int not null references fixtures(id),
  minutes         int,
  goals           int,
  assists         int,
  clean_sheet     boolean,
  goals_conceded  int,
  bonus           int,
  bps             int,
  total_points    int,
  xg              numeric(6,2),
  xa              numeric(6,2),
  xgi             numeric(6,2),
  xgc             numeric(6,2),
  price_at_gw     numeric(5,1),
  ownership_at_gw numeric(6,2),
  primary key (player_id, gw, fixture_id)
);

-- Derived layers (team_form, fixture_difficulty, player_metrics, signals)
-- arrive in Phase 1 (task 1.1) — kept out of v1 on purpose.

-- ============ Indexes ============
create index if not exists idx_snapshots_player on daily_snapshots(player_id, snapshot_date);
create index if not exists idx_gw_stats_gw on player_gw_stats(gw);
create index if not exists idx_fixtures_gw on fixtures(gw);

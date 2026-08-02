-- The Throughball — pipeline schema, Phase 1: derived layers
-- Run in Supabase SQL Editor AFTER schema.sql.

-- Rolling team strength. Until ~3 GWs of our own data exist, rows are seeded
-- from FPL's own strength ratings and marked source='fpl_prior';
-- afterwards computed from rolling xG and marked source='model'.
create table if not exists team_form (
  team_id            int not null references teams(id),
  gw                 int not null,           -- "as of" upcoming GW
  matches_played_l6  int,
  xg_for_l6          numeric(6,2),           -- avg per match, last 6
  xg_against_l6      numeric(6,2),
  attack_strength    numeric(5,1),           -- 0-100, normalized vs league
  defense_strength   numeric(5,1),           -- 0-100, higher = better defense
  source             text not null default 'model',  -- 'fpl_prior' | 'model'
  computed_at        timestamptz default now(),
  primary key (team_id, gw)
);

-- Our own difficulty model (NOT the official FDR). Two dimensions per team
-- and fixture: how hard to score, how hard to keep a clean sheet.
create table if not exists fixture_difficulty (
  fixture_id      int not null references fixtures(id),
  team_id         int not null references teams(id),
  att_difficulty  int check (att_difficulty between 1 and 5),
  def_difficulty  int check (def_difficulty between 1 and 5),
  computed_at     timestamptz default now(),
  primary key (fixture_id, team_id)
);

-- Daily per-player computed metrics (one row per player per day).
create table if not exists player_metrics (
  player_id           int not null references players(id),
  computed_date       date not null,
  price               numeric(5,1),
  total_points        int,
  value_ppm           numeric(6,2),   -- total_points / price
  minutes_l5          int,
  xgi_per90_l5        numeric(6,2),   -- null until >=180 min in last 5 GWs
  overperformance     numeric(6,2),   -- goals - xG, season
  form_slope          numeric(6,2),   -- pts trend over last 5 GWs
  price_7d_delta      numeric(5,1),
  net_transfers_event int,
  primary key (player_id, computed_date)
);

create index if not exists idx_player_metrics_date on player_metrics(computed_date);
create index if not exists idx_fixture_difficulty_team on fixture_difficulty(team_id);

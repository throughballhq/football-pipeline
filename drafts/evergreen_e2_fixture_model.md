# E2 - evergreen draft v1: "Anatomy of our fixture model"

**Status: šuplík - plánované jako 2. řádné úterní vydání (~1. 9.), případně
pojistka. [EDITOR: před publikací refresh všech run averages z aktuálního
packu - čísla níže jsou z pre-season briefu 3. 8.]**

**Headline options:**
1. Why I built my own fixture model
2. One number can't rate a fixture
3. Anatomy of the difficulty model

---

Every FPL manager knows the official FDR - the little coloured squares
that rate each fixture from 1 to 5. I built my own version anyway, and
this issue is the full anatomy: how it works, where it disagrees with
the official one, and - because trust is earned - exactly where it's
weak.

## The problem with one number

The official rating gives each fixture a single difficulty. But a
fixture isn't one question, it's two: **how hard is it to score, and
how hard is it to keep a clean sheet?** Those have different answers
against most teams. A side in chaos can leak goals at one end and still
carry a genuine threat at the other - easy for your forwards, useless
for your defenders. Squash that into one number and both answers get
worse.

So my model rates every fixture twice: **attacking difficulty**
(measured against the opponent's defence) and **clean-sheet difficulty**
(measured against the opponent's attack). Each lands on a 1-5 scale,
built as quintiles - every gameweek, the league is split into five
equal bands, so a 5 always means "top-fifth hardest right now", not
some fixed threshold.

## What feeds it

Once the season is a few rounds old, the engine is **rolling xG over
each team's last six matches**: expected goals created for attack
strength, expected goals conceded for defence strength - per match,
normalised against the league. Not results, not reputation, not league
position. A team can sit eighth and still be the second-best defence
in the underlying numbers; the model only sees the second part.

At the time of writing, pre-season, the model hands **Arsenal the
kindest opening run (2.0 average over six gameweeks)** with Newcastle
next at 2.17, while **Bournemouth drew the roughest start in the
league at 3.33** [EDITOR: refresh from current pack on publish day].

## Where it's honestly weak

Three limits, stated plainly. **One:** until three rounds are played,
there's no xG to roll - so the model starts each season on pre-season
priors and both views look identical. Around gameweek four it switches
to its own data and the attacking and clean-sheet ratings start
disagreeing - with the official FDR and with each other. That
wake-up moment is the whole point of the design. **Two:** quintiles
are relative - a 3 in a strong league year is harder than a 3 in a
weak one. **Three:** it rates teams, not matchups - it doesn't know
your winger torments this specific left-back. That layer is your job.

You can see every rating, both views, for every team at
[app.thethroughball.com/fixtures](https://app.thethroughball.com/fixtures) -
refreshed daily by the same pipeline that writes this newsletter.

[CHART: fixtures_attack.png - attacking difficulty, all 20 teams, the
gameweeks ahead]

*One number tells you a fixture is hard. Two numbers tell you who it's
hard for.*

---

## FACT-CHECK LIST

- oficiální FDR = 1-5 škála - obecně známé, stable ✓
- dva rozměry (att vs. soupeřova obrana, def vs. soupeřův útok) - vlastní
  produkt, kód compute_metrics.py ✓
- kvintily 1-5 v rámci ligy - compute_metrics.quintile() ✓
- rolling xG okno 6 zápasů, normalizace vůči lize - ROLLING_WINDOW=6 ✓
- Arsenal 2.0 / Newcastle 2.17 - fixture_outlook.easiest_attacking_runs[0-1]
  [EDITOR: refresh v den publikace]
- Bournemouth 3.33 - fixture_outlook.hardest_attacking_runs[0]
  [EDITOR: refresh v den publikace]
- přepnutí priors -> model po 3 odehraných kolech - MIN_GWS_FOR_MODEL=3;
  formulace "around gameweek four" ✓
- horizont v appce - v_fixture_matrix, 10 GW - v textu záměrně nečíslováno,
  ať kus nezestárne při změně horizontu ✓

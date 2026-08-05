# E1 - evergreen draft v1: "How to read xG (and when not to trust it)"

**Status: v2 (po editu) - šuplík (primární pojistka / mezinárodní pauza)**

**Headline options:**
1. How to read xG (and when not to trust it)
2. xG, explained by someone who checks it daily
3. The number that knows before the scoreboard does

---

A striker misses from six yards and the pundit calls it "a sitter". A
winger curls one in from 25 metres and it's "world class". xG is just
those two instincts, measured: **every shot gets a number between 0 and 1
- the probability that an average player scores it from there.** The
six-yard sitter might be 0.7. The 25-metre curler, 0.03. One of those
outcomes was normal. The other was a lottery ticket cashing in.

## Why I trust it more than the scoreboard

Goals are rare - a couple per team per match, sometimes none. That's a
tiny sample, and tiny samples lie with a straight face. Chances happen
ten times more often, so **xG gives you roughly ten times the evidence
per match** about how a team or player is actually performing.
[EDITOR: verify shot volumes - PL teams average ~12-14 shots/match]

That's the whole trick. A striker on 2 goals from 5.1 xG isn't finishing
badly forever - he's standing in the right places and the maths hasn't
paid out yet. A team winning 1-0 every week off 0.6 xG isn't "hard to
beat". It's living on borrowed time. The scoreboard tells you what
happened. xG tells you what usually happens from there.

## When NOT to trust it - the part nobody prints

**1. Small samples.** One match of xG is barely better than one match of
goals. I don't take a player's xG seriously until there's ~450 minutes
behind it - that's why every rate stat in my tools runs on a rolling
five-gameweek window, not last Saturday.

**2. Penalties.** A penalty is worth about 0.79 xG on its own - one spot
kick inflates a quiet afternoon into an "elite underlying performance".
Whenever a number looks too good, check who's on pens first.

**3. All shots are not one shot.** Two players can both average 0.45 xG
a game: one takes two big chances, the other throws eight hopeful ones
at the keeper. Same total, completely different sustainability - volume
from bad spots dries up; positioning for big chances tends to travel.

**4. The model doesn't know who's shooting.** Basic xG assumes an
average finisher. Genuinely elite finishers beat their xG year after
year - but far fewer players are "genuinely elite" than fans believe.
My default: assume regression, demand years of evidence for the
exception.

## How The Throughball uses it

Three rules, applied daily by the pipeline: rates over totals (xGI per
90, not season sums), windows over snapshots (last five gameweeks), and
**finishing vs xG as a regression alarm** - goals minus xG, positive
runs cool off, negative ones tend to correct. You'll find all three on
every player card in the [explorer](https://app.thethroughball.com/explorer).

[CHART: xg_scale_explainer.png - a handful of real shots on a pitch,
each labelled with its xG value, from 0.03 to 0.79]

*xG doesn't predict the next match. It tells you which version of the
last one to believe.*

---

## FACT-CHECK LIST

- shot xG range 0–1, definition - standard/general, stable
- penalty ≈ 0.79 xG - široce používaná hodnota [EDITOR: verify proti
  aktuálnímu zdroji, bývá uváděno 0.76–0.79]
- "ten times more chances than goals" - řádový poměr střel ke gólům
  [EDITOR: verify, PL průměr ~12–14 střel a ~1.4 gólu na tým a zápas]
- 450 minut threshold - naše redakční pravidlo (odpovídá min. 180 min
  v pipeline pro xGI/90 + konzervativní rezerva), ne externí fakt -
  formulováno jako "I don't take it seriously until", tedy názor ✓
- rolling 5-GW window, goals−xG regression alarm - vlastní produkt,
  ověřitelné v appce ✓
- příklady (2 góly z 5.1 xG, 0.45 xG profily) - ilustrativní, smyšlené
  jako archetypy, žádné reálné jméno ✓ (záměr: evergreen nesmí zestárnout)

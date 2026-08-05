# The Throughball — Content plán, sezóna 2026/27

Jeden zdroj pravdy pro témata. Rozesílky se NIKDY nepíšou dopředu (data stárnou
denně) — tohle je zásobník témat, evergreen munice a kalendář kotev.
Přesné deadliny ke každému kolu drží pipeline (`v_gameweeks`), tady jsou GW
čísla a orientační data.

Rytmus: **úterý deep-dive** (téma odtud nebo z pondělních signálů) ·
**brief ~24 h před deadline** (vždy z čerstvého packu, neplánuje se).

---

## 1) Zásobník úterních deep-dives (s orientačními daty)

- [ ] **Út 25. 8.** (po GW1) — *"One gameweek is a lie"* — co výsledky prvního
  kola říkají a hlavně neříkají; xG vs. skóre GW1, ukázka na 2–3 extrémech.
- [ ] **Út 1. 9.** (po GW2) — *"The first real signals"* — xGI/90 L5 poprvé
  živé v appce; jak číst malý vzorek bez sebeklamu.
- [ ] **~pol. září** (po 3 odehraných kolech) — ⭐ *"The model wakes up"* —
  fixture model se přepíná z priorů na vlastní xG (`source='model'`); první
  rozpory s oficiálním FDR + att/def pohledy se poprvé rozjedou. Vlajkový kus,
  plánovaný od den 1.
- [ ] **Út 29. 9.** (GW~6) — *"Six gameweeks settle these three things"* —
  co už je signál a co pořád šum. (Interní: kontrolní bod 100 subs 30. 9.)
- [ ] **Říjen** — *"Regression watch #1"* — leaderboard overperformance
  (góly − xG): kdo střílí nad realitu a koho čeká ochlazení. Opakovatelný
  formát — dělat ~1× za 6 týdnů.
- [ ] **Říjen/listopad** — *"The market's memory"* — 2+ měsíce daily
  snapshots = dataset, který nikdo zpětně nemá; price momentum vs. skutečná
  forma, kdo zdražuje bez podkladu v číslech.
- [ ] **Listopad** (mezinárodní pauza) — *"Minutes risk"* — rotace, návraty
  z reprezentací, minutes_l5 jako podceňovaná metrika.
- [ ] **Začátek prosince** — *"Festive congestion, by the numbers"* — prosinec
  = nejvíc zápasů v roce; co dělá nahuštění s xG a čistými konty. (Kotva ⚓ D1)
- [ ] **Leden** — *"January, through the transfer flag"* — zimní okno očima
  našeho team_join_date flagu: skuteční příchozí vs. mediální šum; New
  signings radar dostane žně.
- [ ] **Únor** — *"Half-season in data"* — velké shrnutí: co model trefil,
  kde se mýlil (transparentnost = brand).
- [ ] **Duben/květen** — *"Run-in swings"* — komu se láme rozpis do finiše;
  fixture_difficulty na 10 kol je přesně na tohle.
- [ ] **Konec května** — ⭐ *"The Season in Data"* — ročenka, nejsdílitelnější
  kus roku, sběr odběratelů přes léto. (Kotva ⚓ K1)

*(Doplňuj průběžně — nejlepší témata stejně vygenerují pondělní signály.
Pravidlo: co zestárne za týden, sem nepatří.)*

## 2) Evergreen záložníky (bez data — pojistka proti vynechanému vydání)

Pravidlo z masterplanu: brief se nevynechává nikdy; když nestíháš deep-dive,
jde evergreen. Cíl: mít 2 hotové v šuplíku před GW1.

- [ ] **E1 — "How to read xG (and when not to trust it)"** — explainer:
  co xG je, co měří, kdy lže (malé vzorky, penalty, garbage time); proč mu
  věříme víc než výsledkům. Věčný odkazovací kus — budeme na něj linkovat
  z půlky budoucích vydání.
- [ ] **E2 — "Anatomy of our fixture model"** — transparentní rozbor: proč
  ne oficiální FDR, jak počítáme att/def zvlášť, co jsou priory a kdy se
  model probouzí. Diferenciační kus + FAQ odpověď v jednom.
- [ ] **E3 (rezerva) — "Ownership is a market, not a scoreboard"** — dav,
  template a proč vysoké vlastnictví není doporučení; behavioral úhel.

## 3) Kalendář kotev ⚓ (ne obsah — připravenost)

| Kdy | Co | Poznámka |
|---|---|---|
| 18.–19. 8. | **Launch Issue #0** + distribuce (X, r/FantasyPL) | playbook v masterplanu 1.7 |
| 21. 8. 18:30 UK | GW1 deadline → **start týdenního rytmu** | |
| ~15. 9. | DMARC zpět na `p=quarantine` | technická kotva |
| po 3. odehraném kole | Model switch → vlajkový deep-dive | hlídat `source` v team_form |
| 30. 9. | Kontrolní bod: 100 subs, open rate >40 % | masterplan 2.5 |
| listopad | Hlídat Beehiiv limit 2 500 subs (→ placený plán = dobrý problém) | |
| prosinec | Festive špička + první DGW + **zimní waitlist test** | masterplan F5 |
| 31. 12. | Kontrolní bod: 500 subs; vyhodnotit app vs. landing (utm) | masterplan 4.4 |
| leden | Zimní přestupové okno — transfer flag content | |
| jaro | Rozhodnutí xG API (Sportmonks add-on vs. TheStatsAPI trial) | masterplan 6.3 |
| konec května | Season in Data ročenka + konec sezóny | |
| červen 2027 | Release rozpisů 27/28 → monetizační rozjezd | masterplan F7 |

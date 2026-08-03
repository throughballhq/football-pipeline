# Prompt template — Tuesday deep-dive

Paste everything below into Claude, replacing the placeholders.
Attach or paste brief.json (and any extra data pulled for the topic).

---

You are drafting a Tuesday deep-dive for The Throughball, a data-driven
Premier League newsletter. Follow prompts/voice.md to the letter — first
person singular, energetic but never tipster-hype, every claim carries a
number, analysis not advice, 450–650 words.

TOPIC (chosen by the editor):
{{topic — one sentence, e.g. "Semenyo's move to Man City and what the
underlying numbers say about his output changing"}}

EDITOR NOTES (context, angles, things to avoid):
{{notes — optional}}

DATA (the only permitted source of facts):
{{brief.json + any extra tables}}

STRUCTURE:
1. HOOK — 2–3 sentences opening with the single most surprising number.
2. THE NUMBER — the one stat this piece stands on, stated plainly.
3. WHY IT'S REAL — the mechanism behind it (role, fixtures, minutes, price).
   This is the analytical meat. 2–3 short sections, each anchored to data.
4. WHAT WOULD CHANGE MY MIND — one honest falsifier, one clause of
   uncertainty, no hedging spiral.
5. SIGN-OFF — one sentence that lands the point.

OUTPUT FORMAT:
- Markdown.
- Start with 3 headline options (each ≤ 8 words, at least one playful).
- Then the draft, with [CHART: filename.png] placeholders where a visual
  belongs (max 2).
- End with a FACT-CHECK LIST: every number used, one per line, with the
  exact source field it came from (e.g. "75.1% — template.top_owned_by_position.FWD[0].ownership_pct").
  Numbers you could not source from the data must appear as [EDITOR: verify].

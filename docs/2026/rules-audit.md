# Rules audit — can this actually be explained?

Internal. Audits `rules.md` and the mechanics in `concept.md` against one question, and
evaluates the staged additive-bonus recommendation against the same standard.

## The metric

The repo already contains it. `alternatives-considered.md` rejected rising-landmark-value
partly because "**a team cannot work out its own score by hand, which they should always be
able to do.**" That is the standard, and it has not been applied to the design that was
actually chosen.

Stated fully, the test is:

> Can a team of ten freshmen — new to Hong Kong, new to each other, thirty minutes of
> briefing, no referee present, working in their second language of instruction — compute
> their own score at 14:00 and decide what to do next?

Two things make this stricter than it sounds. Teams are **unsupervised beyond their two
leaders**, so any rule that needs adjudication has no adjudicator. And scores land at
17:00, so a rule a team misunderstands at 11:00 is not discovered until the day is over.

## Result: the rules fail the test, in one specific place

### "Best 2 districts" is undefined, and the intuitive reading is wrong

`rules.md` says *"Pengali hanya berlaku untuk 2 distrik terbaik kalian."* Best by **what**?
Two readings are equally natural and they disagree. A real example from the current board:

| A team owning | Spend | Value | Gain |
|---|---|---|---|
| 3 landmarks in Admiralty | 30 | 54 | +24 |
| 2 landmarks in Causeway Bay | 40 | 56 | +16 |
| 2 landmarks in Central | 70 | 98 | +28 |

- **"My biggest districts"** (by value) → multiply Central + Causeway Bay = **184**
- **"My best districts"** (by gain) → multiply Central + Admiralty = **192**

The correct rule is the second: pick the two districts with the highest `spend × (multiplier
− 1)`. **That phrase appears nowhere in `rules.md`, and no participant will derive it.** The
intuitive reading costs this team 8 points, and the error is invisible until closing.

This is not a wording problem that a better sentence fixes. Ranking districts by gain
requires computing every district's gain first — which is the whole calculation, done twice.

### The rest of the arithmetic a team must do

To answer "what is our score right now?" a team needs to: track cash across four income
streams and every purchase at ladder prices; recall each landmark's **face value** as
distinct from what they paid; group landmarks by district; count each group; apply a
four-row multiplier table; **rank districts by gain**; multiply two of them; add the rest at
face value; add remaining cash.

Nine steps, one of which is undefined. In practice no team will do this, which means **no
team can course-correct**, which means the design's feedback loop does not close.

## Concept inventory

Twenty-three things a participant must hold. Ranked by cognitive cost against design value.

| # | Concept | Cost | Value | Verdict |
|---|---|---|---|---|
| 1 | 150 KD starting allowance | low | high | keep |
| 2 | Starting district, non-binding | low | med | keep |
| 3 | On-site task pays **30% of base price** | **med** | high | **simplify** — print the KD |
| 4 | Buy via Google Form | low | high | keep |
| 5 | Non-exclusive ownership | low | high | keep |
| 6 | Rising price, +25% per buyer | **med** | high | **keep mechanic, cut the arithmetic** |
| 7 | Price cap 2.5× | **med** | high | fold into 6 |
| 8 | First-buyer title | low | low | keep — costs nothing, pure flavour |
| 9 | Prices 10–70, farther = dearer | low | high | keep |
| 10 | Travel warning for far districts | low | high | keep |
| 11 | **A lone purchase scores nothing** | **high** | **critical** | keep — cannot be cut |
| 12 | Multiplier table, 4 tiers | med | high | **cut to 3 tiers** |
| 13 | **Best-2-districts cap** | **highest** | **none** | **CUT** |
| 14 | Landmarks outside best-2 at face value | high | none | cut with 13 |
| 15–18 | Post heats, par, payouts, optional | low | high | keep |
| 19 | 7 objects × 5 KD | low | med | keep |
| 20 | All members in photo | low | high | keep |
| 21 | 16:30 deadline | low | high | keep |
| 22 | Leftover cash counts 1:1 | low | high | keep |
| 23 | Final score formula, 3 terms | high | — | simplifies to 2 terms after 13 |

Concept 11 is the one genuinely hard idea that **must** survive — it is the entire design.
Everything else should be cheap enough to leave room for it.

## Verdict on the additive-bonus recommendation: it fails

The stack recommended in the previous round — multiplier + completion bonus + exploration
bonus — would leave participants holding **three separate district-counting rules** with
different thresholds and different caps:

| Rule | Qualifies on | Counted across |
|---|---|---|
| Multiplier | landmarks owned in a district | best **2** districts |
| Completion bonus | owning **2+** in a district | up to **3** districts |
| Exploration bonus | doing **1 task** in a district | up to **4** districts |

Three rules, three thresholds, three caps, all keyed on the same word. Against a briefing
that already has to land concept 11, this is not affordable. **Do not add either bonus as a
separate rule.**

The underlying goal — making breadth pay without coupling it to spend — is still valid. But
it should be bought by *removing* a rule, not adding two.

## Recommended cuts

### 1. Cut the best-2-districts cap — every district multiplies

The single highest-value change available, and it costs nothing.

- **Explainability:** removes the undefined ranking step, removes concept 14 entirely, and
  reduces the final-score formula from three terms to two.
- **Economically neutral.** The best affordable build is *identical* with and without the
  cap — 6 landmarks in 2 districts, score 473 — because **affordability already limits teams
  to about six landmarks**. The cap was never the binding constraint; money is.
- **Mildly pro-breadth, for free.** A team spread across three districts currently loses its
  third district's multiplier; uncapped it keeps it. That is exactly the breadth nudge the
  additive bonus was being considered for, obtained by deleting a rule instead of adding one.
- **It removes the hardest formula in the Sheet.** `operations.md` calls best-two selection
  "the hardest formula in the build and the most likely thing to be wrong on the day."

The stopping point is not lost. Time and money bind at ~6 landmarks regardless, and with
tiers capped at 3 the marginal return already falls after the third landmark in a district.

### 2. Cut the ×2.2 tier — multiplier becomes `1.0 / 1.4 / 1.8`

Already staged as open item 14, and it closes open item 12 at the same time. One less row to
read, the `4 atau lebih (distrik lengkap)` ambiguity disappears, and it introduces the
diminishing return that gives the fourth landmark in a district a reason not to be bought.

### 3. Print task income as a number, not a percentage

*"sekitar 30% dari harga landmark tersebut"* asks every team to do arithmetic at every
landmark. The value is already fixed and known — put the KD figure next to each landmark on
the printed price list and map. Same mechanic, zero calculation.

### 4. Keep rising prices, but stop asking teams to compute them

The mechanic is load-bearing (`economy.md`) and self-limits the far-district sweep. The
*arithmetic* is not: a team cannot know its position in the ladder without checking the
board anyway. Reframe as "the price rises once others have bought — **the board shows
today's price**," and drop +25% and 2.5× from the participant rules. Both stay in the Sheet.

### 5. Add nothing

No completion bonus, no exploration bonus, no route bonus.

## What this leaves

Score becomes:

```
Nilai akhir = sisa uang + Σ(nilai per distrik × pengali)
```

Two terms, no ranking, no exceptions. A team can compute it at 14:00 on the back of the map.

Concept count drops from 23 to about 18, and the two most expensive non-essential concepts
(13 and 14) are the ones removed — leaving briefing room for concept 11, which is the one
that actually has to land.

**The core design is untouched.** Depth still pays, clustering is still the whole game,
distance compensation is intact, and the 5–6 landmark target is unchanged. Every cut here is
to the *explanation*, not the economy — with the single exception of the ×2.2 tier, which was
already scheduled for removal on independent grounds.

## Still unresolved

**Concept 11 remains the risk.** "Buying one landmark changes nothing" is counterintuitive,
it is the foundation of the scoring, and no simplification removes the need to teach it.
`concept.md` already flags this. The audit's recommendation is to spend the briefing budget
freed by cuts 1–4 on this one idea, and to test it in stage 2 of the design interview
(`playtest.md`) before printing.

# Simulated playtest

> Internal. Replaces the *economic* half of `playtest.md`'s already-reduced plan. The
> committee is away for the summer (2026-08-18) and the design interview scheduled for
> Sat 22 Aug will not happen either — there is no respondent. This document does not
> pretend to replace it. It answers the numeric questions in `economy.md`'s "What the
> playtest must measure" and `playtest.md` Part 3 by simulation instead of by observation,
> and says plainly which questions a simulation cannot touch.

**Update 2026-08-18 — Item 11 has since been applied.** See "Update — applied 2026-08-18"
at the end of this document for what changed and why. Everything below this point is the
original report as written before that decision, kept intact so the reasoning stays
traceable — the findings drove the decision, not the other way around. Every other open
item in `operations.md` remains unchanged.

**Stale as of 2026-09-04 — budget parameter no longer matches the confirmed rundown.**
Every result below was generated with a 270-minute exploration budget (the "270-minute
budget" bullet under `## Method`). `operations.md` item 1 closed the same day with confirmed venue times
that put live exploration at ~4h10m (250 minutes), not 270 — a ~7% reduction. The result
tables and any conclusion drawn from them (far/near gap size, completion rates, the
farm-and-leave comparison) have not been regenerated against the new budget. See
`operations.md` open item 27 before relying on this document for any further pricing
decision.

## What this replaces, and what it doesn't

`playtest.md`'s design interview (Part 2) had five stages. Stages 4 and 5 (dwell-time
range-finding, red-teaming for unmodelled failure modes) need a human improvising, and stage
4's own methodology notes it produces an estimate, not a measurement — no simulation
improves on that, so those remain open exactly as `playtest.md` already records.

**Stages 1–3 are not attempted here at all.** They test whether a first-time reader of
`rules.md` discovers district-clustering and side-crossing *unprompted*, and whether the
score-neutral trap lands. That is a question about reading comprehension, not arithmetic.
A simulated agent that "reads" the rules is really just the code that was written to
implement them — asking it whether it understood them is circular. The "naive" archetype
below is a labelled **guess** at what low-comprehension play looks like economically, so
that its consequences can be measured; it is not a substitute for finding out whether real
players actually play that way.

What *is* attempted: the six numbered questions under `economy.md`'s "What the playtest
must measure" and the unknowns table in `playtest.md` Part 3, to the extent they are
economic rather than comprehension questions.

## Method

`scripts/simulate_playtest.py` runs a discrete-event Monte Carlo of the 25-team day. It is
read-only against `data/landmarks.csv` and `data/districts.csv` — no data file changed.

- **25 teams**, round-robin starting district over the 8 nearest districts
  (`operations.md`).
- **270-minute budget** (10:30–16:30 minus lunch).
- **Six archetypes**, chosen to mirror the specific builds `economy.md` already
  hand-analyzed rather than invent new ones: `near_crossing` and `far_crossing` (both
  2+2+2 across 3 districts / 2 sides, one cheap-anchored and one expensive-anchored),
  `same_side_cluster` (3 districts, 1 side — the discoverability failure `rules.md` warns
  about), `single_district_sweep` (the East Kowloon sweep-and-stop scenario),
  `greedy_adaptive` (no fixed list — buys the cheapest pair in the nearest un-held district
  each step, preferring to cross sides once holding one), and `naive` (buys by raw
  proximity, no deliberate pairing).
- **Three population mixes** (optimistic / base / pessimistic) varying how many of the 25
  simulated teams get each archetype — standing in for the unmeasured comprehension rate.
- **All 25 teams' purchase attempts are pooled and replayed in chronological order**, so
  the price ladder (`base × MIN(2.5, 1 + 0.25 × prior_buyers)`) reflects real cross-team
  contention. This is the one thing a hand-computed single-team example in `economy.md`
  structurally cannot do, and it is where the more interesting findings below come from.
- **200 runs per (dwell, mix) cell**, 9 cells, ~45,000 simulated team-days total.

### Assumptions, stated plainly (per `playtest.md`'s own discipline)

| Assumption | Value / method | Confidence |
|---|---|---|
| Dwell time per landmark | Triangular, mode swept at **20 / 25 / 35 min** | **Unmeasured — this is the whole point of the sweep** |
| Intra-district hop | ~8 min ± variance | `economy.md`'s own illustrative figure |
| Inter-district travel | `\|Δeta_from_bni_min\|`, floor 15 min | Approximation — no landmark-to-landmark matrix exists in the data |
| Task income | 30% of base, rounded to nearest 5, on arrival | From `rules.md`, not assumed |
| Object bonus | Lump sum, mean 20, cap 35 KD | Modelled, not walked per-object |
| Post-heat win rate | 50/50 head-to-head | **Assumed — `playtest.md` itself says this can't be read off a small day** |
| Population mix (comprehension) | Swept across 3 scenarios | **Unmeasured — stands in for the cancelled Stages 1–3** |

The scoring engine itself is not an assumption: `sanity_check()` in the script reproduces
`economy.md`'s literal worked example (Man Mo Temple + PMQ + KJRI + Victoria Park + United
Centre + Pacific Place, 120 KD → 168 same-side / 216 crossing) before any stochastic run is
trusted.

## Results

All figures below are from the **base** population mix unless stated; the dwell sweep
(20/25/35 min) is reported per finding since that's the axis that moves them.

### 1. Does a team finish with 5–6 landmarks?

Depends entirely on which build and on dwell time — and the "reliably hits 6" answer only
holds for the two fixed-list, near-anchored/mid-anchored archetypes:

| Archetype | Plan-completion rate (dwell 20/25/35) | Landmarks owned (mean) |
|---|---|---|
| `near_crossing` | 92% / 91% / 6% | 5.9 → 5.1 |
| `same_side_cluster` | 100% / 100% / 8% | 6.0 → 5.1 |
| `far_crossing` | **1% / 1% / 0%** | 4.2 → 3.4 |
| `single_district_sweep` | 31% / 34% / 23% | 2.3 |

**The expensive far-anchored build essentially never finishes its own 6-landmark plan.**
Under real 25-team contention on East Kowloon and Kai Tak's small, expensive landmark
pools, the price ladder climbs faster than a single hand-computed example shows — `far_crossing`
tops out around 3–4.6 landmarks, not 6, in every scenario tested. This is a genuinely new
finding: the desk analysis in `economy.md` computed the far build's affordability margin
against *one* team buying at first-buyer prices; at 25 teams competing for the same 3
East Kowloon and 4 Kai Tak landmarks, the ladder itself becomes the binding constraint, not
just the allowance.

### 2. Does time bind before money, or the reverse?

This is the single most dwell-sensitive finding in the whole exercise:

| Dwell mode | Time-bound | Money-bound | Plan-completed |
|---|---|---|---|
| 20 min | 29% | 26% | 46% |
| 25 min | 35% | 25% | 41% |
| 35 min | **88%** | 22% | **6%** |

At the low end of the plausible dwell range the two constraints are roughly balanced. At
35 minutes — well within `playtest.md`'s "20–40 min" uncertainty band — **time dominates
overwhelmingly** and almost nobody finishes their intended build. Whether the 5–6 landmark
target pace is achievable at all hinges on where real dwell time lands in that range, and
this remains genuinely unmeasured (see Limitations). If leaders start timing real visits on
the day, this is the number to compare against.

### 3. Can a team that wins no heats still complete two districts?

**Yes, robustly.** 34% of simulated teams never intersect a post's anchor district at all
(see finding 6) and so earn zero post income across the whole day. Of those teams, **68–71%
still hold 2 or more districts** by day's end, across all three dwell settings. The
allowance-plus-task-income safety net described in `economy.md` ("do not cut the allowance
below three landmarks' worth") holds up under simulation.

### 4. Is the endgame spend-down interesting, or does everyone hoard cash?

| Dwell mode | Median cash left | P90 cash left |
|---|---|---|
| 20 min | 46 | 96 |
| 25 min | 54 | 110 |
| 35 min | 72 | 133 |

There is real leftover cash to make a decision about — for a meaningful share of teams,
tens to over 100 KD. But the mechanism driving it skews toward **running out of time to
spend**, not a deliberate stop-and-hoard choice: leftover cash rises with dwell time, i.e.
with how time-constrained teams are, not independently of it. The design intent (a genuine
end-of-day spend-or-hold decision) and the simulated behaviour (forced hoarding when time
runs short) are both present, but the balance between them shifts hard toward "forced" as
dwell time rises — another reason the dwell-time unknown matters more than any other input
tested here.

### 5. Do expensive districts dominate, and by how much?

**Yes, and the gap survives 25-team contention** — this is the finding most relevant to
Item 11.

| Archetype | Mean spend | Mean score | Money-bound rate |
|---|---|---|---|
| `near_crossing` | 145–163 | 150–177 | 8–14% |
| `far_crossing` | 236–252 | **255–269** | **99–100%** |
| `same_side_cluster` | 151–175 | 167–174 | 0% |
| `single_district_sweep` | 189–192 | 256–259 | 66–83% |

`far_crossing` outscores `near_crossing` by **90–105 points**, spending 85–105 KD more to
get there, consistently across all three dwell settings — even though it is money-bound
essentially 100% of the time and never completes its own plan (finding 1). Gain still tracks
spend at roughly 1:1 at the same multiplier tier, which is exactly the "multiplier is
multiplicative" mechanism `economy.md` already named. Adding real cross-team price
contention did not close this gap; it just changed *how* the far build pays for its lead
(fewer landmarks at a worse ladder position, rather than the full planned six).

Separately, at the population level (all archetypes mixed), **teams that crossed a side
scored 22–37 points higher on average than teams that didn't**, consistently across all
three dwell settings — the same-side cap is doing real, measurable work. Both things are
true at once: the cap fixed the specific "3 cheap HK-Island districts" exploit it targeted,
but it does not fully neutralize the separate multiplicative-spend effect that the
compressed price table (`economy.md`, staged but not in effect) was built to address. Per
`economy.md`'s own pre-registered decision rule, this result sits on the "apply the
compressed table" side, not the "leave prices alone" side — recorded here for the record,
**not applied**.

### 6. Do far-travelling teams get as much post-heat exposure as near ones?

Reframed as **exposure** (time budget and route overlap with a post's anchor district), not
win rate — `playtest.md` already notes win rate can't be read off a small day, and this
simulation assumes a flat 50/50 win rate rather than measuring one.

The real driver turned out to be **route overlap with a post-anchor district (Admiralty /
West Kowloon / Kai Tak), not distance from base**:

| Archetype | Post-exposure rate |
|---|---|
| `far_crossing` (includes Kai Tak) | 100% |
| `same_side_cluster` (includes Admiralty) | 100% |
| `naive` (drawn toward the nearest landmarks, incl. Admiralty) | 100% |
| `greedy_adaptive` | 80–82% |
| `near_crossing` (Sheung Wan + Causeway Bay + TST Central) | **0%** |
| `single_district_sweep` (East Kowloon — not a post-anchor district) | **0%** |

**This is the one genuinely new, non-obvious finding.** The exact near-crossing build used
as the worked example in `economy.md` and `rules.md` — Sheung Wan + Causeway Bay + TST
Central — never passes Tamar Park, M+, or Kai Tak Stadium. A team that copies that example
literally gets zero post exposure for the whole day, which works against the social goal in
`game-posts.md` ("posts are the only place teams from different groups collide"). This has
nothing to do with far vs. near; it's specifically about whether the chosen districts
include one of the three post-anchor districts. Cheapest fix, if the committee wants one:
swap the worked example's third district for one that anchors a post (Admiralty itself, or
West Kowloon), which doesn't change its score properties at all — Admiralty and TST Central
are similarly priced.

## Limitations

- No comprehension test. The naive archetype and the three population mixes are informed
  guesses standing in for Stages 1–3, not evidence about how real freshmen read `rules.md`.
- Dwell time is swept, not measured. Every finding above that depends on the time/money
  balance (findings 1, 2, 4) should be read as "here's how the answer moves across the
  plausible range," not as a single number to plan around.
- Post-heat win rate is assumed at 50/50, not modelled from any skill distribution.
- Inter-district travel time is approximated from the eta-from-base figures already in
  `landmarks.csv`, not a real point-to-point matrix — a genuine matrix (or leader-reported
  times on the day, per `operations.md`) would sharpen findings 1, 2 and 4 in particular.
- The Sheet/Form load test that `playtest.md` also called for (concurrent buy submissions,
  25-sequential-buyer price-cap check, the 2+2+2+stray `Standings` case) is **not** covered
  by this pass — it's a correctness check on the ledger implementation, not a behavioural
  question, and needs the actual Sheet/Form to test against once built (`operations.md` item 3).

## Recommendation (not applied)

Three independent signals now point the same direction on Item 11:

1. The same-side cap is doing its job (finding 5, crossed vs. not-crossed gap).
2. The far build essentially never completes its own plan under contention (finding 1) —
   so it isn't a clean "land grab," the affordability brake described in `economy.md` bites
   hard in practice.
3. **But** the residual multiplicative-spend gap between `far_crossing` and `near_crossing`
   is still 90–105 points, wider than `economy.md`'s original desk estimate, and it holds up
   at every dwell setting tested (finding 5).

Read together, this leans toward reconsidering Item 11's "likely discard" default rather
than confirming it — the compressed price table would compress exactly this residual gap
without touching the same-side cap that's already working. That reading rests on assumed
dwell time, an assumed 50/50 post-win rate, and an unmeasured comprehension mix, so it is
offered as evidence, not a verdict. The decision stays with the committee.

## Reproducing this

```
python3 scripts/simulate_playtest.py --sanity          # verify the scoring engine first
python3 scripts/simulate_playtest.py --runs 200 --out /path/to/summary.json
```

## Update — applied 2026-08-18

The recommendation above was acted on the same day it was written. Full record in
`economy.md`'s calibration log; summarized here for continuity with the rest of this
document.

**First attempt, reverted.** `economy.md`'s originally staged transform —
`p' = 30 + 0.75×(p−30)` across the *whole* price range — was applied and re-simulated
before writing anything up. It made the problem worse, not better: raising every 10-KD
landmark to 20 KD (a 100% increase, with the 150 KD allowance untouched) collapsed
near-crossing's own plan-completion rate from 85–98% down to 15–27%, while far-crossing's
cost barely moved (its East Kowloon saving was cancelled by its TST Central landmarks also
hitting the new 20 KD floor). The score gap widened. Reverted before any documentation was
updated to reflect it.

**Second attempt, applied.** A top-only transform — `p' = p` for `p ≤ 30`, else
`p' = 30 + 0.45×(p−30)` — leaves every landmark near-crossing's build uses completely
untouched, and only discounts the four districts above the threshold. Re-simulated across
all nine (dwell × comprehension-mix) scenarios before finalizing:

| Metric | Pre-compression | Applied (ratio 0.45) |
|---|---|---|
| far−near score gap (mean, 9 scenarios) | 90–122 | **62–85** (↓ 25–37%, every scenario) |
| near-crossing plan-completion rate | 85–98% (6–10% at 35 min dwell) | **unchanged** |
| crossed-vs-not-crossed score gap | 22–37 | 24–45 (unaffected, cap still working) |
| East Kowloon best-3, hand-computed score | 299 | **255** |
| Sweep-vs-far, hand-computed comparator | sweep loses by 29–46 | sweep loses by 31–73 (widens) |
| Sweep-vs-far, *simulated* under contention | sweep ties/wins 3–4 of 9 scenarios | sweep ties/wins ~3 of 9 (narrowed, not closed) |

Two other ratios were tested and rejected before settling on 0.45: **0.6** produces
byte-identical near/far/sweep simulation results to 0.45 (neither archetype touches the
specific landmarks the two disagree on), so 0.45 dominates it — same effect, more price
texture preserved. **0.35** narrowed the sweep residual further (down to 2 of 9 scenarios)
but collapsed East Kowloon's price to the same level as Kai Tak's most expensive landmarks,
erasing a distinction `economy.md` treats as intentional — rejected on that basis alone,
independent of the numbers.

**The sweep-and-stop residual is real and was not fully closed by design, not oversight.**
It's driven by time-immunity (0% time-bound across every scenario and every ratio tested,
because it's the only archetype that never needs inter-district travel), not by price
level, so no price lever fully closes it. The user explicitly declined a mechanical
travel-time rule for this. The intended mitigation is non-mechanical: a leader-briefing
addition (`operations.md`) noting that a team parked in one far district all day is playing
a legitimate but non-winning strategy — the same channel already used for the other
comprehension risks the design can't enforce structurally ("two landmarks per district,
then move on"; "a stranded team should farm tasks, not buy").

Runs entirely from `data/landmarks.csv` and `data/districts.csv`; `scripts/verify.py`
passes unchanged before and after, since this script never writes to `data/`.

## Side-count experiment (sides_required=3) — evaluated 2026-08-19, not applied

The committee floated requiring **3 of 3 sides** (instead of the live 2 of 3) to reach
×1.6/×1.8, to push teams toward the East Kowloon side — specifically **Kai Tak**, which is
walkable and hosts Post 3, unlike the separate, MTR-hop-heavy "East Kowloon" district on the
same side. This section evaluates that idea. **Not applied** — `rules.md` and this
document's live rule text are unchanged.

**Method.** `simulate_playtest.py` gained a `sides_required` parameter (default 2, so every
existing invocation is unaffected) threaded through `score_team`, `simulate_one_run`, and
`run_scenario`, plus a new `--sides-required N` flag. Critically, **none of the 6 existing
archetypes ever span all 3 sides** — `near_crossing`/`far_crossing` top out at 2, the rest at
1 — so a new archetype, `three_side_crossing` (2+2+2 across Sheung Wan + TST Central + Kai
Tak, 140 KD, deliberately routed through the Kai Tak post-anchor district), was added so the
experiment measures something real instead of just capping everyone who never attempted a
3rd side. A `--compare-crossing` flag runs it head-to-head against `near_crossing` (today's
best 2-side strategy) as a standalone 50/50 mix. Both `sides_gap()` (formalizing finding 5's
crossed/not-crossed comparison) and two new `summarize()` fields
(`got_post_income_frac`, `sides_touched_frac`) were added to make the comparison automatic
rather than hand-computed. All runs use `--runs 200 --seed 42`.

**Regression check.** `--sanity` and a plain `--runs 200 --seed 42` rerun (default
`sides_required=2`) reproduce this document's recorded numbers — e.g. the far−near score gap
lands at 62–77 points across the three dwell modes, inside the 62–85 range recorded in the
"Update — applied 2026-08-18" section above.

**Population-wide cost of a hard requirement.** Rerunning the existing 6-archetype sweep at
`sides_required=3` (base mix, `score_mean` at dwell 20/25/35):

| Archetype | ×1.8-eligible sides today? | score (sides_required=2) | score (sides_required=3) |
|---|---|---|---|
| `near_crossing` | 2 sides | 180 / 176 / 149 | **150 / 147 / 147** |
| `far_crossing` | 2 sides | 242 / 245 / 227 | **225 / 227 / 227** |
| `greedy_adaptive` | up to 2 sides, stochastic | 253 / 240 / 222 | **213 / 213 / 213** |
| `same_side_cluster` | 1 side (already capped) | 166 / 167 / 174 | 166 / 167 / 174 (unchanged) |
| `single_district_sweep` | 1 side (already capped) | 234 / 238 / 236 | 234 / 238 / 236 (unchanged) |
| `naive` | 1 side (already capped) | 210 / 214 / 217 | 210 / 214 / 217 (unchanged) |

Confirms the mechanism exactly: every archetype that currently benefits from 2-sides
crossing loses 15–40 points, `plan_completed_frac` is untouched (the drop is pure multiplier
penalty, not a change in what teams can afford), and the already-capped archetypes are
unaffected. Across the full population (all 6 archetypes, base mix), `sides_gap(results, 3)`
reports **`crossed_frac` = 0.0 at every dwell mode** — under today's realistic mix, literally
no team ever holds districts across all 3 sides. A hard requirement would, in effect, remove
the ×1.6/×1.8 tier entirely for the population as currently modelled.

**Does the 3-side strategy work if a team actually attempts it?** `three_side_crossing` vs.
`near_crossing`, 50/50 mix, `--compare-crossing`:

| Archetype | sides_required | score | plan_completed | money_bound | got_post_income | sides_touched: 2 / 3 |
|---|---|---|---|---|---|---|
| `three_side_crossing` | 2 | 206 / 206 / 195 | 0.21 / 0.21 / 0.01 | 0.79 / 0.79 / 0.66 | **1.00 / 1.00 / 0.99** | 0.79 / 0.21 (dwell 20–25); 0.99 / 0.01 (dwell 35) |
| `three_side_crossing` | 3 | 193 / 193 / 181 | 0.21 / 0.21 / 0.01 | 0.79 / 0.79 / 0.66 | 1.00 / 1.00 / 0.99 | (same distribution — sides_required doesn't change purchases) |
| `near_crossing` | 2 | 157 / 157 / 137 | 0.78 / 0.78 / 0.07 | 0.22 / 0.22 / 0.00 | 0.00 / 0.00 / 0.00 | all at 2 sides |
| `near_crossing` | 3 | 132 / 132 / 135 | 0.78 / 0.78 / 0.07 | 0.22 / 0.22 / 0.00 | 0.00 / 0.00 / 0.00 | all at 2 sides |

(columns are dwell 20 / 25 / 35)

**A team built specifically to attempt 3-side crossing only actually completes it 1–21% of
the time.** The rest stall at 2 districts — Sheung Wan + TST Central bought, Kai Tak not —
because Kai Tak's 4 landmarks are all priced at the board's top tier (40 KD each) and scarce
under 25-team contention, so the price ladder climbs past what most teams can afford before
they reach it (`money_bound_frac` 66–79%, vs. `near_crossing`'s 0–22%). Under
`sides_required=3`, the majority that stall at 2 districts get the ×1.4 cap instead of the
×1.6 they'd have gotten today for the same 2-district result — which is why
`three_side_crossing`'s own score *drops* under the harder rule despite being the strategy
the rule is meant to reward.

**One genuinely encouraging result: post exposure doesn't require completing Kai Tak.**
`got_post_income_frac` is ~100% for `three_side_crossing` even in the 66–79% of runs that
never finish buying both Kai Tak landmarks — the post-income event fires on first visiting
the district, not on holding it. This decouples the two goals the committee was conflating:
getting a team to *pass through* a post-anchor district (the actual social goal) doesn't
require them to *win* the district-holding multiplier there.

**Verdict.** A hard 3-of-3-sides requirement looks too punishing to adopt as-is: it would
strip the ×1.6/×1.8 tier from the entire current population (nobody reaches 3 sides today)
while giving the archetype built to chase it only a 1–21% success rate, gated by Kai Tak's
price/scarcity rather than by effort or comprehension. It would very likely read as "the
multiplier tier basically disappeared" on the day. Two directions worth exploring instead,
neither simulated in this pass:

1. **Cheapest fix, already flagged (finding 6, above):** since post exposure only needs a
   team to *route through* a post-anchor district, not hold it, retarget the worked examples
   in `rules.md`/`economy.md` to a build that already passes a post (Admiralty or West
   Kowloon), which needs no scoring change at all.
2. **If the committee still wants a scoring incentive for a genuine 3-side spread**, a
   *bonus* tier layered on top of the existing 2-sides floor (e.g. an extra bump for 3 sides,
   without capping teams that stop at 2) would reward the achievement without penalizing the
   entire population that doesn't attempt it — but this only becomes viable once Kai Tak's
   affordability is addressed (price or scarcity), since right now most attempts fail on
   money before they fail on comprehension or time.

This entry is measurement only — `rules.md` is unchanged, and no participant-facing document
should change until the committee decides whether to pursue either direction above.

Reproduce with:
```
python3 scripts/simulate_playtest.py --sanity
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --out baseline.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-required 3 --out sides3.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-required 2 --compare-crossing --out crossing2.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-required 3 --compare-crossing --out crossing3.json
```

## Bonus-tier experiment (sides_bonus, layered on the 2-sides floor) — evaluated 2026-08-19, not applied

The verdict above flagged a softer alternative worth testing: instead of *requiring* 3
sides to reach ×1.6/×1.8 (which punishes the entire population that never attempts it), add
a **bonus** multiplier for teams that do reach all 3 sides, layered on top of the existing
2-sides floor — so nobody's score goes down, only genuine 3-side achievers get a bump. This
section tests that. **Not applied** — same status as the section above.

**Method.** `score_team` gained `sides_bonus_multiplier` (default `None`, disabled) and
`sides_bonus_threshold` (default 3, the only threshold that means anything with 3 sides
total). When enabled, the bonus is applied as `multiplier = max(multiplier, bonus)` *after*
the existing floor logic — it can only raise a team's multiplier, never lower it. Wired
through the same call chain as `sides_required`, plus a `--sides-bonus VALUE` flag. All runs
`--runs 200 --seed 42`, `sides_required=2` (today's live floor, not the rejected hard-3
variant above).

**Confirmed non-punishing.** Rerunning the existing 6-archetype sweep with `--sides-bonus
2.0` against the unmodified baseline: 5,398 of 5,400 archetype/scenario score means are
bit-for-bit identical. The only two that moved are `greedy_adaptive` at two dwell/mix cells,
by **+0.1**, consistent with the stochastic "prefer crossing to a new side" heuristic
occasionally landing that archetype on all 3 sides by chance. This is exactly the intended
shape: a bonus tier can only help, and today it almost never triggers.

**Bonus magnitude vs. completion rate, `--compare-crossing` (`three_side_crossing` vs.
`near_crossing`, 50/50 mix, dwell 20 / 35):**

| `sides_bonus` | `three_side_crossing` score | vs. no bonus (206 / 195) | `near_crossing` score |
|---|---|---|---|
| none (disabled) | 206 / 195 | — | 157 / 137 |
| 2.0 | 212 / 195 | +6 / +0 | 157 / 137 |
| 2.2 | 218 / 195 | +12 / +0 | 157 / 137 |
| 2.5 | 227 / 196 | +20 / +1 | 157 / 137 |
| 3.0 | 241 / 196 | +35 / +1 | 157 / 137 |

**The bonus's own marginal effect is small next to an effect that was already there.**
`three_side_crossing` already outscores `near_crossing` by ~50 points with the bonus
*disabled* — the same multiplicative-spend mechanism flagged in Item 11 (finding 5, above):
it's simply a more expensive build. Isolating the bonus's own contribution (subtracting the
no-bonus score), the marginal gain scales almost exactly as
`completion_frac × (bonus − 1.8) × total_value` — at dwell 20/25 (21% completion), a bonus of
3.0 adds +35 points; at dwell 35 (1% completion), even a 3.0× bonus adds essentially nothing.
**The bottleneck is the completion rate, not the bonus size.** Because most attempts stall at
2 districts (Kai Tak's landmarks are priced at the board's top tier and scarce — see the
section above), raising the bonus mostly pays out to the same ~1 in 5 teams that were already
going to complete it; it doesn't pull more teams into finishing the 3-side build.

**Verdict.** A bonus tier is the safer of the two designs — confirmed non-punishing, and a
value like 2.0–2.5 gives a real, visible reward to a team that pulls off a genuine 3-side
spread without touching anyone else's score. But on its own it is unlikely to change much
observable behaviour on the day: so few teams currently attempt or complete a 3-side build
that the bonus condition would trigger for a small minority regardless of its size. If the
committee wants the bonus to actually shift behaviour (more Kai Tak traffic, not just a
reward for the few who'd have gone anyway), it likely needs to be paired with something that
raises the completion rate itself — e.g. Kai Tak-specific price relief or an object bonus
sited there — rather than adopted alone. Recommend evaluating a bonus tier together with a
Kai Tak affordability change, not as a standalone rule, if this direction is pursued further.

This entry is measurement only — `rules.md` is unchanged.

Reproduce with:
```
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-bonus 2.0 --out bonus.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-bonus 2.0 --compare-crossing --out bonus_crossing2.0.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --sides-bonus 3.0 --compare-crossing --out bonus_crossing3.0.json
```

## Kai Tak price-relief experiment — evaluated 2026-08-19, not applied

Both experiments above converged on the same bottleneck: Kai Tak's 4 landmarks are all
priced at the board's top tier (40 KD) and scarce under 25-team contention, so most attempts
to hold it stall on money, not time or comprehension. This tests the fix they pointed at —
discounting Kai Tak specifically — the same way `economy.md`'s Item 11 compression was
tested before being adopted. **Not applied** — same status as the two sections above, and
**`data/landmarks.csv` is untouched**: this is an in-memory experiment only.

**Method.** `load_board()` gained a `kai_tak_discount` parameter (default `1.0`, no
change) and a `--kai-tak-discount RATIO` flag. When set, it multiplies *only* Kai Tak's
`base_price` by the ratio, rounded to the nearest 5 KD, before the simulation runs — the
separate "East Kowloon" district (same side, different district, already flagged as the
non-walkable one) is untouched, as is every other price in `data/landmarks.csv`. `sanity_check()`
still calls `load_board()` with no arguments, so it keeps testing the live, undiscounted
board regardless of this flag. Swept `--kai-tak-discount` at 0.85 / 0.7 / 0.55 (15% / 30% /
45% off), `--runs 200 --seed 42`, `sides_required=2` (today's live floor, no hard-3
requirement), no bonus unless noted.

**Effect on `far_crossing`** (the existing archetype that already routes through Kai Tak,
base mix, dwell 20 → 35):

| Discount | `plan_completed_frac` (dwell 20) | `money_bound_frac` (dwell 20) | `plan_completed_frac` (dwell 35) |
|---|---|---|---|
| none | 4% | 96% | 0% |
| 0.85 | 7% | 93% | 0% |
| 0.70 | 11% | 89% | 0% |
| 0.55 | 16% | 84% | 0% |

**Effect on `three_side_crossing`** (`--compare-crossing`, sides_touched=3 completion rate):

| Discount | `plan_completed_frac` (dwell 20/25) | `money_bound_frac` (dwell 20/25) | score (dwell 20/25) |
|---|---|---|---|
| none | 21% | 79% | 206 |
| 0.85 | 25% | 75% | 203 |
| 0.70 | 31% | 69% | 200 |
| 0.55 | **50%** | 50% | 192 |

**Price relief works exactly as intended on the constraint it targets — and only that
one.** At dwell 20/25, a 45% discount roughly *doubles* both archetypes' completion rate
(far_crossing 4%→16%, three_side_crossing 21%→50%) by directly loosening the price ladder
that was blocking them. At dwell 35, where time — not money — is already the binding
constraint (established in finding 2, above), the discount barely moves
`plan_completed_frac` even though `money_bound_frac` still falls (three_side_crossing:
66%→33% at 0.55) — teams that would now be able to afford Kai Tak still run out of clock
before they get there. **Price relief is a fix for the money-bound failure mode, not a
substitute for the leader-briefing / timetable-nudge fix needed for the time-bound one.**

**Relief trades completion rate for score.** `three_side_crossing`'s mean score *drops*
slightly as the discount grows (206→192 at 0.55) even though completion roughly doubles —
cheaper Kai Tak landmarks mean less `total_value` to multiply, so a team that now completes
the build owns a build worth less. This is the expected, correct trade for a genuine
affordability fix, but it means price relief alone doesn't make the 3-side strategy look
more attractive by the score-comparison lens used elsewhere in this document — it makes it
more *reachable*, which is the actual goal, not more rewarding in isolation.

**Combining relief with the bonus tier recovers both.** `--kai-tak-discount 0.7
--sides-bonus 2.0` together: `three_side_crossing` completion rises to 31% (same as
discount alone) while score recovers to 207 — matching the no-discount baseline (206) instead
of the discount-alone score (200). The two levers are complementary, exactly as the bonus-tier
section's verdict predicted: the discount raises how many teams *can* finish, the bonus
restores what finishing is *worth*.

**Verdict.** Kai Tak price relief is the most directly effective lever tested across all
three experiments for the stated goal (more teams actually holding, not just passing
through, Kai Tak) — it moves the number the other two designs were bottlenecked on. A
30–45% discount roughly doubles completion at low-to-mid dwell time without any rules-text
change (a price update mirrors the existing `apply_price_compression.py --ratio` workflow
used for Item 11). Recommend, if this direction is pursued: (a) pair it with the bonus tier
rather than adopting either alone, since relief improves reach and the bonus restores reward;
(b) treat the dwell-35 case as evidence that a pricing fix cannot rescue time-bound teams —
that gap still needs the leader-briefing/timetable mitigation already used for the
sweep-and-stop residual (`economy.md`, 2026-08-18 entries); and (c) if adopted, apply it the
same way as Item 11 — via a real `apply_price_compression`-style script writing to
`data/landmarks.csv`, with the change and reasoning logged in `economy.md`'s calibration log,
not by leaving the discount as a simulator-only flag.

This entry is measurement only — `rules.md` and `data/landmarks.csv` are both unchanged.

Reproduce with:
```
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --kai-tak-discount 0.55 --out discount.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --kai-tak-discount 0.55 --compare-crossing --out discount_crossing.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --kai-tak-discount 0.7 --sides-bonus 2.0 --compare-crossing --out combo.json
```

## Kai Tak task-income boost experiment — evaluated 2026-08-19, not applied

Committee-proposed alternative to price relief: instead of discounting Kai Tak's landmarks
(which changes `base_price`, an input to `Standings`'s face-value calculation), boost the
**task income** rate specifically for Kai Tak — the flat "30% of base price, self-service via
the Form" cash a team earns just by visiting a landmark and doing its on-site task
(`rules.md` §2, `economy.md` "Income"). The stated motivation for this lever specifically:
task income lives on the `Board`/`Ledger` tabs, not `Standings`/`Ref`, so it might raise Kai
Tak's appeal without reopening the multiplier formula that was just verified (see the
bonus-tier section's operational-risk discussion, above). **Not applied.**

**The operational premise checks out.** `Standings`'s formula (`operations.md` line 137,
158–162) is `face value → districts held → sides → multiplier → property value → score` —
task income never enters it; it only adds cash on the `Ledger` tab. A Kai Tak-specific task
rate touches a `Board` column, not the `Standings`/`Ref` logic, so — unlike the bonus tier —
it would **not** require re-deriving or re-verifying the four hand-computed `Standings` test
cases in `operations.md`. This is the lightest-touch of the three levers tested.

**Method.** `TASK_INCOME_RATE = 0.3` (the live board rate, matching `rules.md`) and
`KAI_TAK_TASK_RATE` (default `None`) added; when set, `simulate_one_run` uses the override
rate only for Kai Tak's task-income events, everywhere else stays at 30%. New
`--kai-tak-task-rate RATE` flag. Swept 0.5 / 0.7 / 1.0, `--runs 200 --seed 42`,
`sides_required=2`, no discount, no bonus.

**Effect on `far_crossing` and `three_side_crossing`** (base mix / 50-50 crossing mix, dwell
20):

| `kai_tak_task_rate` | `far_crossing` score / completed | `three_side_crossing` score / completed |
|---|---|---|
| 0.3 (baseline) | 242 / 4% | 206 / 21% |
| 0.5 | 260 / 11% | 219 / 26% |
| 0.7 | 280 / 19% | 237 / 32% |
| 1.0 | 301 / 29% | 256 / 38% |

**This lever beats price relief on both axes it was measured against.** Price relief traded
completion for score (§ above: `three_side_crossing` at 0.7 discount → 31% completion but
score *fell* to 200). A task-income boost raises completion **and** score together — at a
comparable ~31–32% completion rate, task-rate 0.7 scores 237 versus discount 0.7's 200,
because it doesn't touch `total_value`/face value at all; the extra cash is pure addition,
either spent on more landmarks or banked as `cash_left`. At dwell 35 the same limitation as
price relief holds: `plan_completed_frac` barely moves (time, not money, is already binding),
though `money_bound_frac` still falls.

**But it reopens a different risk, not a smaller one — task income is earned independent of
purchase.** `rules.md` §2 is explicit: step 2 (do the on-site task, get paid) is separate
from step 3 (decide whether to buy). A team can visit every Kai Tak landmark, complete all
four tasks, and buy nothing.

### Farm-and-leave, quantified

Built a seventh archetype, `kai_tak_task_farm`, to measure this directly instead of
hand-estimating: it visits all 4 Kai Tak landmarks (collecting task income and the Post 3
anchor-district bonus, same as any other archetype that passes through) but the simulation
skips its `purchase_attempt` events entirely — it never buys. Added `time_used` (elapsed
minutes) and `kd_per_min_mean` (`(cash_left + spend − ALLOWANCE) / time_used`, i.e. total
income extracted per minute, spent or banked) to every archetype's summary, and a
`--farm-check` flag to run it standalone. `--runs 200 --seed 42`, dwell 20:

| Archetype | Buys anything? | Score (= final ranking value) | kd/min |
|---|---|---|---|
| `near_crossing` (the taught ×1.8 example) | Yes | 180 | 0.26 |
| `same_side_cluster` | Yes | 166 | 0.41 |
| `three_side_crossing` | Yes | 206 | 0.45 |
| `far_crossing` | Yes | 242 | 0.52 |
| **`kai_tak_task_farm`, rate 0.3 (today's live rate, no boost at all)** | **No** | **240** | **0.69** |
| `kai_tak_task_farm`, rate 0.5 | No | 280 | 1.00 |
| `kai_tak_task_farm`, rate 0.7 | No | 320 | 1.31 |
| `kai_tak_task_farm`, rate 1.0 | No | 360 | 1.62 |

**This is not only a risk of the proposed boost — at today's live, unboosted 30% rate,
task-farming Kai Tak and buying nothing already out-earns every legitimate buy-and-hold
archetype tested, including the strategy `rules.md`/`economy.md` teach as the canonical
×1.8 example.** `near_crossing` — the worked example the participant-facing rules are built
around — nets 0.26 KD/min and scores 180. A team that just walks to Kai Tak, does the 4
tasks, and leaves nets 0.69 KD/min and **scores 240 without ever holding a single district
or risking a single KD on the price ladder.** It takes ~130 of the day's 270 minutes, so a
team could do this *and then* also run a legitimate build with the time left over — it isn't
even a trade-off against buying, just a free addition to any strategy that happens to
include a Kai Tak trip.

This is because farm-and-leave stacks three things that are each individually reasonable —
task income, the object bonus (granted to every archetype regardless of route), and the Post
3 win/lose payout — with **zero** exposure to the price-escalation ladder that makes every
buying archetype's return look weak by comparison. Boosting the task rate doesn't create this
gap, it widens an existing one: at rate 1.0, farm-and-leave (1.62 KD/min) is closing in on
the ~2 KD/min figure that made *uncapped* post-farming unacceptable enough to need the
2026-08-18 cooldown fix, and even the modest 0.5 rate (1.00 KD/min) already sits above the
top of the "~1–1.3 KD/min legitimate play" range that fix was calibrated to land in.

**One modelling caveat, in the direction of understating the gap, not overstating it:** the
simulation charges post income no separate playing time — `game-posts.md` heats actually run
on a 15-minute clock. This applies uniformly to every archetype that touches a post-anchor
district, so it doesn't bias farm-and-leave specifically, but it means every `kd_per_min`
figure above is somewhat optimistic, farm-and-leave included.

**Verdict, revised.** The task-income-boost lever is still operationally the lightest of the
three (no `Standings`/`Ref` reopening). But the farming risk isn't a downside that only
appears once you push the rate up — it's already live at rate 0.3, already beats the taught
strategy, and boosting the rate only makes a pre-existing gap worse, not a new one appear.
Two separable questions for the committee, not one: (1) **should the task rate be boosted at
all**, given it directly amplifies an existing farm-beats-hold imbalance rather than a clean
slate; and (2) **independent of this lever, does farm-and-leave at today's 30% rate need its
own fix** — e.g. paying task income only on landmarks the team goes on to buy, or a
lighter-weight version of the post cooldown — since that finding holds with `kai_tak_task_rate`
left at its live, unboosted default. Recommend surfacing (2) to the committee regardless of
what happens with the boost proposal.

This entry is measurement only — `rules.md` and `data/landmarks.csv` are both unchanged.

Reproduce with:
```
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --kai-tak-task-rate 0.5 --out taskrate.json
python3 scripts/simulate_playtest.py --runs 200 --seed 42 --kai-tak-task-rate 0.5 --compare-crossing --out taskrate_crossing.json
```

## Decision — 2026-08-19: task-rate boost proceeds despite the farm-and-leave residual

Committee reviewed the "Farm-and-leave, quantified" finding above and considered the
obvious mechanical fix — pay task income only on landmarks the team goes on to buy — and
rejected it as too strict: it would convert `rules.md` §2's low-friction "do the task,
decide separately whether to buy" flow into a forfeit-your-earnings-if-you-don't-buy rule,
undermining the safety-net purpose task income is designed for (`economy.md`, finding 3 —
"the allowance-plus-task-income safety net... holds up under simulation").

**Checked whether either of the two other levers already tested closes the gap without a
purchase gate. Neither does:**

- **Price relief moves the wrong way.** Re-checking `three_side_crossing`'s score against
  farm-and-leave's fixed 240 (task rate left at the live 0.3, no boost): discount 0.85 → 203,
  0.7 → 200, 0.55 → 192. Cheaper Kai Tak landmarks mean less face value to multiply, so
  relief *widens* the farm-vs-hold gap, it doesn't close it — consistent with the
  "relief trades completion for score" finding in the price-relief section, above.
- **The bonus tier only ties on average, and only at an extreme value, and only by
  reopening the exact formula this lever was chosen to avoid.** Re-checking `sides_bonus`
  against the same 240.1 target: bonus 2.0 → 212, 2.2 → 218, 2.5 → 227, **3.0 → 240.9** — a
  ×3.0 "triple your money" tier is needed just to edge past farm-and-leave *on the
  population mean*, and since only 21–38% of attempts actually complete a 3-side hold, most
  individual teams following that build would still score below the farm-and-leave value
  even at bonus 3.0. Using the bonus tier to solve this would also mean reopening
  `Standings`/`Ref` anyway — the reopening the task-income lever was specifically chosen to
  avoid (see the bonus-tier section's operational-risk discussion, above).

**No natural, non-purchase-gated fix was found within those constraints.** Per the
committee's direction, the task-rate boost proceeds regardless of the residual, on the
basis that it doesn't create the farm-vs-hold imbalance — it's already live at rate 0.3 —
and the boost's own benefits (raises `three_side_crossing`/`far_crossing` completion,
doesn't touch `Standings`/`Ref`) stand on their own.

**Recommended rate: 0.5, not the full 1.0 swept earlier.** At 0.5, `three_side_crossing`
completion rises from 21% to 26% (most of the gain available), while the farm-and-leave
side effect grows more modestly — score 240→280, 0.69→1.00 KD/min — than at 1.0 (240→360,
0.69→1.62 KD/min, which starts to approach the ~2 KD/min figure that made uncapped
post-farming unacceptable in the first place).

**The farm-and-leave gap itself is carried forward as a separate, open, pre-existing risk —
not resolved by this decision.** It exists today at rate 0.3 and will grow somewhat once the
boost is applied at 0.5. Recommend the committee track it the same way the sweep-and-stop
residual is tracked (`economy.md`, 2026-08-18 entries): named, quantified, and accepted as a
known cost rather than silently left undocumented. Unlike sweep-and-stop, this one cannot be
waved off with a "legitimate but non-winning strategy" leader-briefing line, because it
currently *wins* — any non-mechanical mitigation would need to say something actually true
to participants, which briefing material can't do until the underlying gap is smaller.

**This decision is recorded here as a committee direction, not yet implemented.** No change
has been made to `rules.md`, the printed price list, or the live Sheet's `Board` tab — those
are separate follow-up steps (matching how Item 11's price compression was decided via
simulation first, then applied later via `apply_price_compression.py` as its own step).

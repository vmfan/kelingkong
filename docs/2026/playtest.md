# Validation before printing

> **Update 2026-08-18.** The design interview below (Part 2) did not happen either — the
> committee is away for the summer, and there is no respondent. Its economic questions
> (Part 3, and `economy.md`'s "What the playtest must measure") are answered instead by a
> Monte Carlo simulation in `simulated-playtest.md`. Stages 1–3 of the interview, which test
> whether a first-time reader discovers clustering/crossing from `rules.md` unprompted,
> remain genuinely open — a simulation cannot substitute for a human reading the rules cold.
> **Item 11 (the compressed price table) has since been applied** on the strength of the
> simulation's evidence — a residual 90–105 point far/near gap survived the same-side cap
> under realistic 25-team contention. See `simulated-playtest.md`'s "Update — applied
> 2026-08-18" section and `economy.md`'s calibration log for the full record, including why
> the first attempt at compression was reverted before this one was chosen.

Internal. Covers open item 7 in `operations.md`, and produces the input for item 11
(**closed 2026-08-18** — applied).

**There is no field run.** The committee does not have the time for one. What replaces it
is a desk analysis of the board — already done, findings below — plus a structured design
interview with one informed respondent. This document says what each can and cannot
establish, and what remains genuinely unknown on event day.

## Why the analysis is fixed in advance

`operations.md` records that the earlier "balanced within 3%" finding was wrong. It
credited near-strategy teams with an extra game-post win on an assumption never written
down, which Post 3's siting at Kai Tak Stadium undermines.

That was not a maths error. It was a premise introduced after the fact to explain a number.
Without a field run there is no data to discipline that habit, so the guard has to be
procedural: **conclusions below are recorded with their assumptions attached, and the
interview questions are written before the interview happens.** A respondent who is told
what answer would be convenient will supply it.

## Part 1 — Desk findings

> **Superseded, 2026-08-17.** Findings 2 and 3 below caused the set bonus to be rekeyed from
> depth to districts held, which resolved both. Finding 1 was not resolved by that rekey but
> has since been overtaken too: its archetypes (a 3-landmark far sweep vs. a 6-landmark near
> build) assumed depth-in-one-district still worked, and its gain figures (+168/+136) were
> computed at the retired ×1.8 depth tier. The same-side cap added later on 2026-08-17 also
> removes the sweep's reason to exist — see the update at the end of Finding 1. All three
> findings are kept because they are what prompted both changes.

These came from the board itself. None needed a playtest, and all three are more urgent
than the question the playtest was scheduled to answer.

### Travel time does not defend the balance — it worsens it

`economy.md` closes on the position that far districts lead by ~42 and that "the remaining
defences are travel time and the affordability brake, neither of which has been measured."

Travel time is not a defence. The far archetype buys **three** landmarks; the near archetype
buys **six**. Dwell time dominates travel, so the strategy that buys fewer, dearer landmarks
finishes earlier:

| Archetype | Spend | Gain | Time used | Spare of 270 min |
|---|---|---|---|---|
| Far — East Kowloon best-3 | 210 | +168 | 162 min | **108** |
| Near — Sheung Wan + Central 3+3 | 170 | +136 | 226 min | **44** |

*Assumes 25 min dwell per landmark, 8 min intra-district hop, return to base. Sensitivity:
near uses more time than far whenever `3 × dwell + 2 × hop > 33` — i.e. for any dwell above
about 8 minutes. The sign is not sensitive to the estimate.*

> **Update 2026-08-17 — the far archetype in this table no longer scores anything close to
> +168, and it isn't a 3-landmark build anymore.** Under the district-count multiplier, a
> single-district sweep is capped at ×1.4 (East Kowloon best-3: gain +84, not +168 — see
> `economy.md`, "The multiplier is multiplicative"). Under the same-side cap added later the
> same day, that cap holds regardless of depth, since Kai Tak and East Kowloon are both on
> the `East Kowloon` side. **The 3-vs-6-landmark asymmetry this finding rests on is gone**:
> reaching a competitive multiplier now costs 3 districts and 2 sides — 6 landmarks — for a
> far build exactly as it does for a near one. `economy.md`'s rebuilt comparison (same
> section) uses a 6-landmark far build instead: Kai Tak + East Kowloon + TST Central, 260
> spend, gain +208, but only 230 KD of realistic income against it — no slack, versus the
> matched near build's 120 spend, gain +96, 70 KD of slack. **The time-used columns above
> have not been re-derived for that 6-landmark far build** and should not be read as still
> current — a far build that must now visit 3 districts instead of 1 will use meaningfully
> more travel time than 162 minutes. Re-deriving this table is folded into the design
> interview (Stage 4) rather than re-estimated at the desk, since it depends on real
> inter-district travel, not just intra-district hops.

The far strategy scores 42 higher **and** has an hour more slack. Its real constraint is
cash: East Kowloon best-3 costs 210 against 150 allowance + 60 task income, leaving exactly
0. That affordability brake is the only thing holding it, which makes `economy.md`'s
warning about raising the allowance more load-bearing than it already looked.

### The stated optimum is not the optimum

`concept.md` says "the two-district cap makes the optimum roughly 3+3, matching the 5–6
target exactly." This does not hold. Marginal gain per KD spent rises with district count:

| Owned in district | Multiplier | Gain per KD |
|---|---|---|
| 2 | ×1.4 | 0.4 |
| 3 | ×1.8 | 0.8 |
| 4 | ×2.2 | **1.2** |

Because the return is *increasing*, completing a district is always the best KD available,
and **4+2 beats 3+3 on the same six landmarks** in four of five district pairs tested:

| Pair | 3+3 value | 4+2 value |
|---|---|---|
| Kai Tak + Admiralty | 360 | **512** |
| Mongkok + Sheung Wan | 324 | **370** |
| Sheung Wan + Central | 306 | **318** |
| TST Central + TST Waterfront | 198 | **218** |
| Causeway Bay + Central | **252** | 230 |

The exception holds only because Causeway Bay's fourth landmark is cheap enough that
completing it adds little.

The best affordable and time-feasible build found was **complete Kai Tak (×2.2) plus two
cheap landmarks nearby** — gain ~280, against the 168 and 136 the far/near comparison rests
on. Both compared archetypes are suboptimal, so **the +42 gap is measuring the wrong
contest.** Item 11 should not be decided on it until the comparison is rebuilt around
completion strategies.

This does not break the design — completion still means seeing one neighbourhood properly,
which is the goal. But the target pace, the "roughly 3+3" claim, and the balance analysis
all need restating around it.

### `rules.md` is ambiguous about what completes a district

`rules.md` line 65: `4 atau lebih (distrik lengkap)` — "4 or more (district complete)".
For the nine districts of 3 or 4 landmarks these coincide. For the four with **five**
(Central, TST Central, TST Waterfront, Whampoa–Hung Hom) they are different rules, and
teams will adopt whichever reading pays them.

Participant-facing and unresolvable by measurement — it is a decision. Recommended reading:
**×2.2 at 4 or more owned**, decoupled from completeness, because it keeps the multiplier
table uniform across districts of different sizes and avoids punishing teams for picking a
5-landmark district. Whichever is chosen, the parenthetical has to go.

## Part 2 — The design interview

One respondent who understands the concept, asked what she would do. She is a single
informed person, not a sample, so she cannot supply anything statistical or timed. She can
supply four things, two of them unobtainable any other way.

### Run it in this order — the order is the method

**Do not explain the intended strategy first.** Everything in stage 1 is destroyed by
telling her clustering is the point.

**Stage 1 — cold plan.** Give her only `rules.md`, the price list and a map. Ask for a
concrete plan: which landmarks, in what order, at roughly what times, and what she expects
to score. Concrete, not evaluative — "which would you buy" rather than "does this seem
balanced."

*What it measures:* whether the intended strategy is **discoverable** from the participant
rules alone. If someone who already understands the concept does not reach for district
clustering unprompted, 250 freshmen after a 30-minute briefing certainly will not. Strong
evidence one way: a failure here is decisive. A success is weaker — she has context they
won't.

Since 2026-08-17, `rules.md` also states the same-side cap and gives a worked cross-harbour
example, so this stage now additionally checks whether a cold read of the rules leads her to
cross sides unprompted, not just to cluster districts. A plan that holds three
same-side districts is now the specific failure mode to watch for — it means the cap didn't
land from the text alone and the leader briefing has to carry it instead.

**Stage 2 — the score-neutral trap.** Before explaining anything, ask what a team scores if
it buys one landmark in each of six different districts.

*What it measures:* the single comprehension risk `concept.md` already flags as looking like
a bug. The correct answer is "exactly what they spent — no gain." If she gets it wrong, the
rules text has failed at the one thing it most needs to convey.

**Stage 3 — reveal, then replan.** Tell her set bonuses are the only source of score growth,
that holding three districts (2+ landmarks each) is the top multiplier, and — since
2026-08-17 — that the top multiplier also requires those districts to span two or more
sides of the board (Hong Kong Island / Kowloon / East Kowloon), not just any three
districts. Ask her to plan again.

*What it measures:* the delta between the two plans **is** the comprehension gap, quantified
in score. A large delta means the briefing has to carry the load the rules text isn't.

**Stage 4 — group-of-ten realism.** Walk one landmark with her in detail: arrive at the MTR
exit, find the place, get ten people into one photo, agree on whether to buy, submit.
Ask for a range, not a number — fastest plausible, slowest plausible.

*What it measures:* the dwell-time estimate. **This is an estimate, not a measurement**, and
it will be optimistic — people systematically underestimate group coordination, and she is
imagining a group that already gets along. Treat her lower bound as fiction and her upper
bound as the planning number. Its purpose is a sanity check on the 25–40 min figure the
whole pacing model rests on, not a calibration input.

**Stage 5 — red team.** Ask her to break it: how would she win unfairly, what would she do
if her team got bored at 14:00, what happens if the group splits up, what if the Form is
slow, what if it rains at noon. Then ask her to argue *for* a strategy she thinks is bad.

*What it measures:* failure modes nobody modelled. This is where a motivated human is best
and desk analysis is worst, and it is the highest-value stage. The desk findings above
suggest the strategy space has more in it than the design assumes, so she may well find
more.

### Guard against the single-informant problem

- She understands the concept, so she is **unrepresentative of freshmen** by construction.
  Stage 1 and 2 results are a *ceiling* on participant comprehension, not an estimate of it.
- She may want to be helpful. Ask for concrete plans and specific objections; do not ask
  whether the design seems good.
- One respondent cannot produce a far/near comparison. Do not try to extract one.

## Part 3 — What is still unvalidated on the day

Recorded plainly, because with no field run these do not get resolved and the committee
should know which risks it is carrying.

| Unknown | Consequence if wrong | Cheapest partial mitigation |
|---|---|---|
| **Dwell time per landmark** | The 5–6 target, and every price derived from it, is wrong. Below 4 landmarks a day, the two-district cap never binds | Stage 4 upper bound. Have leaders report actual times on the day |
| **Post pars** | Solo play feels punishing or head-to-head is pointless | Trial each game once with any 10 people — a single run beats guesswork |
| **Sheet under load** | The 2025 failure repeats. Highest operational risk | Load test costs nothing and needs no participants — **do this one** |
| **Whether teams cluster at all** | The whole redesign does not land | Stage 1 |
| **Whether the same-side cap is discoverable, and reads as fair** *(new 2026-08-17)* | Teams hold 3 same-side districts anyway, get capped at ×1.4, and feel cheated at 17:00 rather than warned at 10:30 | Stage 1 (cold-read check) and Stage 3 (does the reveal land) |

### The two that should still happen

Neither needs a field day.

**Sheet load test.** Synthetic, scriptable, no participants. The 2025 retro names manual
scoring as "the single operational failure most likely to repeat," and the Sheet is its
replacement. Test: two `buy` submissions for the same landmark seconds apart — does
`base × MIN(2.5, 1 + 0.25 × prior_buyers)` resolve to 1.00× and 1.25×, or charge both the
same? 25 sequential buyers (price must stop at 2.5×, titleholder stays the first buyer).
The `Standings` case `operations.md` already specifies — 3 + 3 + 1 stray, exactly two
multipliers apply. Submissions at 16:29 and 16:31.

**One run of each post game**, with any ten people, timed *including the explanation*. Par
= slightly below what that group scored. `game-posts.md` makes the 15-minute ceiling a
design input; a game needing 4 minutes of rules has 11 of play.

## Decisions

### Item 11 — the price table

**Applied, 2026-08-18.** *(Superseded the 2026-08-17 "Hold" below — that basis is kept for
the record.)*

The simulation that replaced the cancelled interview (`simulated-playtest.md`) answered the
question this section had been holding open: under realistic 25-team price-ladder
contention, the residual far/near gap was 90–105 points, wider than the desk estimate below
assumed, and it survived the same-side cap. A top-only price compression was applied —
`p' = p` for `p ≤ 30`, else `p' = 30 + 0.45×(p−30)` — which narrowed the simulated gap by
25–37% across every scenario tested without disturbing near-crossing's affordability (a
first, more aggressive attempt at compressing the *whole* range was tried and reverted for
doing exactly that). Full record in `economy.md`'s calibration log.

*(Original 2026-08-17 basis, kept for the record: "Hold. The far/near comparison has since
been rebuilt around crossing builds instead... At matched spend both archetypes now need
the same 3 districts and 2 sides, and the far build's edge shrinks to a raw-KD effect with
no affordability slack (260 spend against 230 realistic income) versus the near build's
comfortable margin (120 against 190). Hold still applies: whether that residual gap is
worth compressing prices for is what the playtest below should answer." — resolved by
simulation instead, per above.)*

### Ordering

1. ~~Resolve the ×2.2 ambiguity~~ · ~~restate the target pace~~ — **done 2026-08-17**, both
   superseded by rekeying the set bonus to districts held. See `economy.md`.
2. ~~Re-derive the far/near comparison under the new multiplier, then decide item 11~~ —
   **done 2026-08-17**, alongside the same-side cap. Both rebuilt in `economy.md`.
3. ~~Sheet load test~~ — **done 2026-08-19.** The Sheet now exists, and the
   scoring half is verified: `Standings` was checked against a seeded four-team scenario
   covering the 2+2+2 crossing case, the same-side cap, a 2-district/2-side build and a
   stranded single, plus an 11-buyer price-cap run — and every figure agrees with an
   independent recomputation by `../../scripts/simulate_playtest.py`'s `score_team`, which
   predates the Sheet. The **concurrency half is still open**: the lock, the idempotency key
   and append-first ordering all need the deployed endpoint and genuinely parallel requests.
   The concurrency half is now also verified against the deployed endpoint: 8 simultaneous
   buys of one landmark took 8 distinct ladder positions, a replayed submission ID did not
   double-charge, and the 2.5x cap bound correctly. Measured throughput ~0.6/s against an
   event need of ~1.5/min. Harness: `../../scripts/seed_transactions.py --all`. Full results
   in `ledger-system.md`. Only append-first ordering remains unexercised.
4. ~~Design interview against the redrafted `rules.md`~~ — **cancelled**, replaced by the
   simulation (see the update banner at the top of this document). Item 11 **closed**
   2026-08-18 on the strength of that simulation.

### Unchanged

- Adjust **price range first, multipliers second** (`economy.md`).
- **The allowance is not a balance lever.** *(Updated 2026-08-17: it is no longer the*
  *only* *thing constraining the far strategy — the same-side cap adds a second,*
  *structural one, since a far build now needs 3 districts across 2 sides regardless of*
  *budget. The affordability brake still applies on top of that; do not raise the allowance*
  *without re-deriving the far build against both constraints.)*

## Where results go

| Output | Destination |
|---|---|
| Simulated economic findings (interview substitute, 2026-08-18) | `simulated-playtest.md` |
| Interview notes, both plans, stage-5 findings | `interview-notes.md` (new, written on the day) |
| Any change to prices or multipliers | `../../data/landmarks.csv` + calibration log in `economy.md` |
| Par scores | `game-posts.md` |
| Sheet defects | Open items in `operations.md` |

After any change to `../../data/landmarks.csv`, run `python3 scripts/verify.py`. Its cap and
correlation checks are derived from the data rather than hardcoded, so the compressed table
would need no change to the script — it reports worst case 150 and correlation 0.92 against
a 0.7 floor. A *fall* in correlation means the transform was misapplied.

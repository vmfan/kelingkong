# Economy

All numbers here are **starting values to be calibrated by playtest**, not settled
answers. The calibration log at the bottom records what changed and why.

The board itself lives in `../../data/landmarks.csv`; if this document and the CSV
disagree, the CSV wins.

## Currency

Called **Dollar Kelingkong (KD)** in participant materials. Base prices run 10–50 KD
*(compressed 2026-08-18 from the original 10–70 — see Calibration log)*.

## Base prices

Base price = **2025 point value × 10**, then compressed above 30 KD (see Calibration log,
2026-08-18) to close a residual gap the same-side cap didn't reach. `base_price_precompression`
in `landmarks.csv` keeps the original 2025×10 value for traceability.

This preserves 2025's most important design property: **the pricing is
distance-compensating.** Hong Kong Island landmarks sit 5–18 minutes from base and cost
10–30 KD; East Kowloon landmarks sit 33–37 minutes away and cost 50 KD. Without that
gradient nobody would ever leave Hong Kong Island.

| District | Landmarks | Mean price | Mean ETA from base |
|---|---|---|---|
| Admiralty | 3 | 10 | 7 min |
| TST Waterfront | 5 | 12 | 19 min |
| Causeway Bay | 4 | 15 | 13 min |
| TST Central | 5 | 18 | 13 min |
| Central | 5 | 20 | 15 min |
| Wan Chai | 3 | 23 | 11 min |
| Sheung Wan | 4 | 25 | 16 min |
| Sham Shui Po–Prince Edward | 3 | 30 | 21 min |
| Mongkok | 4 | 30 | 16 min |
| West Kowloon | 3 | 33 | 28 min |
| Whampoa–Hung Hom | 5 | 32 | 24 min |
| Kai Tak | 4 | 40 | 35 min |
| East Kowloon | 3 | 50 | 35 min |

Price/distance correlation is **r = 0.87** across districts (was 0.91 pre-compression),
checked by `scripts/verify.py` — still comfortably above the 0.7 floor.

### Two inherited distortions

**Mongkok and Sham Shui Po were overpriced for their distance**, because the 2025 sheets
scored them under the *Kai Tak* region despite sitting in Zone 1 on the Landmarks tab —
audit item 4 in `../2025/data-audit.md`. The 2026-08-18 compression happened to correct
most of this as a side effect: both now sit at the board's median price (30) rather than
above it.

**TST Waterfront is underpriced.** Five landmarks averaging 12 KD at 19 minutes out —
`verify.py` still flags it as the largest outlier on the trend; it wasn't touched by the
compression (all five landmarks are ≤20 KD, below the 30 KD threshold the transform
applies above). Left as-is so the inherited value stays traceable; the effect is that TST
Waterfront is a bargain.

### Distance-compensation only works if the trip is chosen

The pricing above assumes a team weighs travel cost against value and decides. That
assumption breaks if a team is *assigned* a far district rather than choosing one — an
imposed 35-minute trip to East Kowloon is not a bet, it is a handicap, and it works
directly against the pacing goal by putting that team behind before they've done
anything.

This is why the starting-district assignment (`operations.md`) draws only from the 8
cheapest, nearest districts — Admiralty through TST Waterfront, capped at 18.6 min mean
ETA. The five most expensive districts (Sham Shui Po–Prince Edward, Whampoa–Hung Hom,
West Kowloon, Kai Tak, East Kowloon) are reachable all day but never assigned as a
starting point. They stay what the pricing requires them to be: a trade a team opts into,
not a cost imposed by lottery.

## Set bonuses

**Revised 2026-08-17.** The multiplier is keyed on **how many districts a team holds**, not
on how deep it goes in any one. See the calibration log and `rules-audit.md` for why.

A district counts as **held** when a team owns **2 or more landmarks** in it. The resulting
multiplier applies to **everything the team owns**:

| Districts held | Multiplier |
|---|---|
| 1 | ×1.4 |
| 2 | ×1.6 |
| **3 or more** | **×1.8** |

A landmark sitting alone in a district scores face value and does **not** make that district
held.

Why this shape:

- **It is the only version that pays for breadth.** Under the previous depth-tiered table a
  third landmark in an existing district returned +1.6p against +0.4p per landmark for
  opening a new one — depth won by 4×, so breadth never happened. Here, opening a third
  district lifts the multiplier on the *entire* portfolio.
- **Two landmarks still profits**, so a team that only ever holds one district is not wiped
  out — it earns 0.4 × spend rather than nothing.
- **A lone purchase is still score-neutral.** The central idea in `concept.md` is untouched;
  it is now easier to state, because "2 in a district" is the only threshold that exists.
- **The optimum is 2+2+2**, six landmarks across three districts — the target pace, and one
  more district than the old design produced.
- **Gain is still proportional to spend**, so money keeps binding before time does. This is
  what an additive bonus could not preserve (`alternatives-considered.md`, option 5).
- **One table, one threshold, no ranking step.** Score is `cash + total value × multiplier`.

### What this replaced

Three mechanics collapsed into one: the four-tier depth table, the best-two-districts cap,
and the `4 atau lebih (distrik lengkap)` ambiguity. Open items 12, 13, 14 and 15 all close.

**Known cost — late buyers on a thin portfolio.** The multiplier now varies by team, so a
team holding one district (×1.4) loses money on any landmark it buys at the 3rd position or
later, where a team holding three (×1.8) still profits to the 4th. That penalty pushes a
narrow team toward opening another district, which is the intended direction, but it does
mean the trailing team faces the worse price ladder. Watch for it; the 2.5× cap bounds it.

### Same-side cap

**Added 2026-08-17.** The table above is satisfiable without leaving Hong Kong Island:
Admiralty, Sheung Wan and Causeway Bay are three of the four cheapest, nearest districts on
the board (`Base prices` above), so 2+2+2 across just those three reaches ×1.8 — this was
in fact the worked example below until today. That undercuts the event's own goal
(`event-brief.md`: "students see parts of Hong Kong they wouldn't have found alone").

**The multiplier is capped at ×1.4 unless a team's held districts span 2 or more sides** —
`side` in `../../data/districts.csv`: Hong Kong Island / Kowloon / East Kowloon. Holding
any number of districts on one side alone scores like holding one district. Reaching ×1.6
or ×1.8 now requires an actual harbour crossing.

The cap asks for 2 of 3 sides, not all 3. East Kowloon is flagged elsewhere in this
document as barely walkable — three separate MTR stops, no adjacency between its
landmarks — so making it mandatory for the top tier would turn a breadth guardrail into a
forced trip to the board's worst-served district. Hong Kong Island + Kowloon already
satisfies the cap.

2025 had its own answer to this — +30 for visiting 2+ landmarks in each of 3 regions
(HK Island / TST / Kai Tak) — which did not carry over when the board moved to the finer
13-district system, and nothing replaced it until now. A flat bonus of that size would in
any case be too small to matter: it is a rounding error against the +96 the multiplier
alone is worth in the worked example below. Capping the existing multiplier, rather than
adding a second score, keeps the "one lookup, no second currency" property intact.

### Worked example

A team buys two landmarks in each of three districts — Sheung Wan (30 + 30), Causeway Bay
(20 + 20), Admiralty (10 + 10) — spending 120 KD and holding 3 districts. All three are
Hong Kong Island districts, so the same-side cap applies:

```
total value 120 × 1.4 = 168
```

120 KD of cash becomes 168 of property value — a gain of 48, not the 96 this build would
have earned before 2026-08-17.

Swap Admiralty for TST Central — K11 Art Mall (10 + 10) — same 120 KD, same 3 districts,
now spanning Hong Kong Island and Kowloon:

```
total value 120 × 1.8 = 216
```

Crossing the harbour is worth 48 KD of property value on an otherwise identical build.

| Spend pattern (all 120 KD) | Districts held | Sides touched | Multiplier | Final |
|---|---|---|---|---|
| Sheung Wan + Causeway Bay + TST Central | 3 | 2 (HK Island, Kowloon) | ×1.8 | **216** |
| Sheung Wan + Causeway Bay + Admiralty | 3 | 1 (HK Island) | ×1.4 (capped) | 168 |
| All 4 of Sheung Wan (100) + the 2 cheapest in Causeway Bay (20) | 2 | 1 (HK Island) | ×1.4 (capped) | 168 |
| All 4 of Sheung Wan (100), 20 held as cash | 1 | 1 (HK Island) | ×1.4 | 140 + 20 = 160 |

And six landmarks in six *different* districts holds none of them — every landmark is alone,
so it scores 120, exactly what they started with. The score-neutrality of a lone purchase is
unchanged, and it isn't affected by the cap either way.

## Income

| Source | Value | Notes |
|---|---|---|
| Starting allowance | **150 KD** | Covers ~3 landmarks unaided |
| On-site task | **30% of that landmark's base price**, rounded to 5 — **Kai Tak: 50%** | Self-service via the Form |
| Object-to-find bonus | **5 KD**, once per object per team | Max 35 KD across all seven |
| Post win | **40 KD** | Runner-up or par-clear: **20 KD** |

The Kai Tak rate applies only to Kai Tak's 4 landmarks (all 40 KD base price, so task income
there is 20 KD instead of 10). Applied 2026-08-19 — see calibration log below for why, and
`simulated-playtest.md`'s Kai Tak task-income boost / farm-and-leave sections for the
evidence and the known residual it carries.

A team doing everything available might see roughly 150 + 90 + 35 + 120 = 395 KD across
the day, against roughly 120–200 KD for a 2+2+2 build depending on which districts
(was 120–260, pre-compression). That surplus is intentional — leftover cash still scores,
so the endgame is a genuine decision about whether to spend down. (The "90" is a board-wide
rough figure and doesn't isolate the Kai Tak exception, which only touches 4 of 51
landmarks.)

### There is no stipend

The committee chose not to include a periodic payout. That removes the safety net for a
team that stalls, so **the allowance and the on-site tasks carry that job instead**:

- On-site tasks are self-service and cannot be lost. A team that wins zero heats can
  still fund itself.
- The 150 KD allowance alone covers **three pairs in the three cheapest districts** (20 KD
  each), which is already the top ×1.8 multiplier. The safety net is stronger under the
  district-count multiplier than it was under the depth tiers.

**Do not cut the allowance below three landmarks' worth during calibration.** It is the
only thing standing between an unlucky team and a scoreless day.

## Ownership and pricing

- **Non-exclusive.** Any team may buy any landmark. Nobody is locked out.
- **Rising price:** each subsequent buyer pays +25% of base — 1.00×, 1.25×, 1.50× …
- **Hard cap at 2.5× base.**
- **Scoring uses base face value**, never the price paid.
- **First-buyer title:** the first team to buy is named as titleholder on the live board.

### The cap is load-bearing

Uncapped, with 25 teams, the last buyer of a landmark would pay **7× base** — 210 KD on a
30 KD landmark, against a 150 KD allowance. Popular landmarks would become **exclusive by
price**, which contradicts the whole non-exclusive design and quietly recreates the land
grab the format exists to avoid.

At 2.5×, the worst case on the board is **125 KD** (the three East Kowloon landmarks, 50
base — was 175 KD at the pre-compression 70 base) and the cheapest landmark tops out at
25 KD, unchanged. `scripts/verify.py` asserts both.

### The affordability margin is no longer thin — a side effect worth flagging

**Superseded by the 2026-08-18 compression.** East Kowloon's best-3 used to cost 210 KD
against a 150 allowance plus 60 in on-site tasks — affordable with 0 KD to spare, which is
what made this margin "load-bearing" in the first place. At the new 50 KD base it costs
**150 KD** against 150 allowance plus **45** in tasks — **+45 KD of slack**, not zero.

Compare Sheung Wan (95 KD left over) or Central (85, both unchanged by the compression).
The gap narrowed — the far strategy no longer buys its gain with *all* its financial
headroom — but the affordability brake this section used to describe as thin is
meaningfully weaker now than it was. This isn't a defect: the compression was applied
specifically to blunt the far-district advantage, and a wider affordability margin is one
of the mechanisms through which that happens (a far team is less likely to be stopped by
running out of cash mid-plan). But it does mean **this margin should no longer be cited as
"thin by accident, not by design"** — re-derive it before relying on it in any future
argument. `simulated-playtest.md`'s 25-team contention model is a better source than this
single-team calculation for how binding it actually is in practice.

Before Kwun Tong Promenade was dropped this margin was negative — East Kowloon's best-3
was genuinely unaffordable without objects or a post win. Removing the 80 KD landmark
lowered the barrier as a side effect, same as this compression does again. That is a real
cost of both changes, recorded here so neither is mistaken for a free improvement.

## Final score

```
score = cash + (total face value of all landmarks owned × multiplier)

where multiplier = 1.4 / 1.6 / 1.8 for 1 / 2 / 3+ districts held
      and a district is held when the team owns 2+ landmarks in it
      capped at 1.4 unless held districts span 2+ sides (data/districts.csv: side)
```

Two terms, one lookup, no per-district ranking. A team can compute this on the back of its
map at 14:00 — the standard `alternatives-considered.md` set and the previous design failed
(`rules-audit.md`).

For `Standings`, this is a count of qualifying districts per team, one lookup, and one
multiplication against a sum — replacing the best-two-district selection that
`operations.md` called the hardest and most failure-prone formula in the build.

## Surprise missions

Decided 2026-08-20 (see Calibration log). Committee-broadcast ad-hoc tasks during the day,
carried over from 2025 (`docs/2025/format.md:61`) but rekeyed from reward to penalty.

**Mechanic:** each mission has a 20-minute window from broadcast. Any team without an
un-voided completion photo or video by the deadline is deducted a flat KD amount at `Standings`.
There is no reward for completing one — completing just avoids the penalty.

**Why 20, not 15:** widened from the original 15 minutes (`docs/2026/missions-build-spec.md`,
"Broadcast schedule") so that a team caught mid-heat at a game post when a mission fires is
mathematically guaranteed at least 5 minutes free after the heat ends, regardless of timing —
heats cap at 15 minutes (`game-posts.md`), so `window − 15` is a hard floor on post-heat slack
that no scheduling choice alone can provide. See that section for the full reasoning and how
it combines with biasing broadcast times toward the end of the heat cycle.

**Penalty magnitude: 10 KD, working default, not finalized.** Mirrors 2025's flat +10 pt
reward in size. Sanity check against the live economy: the cheapest landmark on the board
is 10 KD, so one missed mission costs as much as forgoing the cheapest purchase available;
at 4 missions/day (reduced from 2025's count of 5 — see the 2026-08-31 calibration log entry)
the worst-case exposure is 40 KD, roughly a quarter of the 150 KD starting allowance — enough
to be felt, not enough to end a team's day. It is stored per mission row in the `Missions` tab
(`penalty_kd`, see `ledger-system.md`), not as a single board-wide constant, so the committee
can vary it per mission or change it mid-event without a rules or code change. Neither this
number nor which of the 2025-style missions carry over is locked — both remain the
committee's call, same as `[TBD]` prices before playtest.

**Retroactive voiding:** if a submitted mission photo/video is later voided by Kontrol, the
penalty re-applies. This needs no new mechanism — the `Standings` condition checks "team has
an *un-voided* submission for this mission," not merely "team has a submission," so a later
void simply flips a live formula back to its penalized state on its own.

**Does not touch `Board` or the face-value/multiplier calculation** — this is a pure
`Standings`-level deduction, same non-interaction property the Kai Tak task-rate change
above was careful to preserve. Unlike that change, though, this *is* new formula surface:
every existing `Standings`/`Board`/`Ledger` formula sums *positive* submissions a team made;
this is the first roster-wide "prove absence" check in the sheet. See `ledger-system.md` for
the build spec and the verification pass this needs before going live.

**Comms:** missions are broadcast in the leader group chat, prefixed `🚨 RAZIA PAJAK` so
they're spottable in a busy, ~50-person channel with no delivery confirmation
(`operations.md`, Briefing the leaders). The participant page (`web/index.html`) carries a
server-clocked countdown box as the actual fairness backstop for chat-delivery lag — the
countdown authority is a server timestamp, not "time since a leader read the chat," so
opening the page late still shows true remaining time.

## Calibration log

Record every change here with the reason, so the numbers stay traceable.

| Date | Change | Reason |
|---|---|---|
| 2026-08-16 | Initial values set | Derived from 2025 points × 10; untested |
| 2026-08-16 | Kwun Tong Promenade dropped from the board | 45 min from base, the furthest point, and the only landmark never assigned an MTR district in 2025 (audit item 10). East Kowloon 4→3, price range 10–80→10–70, cap worst case 200→175. Preserved in `landmark-candidates.csv` |
| 2026-08-17 | **Set bonus rekeyed from depth to breadth.** Tier table `1.0/1.4/1.8/2.2` on best-2 districts → **`1.4/1.6/1.8` on the count of districts held (2+ landmarks each)**. `data/landmarks.csv` unchanged | Committee asked for more breadth. Depth-tiered multipliers cannot deliver it: a 3rd landmark in an existing district returned +1.6p against +0.4p per landmark for opening a new one, so breadth never happened at any tier setting. Keying on district count inverts that, and best build goes from 6 landmarks in 2 districts to 7 in 3. Also closes items 12–15 in one change, reverses the far/near gap (East Kowloon sweep 168 → 84 gain, three-district near build → 136), and replaces the hardest formula in `Standings`. Gain stays proportional to spend, so money still binds before time — the property an additive bonus would have destroyed |
| 2026-08-17 | **No number changed.** Field run cancelled — no committee time. Replaced by desk analysis + design interview (`playtest.md`) | Three desk findings, none of which needed a playtest: (a) travel time is not a defence against far districts, it favours them — far uses 162 min against near's 226; (b) the optimum is not 3+3, because marginal gain per KD *rises* with district count, so completing a district dominates; (c) `rules.md` is ambiguous on whether ×2.2 needs 4 owned or a complete district. **Item 11 on hold**: the +42 gap compares two archetypes that are both suboptimal, so compressing prices would aim the wrong lever at a mis-specified problem |
| 2026-08-17 | **Same-side cap added.** Multiplier stays `1.4/1.6/1.8` on districts held, but is now capped at ×1.4 unless the held districts span 2+ sides (`data/districts.csv`: `side` — Hong Kong Island / Kowloon / East Kowloon) | The district-count rekey (above, same day) fixed depth-vs-breadth but left a second exploit open: Admiralty + Sheung Wan + Causeway Bay are 3 of the board's 4 cheapest, nearest districts and all sit on Hong Kong Island, so 2+2+2 there reached ×1.8 without a harbour crossing — this was the worked example until this change. That contradicts the event goal in `event-brief.md`. 2025 addressed this with a flat +30 region bonus that did not carry over to the 13-district board; a flat bonus of that size would in any case be dwarfed by the multiplier (+96 in the worked example). Capping requires only 2 of 3 sides, not all 3, because East Kowloon is already flagged as barely walkable — see "East Kowloon is still not walkable" below — and making it mandatory for the top tier would force a trip into the board's worst-served district rather than merely discourage clustering |
| 2026-08-17 | **No number changed — stale figures corrected and the far/near comparison rebuilt.** "Three known weaknesses" was still using gain numbers computed under the retired depth-tiered multiplier (best-3-in-one-district at the old ×1.8), even after the 2026-08-17 rekey. Recomputed every affected table at the live rules: single-district best-3 gains (East Kowloon +168→+84, Kai Tak +136→+68, Sheung Wan +64→+32, Admiralty +24→+12), the compressed-price-table projections, the East Kowloon-drop before/after table, and the East Kowloon sweep-and-stop scenario (383→299, its "complete Kai Tak" comparator replaced since completion past 2 landmarks no longer moves the multiplier). Archived four subsections (`Staged fix — cap the multiplier at 3`, `Capping at 2`, `Cap at 2, done properly`, `Why no tier table can produce breadth`) as historical record — they analyse patches to the retired per-district depth table, which was replaced outright, not capped | Found while checking whether the same-side cap affected the East Kowloon gain table; it didn't directly, but the table was already broken by the prior day's rekey. The old best-3-in-one-district framing is also obsolete on its own terms — depth past 2 landmarks buys nothing now — so the far/near comparison is rebuilt around matched 3-district/2-side crossing builds instead. New finding: at matched spend, a near-anchored crossing build (120 KD → gain 96, 70 KD slack) now beats a far-anchored one (260 KD → gain 208, but −30 KD short of realistic income) on safety, and the East Kowloon sweep-and-stop scenario is now dominated outright by any build that crosses a side, including one still anchored in Kai Tak. Precise magnitude of any residual far/near gap remains a playtest question (Sat 22 Aug) — see `#### What the playtest must measure` |
| 2026-08-18 | **No field run happened either — Sat 22 Aug interview cancelled, committee away.** Replaced by a Monte Carlo simulation of the 25-team day (`../../scripts/simulate_playtest.py`, full method and results in `simulated-playtest.md`). Confirmed two things the desk analysis couldn't: the same-side cap is doing real, measurable work (crossed-side teams score 22–37 points higher, population-wide, at the original prices), but a residual gap survives it — far-crossing builds still outscored near-crossing ones by 90–105 points under real 25-team price-ladder contention, and a new "sweep-and-stop" finding (see below) showed a single expensive district, held and abandoned, is structurally immune to time pressure (0% time-bound across every scenario tested) in a way no existing cap addresses | Item 11 had been on indefinite hold pending exactly this evidence. The simulation supplied it |
| 2026-08-18 | **Item 11 applied, then partially reverted, then re-applied at a different setting.** First tried `p' = 30 + 0.75×(p−30)` across the *whole* range (the table originally staged below) — reverted after simulating it, because it raised every 10-KD landmark to 20 KD (a 100% increase) with the allowance untouched, which collapsed near-crossing's own plan-completion rate from 85–98% to 15–27% while leaving far-crossing's cost roughly flat (its East Kowloon saving was cancelled by TST Central hitting the new floor) — **the score gap widened, not narrowed.** Replaced with a **top-only transform**: `p' = p` for `p ≤ 30`, else `p' = 30 + 0.45×(p−30)`, rounded half-up to the nearest 10 (`scripts/apply_price_compression.py --ratio 0.45`, now the script default). Leaves every ≤30 KD landmark — everything near-crossing's build touches — untouched, and only discounts the four districts above it (Mongkok, West Kowloon, Whampoa–Hung Hom, Sham Shui Po–Prince Edward, Kai Tak, East Kowloon). Price range 10–70 → 10–50; `base_price_precompression` preserves the original 2025×10 value per landmark | Two ratios were tested against 0.45 before settling: 0.6 (gentler) produces byte-identical far/near/sweep results to 0.45 in simulation — neither the far-crossing nor the sweep archetype touches the specific landmarks the two ratios disagree on — so 0.45 dominates it outright (same effect, more of the price gradient preserved, including keeping East Kowloon priced above Kai Tak's most expensive landmarks). 0.35 (steeper) narrowed the sweep-vs-far residual further (from sweep winning outright in 3–4 of 9 simulated scenarios down to 2, plus one near-tie) but collapsed East Kowloon and Kai Tak's top tier to the same price, erasing a distinction the board's own design intentionally preserves (`East Kowloon is still not walkable`, below) — rejected on that basis. **The sweep-and-stop residual is narrowed, not eliminated**, by design: it's a time-immunity effect, not a pure price effect, and no price lever fully closes it (see the single-district endgame section, below). The remaining gap is intended to be closed non-mechanically, via the leader briefing (`operations.md`) rather than a further price or rules change |
| 2026-08-18 | **Post-heat cooldown added.** A team may not play the next heat at the same post it just attended — win, lose, beat par, or miss par all trigger it. Rules-text lives in `game-posts.md` (Heats → Cooldown) and `rules.md` §4. No price or multiplier changed | Uncapped, farming one post was worth roughly 2 KD/min, ahead of even the best-case landmark return (~1.2 KD/min for a team already at ×1.8 buying one more landmark). That outpaced the entire point of the payout cap in `game-posts.md`'s "What posts are for" — posts were meant to pay worse than exploring, not better. The cooldown roughly halves the ceiling to ~1–1.3 KD/min, back in line with landmark play, without capping how many times a team can visit a post across the whole day. Enforcement only needs a 2-team lookback against the prior heat at that post, so it doesn't reintroduce the manual-tracking risk the 2025 retro warns about |
| 2026-08-19 | **`sides_required=3` experiment run and evaluated — NOT applied.** Added `sides_required` as a real parameter to `score_team`/`simulate_one_run`/`run_scenario` (default 2, live behavior unchanged) and a new `three_side_crossing` archetype (Sheung Wan + TST Central + Kai Tak, 2 each) since none of the 6 existing archetypes span 3 sides and a naive threshold flip would just cap everyone by default rather than test anything. Full results in `simulated-playtest.md`'s "Side-count experiment" section. `rules.md` and this document's live "Set bonuses"/"Same-side cap" text are unchanged | Committee floated requiring 3 of 3 sides instead of 2 of 3 to push exploration toward Kai Tak/Post 3 (walkable, volunteer-run, unlike the separate "East Kowloon" district on the same side). Verdict: a hard requirement is too punishing to adopt as-is — 0% of the current population ever reaches 3 sides, so every archetype that benefits from the existing 2-sides rule would simply lose 15–40 points, and even the archetype built specifically to attempt 3 sides only completes it 1–21% of the time (Kai Tak's landmarks are all top-tier priced and scarce under 25-team contention, so most attempts stall at 2 districts and get money-bound, not comprehension-bound). One useful side finding: post exposure doesn't actually require holding Kai Tak, only routing through it, so the cheaper fix for the original social goal is retargeting the worked examples toward a post-anchor district (already flagged in finding 6), not changing the multiplier |
| 2026-08-19 | **`sides_bonus` experiment run and evaluated — NOT applied.** Added `sides_bonus_multiplier`/`sides_bonus_threshold` to `score_team` (default `None`, disabled): when set, a team spanning all 3 sides gets `multiplier = max(multiplier, bonus)`, applied *after* the existing floor so it can only raise a score, never lower one. New `--sides-bonus VALUE` flag. Full results in `simulated-playtest.md`'s "Bonus-tier experiment" section. `rules.md` unchanged | Follow-up to the rejected hard-3 requirement above — tests the softer alternative it flagged: reward a 3-side spread instead of requiring it. Verdict: confirmed non-punishing (5,398/5,400 archetype-scenario cells bit-for-bit unchanged at `--sides-bonus 2.0`; the only movement is +0.1 on `greedy_adaptive`, from its stochastic heuristic rarely landing on 3 sides by luck), but the bonus's own effect is small next to the pre-existing multiplicative-spend gap (Item 11, finding 5) and scales with `completion_frac × (bonus − 1.8) × total_value` — since only 1–21% of attempts actually complete a 3-side hold (bottlenecked by Kai Tak's price/scarcity, not the multiplier), even a 3.0× bonus adds only +35 points at best and ~0 at high dwell time. A bonus tier alone is safe to add but unlikely to change much observed behaviour; recommended only paired with a Kai Tak affordability change, not adopted standalone |
| 2026-08-19 | **Kai Tak price-relief experiment run and evaluated — NOT applied, `data/landmarks.csv` untouched.** Added `kai_tak_discount` to `load_board()` (default `1.0`, no change) and a `--kai-tak-discount RATIO` flag: multiplies only Kai Tak's `base_price` in memory, rounded to the nearest 5 KD, for the duration of one simulation run. `sanity_check()` still loads the undiscounted board. Full results in `simulated-playtest.md`'s "Kai Tak price-relief experiment" section | Follow-up to both experiments above, which converged on the same bottleneck: Kai Tak's 4 landmarks are all top-tier priced and scarce, so most 3-side attempts stall on money, not comprehension. Verdict: relief works exactly on the constraint it targets — a 45% discount roughly doubles completion for both `far_crossing` (4%→16%) and `three_side_crossing` (21%→50%) at low/mid dwell time, but does nothing for the dwell-35 case where time, not money, already binds (established in finding 2) — pricing can't rescue a time-bound team. Also trades completion for score (cheaper Kai Tak means a completed build is worth less), which the bonus tier above offsets when paired: `--kai-tak-discount 0.7 --sides-bonus 2.0` together restores the no-discount score (207 vs. 206) while keeping the improved 31% completion rate. Recommend, if pursued: pair with the bonus tier rather than adopting alone, keep the leader-briefing/timetable fix for the time-bound case, and apply via a real `apply_price_compression`-style data script (logged here) rather than leaving it as a simulator-only flag |
| 2026-08-19 | **Kai Tak task-income boost experiment run and evaluated — NOT applied.** Added `KAI_TAK_TASK_RATE` (default `None`) and a `--kai-tak-task-rate RATE` flag: overrides the 30% task-income rate for Kai Tak's landmarks only, everywhere else unchanged. Touches `Board`/`Ledger`-equivalent cash flow only — never `Standings`/`Ref`. Full results in `simulated-playtest.md`'s "Kai Tak task-income boost experiment" section | Committee-proposed alternative to price relief, specifically to avoid reopening the just-verified `Standings` formula (`operations.md`: "Sheet built and `Standings` verified 2026-08-19"). Confirmed structurally correct — task income never feeds `Standings`'s face-value/multiplier calculation, so this needs no re-verification of the four hand-computed test cases the way the bonus tier would. Economically it beats price relief on both axes: at a comparable ~31% completion rate, a 0.7 task-rate scores 237 vs. price relief's 200 (task income is pure addition, doesn't shrink face value the way a discount does). But it reopens a different risk: `rules.md` §2 pays task income independent of purchase, so a team can do all 4 Kai Tak tasks and buy nothing — at rate 1.0 that's 160 KD uncontested, more than the full starting allowance, the same purchase-decoupled farming pattern the 2026-08-18 post cooldown was built to close, and unlike posts there is currently no cooldown/rate-limit on tasks. Recommend, if pursued: keep the rate modest (0.5, not 1.0), and simulate a dedicated task-farm-and-leave archetype before adopting, matching the rigor the post-cooldown decision was held to |
| 2026-08-19 | **Task-farm-and-leave archetype built and measured — finding revises the row above.** Added `kai_tak_task_farm` (visits all 4 Kai Tak landmarks, collects task + Post 3 income, buys nothing — `simulate_one_run` skips its purchase events) plus `time_used`/`kd_per_min_mean` fields on every archetype's summary and a `--farm-check` flag. Full results in `simulated-playtest.md`'s "Farm-and-leave, quantified" subsection | **This is not only a risk of boosting the task rate — it already holds at today's live, unboosted 30% rate.** Farming Kai Tak's 4 tasks and buying nothing scores 240 at 0.69 KD/min, beating every legitimate buy-and-hold archetype tested including `near_crossing` (score 180, 0.26 KD/min) — the exact strategy `rules.md`/`economy.md` teach as the canonical ×1.8 worked example — while risking zero KD on the price ladder and leaving ~140 of 270 minutes free to also run a legitimate build on top. Boosting the rate (previous row) doesn't create this gap, it widens one that already exists: at rate 1.0, farm-and-leave (1.62 KD/min) approaches the ~2 KD/min figure that made uncapped post-farming unacceptable in the first place. Two separate questions for the committee now: whether to pursue the rate boost at all, and — independent of that — whether farm-and-leave at the *current* 30% rate already needs its own fix (e.g. paying task income only on landmarks later bought). Recommend surfacing the second question regardless of the boost decision |
| 2026-08-19 | **Decision: task-rate boost proceeds at 0.5, farm-and-leave residual accepted as a known, separate open item — not yet implemented.** Committee rejected the purchase-gated fix (pay task income only on bought landmarks) as too strict against `rules.md` §2's low-friction task/purchase split. Checked whether price relief or the bonus tier close the gap without one: neither does — price relief *widens* it (`three_side_crossing` score 206→192 as discount grows, since cheaper Kai Tak means less face value to multiply); the bonus tier only ties farm-and-leave's 240 on the population mean at an extreme ×3.0 setting, and doing so means reopening `Standings`/`Ref` anyway, defeating the reason the task-rate lever was chosen. Full record in `simulated-playtest.md`'s "Decision — 2026-08-19" section | No natural fix found within the constraints (no purchase gate, no `Standings` reopening), so the boost proceeds on its own merits per committee direction. Rate set to 0.5, not the swept 1.0, to take most of the completion gain (`three_side_crossing` 21%→26%) while keeping the farm-and-leave side effect's growth modest (240→280 score, 0.69→1.00 KD/min) rather than approaching the ~2 KD/min danger zone at 1.0. The farm-and-leave gap itself is carried forward, not resolved — recommend tracking it like the sweep-and-stop residual, except a leader-briefing mitigation can't apply here since farming currently *wins*, not merely resists time pressure. **Not yet implemented**: no change made to `rules.md`, the printed price list, or the Sheet's `Board` tab — those are separate follow-up steps, same sequencing as Item 11 |
| 2026-08-19 | **Applied — Kai Tak on-site task rate raised to 50% (from the board-wide 30%).** Income table above updated. `rules.md` needed no change — it already only says the task's payout "is on the price list," never states the 30% figure, per operations.md item 16, so the participant-facing text is correct at either rate. `operations.md`'s `Board` tab description and item 16 updated to flag the exception for whoever builds the Sheet formula. **The live `Kelingkong Ledger` Sheet's `Board` tab itself is not yet updated** — that edit (4 rows, Kai Tak's landmarks) is outside this repo and needs a deliberate, verified pass against the already-built, already-verified Sheet, not an automatic one | Closes the decision recorded above. Concrete effect: Kai Tak's 4 landmarks (all 40 KD base price) now show 20 KD task income instead of 10. The farm-and-leave residual grows correspondingly (240→280 score, 0.69→1.00 KD/min per `simulated-playtest.md`) and remains open, tracked, not resolved by this change |
| 2026-08-20 | **Surprise missions rekeyed from reward to penalty.** 2025 ran five committee-broadcast missions (`docs/2025/format.md:61`) as a pure +10 pt bonus, no downside for ignoring one. 2026 switches to a flat KD penalty (10 KD working default, not finalized, stored per-mission not board-wide) deducted at deadline from any team without an un-voided completion photo. Detail in the new `## Surprise missions` section below | Committee wanted a "mandate," not a bonus — passive teams currently pay no cost for ignoring missions. A "deposit and refund" alternative (charge upfront, refund on completion) was considered and rejected: it is mathematically identical to the flat penalty (same team-relative point swing either way, since both are a uniform shift off the reward baseline), but costs two ledger touches instead of one and charges a team before the outcome is known — strictly worse on both axes, no upside kept. A geography-gated "flow control" checkpoint version (aimed at the Kai-Tak farm-and-leave residual, above) was also explored — reachable in ~15–20 min from the Kai Tak cluster via the Ho Man Tin interchange, not the ~65–70 min a naive base-relative bound suggests — but turned out moot: the actual 2025 mission text is entirely location-agnostic ("any MTR station," street art, a bakery, a minimart, a pose), so there is no checkpoint to gate on unless a future mission is deliberately written to require one. That stays a documented option, not adopted here |
| 2026-08-31 | **Surprise missions reduced from 5 to 4/day, afternoon schedule rebalanced.** The 2026-08-20 broadcast schedule (M1 10:59, M2–M5 13:44/14:29/14:59/15:29) packed four of five missions into a 13:44–15:49 span — under two hours — while the rest of the day carried only one. Dropped M5 and retimed M4 from 14:59 to 15:14, giving three evenly-spaced afternoon missions (13:44 / 14:29 / 15:14, 45 min apart) instead of four unevenly spaced ones (45/30/30 min apart). Worst-case penalty exposure drops from 50 KD to 40 KD accordingly (`## Surprise missions`, above). Full schedule and rationale in `missions-build-spec.md`'s "Broadcast schedule" — every existing constraint (lunch-clear, `:14/:29/:44/:59` heat-offset phase, clear of the 16:00 last-heats crunch and 16:30 Form close) still holds, none were loosened to make room | Raised as a participant-experience concern: four mandatory 20-minute response windows inside under two hours, on top of 15-minute heats and ordinary landmark shopping, risked feeling like a barrage rather than an occasional interruption. The KD-exposure math alone (economy.md's original 2026-08-20 entry) didn't capture this — it sized the *penalty*, not the *cadence*. Reducing the count was chosen over redistributing all 5 (e.g. adding a second morning slot) because the morning window is only 40 minutes wide (`issued_at` between 11:00 and 11:40), too tight to comfortably fit a second mission without recreating a smaller version of the same clustering problem. **Live Sheet not yet updated** — the 2026-08-20 `Missions` tab pre-fill (`ledger-system.md`) still reflects the old 5-mission schedule and needs a deliberate re-application, same convention as every other Sheet-side change tracked from this repo |
| 2026-09-04 | **Event timings confirmed against venue; rundown and mission schedule retimed.** `operations.md` open item 1 closed with real numbers: committee 08:00, assemble 09:45, disperse 11:05, first heat 11:30, heats now pause 12:30–13:45 for lunch (new — 2025's and the earlier 2026 design's heats ran continuously through lunch), last heat 16:30 (ends 16:45), submission deadline 16:45 (previously a 30-min buffer after the last heat; now flush against it), closing 17:15. Live exploration falls from the assumed 4.5h to ~4h10m. Mission broadcast schedule re-derived by the same method as the 2026-08-31 revision against these new inputs: `M1`–`M4` = 11:29 / 13:44 / 14:44 / 15:44 (deadlines +20 min each), afternoon spacing widened from 45 to 60 minutes since the later deadline opens more safe room to fill evenly. Worst-case exposure unchanged at 40 KD (still 4 missions × 10 KD). Full derivation in `missions-build-spec.md`'s "Broadcast schedule" | Venue availability was the last unconfirmed input the whole pacing model assumed a placeholder for (`operations.md`, open item 1). The mission schedule is explicitly built to be re-derived whenever the rundown moves (`missions-build-spec.md`'s own "Constraints that produced these times" section), so this is a mechanical re-application of that method, not a new design decision. The ~7% exploration-time compression (4.5h → ~4h10m) is flagged as a new open item (27) rather than acted on here — re-validating the 6-landmark target and derived prices against it is a judgement call for the committee, same footing as item 7's economy validation, and `simulated-playtest.md`'s 270-minute-budget simulation needs a rerun before its findings can be trusted at the new budget. **Live Sheet and `Code.gs` not yet updated** — `apps-script/Code.gs`'s `CONFIG.DEADLINE` was retimed in this repo but still needs `clasp deploy`; the `Missions` tab's `M1`/`M3`/`M4` rows need retiming to match. See `operations.md` open item 24 (reopened) |
| 2026-09-01 | **Team count fixed at 21, not the 25 this model was built against — re-ran the far/near comparison, no repricing warranted.** Every simulation cited above (including the 90–105 pre-compression gap and the 0.45-ratio compression decision, both 2026-08-18) assumed `simulate_playtest.py`'s `TEAMS = 25`; those entries are left as written since they're an accurate record of what was modeled at the time. With the real count now fixed at 21 (`operations.md` item 26), set `TEAMS = 21` and re-ran `--compare-crossing --runs 200 --seed 42` against the live, already-compressed board. Result: the far/near gap **widened slightly** at 21 vs. 25 teams — dwell20/25: 49.9→53.0; dwell35: 58.1→60.4 (roughly +6–10%), same direction as the pre-compression finding, not a reversal. **No repricing follow-up needed**: fewer teams means less price-ladder contention, which makes far-crossing's landmarks marginally easier to secure, not harder — the compression ratio item 11 landed on (0.45) still narrows the gap it was chosen to narrow. `simulate_playtest.py`'s `TEAMS` constant is now permanently 21, matching the real event | Closes the "judgement call" item 26 flagged: a team-count change could in principle have invalidated item 11's calibration if contention shifted enough to change which compression ratio dominated. It didn't — the shift was single-digit-percent, well inside the range the original 0.45-vs-0.6-vs-0.35 comparison (2026-08-18 entry) was decided across. `data/landmarks.csv` prices are unchanged |

**No field run and no design interview happened.** `simulated-playtest.md` replaced the
economic half; Stages 1–3 (does a first-time reader discover clustering/crossing from
`rules.md` unprompted) remain genuinely untested — no simulation can substitute for that.

**Do not adjust the allowance to fix district balance.** It cannot: leftover cash scores
1:1, so a change to the allowance moves every strategy's score by the same amount and
cancels out of any comparison between them. What it *does* do is remove the affordability
brake described above — which the 2026-08-18 compression has already narrowed once (see
"The affordability margin is no longer thin", above); stacking an allowance increase on
top would narrow it further and is not recommended. (Raising it for other reasons — teams
stranded, unable to afford anything — is still fine. Just don't expect it to touch the
far/near gap.)

Questions the playtest must answer:

- Does a team finish with 5–6 landmarks?
- Does time bind before money, or do teams sit around unable to afford anything?
- Can a team that wins no heats still complete two districts?
- Is the endgame spend-down interesting, or does everyone just hoard cash?
- **Do expensive districts dominate, and by how much?** See below — the most important
  question of the five, and the only one with a number attached.
- **Do far-travelling teams win as many post heats as near ones?** The balance case rests
  on the answer being no. Post 3's siting in Kai Tak suggests it may be yes.

**Answered 2026-08-18 by simulation, not by the field run** — see `simulated-playtest.md`
for the full results and its own list of what it could and couldn't measure. Headline: yes
to the first four (5–6 landmarks reliably except at the high end of the dwell-time
uncertainty range; both time and money bind depending on dwell; a zero-post-income team
holds 2+ districts 68–71% of the time; leftover cash exists but is partly forced by time
pressure rather than chosen); the fifth was reframed as post-heat *exposure* rather than
win rate, and turned out to depend on which specific districts a build visits, not on
distance — see that document's finding 6.

## Three known weaknesses

The first two were found while building the board. The third was found by working through
the "sweep the far district and stop" scenario; it is the one with the clearest fix.

### The multiplier is multiplicative, so gain scales with spend

Because the bonus multiplies the money spent, more expensive purchases return more raw KD
of gain **at the same multiplier tier**. That was true before the district-count rekey and
is still true after it and after today's same-side cap — neither one touches this.

**What has changed: depth within a district no longer buys a higher tier.** A team that
sweeps one expensive district gets the same ×1.4 as a team holding one cheap district —
there is no "best-3" shortcut anymore:

| District | Best-3 spend | Value (×1.4) | Gain |
|---|---|---|---|
| East Kowloon | 150 | 210 | +60 |
| Kai Tak | 120 | 168 | +48 |
| Sheung Wan | 80 | 112 | +32 |
| Admiralty | 30 | 42 | +12 |

*(Corrected 2026-08-18 for the price compression — see the calibration log. East Kowloon
and Kai Tak both dropped (base 70→50 and 55→40 respectively); Sheung Wan and Admiralty are
unchanged, since every landmark in both districts is ≤30 KD, below the compression
threshold. Before this, the table read +84/+68/+32/+12, corrected 2026-08-17 for the
district-count rekey.)*

These four numbers now differ only by which single district a team parks in — a choice
that no longer moves the multiplier at all. **The real question has moved to which
districts a team pairs to cross a side**, since that's the only remaining lever on the
multiplier.

**Matched comparison, near vs far, both reaching ×1.8:**

| Build | Districts / sides | Spend | Gain | Task income | Available (150 + task income) | Slack |
|---|---|---|---|---|---|---|
| Near: Sheung Wan + Causeway Bay + TST Central | 3 / 2 (HK Island, Kowloon) | 120 | +96 | 40 | 190 | **+70** |
| Far: Kai Tak + East Kowloon + TST Central | 3 / 2 (East Kowloon, Kowloon) | **200** | **+160** | **60** | **210** | **+10** |

*(Recomputed 2026-08-18 for the price compression — see the calibration log. Far's spend
dropped 260→200 and gain dropped 208→160; slack **flipped from −30 to +10**. The near row
is unchanged: every landmark it uses is ≤30 KD, below the compression threshold. Task
income = 30% of each landmark's base price, rounded to the nearest 5, self-service. Both
builds use each district's two cheapest landmarks, except East Kowloon, whose three
landmarks are all the same price — 50 KD post-compression — so any two cost 100.)*

The far build still banks more raw gain — gain scales with spend, and it still spends
substantially more. Compression narrowed that gap (was +208 vs +96, a 112-point spread; now
+160 vs +96, a 64-point spread) without eliminating it, and it also **removed the far
build's negative margin**: it used to need an object or a post win just to clear its own
plan (−30 slack); now it has +10 to spare, comfortably affordable at first-buyer prices.
The near build still carries more slack (+70) and is still the safer choice, but the far
build is no longer the razor-thin bet it was.

**"Far dominates" is still not the finding, but it's closer to one than the 2026-08-17
entry suggested.** Reaching the top tier still costs the same three districts and two
sides regardless of price level. The same-side cap doesn't eliminate the
multiplicative-gain effect itself (a well-funded far build still out-earns a well-funded
near one at the same tier) — it removes the shortcut that let a team reach the top tier
just by being expensive and clustering on one side. The compression above targets what the
cap doesn't: the residual size of that per-tier gap. **This single-team, first-buyer-price
comparison is still the optimistic case** — `simulated-playtest.md`'s 25-team contention
model confirms the same direction (the applied 0.45-ratio compression narrowed the
simulated far/near score gap by roughly 25–37% across every dwell-time and comprehension
scenario tested) but not the same magnitude: far-crossing is money-bound on the price
ladder in almost every simulated run, so it rarely realizes the full +160 gain this static
comparison assumes. Treat this table as the best case, and the simulation's 62–85-point
residual gap (down from 90–122 pre-compression) as the more realistic one.

#### What the playtest must measure

> For each team, record final score, how many districts it held, which sides those
> districts spanned, and their combined base price. Split teams by whether they crossed a
> side at all, and separately by whether their spend is above or below ~150.

- **Teams that didn't cross a side score noticeably lower than teams that did** → the
  same-side cap is doing its job; no further change needed on this axis. **Confirmed by
  simulation 2026-08-18**: crossed-side teams scored 22–37 points higher, population-wide,
  consistently across every scenario tested — see `simulated-playtest.md`.
- **Far-crossing teams still pull far ahead of near-crossing teams at matched spend** →
  apply the compressed price table below; the residual spend-scaling effect is worth
  dampening. **This is what happened.** See the calibration log entry for 2026-08-18.
- **Gap is small, or near-crossing teams simply finish more builds** → leave prices alone;
  the affordability brake and the same-side cap together are enough. Not what the
  simulation found — the gap survived the cap, hence the compression above.

#### The fix, in order

1. ~~Compress the price range.~~ **Done 2026-08-18** — see the calibration log. Gain =
   spend × (m−1) still holds; the top-only transform narrows the residual price spread
   above 30 KD without disturbing the affordable end of the board.
2. **Make the bonus additive** — a flat award per district tier rather than a multiplier.
   Still a secondary option, now more so: compression closed most of what was open. Only
   worth revisiting if a future playtest or dry run shows the residual gap (see
   `simulated-playtest.md`) still matters after the compression above.

**Not on the list: the allowance.** See the calibration log for why.

### The single-district endgame: sweep the far district, then stop

**The scenario.** A team goes straight to East Kowloon, buys all three landmarks and stops.
Post-compression this costs **150 KD** (was 210) — exactly its 150 allowance, before even
counting task income — so it now clears with room to spare rather than exactly zero. It has
seen three places, it is done by about 13:00, and it has roughly 109 minutes and **45 KD**
left (was 5). This directly contradicts goal 2 in `../event-brief.md` — students seeing
parts of Hong Kong they wouldn't have found alone. **The compression made this scenario
more affordable, not less** — a real cost of the fix, flagged here rather than left to be
discovered late.

**Two things currently contain it, one of them weaker than it used to be.**

*The price ladder limits it to about four teams now, not two.* Sweeping all three East
Kowloon landmarks (all 50 KD post-compression) costs 150 at first-buyer prices, 188 at
second, 225 at third, 263 at fourth — against a realistic ceiling of ~290 with objects and a
post win:

| Buyer position | Cost of all 3 | Verdict |
|---|---|---|
| 1st | 150 | affordable on the allowance alone |
| 2nd | 188 | affordable with ordinary task income, no objects needed |
| 3rd | 225 | affordable with objects **or** a post win |
| 4th | 263 | needs objects **and** a post win, close to the ceiling |
| 5th+ | 300+ | **cannot afford** |

*(Recomputed 2026-08-18 for the compression — see the calibration log. Pre-compression this
table read 210/262/315/368+, containing the sweep to roughly two profitable buyers. At the
new 50 KD base it contains roughly four — the price ladder is doing less of the containment
work than it used to, which is a direct, intended-tradeoff consequence of lowering East
Kowloon's price to close the far/near gap elsewhere.)*

This is the price cap doing work it was not designed for, and it is worth knowing it is
weaker here than it was, not just load-bearing.

*It still does not win outright, and the same-side cap still makes that decisive.* East
Kowloon is one district on one side, so under the cap it stays at ×1.4 no matter how
completely a team sweeps it. The sweep's score at 13:00: cash 45 + value (150 × 1.4) =
**255** (was 299). Two genuinely competitive six-landmark builds, for comparison:

| Build | Districts / sides | Spend | Score (cash + value × m) |
|---|---|---|---|
| East Kowloon sweep, stop | 1 / 1 | 150 | **255** |
| Kai Tak (2) + Admiralty (2) + TST Central (2) | 3 / 3 | 120 | 286 |
| Sheung Wan (4) + Causeway Bay (2) + TST Central (2) | 3 / 2 | 160 | **328** |

*(Recomputed 2026-08-18. Sweep dropped 299→255 and the Kai Tak-anchored comparator dropped
312→286 — both fell, since both draw on Kai Tak/East Kowloon's now-cheaper landmarks — but
the **margin between them widened**, from +13 to +31. The Sheung Wan-anchored comparator is
completely unchanged at 328, since none of its landmarks exceed the 30 KD compression
threshold, and it remains the clear best of the three.)*

The middle row matters most: it starts from the *same* far corner of the board — a team
already near Kai Tak — and beats the sweep just by crossing into two more sides instead of
finishing East Kowloon, by a wider margin than before compression. Three landmarks and half
a day lose to six landmarks either way, and there's still no completion trick that closes
the gap.

**This hand-computed comparison is the optimistic case, same as the far/near one above —
and here the gap between it and reality is larger.** `simulated-playtest.md`'s 25-team
model shows the sweep-and-stop archetype is **structurally immune to time pressure**
(0% time-bound across every one of nine scenarios tested, at every compression ratio tried,
because it only ever visits one destination) in a way this static comparison can't capture.
At higher simulated dwell times the sweep still occasionally ties or edges out a
far-crossing build in practice, even though this table shows it losing decisively. Price
compression narrowed that gap (a steeper ratio narrows it further, at the cost of
flattening East Kowloon's price against Kai Tak's — see the calibration log for why 0.45
was chosen over a steeper alternative) but did not close it, because the mechanism is about
time, not price. The residual is intended to be closed non-mechanically, via the leader
briefing below, not by further price changes.

**What broke both defences, before 2026-08-17: the ×2.2 ambiguity.** *(Resolved — the tier
table was retired entirely. Kept for the record.)* East Kowloon has exactly three
landmarks, so owning all three *is* a complete district but is *not* "4 or more". Under the
completion reading the sweep scores **467** instead of 383 — near-competitive, for half the
work and a third of the exploration. **This is the strongest reason to resolve open item 12
as "×2.2 at 4 or more owned"**, which caps every three-landmark district at ×1.8 and keeps
the sweep firmly mediocre.

**The residual problem is not the score, it is the clock.** A mediocre final score punishes
the team at 17:00, far too late to change what they did with their afternoon. Nothing in
the economy tells them at 13:00 that they should move.

**The good news is that the incentive already points the right way, and the same-side cap
makes it point harder — if anyone tells them.** Cash scores 1:1 and on-site tasks are
self-service and need no purchase, so for the stranded East Kowloon team at 13:00 — now
cash **45**, not 5, and stopping at **255**, not 299 (see above) — the same three options
still apply directionally: farm tasks in Kai Tak, cross to Admiralty (unlocks a second held
district on a second side → ×1.6), or buy one more unpaired landmark.

**Not re-derived to exact figures for the 2026-08-18 compression** — the table below is
kept as the last precisely-computed version (against the pre-compression 299 baseline) for
its *shape*, not its numbers: Kai Tak's own task rate also dropped under compression, so all
three deltas shift, and re-deriving them precisely wasn't judged worth doing by hand when
`simulated-playtest.md`'s model already captures this kind of afternoon-reallocation
behaviour more realistically than a static three-option table can. If this specific
guidance is going into the leader briefing, re-derive it against the current prices first.

| Afternoon option | Resulting score | vs. stopping (299, pre-compression) |
|---|---|---|
| Farm on-site tasks in Kai Tak, buy nothing | 369 | +70 |
| Earn 70 farming, travel to Admiralty, buy all 3 (crosses to a 2nd side → ×1.6) | **429** | **+130** |
| Buy one more (unpaired) landmark anywhere | 373 | +74, roughly flat with farming |

*(Corrected 2026-08-17, pre-compression. Crossing to Admiralty used to be the worst of the
three options, +24 against farming's +70, because it was priced under the old ×1.8 tier
without crediting the district it opens. Under the district-count rule it unlocks a second
held district on a second side, which lifts the *entire* portfolio to ×1.6 — making it the
best option by a wide margin, not the worst. That ranking should still hold post-compression
even though the exact deltas have shifted — crossing still opens a second district, which
still moves the whole portfolio's multiplier, and compression didn't touch that mechanic.)*

Task-crossing — not just task-farming — is now both the highest-scoring option and the most
exploration-positive one. No team will derive that unaided, so it belongs in the leader
briefing rather than in the economy — see `operations.md`.

### Staged fix — cap the multiplier at 3 (NOT IN EFFECT)

*Superseded 2026-08-17 — historical record only.* This proposed capping the per-district
depth tier table (`1.0/1.4/1.8/2.2`) at 3. That table was retired entirely, not capped, when
the multiplier was rekeyed to district count; there is no per-district depth tier left to
cap. Kept for the reasoning, not as a live option.

**Proposal:** change the tier table from `1.0 / 1.4 / 1.8 / 2.2` to
**`1.0 / 1.4 / 1.8 / 1.8`** — the multiplier stops rising after the third landmark in a
district. `data/landmarks.csv` is unaffected; this is a rules change, not a price change.

**Why it works.** Because the multiplier applies to the *whole* district spend, marginal
return currently *rises* with depth, which is why completion dominates and why there is no
reason to leave a district. Capping the top tier is the only change that makes the marginal
return fall:

| Tier table | 2nd landmark | 3rd | 4th | Shape |
|---|---|---|---|---|
| `1.0/1.4/1.8/2.2` (current) | +0.8p | +1.6p | **+2.4p** | rises — never stop |
| `1.0/1.4/1.8/1.8` (capped at 3) | +0.8p | +1.6p | **+0.8p** | **falls at the 4th** |
| `1.0/1.4/1.4/1.4` (capped at 2) | +0.8p | +0.4p | +0.4p | falls at the 3rd, then flat |

What this buys:

- **A real stopping point at 3 per district**, which with the two-district cap makes the
  optimum genuinely 3+3 and the best build 6 landmarks — restoring the target pace and the
  claim in `concept.md` that the desk analysis found to be wrong.
- **Item 12 dissolves.** With the top tier at 3, "4 or more (district complete)" never
  arises, so there is nothing to disambiguate and nothing to reprint around.
- **The completion-dominance finding goes away** — 4+2 no longer beats 3+3.

What it does **not** do: the far/near gap is unchanged at +32, because gain is still
proportional to spend. That remains the compressed price table's job.

**Cost:** profitable buyer positions per landmark drop from 5 to 4 (see below). Acceptable
at 25 teams; it would not be at 35.

### Capping at 2: only fails at ×1.4, and the fix is to raise the multiplier

*Superseded 2026-08-17 — historical record only.* Same as above: this is buyer-position
analysis for the retired per-district depth tier table, not the live district-count
multiplier. Kept for the reasoning, not as a live option.

The shallower version — `1.0 / 1.4 / 1.4 / 1.4` — is not viable, for a reason that is easy
to miss. **But the failure is caused by the multiplier being too low, not by the cap**, and
raising it repairs the problem completely. See "cap at 2, done properly" below.

A buyer at ladder position *n* pays `base × (1 + 0.25(n−1))` but scores `base × m`. The
purchase is only worth making while **m exceeds the ladder**:

| Top multiplier | Buyers who profit | First buyer who loses money |
|---|---|---|
| ×2.2 (current) | 1–5 | 6th |
| ×1.8 (cap at 3) | 1–4 | 5th |
| **×1.4 (cap at 2)** | **1–2** | **3rd** |

At ×1.4 only the first two buyers of any landmark can profit from it. Across 51 landmarks
that is ~102 worthwhile purchases for 25 teams needing ~6 each — roughly 150. Most teams
would be making score-negative purchases, which is **exclusivity by price**: precisely the
land grab the 2.5× cap exists to prevent (see "the cap is load-bearing" above).

**The general constraint:** the top multiplier and the price ladder are coupled. Supporting
*b* profitable buyers requires `m_top > 1 + 0.25(b−1)`.

### Cap at 2, done properly (NOT IN EFFECT)

*Superseded 2026-08-17 — historical record only.* Also written for the retired per-district
depth tier table. Kept for the reasoning, not as a live option.

Applying that constraint in reverse: a two-tier table works fine if the top multiplier is
raised to restore the headroom.

| Table | 2nd landmark | 3rd | 4th | Buyers who profit |
|---|---|---|---|---|
| `1.0/1.4` | +0.8p | +0.4p | +0.4p | 1–2 — **not viable** |
| `1.0/1.8` | **+1.6p** | +0.8p | +0.8p | 1–4 — same as cap-at-3 |
| `1.0/2.2` | **+2.4p** | +1.2p | +1.2p | 1–5 — same as today |

Both raised variants are viable. What they change is *where the peak sits*: the big reward
moves to the **second** landmark in a district, then flattens. Compare cap-at-3, which peaks
at the third and then falls. So a two-tier table rewards **opening** districts rather than
finishing them — which is the shape a breadth-first design wants.

**But it does not actually deliver breadth**, and this is the important finding.

### Why no tier table can produce breadth

*Superseded 2026-08-17 — historical record only.* This finding is written for per-district
depth tier tables and doesn't describe the live mechanic, but its conclusion is the reason
the design moved away from depth tiers entirely: the district-count multiplier plus the
same-side cap (`Set bonuses` above) is the breadth fix this section concluded a tier table
couldn't deliver. Kept because it explains why the current design looks the way it does,
not as a live proposal.

Under every variant tested — current, cap-at-3, cap-at-2 at ×1.8, cap-at-2 at ×2.2 — the
best affordable build is **six landmarks in two districts**, and East Kowloon appears in it.
Raising the district cap from 2 to 3 changes nothing: the search still picks two districts,
because **money runs out before a third can be opened.**

The cause is structural. Gain = `spend × (m − 1)`, so gain is proportional to spend no
matter how the tiers are arranged. Expensive districts therefore always win, and the cheap
districts a breadth strategy would need are exactly the ones that return least. The tier
table cannot reach this; it is the same coupling described in the first known weakness.

**The lever that can is the additive bonus** — fix 2 in "the fix, in order" above. A flat
award per district tier decouples gain from spend, which makes breadth-versus-depth a
*tunable* ratio rather than a fixed consequence of the price list. For example, at +50 per
district held at 2 and +70 at 3, a 2+2+2 build scores 150 against 3+3's 140 and breadth
wins; at +40 and +80 the ranking reverses. That knob does not exist under a multiplier.

It remains a last resort — `rules.md`, the worked example and `Standings` all need
rebuilding — but it is the only mechanism here that actually answers "balance depth and
breadth."

### Staged fix — the compressed price table (SUPERSEDED, see below for what's live)

*Superseded 2026-08-18 — historical record only, not the live transform.* This was the
original proposal: compress the **whole** price range at `p' = 30 + 0.75×(p−30)`, mapping
10→20, 20→20, 30→30, 40→40, 50→50, 60→50, 70→60. It was tried first and reverted after
simulation showed it doubled the price of every 10 KD landmark with the allowance left
untouched, which broke near-crossing's affordability (plan-completion 85–98% → 15–27%)
without meaningfully helping the far/near gap it targeted. Kept here for the record — the
diagnosis it prompted (compression must leave the cheap end alone) is what led to the
version actually applied.

**What's live instead**, applied 2026-08-18: `p' = p` for `p ≤ 30 KD`, else
`p' = 30 + 0.45×(p−30)`, rounded half-up to the nearest 10 —
`scripts/apply_price_compression.py`, now defaulting to this ratio. It only touches the
four districts whose landmarks exceed 30 KD (Mongkok, West Kowloon, Whampoa–Hung Hom,
Sham Shui Po–Prince Edward, Kai Tak, East Kowloon); everything at or below 30 — which is
most of the board, and all of near-crossing's build — is untouched. See the calibration
log for the full before/after, including why 0.45 was chosen over the two other ratios
tested (0.6 and 0.35).

Costs of the applied version, for the record:

- **It breaks the `2025 points × 10` traceability** for the landmarks it touches. Mitigated
  by `base_price_precompression`, a new column in `landmarks.csv` holding the original
  2025×10 value — `points_2025` itself is untouched.
- **It thins the top of the board's price texture**: Mongkok, West Kowloon, Whampoa–Hung
  Hom and Sham Shui Po–Prince Edward all land at or near 30–33 KD, close together where
  they used to spread 30–42. The cheap end (≤30 KD, roughly two-thirds of the board) keeps
  its full texture, unlike the reverted whole-range version.
- **The affordability brake on East Kowloon sweeping is measurably weaker** — see "The
  single-district endgame" below. This is a direct, intended-tradeoff consequence, not an
  oversight, but it means the sweep-and-stop scenario is now easier to attempt, not harder.

### East Kowloon is still not walkable

Set bonuses assume a district is a cluster you can walk around. East Kowloon is not — it
was merged from Choi Hung, Lok Fu and Diamond Hill, which held one landmark each and were
too few to form a set on their own.

**This is not fully fixable, and that conclusion is the finding.** There is no walkable
cluster of three landmarks in the east of the territory. Every available option is a choice
about how bad the travel is, not a route to walkability. Rebuilding the district around
Kai Tak and Sung Wong Toi was considered and rejected: it leaves Choi Hung Rainbow and Nan
Lian Garden with no district, and `verify.py` requires every landmark to sit in a district
of 3–5.

**What was done: Kwun Tong Promenade is dropped** (2026-08-16, see the calibration log). It
was 45 minutes from base — the furthest point on the board — and audit item 10 records that
it was the one scored landmark the 2025 *Landmarks* tab never assigned to an MTR district
at all, so its placement in East Kowloon was always an inference. It is preserved in
`data/landmark-candidates.csv`.

What that bought:

| | Before | After |
|---|---|---|
| Landmarks | 4 | 3 |
| Worst ETA | 45 min | 37 min |
| Separate MTR stops | 4 | 3 |
| Best-3 gain (single district, ×1.4) | +88 | +84 |

The three that remain are a tighter shape than the sprawl they replace: Choi Hung and
Diamond Hill are adjacent on the Kwun Tong line, and Sung Wong Toi is one interchange away.
It is a compact MTR triangle rather than a walk.

**East Kowloon is therefore now explicitly the expedition district** — three train rides
for the highest gain of any *single* district (+60 post-compression, was +84 — see "The
multiplier is multiplicative" above), though a crossing build now out-gains it outright.
That is a legitimate high-risk play, but it is only legitimate if teams can *see* it coming.
Two things follow:

- `rules.md` should warn that the far districts cost significantly more travel time, so a
  team choosing one is choosing it knowingly rather than discovering the cost at 14:00.
- It remains the weakest district on the board. If the playtest shows teams taking it and
  running out of day, dropping it entirely is a reasonable outcome — the three landmarks
  would move to `landmark-candidates.csv` alongside Kwun Tong Promenade.

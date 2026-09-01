# Kelingkong 2026 — concept

## Why the format changed

2025 scored by **visiting**. Every landmark added points with no diminishing return, so
the optimal play was to cover as much ground as possible before 16:30. The format
rewarded hurrying, and the committee's own retro recorded the result: *terlalu kompetetif
(gabisa di enjoy)* — too competitive to enjoy.

There was no point at which a group could reasonably say "we have enough, let's sit down."

2026 scores by **owning**. Teams buy landmarks with in-game currency, and the winner has
the highest property value plus remaining cash. The reason for the change is not novelty
— it is that a purchase economy lets us make **depth pay better than distance**, which is
the direct fix for a day that felt rushed.

## The core loop

> Travel to a landmark → complete its on-site task to earn currency → decide whether to
> buy it → cluster purchases within a district to trigger multipliers → optionally drop
> into a scheduled game post heat for a cash injection.

## How pacing is enforced

Everything is derived from one number: **a team should own 5–6 landmarks by 16:30.**

About 4.5 hours of the day is live exploration once assembly, lunch and closing are
subtracted. A landmark costs a team 25–40 minutes all in — travel, finding it, doing the
task, deliberating, submitting. That puts a comfortable day at 5–6 landmarks and a
sprint at 9–11.

Three mechanisms hold the pace there:

1. **Set bonuses reward pairing, not coverage.** A landmark only counts once it has a
   partner in the same district, so walking Sheung Wan's four sites beats sprinting Central →
   Mongkok → Kai Tak. Travel time collapses.
2. **The multiplier is keyed on how many districts you hold**, not how deep you go in one.
   Holding a district means owning 2+ landmarks there; holding three districts is the top
   tier. That makes the optimum **2+2+2** — six landmarks, three neighbourhoods. Past the
   third district the multiplier stops rising, so there is a natural stopping point — the
   thing 2025 lacked entirely.

   *Revised 2026-08-17 from a depth-tiered table capped at the best two districts, which
   could not reward breadth at any setting: a third landmark in an existing district paid
   four times what opening a new one did. See `economy.md` and `rules-audit.md`.*

   **The three districts also have to cross sides.** District-count breadth alone is
   satisfiable inside Hong Kong Island — Admiralty, Sheung Wan and Causeway Bay are three
   of the board's four cheapest, nearest districts, so 2+2+2 there hit the top tier without
   a harbour crossing, contradicting the "see parts of Hong Kong you wouldn't find alone"
   goal in `event-brief.md`. The multiplier is now capped at ×1.4 unless held districts
   span 2+ sides (Hong Kong Island / Kowloon / East Kowloon). *Added 2026-08-17; see
   `economy.md`.*
3. **Time binds before money does.** The clock allows about 6 landmarks; income covers
   about 5. Money forces choices *between* landmarks rather than rewarding speed.

**Staggered starting districts** prevent a fourth failure mode: all 250 people converging
on the same landmarks at 10:30 because set bonuses point everyone toward the same
"obviously good" cluster. Each team is assigned a different district to start in — but
only from the 8 nearest, cheapest districts, not all 13. The far districts are priced on
the assumption that going there is a *chosen* bet; assigning one by lottery would turn
that bet into an imposed handicap for whichever team drew it. See `economy.md` for the
pricing logic and `operations.md` for the assignment mechanism.

## Locked decisions

| Area | Decision |
|---|---|
| Date | Saturday 12 September 2026 |
| Participants | 210 baseline |
| Teams | 21 teams of 10, 2 leaders each (~42 leaders) — fixed 2026-09-01, holding at the 2025 team count rather than the 25 this table originally targeted; see "Group size" below |
| Target pace | 5–6 landmarks owned per team |
| Value model | Set bonuses keyed on **districts held** (2+ landmarks each): ×1.4 / ×1.6 / ×1.8 for 1 / 2 / 3+, capped at ×1.4 unless held districts span 2+ sides |
| Ownership | Non-exclusive, rising price capped at 2.5×, first buyer holds the title |
| Income | Starting allowance + on-site tasks + game post winnings. **No stipend.** |
| Game posts | 3 posts × 3 helpers = 9 staff, separate from group leaders |
| Post format | Scheduled 15-minute heats, 2 teams, fire on time regardless of turnout |
| Ledger | Apps Script (write) → Sheet (compute) → published board (read). See `ledger-system.md` |

## Three things that look like bugs but aren't

**A lone purchase is score-neutral.** A first buyer pays face value for face value, so
buying one landmark in a district changes nothing — and it does not make that district
*held*, so it does not move the multiplier either. **Set bonuses are the only source of
score growth.** This is deliberate — it is what makes pairing the whole game — but it
must be stated plainly in the participant rules, or teams will scatter and wonder why
their score never moved. It is now the only threshold in the design, which is the main
reason the 2026-08-17 revision was worth making.

**Later buyers pay more for the same value.** Someone buying Man Mo Temple fifth pays
1.5× what the first buyer paid, for identical scoring value. That is a gentle reward for
decisiveness. It never blocks anyone, because the price is capped at 2.5×.

**Game posts don't pay very well.** A win is worth roughly one mid-tier landmark. Posts
exist for the *social* goal, not the economic one — they are the only place teams from
different groups meet all day, since on-site tasks need no volunteers and keep each team
sealed in its own bubble. If posts paid well, teams would farm them instead of exploring
Hong Kong.

## What this does not fix

**Group size.** This table originally targeted 25 teams of 10 — a *growth* from 2025's 21
— on the hope that recruitment would clear ~50 leaders. **Fixed 2026-09-01 at 21 teams of
10**, the same team count as 2025: recruitment held flat rather than growing. Either way,
group size itself stays at 10, unimproved. *"Group terlalu rame"* was the first complaint
in the retro, at exactly 10 per team. No mechanic here touches it — team size is a
function of how many leaders get recruited, so it is a recruitment decision. Getting to
8–9 per team means 28+ teams and ~56 leaders — further out of reach at 21 teams than it
was at the hoped-for 25.

## Where things are

- Prices, multipliers and the calibration log → `economy.md`
- How the numbers get validated before printing → `playtest.md`
- Post timetable, heats and par scores → `game-posts.md`
- Participant-facing rules → `rules.md`
- Rundown, rain plan, open items → `operations.md`
- The board itself → `../../data/landmarks.csv`

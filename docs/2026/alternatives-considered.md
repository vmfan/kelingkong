# Alternatives considered

Five mechanics the committee proposed that did not make the final design. All five were
reasonable, and **each one's intent survived** — what changed was the mechanism. This
document exists so those decisions can be revisited with the reasoning intact, rather than
re-argued from scratch.

Read alongside `concept.md` for what was chosen.

---

## 1. Discount scaled by distance

**The proposal.** Landmarks list below their scoring value, discounted more heavily the
further they are from base. Buy a 40-value landmark for 28 and you profit 12 on the spot.

### What it got right

Two real problems, solved cleanly:

- **Score-neutrality.** Under the final design a lone purchase earns nothing, which is
  counterintuitive and has to be explained carefully. Under a discount model every
  purchase visibly profits. That is easier to teach.
- **Travel compensation.** Distance-scaling directly pays teams for the time cost of going
  far, which the 2025 board needed.

### Why it lost

**It makes volume the winning strategy.** If every purchase profits, then more purchases
means more score, linearly and without limit. The optimal play becomes buying as many
landmarks as possible as fast as possible — which is precisely the 2025 experience with a
payment step bolted on. The complaint we are fixing is pace, and this mechanic rewards
speed.

**It never says "you have enough."** 2025's deepest flaw was that nothing in the rules
gave a team permission to stop. A per-purchase profit has the same property: there is
always another profitable purchase, so a team that sits down to eat is losing.

The decisive factor was the income model. With a **fixed allowance and no earning**, this
mechanic is genuinely calm — you cannot buy more by hurrying, only by choosing better, and
the day becomes an allocation puzzle. But the committee chose three income streams
(allowance, on-site tasks, post winnings). With money continuing to arrive all day,
per-purchase profit compounds into a grind.

### What survived

**The distance compensation, in full.** Base prices are still scaled by travel time —
price and distance correlate at **r = 0.91** across districts, and `scripts/verify.py`
fails the build if that relationship weakens. Hong Kong Island landmarks cost 10–40;
East Kowloon costs 70.

What changed is that distance now scales **both** price and value, rather than opening a
gap between them. Far landmarks are a bigger bet, not a free profit.

---

## 2. Exclusive ownership with buyout

**The proposal.** One owner per landmark. A rival can take it by paying a premium —
around 2× — to the current owner.

### What it got right

This is the strongest version of the Monopoly fantasy, and it has a genuinely elegant
property: **at 2× paid to the owner, being bought out is good for you.** You paid 20 and
received 40. It creates real interaction between teams without the usual feel-bad of
losing something.

It is the option that best delivers what "like Monopoly" actually means to people.

### Why it lost

**Board size — this is the decisive one.** 25 teams owning 5–6 landmarks each needs about
**150 ownership slots.** The 2025 board has around 50 landmarks. Exclusive ownership would
mean roughly **tripling the board**: sourcing, pricing, districting, writing an on-site
task for, and physically verifying about 100 new landmarks — in under four weeks, on top
of everything else. That is a schedule risk we cannot absorb.

**At the current board size it becomes a land grab.** With ~50 exclusive landmarks and 25
teams, each team can own two. Scarcity that severe produces a race for the good spots,
which is the pace problem returning through the front door.

**It enables blocking.** Combined with district set bonuses, a team can buy a single
landmark purely to deny a rival their district multiplier. That is authentically Monopoly
and also fairly mean — hard to square with *mau dibikin santai*.

**Enforcement is harder than it looks.** Exclusivity requires an authoritative, real-time
ledger that every team trusts. Any lag between two teams submitting the same landmark
creates a dispute with no referee present, since teams are unsupervised beyond their two
leaders.

### What survived

**Ownership prestige, via the first-buyer title.** The first team to claim a landmark is
named as its titleholder on the live board. The claim is real and visible; it just does
not exclude anyone.

**A softened form of scarcity**, via rising prices. Each subsequent buyer pays +25% of
base, so being first is worth something — but the 2.5× cap means nobody is ever locked out.

---

## 3. Rising landmark value over time

**The proposal.** A landmark's value grows the longer a team holds it, so buying early is
worth more than buying late.

### What it got right

It solves score-neutrality without any explanation at all — property obviously beats cash
because property grows. And it rewards decisiveness, which is a genuinely good thing to
reward.

### Why it lost

**It front-loads a sprint.** If holding longer pays more, the optimal play is to acquire as
much as possible as early as possible. The likely shape of the day becomes a frantic
10:30–12:00 followed by a dead afternoon. The pace problem is not solved — it is
concentrated into the morning, where it gets worse.

**It punishes stopping.** Any time not spent buying is time your money is not
appreciating. Lunch becomes a scoring penalty. Given that "have time to sit down and eat"
is close to the whole point of the redesign, this is the wrong incentive.

**It compounds into a runaway.** Teams that buy early hold longer, score more, and can
afford more. A team that starts slowly — because they got lost, or their first task took
too long — falls behind in a way they cannot recover from. With no stipend in the final
design, there is nothing to catch them.

**It makes the ledger substantially harder.** Every score becomes time-dependent, so the
Sheet must recompute each holding against elapsed time. That is a much more fragile
formula on a day when the ledger cannot be allowed to fail — and it means a team cannot
work out its own score by hand, which they should always be able to do.

### What survived

**The reward for decisiveness — inverted.** Instead of value rising over time, the
**purchase price** rises with each buyer. Move early and you pay less for the same value;
arrive late and you pay a premium.

This produces the same incentive to commit, without the morning sprint, without the
compounding, and without a time-dependent score. It also has a property the original
lacks: the pressure comes from *other teams*, not from the clock — so a team that stops
for lunch loses nothing except the chance that someone else bought first.

---

## 4. Adjacency instead of same-district

**The proposal.** Tighten the set bonus so it requires landmarks to be *adjacent* — sharing
a nearest MTR station — rather than merely sharing a district. A district is a loose unit;
adjacency would guarantee teams walk between their purchases instead of riding.

### What it got right

The intent is sound and it targets a real gap. `economy.md` already records that East
Kowloon is "a compact MTR triangle rather than a walk," so the district rule does let a team
claim a set bonus for three train rides. Requiring adjacency would make the clustering
mechanic mean geographically what it already means arithmetically — which is exactly goal 2
in `../event-brief.md`, spending enough time somewhere to actually be there.

It is also cheap to *define*: `nearest_mtr` is already a column in `../../data/landmarks.csv`,
so no new data collection is needed.

### Why it lost

The board does not support it. Grouping the 51 landmarks by station instead of district:

| Landmarks at the station | Stations | Landmarks |
|---|---|---|
| 1 | 8 | **8** |
| 2 | 2 | 4 |
| 3 | 5 | 15 |
| 4 | 2 | 8 |
| 6 | 1 | 6 |
| 10 | 1 | 10 |

**Eight landmarks (16% of the board) would be the only landmark at their station and could
never form a pair.** They become dead stock — buyable, but permanently score-neutral.

Worse, the orphans are not spread evenly. **All three East Kowloon landmarks sit at
different stations, so the entire district dies** — 210 KD and the three most expensive
landmarks on the board become unbuyable for score. Wan Chai and Sham Shui Po–Prince Edward
drop to a maximum pairable group of 2.

The resulting units are also badly shaped. Districts are 13 groups of 3–5 with zero orphans.
Stations are 19 groups ranging from 1 to 10, and two of them (TST, Central) span two
districts, so adjacency does not nest inside the district structure — it replaces it.

That last point is what makes this expensive rather than merely imperfect. Districts are
load-bearing across the whole design: the `Standings` best-2 calculation, the starting-
district assignment, the game posts anchored one per district, and `scripts/verify.py`'s
district-size checks. Adjacency orphans all of them.

### What survived

**The diagnosis, not the mechanism.** The walkability problem is real but it is
*concentrated*, not general — nine of thirteen districts already have a pairable group of 3
or more at a single station. Rebuilding the scoring unit to fix what is substantially one
district is disproportionate.

Two cheaper routes to the same end:

- **Print walking times between landmarks on the district maps**, so teams self-select
  toward tight clusters without a rule change.
- **Fix the one broken district.** `economy.md` already contemplates dropping East Kowloon
  to `landmark-candidates.csv` if it proves unworkable; the station data is further evidence
  for that, and it would resolve the single-district sweep worry at the same time.

---

## 5. Completion bonus instead of the multiplier

**The proposal.** Drop the district multiplier entirely. Landmarks score face value, and the
only source of growth is a flat **+B for every district where a team owns two landmarks**.
One rule, replacing three (the tier table, the best-2 cap, and the face-value-vs-price-paid
distinction).

### What it got right

By the standard in `rules-audit.md` this is the strongest proposal on the table. Score
becomes `cash + face values + B × qualifying districts` — addition only, no multiplication,
no ranking step, computable by a tired team on the back of a map at 14:00. It is
spend-independent, so it does not inherit the far-district dominance that the multiplier
causes. And it encodes the target shape directly: two landmarks each, in three districts.

It also answers the depth/breadth question honestly, which the multiplier cannot: breadth
becomes a tunable number rather than a fixed consequence of the price list.

### Why it lost

**It removes the budget constraint, and the budget constraint is what stops the race.**

Under face-value scoring, spending cancels — a team pays base and scores base, so the money
spent is neither a cost nor a gain. Qualification is therefore all that costs anything, and
qualification is cheap:

| | Affordable | Time allows | Binds first |
|---|---|---|---|
| Multiplier | ~6 landmarks | ~6 landmarks | **money** |
| Flat completion bonus | **16 landmarks** | ~6 landmarks | **time only** |

Eight districts can be qualified for 240 KD. `concept.md` is explicit that the design
depends on the opposite: *"Time binds before money does… Money forces choices between
landmarks rather than rewarding speed."* Remove that and the optimal play is once again to
cover as much ground as the clock permits — which is precisely the 2025 failure the redesign
exists to fix.

**A flat bonus also kills distance compensation.** Five districts qualify for 20 KD;
East Kowloon costs 140 for the identical bonus. Nobody would ever go, and the far half of
the board becomes dead stock.

| Cheapest qualifying pair | Districts |
|---|---|
| 20 KD | Admiralty, Causeway Bay, Central, TST Central, TST Waterfront |
| 40–80 KD | Sheung Wan, Wan Chai, Mongkok, West Kowloon, Sham Shui Po, Whampoa |
| 100–140 KD | Kai Tak, East Kowloon |

**And it concentrates every team on the same five cheap near districts**, which is the
congestion the starting-district assignment exists to prevent.

Making **B a per-district number printed on the map** repairs the second and third problems
while keeping the rule to a single sentence, and is worth revisiting if the multiplier is
ever abandoned for other reasons. It does not repair the first — no additive scheme does,
because the defect is face-value scoring itself.

### What survived

**The diagnosis, and most of the simplification.** The proposal's real target was the
multiplier's *explanation cost*, and that is addressable without touching the economy.
`rules-audit.md` recommends cutting the best-2-districts cap and the ×2.2 tier, which leaves:

> Own landmarks in the same district and they multiply. Every district counts.

A three-row table applied uniformly — arguably simpler than thirteen printed district
bonuses, and it keeps money binding.

**The multiplier survives because it does a job nothing else does:** it makes spending buy
score, which is what keeps the budget a real constraint, which is what stops the day
becoming a race.

---

## The pattern

The first three proposals were attempts to answer the same question: **what makes property worth
more than the cash you paid for it?** That question is real and unavoidable — without an
answer, buying is pure ceremony.

The final design answers it with **district set bonuses**: value comes from *where* your
landmarks are relative to each other, not from how many you have, how early you bought, or
how far you travelled.

That choice was made because it is the only one of the four that makes **concentrating**
the winning strategy. The other three all reward acquiring more, sooner, or faster — and
every one of those is a variant of the thing that made 2025 feel rushed.

# Game posts

## What posts are for

**Posts exist for the social goal, not the economic one.** On-site landmark tasks need no
volunteers, which is efficient — but it also means a team can spend the entire day
without meeting anyone outside its own ten people. Posts are the only place teams from
different groups collide, and freshmen meeting each other is half the reason Kelingkong
exists.

This is why post payouts are capped at roughly one mid-tier landmark. If posts paid well,
teams would farm them instead of exploring Hong Kong, and the posts would stop being a
social mechanism and start being a grind.

## The three posts

| Post | Location | District it anchors |
|---|---|---|
| Post 1 | Tamar Park | Admiralty |
| Post 2 | M+ | West Kowloon |
| Post 3 | Kai Tak Stadium | Kai Tak |

**Each post sits inside a district on purpose.** A team arriving between heats spends the
gap buying a landmark three minutes away — which is exactly what the set bonuses want them
doing. Waiting stops being dead time and becomes the reason they explore that district at
all.

3 helpers per post, 9 total. Separate from group leaders.

## Heats

**Heats run every 15 minutes**, on the quarter hour, printed on every team's map. A heat
holds **2 teams (~20 people)**.

### The rule that makes this work

**A heat fires on schedule regardless of how many teams are present.**

- Two teams present → they compete head-to-head.
- One team present → it plays against a **par score** and is paid on the same scale.
- Nobody present → the heat is skipped, no harm done.

**No team ever waits for another team to show up.** This is the whole point. A scheduled
format that needs two teams to start would just convert queueing into waiting-for-
strangers — the same dead time in a different costume. The worst case here is a team
arriving at :05 and choosing whether to spend ten minutes nearby or come back later.

### Payouts

| Result | Payout |
|---|---|
| Win a head-to-head | 40 KD |
| Lose a head-to-head | 20 KD |
| Beat par (solo) | 40 KD |
| Miss par (solo) | 20 KD |

Losing still pays. A team that turns up and tries is never worse off for having come,
which matters given there is no stipend to fall back on.

### Cooldown

**Added 2026-08-18.** A team cannot play the very next heat at the same post it just
attended. This applies regardless of result — win, lose, beat par, or miss par all start
the cooldown identically. The team must sit out one 15-minute slot at that post before
it may play there again. It can still return to the same post later in the day, and it
can play a different post in the meantime — the three posts sit far enough apart that no
amount of hustling covers the distance inside 15 minutes anyway, so the cooldown only
needs to be enforced per post, not across all three.

**Why:** uncapped, a team parked at one post could clear roughly 30 KD every 15
minutes — on the order of 2 KD/min, well above what buying landmarks returns even at the
best case (a team already at the ×1.8 tier buying one more landmark nets somewhere around
1.2 KD/min once dwell time and task income are counted). Posts paying more per minute
than the landmark economy would turn the social mechanic in "What posts are for" above
into the best-paying strategy on the board — exactly what the payout cap there exists to
prevent. The cooldown roughly halves the ceiling, to somewhere around 1–1.3 KD/min
depending on whether the idle slot gets used for a nearby task, which lands back in the
same range as legitimate landmark play instead of dominating it.

**Enforcement is cheap.** Only the two team IDs from the immediately preceding heat at
that post need checking — a 2-team lookback, not a running total — so post staff can
track it by memory or a slip of paper. The Form submission already logs team ID and
placement per heat if a Sheet-side check is wanted instead.

### Par scores

Every game needs a par: the score a team of ten should hit with reasonable effort. Set
each par during the playtest, not by guesswork — a par that is too high makes solo play
feel punishing, and one that is too low makes head-to-head pointless.

Procedure in `playtest.md` (instrument C): run each game 3+ times with different groups of
ten, and set par slightly below the median group's score. Time every run *including the
explanation*, since the 15-minute ceiling above is what the games have to fit inside.

## Posts are optional

**There is no penalty for skipping a post.** 2025's −10 for visiting none is dropped; it
punished exactly the teams already having the worst day.

Because posts are optional, demand self-regulates. A team that sees a busy post simply
leaves and buys a landmark instead.

## Capacity

| | Value |
|---|---|
| Heats per post | 18 (15-min intervals across ~4.5 h) |
| Team-slots per post | 36 |
| Total team-slots | **108** |
| Ceiling demand | 75 (25 teams × 3 posts) |
| **Utilisation** | **69%** |

The 15-minute interval is what absorbs 250 participants. At 20-minute heats the same
demand runs at 96% — effectively saturated, which means a team arrives at a full heat and
waits 20 minutes for the next one. Shortening the interval costs no extra helpers.

**The constraint this creates: every game must finish inside 15 minutes**, including
explaining the rules to a group that has never seen it. That is an input to game design,
not something to discover on the day.

## Designing the games

Requirements, in order of how hard they are to retrofit:

1. **Completes in under 15 minutes**, explanation included.
2. **Works for 20 participants with 3 staff.** Relays, mass quizzes, and
   everyone-participates formats work. Anything fiddly or equipment-heavy does not.
3. **Works head-to-head *and* solo against par.** If a game only makes sense with an
   opponent, it breaks the moment a single team turns up.
4. **Mixes the two teams where possible.** Two teams competing as blocks is fine; two
   teams shuffled into mixed sides is far better for the social goal.

## Optional: suggested slots

Each team can be given a *suggested* heat time per post at kickoff — 2025's lottery
reworked as a timetable. It spreads load deterministically and is ignorable without
penalty. Worth doing if signups come in at the top of the range.

## Briefing the 9

Post staff need to understand, in this order:

1. Heats start on the clock. Do not wait for a second team.
2. A solo team plays against par and gets paid.
3. Losing pays 20 KD. Nobody leaves with nothing.
4. A team that just played sits out the next slot at this post — win, lose, or solo,
   it doesn't matter which.
5. How to record a result in the Form — team ID, placement, done.

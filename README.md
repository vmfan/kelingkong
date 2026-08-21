# Kelingkong

Orientation event for Indonesian university students in Hong Kong. Students are grouped
into teams and explore Hong Kong together, so freshmen meet each other naturally while
being introduced to the city.

**Next event: Saturday 12 September 2026.** Target 250 participants across 25 teams.

2026 replaces 2025's points-based landmark hunt with a **property-ownership game**: teams
buy landmarks with in-game currency, and the winner has the highest property value plus
remaining cash. The point of the change is pacing — a purchase economy lets us make
*depth* pay better than *distance*, which is the direct fix for 2025's main complaint
that the day felt rushed.

## Layout

| Path | What it holds |
|---|---|
| `docs/event-brief.md` | What Kelingkong is and who it serves |
| `docs/2025/` | How last year ran, what went wrong, and an audit of its data |
| `docs/2026/` | This year's system: concept, economy, game posts, rules, operations |
| `apps-script/` | The ledger write layer. Deployed with `clasp` |
| `web/` | The participant page — live board, team view, standings |
| `data/` | The board — landmarks, districts, prices. Source of truth. |
| `Old Kelingkong (2025)/` | Original spreadsheet, archived read-only |

## Start here

- New to the project → `docs/event-brief.md`
- Want to know how the game works → `docs/2026/concept.md`, then `economy.md`
- Running a game post → `docs/2026/game-posts.md`
- Working on the board → `data/landmarks.csv` and `docs/2026/economy.md`
- Wondering why something changed → `docs/2025/retrospective.md`

## Current status

Mechanics are locked; see `docs/2026/concept.md` for the decision table. Open items and
the countdown to event day are tracked in `docs/2026/operations.md`.

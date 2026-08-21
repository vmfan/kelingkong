# Surprise missions — Sheet/Apps Script build spec

Handoff document for whoever builds this in the live `Kelingkong Ledger` Google Sheet and its
Apps Script. **This lives outside this repo** — same convention as every other Sheet/`Code.gs`
change referenced from here (e.g. the Kai Tak task-rate edit logged in `economy.md`,
2026-08-19: "the live Sheet's `Board` tab itself is not yet updated... outside this repo and
needs a deliberate, verified pass"). Nothing here has been applied to the live Sheet yet.

**Not finalized:** the penalty amount and which 2025-style missions get used are open — this
spec is written so neither has to be decided before the build starts. See "What's still open"
at the bottom.

## What this is for

2026 keeps 2025's surprise missions (`docs/2025/format.md:61`: committee-broadcast ad-hoc
tasks, five per day in 2025) but changes the mechanic from reward to penalty. Design rationale
lives in `docs/2026/economy.md`'s `## Surprise missions` section and its 2026-08-20 calibration
log entry — read that first if anything here seems arbitrary. Short version:

- Each mission gets a 20-minute window from when the committee issues it (widened from 15 on
  2026-08-20 — see "Broadcast schedule" below for why).
- Any team without an un-voided completion photo by the deadline is deducted a flat KD amount.
- There is no reward for completing a mission — completing just avoids the deduction.
- If a submitted mission photo is later voided by a banker (Kontrol review), the deduction
  re-applies, even though it looked avoided at the deadline.

## Prerequisite reading

- `docs/2026/ledger-system.md` — the three-layer architecture (`Board`/`Ledger`/`Standings`
  formulas, Apps Script write layer, Kontrol post-hoc photo review). Everything below assumes
  and extends this, it does not replace any of it.
- `docs/2026/economy.md`, `## Surprise missions` and `## Final score` — the mechanic and how
  `Standings` currently computes a team's score.
- The live Sheet's existing `Journal`/`Transactions` tab and `Code.gs` — this spec describes
  the *shape* of the new pieces (columns, fields, formula logic) but you should match your
  actual current column letters/tab names rather than assume the ones implied here. Where this
  doc can't be authoritative about the live layout (it isn't in this repo), it says so.

## 1. New `Missions` tab

A small manually-populated tab. One row per mission — either **added live**, at the moment
each mission is broadcast, or **pre-filled ahead of the event** with a future `issued_at`. Both
are the same mechanism: `?misi=1` and the `Standings` penalty are purely `NOW()`-driven (§3,
§4 below), so nothing distinguishes "typed five seconds before it goes live" from "typed a week
earlier with a scheduled time" — the row just sits inert until real time enters its window.
Pre-scheduling does not leak anything to participants early: `?misi=1` returns `active: false`
for any row whose `issued_at` hasn't arrived yet, same as an empty tab.

**What pre-scheduling does not remove: the chat broadcast.** `rules.md` §5 has teams watching
the leader chat for the `🚨 RAZIA PAJAK` message as the primary signal (the in-app countdown box
is the backstop, not the trigger a team is told to expect). Nothing in this system can post to
that chat — it's an external channel — so if missions are pre-scheduled, a person still needs
to paste the pre-written `text` into chat at the scheduled minute. Pre-scheduling turns the
day-of job from "compose and enter a mission" into "copy and paste on a timer," not into
nothing. If that residual manual step is unwanted, the fallback is dropping the chat trigger
and relying solely on the app's countdown box — that needs a `rules.md` §5 rewrite and is a
separate decision, not implied by pre-scheduling alone.

| Column | Type | Notes |
|---|---|---|
| `mission_id` | text | Short unique id, e.g. `M1`, `M2`. Committee-assigned when the row is added |
| `text` | text | Free text shown to participants, e.g. "Foto tim kalian di stasiun MTR mana saja!" (Indonesian — see `rules.md`'s participant-facing convention in `CLAUDE.md`) |
| `issued_at` | datetime | When the mission's window opens. `=NOW()` for a live-entered mission, or a specific future timestamp for a pre-scheduled one — see above. Must be typed as real Hong Kong wall-clock time if not a formula (`apps-script/README.md`: the spreadsheet's timezone must be Asia/Hong_Kong for this to mean what it says) |
| `deadline` | datetime | `issued_at + 20 minutes`, formula or manual (widened from 15 on 2026-08-20 — see "Broadcast schedule") |
| `penalty_kd` | number | KD deducted per team that misses this mission. **Per-mission, not a board-wide constant** — the committee can vary it mission to mission. 10 is the current working default (see "What's still open") |

~5 rows/day at 2025's pace. No headcount implication — populating a row and sending the
`🚨 RAZIA PAJAK` chat message (`operations.md`, Briefing the leaders) is the entire committee
action per mission.

## Broadcast schedule

**Decided 2026-08-20, revised same day.** *When* the five missions fire, independent of what
they say (mission text and `penalty_kd` stay open — see "What's still open" below). Built
against `operations.md`'s rundown: dispersal 10:30, first heats 10:45, lunch ~12:00–13:30,
last heats 16:00, Form close 16:30.

### The post-heat clash, and why two changes together fix it

The first pass of this schedule only offset mission times 5 minutes from the heat
quarter-hours, which avoided the *chat-message* collision but not the underlying one: heats
(`game-posts.md`) run continuously every 15 minutes from 10:45–16:00, so **some** heat is
always in progress somewhere, and a team caught mid-heat when a mission fires has to choose
between the game and the photo. No choice of broadcast time removes this — it's structural,
not a scheduling bug — but two changes together make it a non-issue:

1. **The window widened from 15 to 20 minutes** (`economy.md`, `rules.md` §5, both updated
   2026-08-20). Since heats cap at 15 minutes, `window − 15` is a hard floor on how much of
   the mission window survives after the worst-case heat ends — with a 20-minute window
   that floor is **5 minutes, guaranteed, for every team in every phase**, independent of
   timing. This is the piece that actually closes the gap; nothing else here does.
2. **Broadcast times are biased to land 1 minute before the next heat's quarter-hour** (`:14`
   / `:29` / `:44` / `:59` past the hour, not `:00`/`:15`/`:30`/`:45`) instead of just after
   it. This doesn't change the guaranteed floor from (1), but it changes who hits it: only a
   team whose heat happens to *start* in the minute right after broadcast sees the bare
   5-minute floor. A team already mid-heat when the mission fires is, on average, close to
   finishing — e.g. a team in the heat that started 14 minutes earlier gets nearly the full
   20 minutes free once that heat ends. Firing near the *end* of the cycle instead of the
   start pushes most affected teams toward the generous case rather than the tight one.

Combined with the operational note that a mission only needs one leader to step aside for the
photo, not the whole team to stop playing (see "Briefing the leaders" in `operations.md`),
this treats the clash as closed rather than merely mitigated.

### Schedule

| Mission | `issued_at` | `deadline` (20 min) | Rationale |
|---|---|---|---|
| M1 | 10:59 | 11:19 | ~29 min after dispersal, 1 min before the 11:00 heat — teams have reached a first landmark, well clear of lunch |
| M2 | 13:44 | 14:04 | Earliest slot on this offset that's fully clear of lunch (`issued_at ≥ 13:30`) |
| M3 | 14:29 | 14:49 | +45 min |
| M4 | 14:59 | 15:19 | +30 min |
| M5 | 15:29 | 15:49 | +30 min — 41 min clear of the 16:30 Form close, and ends before the 16:00 last-heats crunch even starts |

Constraints that produced these times, so a future reader can re-derive them if the rundown
shifts (`operations.md` open item 1, "Confirm event timings against venue"):

- **No mission's window (issued_at → issued_at+20) touches lunch.** For a morning slot this
  means `issued_at + 20 ≤ 12:00`, i.e. `issued_at ≤ 11:40`; for an afternoon slot it means
  `issued_at ≥ 13:30`. Combined with the `:14/:29/:44/:59` offset (below), the latest safe
  morning slot on that phase is `10:59` and the earliest safe afternoon slot is `13:44` — both
  used above.
- **Nothing before ~11:00.** Teams need time to actually reach their first landmark after the
  10:30 dispersal before the first mandate lands.
- **Nothing after 15:29.** `deadline` (15:49) leaves 41 minutes of clear runway before the
  16:30 Form close and finishes before the 16:00 last-heats crunch entirely, so a team that
  misses this one at the buzzer still has time to travel and submit before the Form closes.
- **Times land on `:59`/`:14`/`:29`/`:44`** — one minute *before* the next heat's
  quarter-hour start, not just after it. See "The post-heat clash" above for why this phase
  (biased toward the end of the heat cycle) beats the originally-considered `:05`/`:20`/`:35`/
  `:50` phase (biased toward the start): both avoid the chat-message collision equally, but
  this one skews more teams into the generous case when a heat is in progress at broadcast
  time.

Gaps between missions are uneven on purpose (20 min, then a lunch-spanning gap, then 45 / 30
/ 30) — the spacing follows the constraints above, not a fixed cadence. Any other 15-minute
increment on the same `:14/:29/:44/:59` phase that respects the lunch and end-of-day bounds
works equally well; this is one valid solution, not the only one.

**Applied to the live Sheet, 2026-08-20.** `Missions!deadline`'s formula is now `issued_at +
20 min`, and the five `issued_at` values above are pre-filled as `M1`–`M5` (`mission_id`,
`issued_at` only — `text` and `penalty_kd` left for the committee, as planned). Verified
against the deployed endpoint at the 19-of-20-minute boundary, where the prior `+15` formula
would already have expired. Full record in `ledger-system.md`.

## 2. `doPost`: new `action = "mission"`

Extend the existing action-type handling (alongside `buy`, `task`, `object`) with a `mission`
branch. Reuse everything the existing types already do — this needs no new subsystem:

- **Same payload shape** the participant page already sends for every action:
  `{ submissionId, team, action: "mission", item: <mission_id>, photo }`. `item` is the
  `mission_id` from the `Missions` tab, not the mission text.
- **Same append-first write.** Write the raw row to the journal before any validation, same as
  every other action — a submission must survive even if something downstream throws.
- **Same idempotency handling** via `submissionId` — a duplicate mission submission (network
  retry, double-tap) is a no-op, not a double credit. There is no credit to double here (no
  reward on success), but the *done* state still needs to be idempotent so the participant page
  doesn't show a resubmit as a fresh, still-pending action.
- **Same universal photo requirement** — `operations.md` states a photo is required for every
  action; `doPost` already rejects a photoless `buy`/`task`/`object`, extend that check to
  `mission`.
- **Validate `item` against the `Missions` tab**, not `data/landmarks.csv`: reject (flag
  `pending`/invalid, same as an unrecognized landmark today) a `mission_id` that doesn't exist
  in `Missions`, or whose `deadline` has already passed at write time — a late submission still
  gets written (append-first), it just won't satisfy the `Standings` check below, which is the
  correct outcome, not an error.
- **No new revocation path.** A mission photo goes into the same Kontrol post-hoc review queue
  as everything else. A banker voiding it uses the exact mechanism that already exists for a
  voided purchase or task — `status` flips to `voided`, nothing mission-specific needed here.

## 3. New `Standings` formula block: the penalty

This is the one genuinely new piece of formula logic in the whole system. Every existing
`Board`/`Ledger`/`Standings` formula sums *positive* submissions a team made. This is the first
one that has to prove a team did **not** submit something, across the full team roster —
budget a verification pass for it (see "Verification," below) with the same rigor the
district-count rekey and bonus tier formulas got (`ledger-system.md`, "Verified 2026-08-19").

For each `(team, mission)` pair — every team roster row crossed with every row currently in
`Missions` — compute:

```
penalty(team, mission) =
  IF( NOW() > mission.deadline
      AND NOT EXISTS(
            row IN Journal
            WHERE row.team = team
              AND row.action = "mission"
              AND row.item = mission.mission_id
              AND row.status <> "voided"
          ),
      -mission.penalty_kd,
      0 )
```

Sum `penalty(team, mission)` over all missions issued so far and add it into `Standings`'s
final score for that team, alongside the existing `cash + face_value × multiplier` term
(`economy.md`, `## Final score`). It must **not** touch `Board` or the face-value/multiplier
calculation — this is purely additive at the `Standings` level, same non-interaction property
the Kai Tak task-rate change was careful to preserve (`economy.md`, 2026-08-19 log entry).

**Why this needs no cron/trigger:** the whole expression is `NOW()`-driven and lives in a cell,
like every other formula in the system (`ledger-system.md`: "Fails soft. A wrong number is a
cell a non-technical person can fix at 14:00"). It recalculates on every sheet recalculation,
same as everything else — no Apps Script time-based trigger needed.

**Why the retroactive-void behavior falls out for free:** the `NOT EXISTS(... status <> "voided")`
clause is checked live, not snapshotted at the deadline moment. If a banker voids a mission
submission an hour after the deadline passed, the `NOT EXISTS` condition flips back to true on
the next recalculation and the penalty reappears — no separate "reapply" logic, no trigger, no
backfill job. This is a direct consequence of `Standings` being a live formula rather than a
value written once and left alone.

## 4. New live-read endpoint for the participant page

The participant page (`web/index.html`) needs to know the *currently active* mission with a
server-authoritative clock, polled independently of the board's slower cached-CSV reads (see
`web/README.md` and the comment above `CONFIG.CSV.objek` in `index.html` for why the CSV
publish-to-web path is wrong for this — it recaches on Google's own schedule, minutes not
seconds, which would silently eat into a team's 20-minute window before the countdown box ever
appeared).

Add a `doGet` branch for `?misi=1` that returns JSON:

```json
{
  "active": true,
  "mission_id": "M3",
  "text": "Foto tim kalian di stasiun MTR mana saja!",
  "now": 1755678900000,
  "deadline": 1755679800000,
  "penalty_kd": 10
}
```

- `"active": false` (or an empty/absent payload) when no mission's window is currently open —
  the page treats this as "hide the box."
- `now` and `deadline` are **server epoch milliseconds**, not sheet-locale datetime strings —
  the page computes `deadline - (now + clientElapsedSinceFetch)` to get a clock-skew-corrected
  countdown, so these need to be real timestamps, not display strings.
- "Currently active" = the most recent `Missions` row where `NOW()` is between `issued_at` and
  `deadline`. If two missions somehow overlap, return the one with the later `issued_at` —
  this shouldn't happen given the committee broadcasts one at a time, but the endpoint should
  degrade predictably rather than error if it does.
- This is a **read**, same failure-independence principle as the rest of the system
  (`ledger-system.md`, "reads and writes are meant to fail independently") — it should not be
  blocked by or coupled to `doPost`'s write path.

## 5. Related, smaller piece: the `objek` (Objects to Find) tab

Not part of the mission mechanic itself, but decided alongside it and touching the same
participant page: the "Objects to Find" list (`rules.md` §6) is also not finalized, so it's
being made sheet-driven instead of hardcoded in `index.html`, the same reasoning as missions
being free-text rather than a fixed catalog. Two columns, header row then one row per object:

| Column | Type | Notes |
|---|---|---|
| `nama` | text | Object name shown on the page, e.g. "Bolo Bun" |
| `harga` | number | KD paid on submission. The page's *display* of this comes from a published CSV of this tab; the actual credit still comes from `doPost`'s existing `object` handling — keep those two in sync, the CSV is not the source of truth for what a team gets paid, only for what the button says |

Publish this tab the same way `aktivitas` was published (`web/README.md`: File ▸ Share ▸
Publish to web ▸ this sheet ▸ CSV), paste the URL into `CONFIG.CSV.objek` in `index.html`. No
`doPost`/`doGet` change needed for this part — `object` as an action type already exists and
already validates by name; only the *list the page shows* was hardcoded before, not the
handling.

## Verification

Before this goes live, at minimum:

1. **Hand-computed test cases for the `Standings` penalty formula**, same rigor as the
   district-count rekey and bonus tier got (`ledger-system.md`, "Verified 2026-08-19" section)
   — this is new formula surface (first absence-check in the sheet), not a tweak to existing
   logic, and deserves the same treatment, not less.
2. **Confirm the retroactive-void path** with an actual test: submit a mission photo before
   deadline (penalty absent), void it via Kontrol, confirm the penalty reappears on the next
   recalculation without any manual intervention.
3. **Confirm `?misi=1` degrades safely** when no mission is active and when `Missions` is
   empty — the participant page must never show a stale or wrong countdown.
4. **Load-check** is not really needed here — 5 missions × 25 teams is negligible next to the
   ~550 submissions/day, 0.6 submissions/sec the write layer is already tested against
   (`ledger-system.md`: "Verified 2026-08-19" throughput section).

## What's still open (do not block the build on these)

- **Penalty magnitude.** 10 KD is the current working default (`economy.md`, `## Surprise
  missions`) — sized so one miss costs about as much as the cheapest landmark on the board, and
  five misses in a day cost about a third of the starting allowance. It is stored per-row in
  `penalty_kd`, not as a board-wide constant, specifically so this doesn't need to be locked
  before the build starts, or even before the event starts — the committee can set it row by
  row live.
- **Which 2025 missions carry over.** 2025 ran five (`docs/2025/format.md:61`: any MTR station,
  street art, a bakery item, a 7-Eleven purchase + video, forming a star). None of these need
  to be pre-loaded into `Missions` — it can be populated live, day-of, or pre-filled ahead of
  time (see "New `Missions` tab", above); either way this is a committee decision, not a build
  dependency.
- **Whether missions are pre-scheduled or entered live on the day.** Both work against the
  same mechanism with no code change either way — added 2026-08-20 to confirm this explicitly,
  since it wasn't addressed in the original spec. Pre-scheduling still needs a person to paste
  the mission text into the leader chat at the scheduled minute (see "New `Missions` tab"),
  unless the committee also decides to drop the chat trigger and rely solely on the app's
  countdown box, which is a separate `rules.md` change, not implied by scheduling alone.
  **The *when* half of this is now decided** — see "Broadcast schedule" above for the five
  `issued_at` times; only mission text/`penalty_kd` content and the live-vs-pre-filled choice
  of *entry method* remain open.
- **Whether a future mission is ever location-gated.** All five 2025 missions are location-
  agnostic (doable from wherever a team already is). `economy.md` records a reachability
  finding (Kai Tak/East Kowloon to the Whampoa–Hung Hom corridor is ~15–20 min via the Ho Man
  Tin interchange, not the ~65–70 min a naive base-distance bound suggests) in case the
  committee later wants a mission that requires travel — nothing in this spec assumes that,
  and the `Missions` tab's free-text `text` field supports it without any schema change if it
  comes up.

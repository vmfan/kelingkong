# The ledger system

Why the ledger is built the way it is, and what was rejected. `operations.md` carries the
build spec; this document exists so the decision can be revisited with the reasoning intact
rather than re-argued from scratch — the same job `alternatives-considered.md` does for the
game mechanics.

Decided 2026-08-19. Supersedes the `Google Sheet + Form` row in `concept.md`.

## Relationship to `ledger-build.md`

`ledger-build.md` (2026-08-18) asked a narrower question — how raw `Transactions` rows become
the derived tabs — and treated the *input* method as closed, on the grounds that
`operations.md`, `rules-audit.md` and `rules.md` all already committed to a Google Form.

**The two documents agree on the aggregation layer and this one implements its
recommendation.** `Board`, `Ledger` and `Standings` are native formulas. Apps Script writes
only the `Transactions` journal and never the derived tabs — precisely the split
`ledger-build.md` argues for, and for its reason: an aggregator that stops running degrades
to "scores stop updating," which nobody notices until it is too late to fix.

**They disagree on the input layer, and this document supersedes it there.** That question
was reopened deliberately, on the committee's decision, after the forced-Google-sign-in
constraint came to light — a fact not available when `ledger-build.md` was written, and one
that makes the Form unworkable rather than merely imperfect. `ledger-build.md`'s Option A/B
analysis stays valid on its own terms and is preserved as the record of how the aggregation
layer was settled.

One consequence worth noting: `ledger-build.md` argues the Form's weakness is that it cannot
reject a bad submission, leaving mistyped team IDs and non-canonical landmark names sitting
in `Transactions` unjoined. Moving the input to Apps Script closes that gap as a side effect —
the same gap, fixed at the door rather than flagged after the fact.

## Why this needed deciding

2026 is a purchase economy, so a live, shared, authoritative ledger is a hard requirement,
not a convenience. Prices escalate with each buyer, balances are virtual, and `rules.md` §2
makes a promise to participants in writing — *"Harga hari ini selalu ada di papan skor"*.
There is no paper version of this game.

`concept.md` had locked the ledger as "Google Sheet + Form" without an evaluation.
`alternatives-considered.md` covers five game mechanics and zero systems options; this was
the one locked decision in the design with no recorded reasoning behind it.

The specific concern that reopened it: **a published Google Sheet tab is the operator's data
model wearing a participant's hat.** A 51-row price grid and a 25-team standings matrix on a
phone is zoom-and-pan, has no "my team" view, and exposes machinery — buyer counts, ladder
positions, formulas — that `rules-audit.md` deliberately removed from the participant rules.

## The decision: three layers, three failure domains

The original decision bundled three independent choices. Unbundling them is the whole point.

| Layer | Choice | Why |
|---|---|---|
| **Write** | Apps Script web app | Validates at write time, confirms the price paid on the spot, and needs no Google sign-in |
| **Compute** | Sheet formulas | Fails soft. A wrong number is a cell a non-technical person can fix at 14:00 |
| **Read** | Static page over published CSV tabs | Read-only and stateless, so a better tool here carries no operational risk |

Reads and writes are deliberately independent. If the write layer throws or hits a quota, the
board still renders and only purchases stop. Serving the participant page *from* Apps Script
(`HtmlService`) would be simpler to deploy and was rejected for exactly that reason: it
collapses both into a single failure, and reads are what 250 people depend on continuously.

## Why Apps Script for the write layer

1. **It removes a forced Google sign-in.** A Google Form containing a file-upload question
   requires every respondent to sign in to a Google account; there is no anonymous-upload
   setting. `operations.md` requires a photo on *every* action including `buy`, so the Form
   design walks 25 teams into a login wall at 10:45 — and into an outside-the-organisation
   wall too, if the Sheet lives in a Workspace account. This alone decided it.
2. **Write-time validation** a Form cannot do: reject an unaffordable purchase, a duplicate
   buy, a post-16:30 submission, an unknown landmark, a `game-posts.md` cooldown violation.
3. **The team learns what it paid immediately** rather than waiting for the board to refresh.
4. **Client-side photo downscale** to ~200 KB instead of a 4 MB original. Across ~550
   submissions that is ~3 GB → ~150 MB, which matters for mobile data and for the free
   15 GB Drive tier.
5. **It removes the hardest formula from the Sheet.** Price is resolved at write time and
   written into the row, so `Ledger` and `Standings` reduce to `SUMIFS` and `COUNTIFS`.

### The four risks it introduces

These are the build. Everything else is straightforward.

| Risk | Mitigation |
|---|---|
| **Ladder race** — two concurrent buys both read the same prior-buyer count and are charged the same price | `LockService` around count → append → `flush()`. The flush must be *inside* the lock or the append can sit in a write buffer while another execution counts |
| **Double-submit** — a double-tap or retry buys twice | Client-generated UUID per action; a replay returns the original result |
| **Custom code between participant and durable record** — the one real virtue of a Form | Append-first ordering: the raw row is written before any pricing or validation runs. If the code throws, the record exists and `Kontrol` surfaces it as `pending` |
| **Single point of failure, nobody on call** | A backup Google Form, built and unlisted. The page's Beli button reads one config flag |

## What was rejected

**Google Form as the write layer** (the previously locked choice). Its real virtue is being
append-only: a submission survives even when everything downstream is broken, which is
exactly what 2025 lacked when the score sheet covered 3 of 21 groups. It loses on the forced
sign-in, and on being unable to validate, price, or confirm anything at the moment of
purchase. *What survives:* the append-only property, reproduced by append-first ordering
inside `doPost` — and the Form itself, kept unlisted as the failover.

**Full custom app (Next.js + Postgres + auth).** Best possible UX and buildable in the time.
It loses on failure mode, not capability: it fails hard and centrally, at the moment both
technical people are running an event rather than watching a deploy, and it needs 25
credentials distributed, recovered and supported on the day. *What survives:* the participant
UI, extracted as a read-only page — most of the UX win at a fraction of the risk.

**Glide / AppSheet on the Sheet.** A real mobile app for near-zero code, and the closest
thing to a drop-in answer. Rejected on licensing uncertainty: both meter users and rows, the
free tiers target pilots rather than 25 concurrent teams, and discovering a paywall in the
final week is the wrong risk to carry. Worth a timeboxed spike only if the static page
disappoints.

**WhatsApp / Telegram bot.** Participants already live in WhatsApp. Rejected: Business API
onboarding does not fit the schedule, a Telegram bot needs a server nobody can babysit, and
photo handling is worse than what we already have.

**Physical KD banknotes.** Tactile, and it deletes balance tracking entirely. Rejected
because price escalation needs shared central state regardless, and there is no cashier at
any landmark — `rules-audit.md` is explicit that teams are unsupervised beyond their two
leaders. *What survives:* printing the 150 KD allowance as a prop note, if anyone wants it.

## Two things found while building it

**The `Standings` spec was wrong.** It specified district count alone and omitted the
same-side cap, and its worked verification case asserted ×1.8 for a three-district team
without checking sides. A `Standings` built from it scores every same-side team 29% high.
Corrected in `operations.md`, which now carries four verification cases.

**Inserting a row rewrites absolute references.** Seeding 18 test rows silently rewrote
`Transactions!$C$2:$C` to `$C$20:$C` across `Board`, `Ledger` and `Standings`, and every
score quietly read zero — no error, just wrong numbers. All formulas now use full-column
references, which are immune. This is the failure mode most likely to recur, because it
looks like nothing happened.

## Verified 2026-08-19

Against a seeded four-team scenario, since removed:

| Case | Expected | Got |
|---|---|---|
| 2+2+2 across two sides, plus a stray | ×1.8 on all seven landmarks | 234 |
| Same shape, all three districts on Hong Kong Island | **×1.4, capped** — `rules.md` says 168 | 168 |
| Two districts spanning Kowloon + East Kowloon | ×1.6 | 224 |
| Scoring uses face value, not price paid | 168 despite spending 146 | 168 |
| 11 buyers of one landmark | capped at 2.5× = 75; titleholder unchanged | 75, team 1 |
| Lone purchase at ladder position 3 | scores *below* the 150 allowance | 135 |

The last row is open item 19 made concrete.

Every figure above was also reproduced by `../../scripts/simulate_playtest.py`'s
`score_team`, which was written before the Sheet existed and so cannot have inherited its
bugs. Two independent implementations agreeing is the strongest evidence available without a
field run.

**Concurrency verified 2026-08-19 against the deployed endpoint.**

| Case | Result |
|---|---|
| 8 teams buy one landmark simultaneously | Positions 1-8 all distinct; prices 30/38/45/53/60/68/75/75, the last two capped. **The lock holds** |
| Same `submission_id` twice | Replay recognised, balance unchanged. No double charge |
| 12 sequential buyers of a 50 KD landmark | 50/63/75/88/100/113/125 then flat at 125; titleholder unchanged |
| Full 25-team day, 120 submissions | All 25 teams' landmarks, multiplier and score match `score_team` exactly. The same-side cap fired for 4 teams under contention |

**Throughput: ~0.6 submissions/second**, measured over 120 concurrent submissions. Per-request
latency is ~3.3 s, but most of that is Apps Script's per-invocation container overhead, which
sits *outside* the lock and parallelises; the serialised portion is ~1.7 s. Against an event
load of ~550 submissions over six hours (~1.5/min average) that is roughly 20x headroom, and a
worst-case burst of all 25 teams at once drains in ~40 s, inside the 60 s lock wait.
Two things follow: the participant page **must** show a spinner and disable the button during
the ~3 s round trip, or teams will double-tap; and the idempotency key is what makes that
double-tap harmless.

Attempts to shorten the critical section (opening the spreadsheet before the lock, merging two
writes into one, dropping a flush) each moved the mean by less than the run-to-run noise, which
is how we know the cost is container start-up rather than anything in the sheet logic. The
optimisations were kept where they were free; the append-first flush was restored.

### The participant page, verified 2026-08-19

Built and driven end-to-end against the live endpoint (`web/index.html`). Two behaviours are
worth recording because they are the design working, not just the code:

**A purchase visibly does not move the score.** Buying a 30 KD landmark took the team from
150 to… 150 — 120 cash plus 30 face value at ×1.0. `concept.md` calls this the one idea that
has to land in the briefing, and the page now demonstrates it rather than relying on 50
volunteers to explain it.

**The hint names the specific next purchase.** Holding one landmark in Sheung Wan, the page
said: *"Beli Hollywood Road Park (Sheung Wan, 20 KD) → kalian menguasai Sheung Wan, pengali
jadi ×1.4, untung sekitar +20"* — cheapest completion, correct gain. On buying the pair it
switched to the same-side warning: *"Semua distrik kalian ada di Hong Kong Island. Pengali
kalian mentok di ×1.4…"*. The cap warns exactly when it starts binding.

The page's scoring mirror uses the same rule as `Standings`, so a hint cannot contradict the
ledger. Photo upload to Drive was confirmed on real submissions.

**Gap closed in the same pass:** the write layer was not enforcing the photo requirement that
`operations.md` states for every action. It now rejects a photoless `buy`, `task` or `object`,
and exempts `post`, which stationed staff submit having witnessed the heat.

**Still untested:** append-first ordering, which needs a fault injected between the append and
the pricing. Verify by reading `doPost` and confirming `Kontrol` block 3 surfaces a row left at
`pending`.

**One deployment quirk worth knowing.** Apps Script answers a POST with a 302 to a content URL.
A client that follows it by converting POST to GET — as Python's `urllib` does, per RFC — will
intermittently land back on `/exec` and read `doGet`'s reply instead of `doPost`'s. The
submission still lands correctly; only the client's view of the result is lost. A browser's
`fetch()` follows the redirect properly and does not hit this, but any non-browser client must
allow for it. `seed_transactions.py` detects and reports it rather than scoring it as a
failure, because the first run of this test reported a phantom lock bug on exactly this
basis.

---

## Photo verification: post-hoc review, not an approval gate (2026-08-19)

Photos were stored to Drive and never looked at, and a written transaction could not be undone.
The exploit that opens is not marginal: board task income totals **450 KD**, three times the
150 KD starting allowance, so a team submitting fake photos from a café could farm the whole
board in ~25 minutes without moving — strictly better than the farm-and-leave gap already
tracked as open item 21.

**Bankers review after the fact and void what is wrong. Nothing waits on a human.**

Blocking approval was rejected, and the reason is architectural rather than a question of
staffing — it does not change now that bankers have been recruited:

- **Ladder position is assigned at write time.** If a human gates a purchase, the team cannot be
  told what it paid, or whether it can afford it, at the moment it decides. Immediate
  confirmation is the decisive reason this layer is Apps Script and not a Form.
- **A human queue has no failover.** Write-layer failure falls through to a backup Form; a
  reviewer who stops reviewing stalls purchasing for 250 people with nothing to fail over to.
- **Review does not catch the realistic mistakes.** A banker cannot detect a mistyped team
  number at all, and cannot detect a wrong landmark without recognising 51 Hong Kong locations
  from a thumbnail. The common failure is a mistake, not a cheat, and mistakes need
  *reversibility*, not inspection.
- **The better witnesses already exist.** Two leaders travel with every team. A team cannot
  stage a fake photo with its own leader present unless the leader colludes.

### Void releases the ladder slot

The alternative — a voided buy keeps its slot, so later buyers are not renumbered — was
considered and rejected. Releasing the slot means **every consumer filters `status = "ok"`
with no exceptions**, which is why this change needed no new logic in `Code.gs` at all: `price()`
already counted prior buyers, detected duplicates and computed balances exactly that way. Keeping
the slot would have required `Board` and `Code.gs` to disagree deliberately about what counts as a
buyer — reproducing the two-places-in-sync hazard that the Kai Tak task rate had just demonstrated.

The cost accepted: a displayed price can *fall* when a void lands, which `rules.md` does not
promise. It is rare and always in the participant's favour.

### One hazard found while building it

Applying the `diperiksa` checkbox as data validation across the whole of column M wrote `FALSE`
into all ~2000 rows, which pushed `getLastRow()` to the bottom of the sheet; the next transaction
appended at row 2019 instead of row 13. Results stayed correct, but the journal fragmented and the
grid grew.

Validation alone turned out to be harmless — only written values move `getLastRow()`. The deeper
problem is that **the append position must not depend on a column an operator can edit**, and a
banker mis-clicking a checkbox on an empty row 1500 would have broken appends for the rest of the
day. `doPost` now measures the append row from **column A alone** (`lastDataRow`), which only the
script ever writes. Verified by ticking a checkbox at row 1500 and confirming the next submission
still landed at row 3. Deployed **@8**.

## Surprise missions: build spec (2026-08-20, not yet implemented)

`economy.md`'s "Surprise missions" section decided the mechanic — an absence-of-proof KD
penalty at a 20-minute deadline (widened from 15 on 2026-08-20, see below), retroactive on
Kontrol void. The full build spec (new
`Missions` tab, `doPost`'s new `action = "mission"`, the `Standings` anti-join formula, the
`?misi=1` live-read endpoint, and the related `objek` tab for the participant page's Objects
to Find list) is a standalone handoff document: **`docs/2026/missions-build-spec.md`**, written
to be handed to whoever builds it without needing this file's or `economy.md`'s full context.
**Not built yet** — same status as the Kai Tak `Board` tab edit still pending from the
2026-08-19 entry in `economy.md`'s log.

The one thing worth restating here rather than only in that spec: this is **the first
anti-join formula in the sheet**. Every existing formula — `Board`, `Ledger`, `Standings`'s
district/multiplier calculation — sums *positive* submissions. This is the first one that has
to prove absence across the full team roster, and it needs the same hand-verified-test-case
pass the district-count rekey and bonus tier got before going live (the "Verified 2026-08-19"
section above) — a named, budgeted step, not something that falls out of writing the formula.

---

## Surprise missions built (2026-08-20)

Applied `docs/2026/missions-build-spec.md` to the live Sheet and `Code.gs` — the spec's own
prerequisite reading and verification list were followed as written; not repeated here.

**New tabs:** `Missions` (mission_id · text · issued_at · deadline · penalty_kd; `deadline` is
a formula, `issued_at + 15 min`, protected against accidental overwrite) and `objek` (nama ·
harga, seeded with the 7 current objects at 5 KD, matching `CONFIG.OBJECTS`' fallback in
`web/index.html` so publishing it later changes nothing observable).

### Window widened to 20 minutes (2026-08-20, not yet applied to the live Sheet)

`docs/2026/missions-build-spec.md`'s "Broadcast schedule" section changes the mission window
from 15 to 20 minutes, so that a team caught mid-heat at a game post (heats cap at 15 min,
`game-posts.md`) is guaranteed at least 5 minutes free after the heat ends no matter when the
mission fires. `economy.md` and participant-facing `rules.md` §5 are updated to say 20 minutes.
**The live Sheet's `Missions!deadline` formula (`issued_at + 15 min`, described above) is not
yet updated to `+ 20 min`** — same convention as the Kai Tak `Board`-tab edit in `economy.md`'s
2026-08-19 log: this lives outside this repo and needs a deliberate, verified pass against the
already-built Sheet, not an automatic one. Until that pass happens, the live Sheet's actual
penalty behavior is still 15 minutes, disagreeing with the docs.

**`Standings`** gained column N, `mission_penalty` — a per-row `SUMPRODUCT` over `Missions`
(bounded at 100 rows, not full-column: `Missions` grows by manual committee entry, not by the
script's own row arithmetic, so the hazard that forced full-column refs on `Transactions`
doesn't apply here, and a bounded SUMPRODUCT is both simpler and faster than one over full
columns). `M` (score) now sums `K + L + N` instead of `K + L`. The vectorized-`COUNTIFS`
technique already used for `Ledger`/`Standings`'s other cross-tab counts carries over directly.

**`Code.gs`** gained a `mission` action (validates against `Missions`, rejects unknown ids,
duplicates, and post-deadline submissions — but always append-first, so a late or invalid
attempt still leaves a photo in the banker queue) and a `?misi=1` `doGet` branch serving the
currently active mission window as epoch-millisecond timestamps, independent of the
published-CSV read path per the spec's reasoning. Deployed **@11**.

### One bug found, outside the scope of the spec

**The spreadsheet's own timezone property was not set to Hong Kong.** Every existing
date/time formula in the workbook (the 90-minute idle check, the impossible-travel flag, the
rejected-transaction log) computes a *difference* between two timestamps both read from the
same misconfigured sheet, so the offset cancelled out and nothing looked wrong. `Missions`'
`issued_at` is the first place a human types an *absolute* wall-clock time expecting it to
mean real Hong Kong time, compared against `Code.gs`'s `Date.now()` (true UTC) — and there the
offset doesn't cancel. Verified concretely: a mission entered as issued at the real current
time read back as inactive; `=NOW()` on the sheet was a full hour behind the real clock.
Fixed via `spreadsheets.batchUpdate`'s `updateSpreadsheetProperties` (`timeZone:
"Asia/Hong_Kong"`), confirmed by re-reading `NOW()` against a real clock. Every relative
calculation elsewhere in the sheet is not known to have been affected, since a shared,
consistent offset is undetectable that way — but they were never at risk in the first place,
and are now correct in absolute terms too.

**Consequence for whoever runs the day:** `issued_at` must be typed as real Hong Kong wall-
clock time, or entered as `=NOW()`. Either is now safe.

---

## Window widened to 20 minutes, schedule pre-filled (2026-08-20)

Applied `missions-build-spec.md`'s "Broadcast schedule" section to the live Sheet.

- **`Missions!D`'s formula changed from `issued_at + 15 min` to `+ 20 min`**, on all 100
  pre-filled rows. No `Code.gs` logic change — the window length was never hardcoded in the
  script; it lives entirely in the Sheet formula, which is exactly why this needed no
  redeploy for the mechanic itself. One stale doc-comment (`?misi=1`'s handler still said
  "15-minute window") was fixed and pushed for consistency — deployed **@12**.
- **The five retimed `issued_at` values are pre-filled** as `M1`–`M5` (10:59 / 13:44 / 14:29 /
  14:59 / 15:29, all 2026-09-12), per the spec's schedule table. `text` and `penalty_kd` are
  left blank for the committee, as the spec directs.
- **Verified live** at the 19-of-20-minute boundary: a test mission issued 19 minutes ago read
  as still active (`?misi=1` returned `active: true`, ~48s left) — under the prior `+15`
  formula that window would already have closed 4 minutes earlier. Confirmed the five
  pre-filled event-day rows correctly read `active: false` today, same as an empty tab.

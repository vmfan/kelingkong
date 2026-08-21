# Ledger write layer — Form + formulas, Apps Script narrowly for validation

Internal. Resolves open item #3 in `operations.md`: *"Build Sheet + Form, `Standings`
working — Hardest technical piece."* Evaluates how `Transactions` (raw Form responses)
becomes `Board` / `Ledger` / `Standings` / `Live board`, and what role, if any, Apps Script
should play.

## What's already decided, and what isn't

The participant-facing input method is not open. `operations.md`'s ledger section commits to
"a Google Form feeding a Google Sheet," `rules-audit.md` independently re-audits "Buy via
Google Form" and keeps it, and `rules.md` already tells participants to submit that way. Any
comparison that re-litigates Form-vs-something-else for the *input* is solving a closed
question.

What's open is the layer above it: how raw `Transactions` rows become the derived tabs, live,
correctly, over the 4.5-hour window, with 25 teams submitting concurrently — and who can fix
it if it breaks at 14:00, given teams are unsupervised beyond their two leaders and volunteers,
not participants, are this event's binding constraint (root `CLAUDE.md`).

## Options

### A — Form + native Sheets formulas only

`Board`, `Ledger`, and `Standings` computed with `COUNTIFS` / `SUMIFS` / `QUERY` / `VLOOKUP`
reading `Transactions` directly. No code.

The `Standings` formula that made this "the hardest technical piece" no longer exists in that
form. Since the 2026-08-17 revision (`operations.md`), it's one count (districts where a team
owns 2+ landmarks), one lookup (1.4 / 1.6 / 1.8), one multiplication against total face value —
no best-two selection, no ranking-by-gain. That's within native-formula range; the "hardest
piece" framing predates the simplification that made it easier.

**Strength:** self-healing. Any spreadsheet-literate committee member can open a formula, read
it, and patch it without knowing who wrote it or being reachable by phone. No trigger, no
script quota, no silent failure mode — a wrong formula is visible in the cell and fixable by
inspection, the same "hand-verifiable" property `rules-audit.md` demands of the rules
themselves, extended to the build.

**Weakness:** no way to *reject* or flag a bad submission automatically. A mistyped team ID or
a landmark name that doesn't match `data/landmarks.csv`'s canonical spelling just sits in
`Transactions` as a row that doesn't join correctly — visible only if someone happens to look.

### B — Form + Apps Script as the aggregation layer

An `onFormSubmit` trigger validates each submission and writes `Board` / `Ledger` /
`Standings` directly, replacing live formulas with computed values.

The committee has someone who can write and test this, so it's not ruled out by capacity —
that's the difference from the general case. It genuinely can do things formulas can't: reject
or flag a submission with a bad team ID or unrecognized landmark before it corrupts a team's
number, dedupe, alert a committee phone.

**Weakness:** it becomes a single point of failure sitting on the score-critical path. Apps
Script triggers can throw on a malformed row, hit an execution or quota limit, or simply have
a bug that only shows up under real concurrent load — and if that happens, `Board` and
`Standings` stop updating silently. Nobody may notice until standings are meant to be
finalized at 17:00, which is exactly the failure mode `operations.md` already flags for the
2025 hand-tallied sheet, just moved one layer up the stack. A script bug is also harder to
triage in the room than a wrong formula: it needs the person who wrote it, not "any
spreadsheet-literate volunteer."

### C — Other alternatives

Briefly, for completeness — none of these change the recommendation:

- **Airtable / Glide / Fillout + automations.** Comparable power to Apps Script for
  validation, but a new tool with zero committee familiarity, days before the Aug 17–23
  mechanics freeze, and it breaks the "everything lives in one Google Sheet" model `rules.md`
  and `operations.md` are already written around.
- **Custom web form + Sheets API.** Would only be worth it if Google Forms couldn't do the
  required photo upload + team/landmark dropdown — it already can. Trades a free, mobile-ready,
  offline-queuing form for one the committee has to host and maintain, for no offsetting gain.
- **Chat-bot (WhatsApp/Telegram) + backend.** Real backend engineering — a webhook server,
  hosting, uptime — for a one-day volunteer-run event. This repo's own `CLAUDE.md` scopes it
  as "a planning repo... not a software project"; this option is the one place that line would
  actually be crossed.
- **Fully manual tally.** This is 2025's documented failure, cited by name in
  `data-audit.md` item 6 as the reason the Sheet + Form is being built at all. Already closed.

## Recommendation

**Keep `Board`, `Ledger`, and `Standings` as native formulas (Option A).** The score-critical
path stays hand-verifiable by any committee member, not just whoever wrote the script — the
same standard `rules-audit.md` applies to the rules themselves, applied here to the build.

**Scope Apps Script (Option B), if used at all, to submission validation only** — checking
team ID against the team roster and landmark/object against `data/landmarks.csv`'s canonical
names, and flagging (not silently auto-correcting) a suspect row in `Transactions` for a human
to review. That's the one job formulas genuinely can't do. It should never become the writer
of `Board` / `Ledger` / `Standings` — a validator that stops running degrades to "flags stop
appearing," which someone will eventually notice and can route around by eye. An aggregator
that stops running degrades to "scores stop updating," which nobody notices until it's too
late to fix.

This also sets up the two other things still open:

- **Item #3 itself** gets cheaper to build: formulas over `Transactions`, plus an optional,
  separable validation script — not one script that has to get the whole aggregation right on
  the first try.
- **The Sheet/Form load test**, flagged as outstanding in both `playtest.md` and
  `simulated-playtest.md`, gets cheaper too. Load-testing a formula-only `Board`/`Standings` is
  pasting N synthetic rows into `Transactions` and timing recalculation. Load-testing a script
  means testing trigger throughput and quota behavior under concurrent submissions — a
  materially bigger test to run before Sep 7–11's end-to-end dry run.

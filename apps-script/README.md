# Ledger write layer

The `doPost` endpoint behind the participant page. See `docs/2026/ledger-system.md`
for why this replaced the Google Form, and `Code.gs`'s header for the three
properties it exists to guarantee.

## Live IDs

Deployed 2026-08-19 under **deploy-account-a@example.com**.

| | |
|---|---|
| Script | `<script-id>` |
| Editor | <https://script.google.com/d/<script-id>/edit> |
| Deployment | `YOUR_DEPLOYMENT_ID` (@1) |
| `/exec` | `https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec` |

**One-time authorization is required before the endpoint answers.** `clasp login` grants
clasp's scopes, not the script project's. A web app deployed `executeAs: USER_DEPLOYING`
cannot run until the deploying account has consented to the script's own scopes
(`spreadsheets`, `drive`) — until then every request gets a 403 "Akses Ditolak" HTML page,
which looks like a broken deployment rather than a missing consent.

To grant it: open the editor URL above as deploy-account-a@example.com, select `doGet` in the
function dropdown, press **Run**, and accept the consent screen (it warns the app is
unverified — *Advanced* → *Go to Kelingkong 2026 ledger*). Authorization is per-account, not
per-deployment, so it survives later `clasp push` / `clasp deploy` cycles.

## Deploy

Requires clasp v3 (`npm i -g @google/clasp`). Deploying account: **deploy-account-a@example.com**.

Two prerequisites, both one-off and both easy to forget:

1. **Enable the Apps Script API** for that account at
   <https://script.google.com/home/usersettings>. `clasp push` fails with a bare 403 if it
   is off, and the error does not say which setting is wrong.
2. **The deploying account must own or have edit access to both IDs in `Code.gs`** — the
   spreadsheet and the photo folder. The web app runs as the deployer (`USER_DEPLOYING`),
   so if those were created under a different Google account, every submission fails at
   `openById` with a permission error rather than anything descriptive.

```
clasp login                                     # interactive; sign in as deploy-account-a@example.com
clasp create-script --type webapp --title "Kelingkong 2026 ledger"
clasp push
clasp create-deployment --description "v1"
clasp open-web-app                              # confirm the /exec URL responds
```

`clasp create-script` writes `.clasp.json` with the new script ID. Copy
`.clasp.json.example` instead if you are attaching to a script that already exists.

Then run the concurrency tests, which cannot pass or fail until this is live:

```
python3 ../scripts/seed_transactions.py --url <exec-url> --all
```

## The deployment settings are load-bearing

`appsscript.json` pins:

- **`executeAs: USER_DEPLOYING`** — the script touches the Sheet and Drive with
  the deployer's authority.
- **`access: ANYONE_ANONYMOUS`** — this is the whole reason the write layer is
  not a Google Form. A Form carrying a file-upload question requires every
  respondent to sign in to a Google account, which would put 25 teams behind a
  login wall at 10:45 on event day.

Re-deploy with `clasp deploy` after any change — `clasp push` alone updates the
code but **not** the live web-app URL's served version.

## Testing the lock

The concurrency case must be tested with genuinely parallel requests. A
sequential loop passes whether or not the lock exists:

```
scripts/seed_transactions.py --url <webapp-url> --concurrent-buy "Man Mo Temple"
```

Expected: two teams buying the same landmark at once are charged 1.00x and
1.25x — never both 1.00x.

## `Transactions` column M is not the script's

Columns A–L are the write contract (`N_COLS = 12`) and `doPost` writes exactly those.
Column M (`diperiksa`) is a checkbox bankers tick when they have looked at a submission's
photo; the script never reads or writes it.

**This is why the append row is computed by `lastDataRow()` and not `getLastRow()`.**
`getLastRow()` returns the last row containing anything in *any* column, so a single stray
checkbox on an empty row 1500 would send every subsequent transaction 1400 rows below the
journal. `lastDataRow()` measures from column A, which only this script writes, so no
operator edit can move the append position. Do not "simplify" it back.

## Voiding

Operators reverse a transaction by setting `Transactions!K` to `void`. Nothing in `Code.gs`
handles this and nothing needs to: `price()` and `balanceOf()` already filter `status === 'ok'`,
so a voided buy releases its ladder slot, refunds the team, and lets that team buy the landmark
again. If you ever change those filters, re-read `docs/2026/ledger-system.md` first — the void
semantics depend on them.

## Surprise missions

`Missions` is populated live by the committee — one row per mission, `issued_at` typed as
real Hong Kong time or `=NOW()`. **Never type into column D (`deadline`)** — it's a formula,
`issued_at + 15 min`, protected in the Sheet UI against accidental overwrite. If it ever shows
a plain value instead of a computed time, re-enter `=IF($C2="","",$C2+15/1440)` and copy it
down; a blank/broken deadline is read as "always passed," which starts penalizing every team
immediately.

`price()`'s `mission` branch and `?misi=1` both read `Missions` fresh on every call — no
cache, unlike `Board`. It's a handful of rows; freshness matters more than the round trip.

**The spreadsheet's timezone must be Asia/Hong_Kong** (Spreadsheet settings, not just
`appsscript.json`'s script-level `timeZone`). It was found unset to that on 2026-08-20 while
building this feature — every other date/time formula in the sheet only ever computes a
*difference* between two of its own timestamps, so the wrong zone canceled out silently.
`Missions.issued_at` is compared against `Code.gs`'s real `Date.now()`, where it doesn't
cancel. If missions ever seem to activate an hour off from when they were entered, check this
first.

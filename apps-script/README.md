# Ledger write layer

The `doPost` endpoint behind the participant page. See `docs/2026/ledger-system.md`
for why this replaced the Google Form, and `Code.gs`'s header for the three
properties it exists to guarantee.

## Live IDs

Deployed 2026-08-19 under deploy-account-a@example.com. Briefly migrated 2026-08-22 to a personal
account to get away from a shared password anyone on the committee could use to break the
script — but the deploying account also owns every file the script creates (see "Storage is
tied to the deploying account, not the folder" below), so that moved photo-upload storage
onto a personal Google account instead. Reverted the same day back to **deploy-account-a@example.com**
with its password rotated and 2FA enabled, which fixes the original access-control problem
without moving storage anywhere.

(In passing, the 2026-08-22 migration also surfaced a real bug: a data-validation rule someone
had added to `Transactions!K` was silently rejecting every status write. That rule has been
removed — column K is the script's to write, per "Column M is not the script's" below re:
what operators vs. the script own.)

**Migrated again 2026-09-09**, this time deliberately, to `deploy-account-b@example.com` — a
dedicated account created specifically to absorb photo/video storage, not a personal Gmail,
so the reasoning above for reverting the 2026-08-22 move does not apply here. `SPREADSHEET_ID`
and `PHOTO_FOLDER_ID` were left unchanged; only the deploying identity moved, so future
`savePhoto()` uploads are now created by (and billed to) the new account while existing files
keep their original owner. Sharing on the Spreadsheet, the photo folder, and a protected
range on `Transactions` all had to be extended to the new account before writes worked — the
protected-range block was not covered by file-level sharing and is not mentioned anywhere
else in this doc, worth remembering next time. Verified via
`scripts/seed_transactions.py --with-photo` (lock, idempotency, and Drive upload all passed)
before redeploying the existing deployment ID under the new account, then re-confirmed
against the live `/exec` URL after redeploying.

**Migrated a third time 2026-09-11** (the day before the event) after access to
`deploy-account-b@example.com` was lost outright — its cached local `clasp` credential came
back `invalid_grant`, confirming it wasn't just a browser-login problem. Deployed to
`deploy-account-c@example.com` with its own new GCP project, rather than reverting to
`deploy-account-a@example.com`, on the reasoning that riding on either previously-troubled account
again wasn't worth it with one day left. **Learn from now having lost account access twice:
make sure whoever holds the deploying account credential going forward keeps it recoverable
(password manager + backup 2FA), and keep at least one other trusted account as a standing
editor on the script so a future migration doesn't again depend on account recovery.** Same
verification approach as 2026-09-09 — `--with-photo` concurrent-buy and idempotency checks
against a throwaway deployment first, then one more against the live URL after redeploying —
all passed.

| | |
|---|---|
| Script | `<script-id>` |
| Editor | <https://script.google.com/d/<script-id>/edit> |
| Deploying account | `deploy-account-c@example.com` (since 2026-09-11) |
| GCP project | `<gcp-project-number>` (owned by deploy-account-c@example.com) |
| Deployment | `<deployment-id>` (@27) |
| `/exec` | `https://script.google.com/macros/s/<deployment-id>/exec` |

**One-time authorization is required before the endpoint answers.** `clasp login` grants
clasp's scopes, not the script project's. A web app deployed `executeAs: USER_DEPLOYING`
cannot run until the deploying account has consented to the script's own scopes
(`spreadsheets`, `drive`) — until then every request gets a 403 "Akses Ditolak" HTML page,
which looks like a broken deployment rather than a missing consent.

To grant it: open the editor URL above as deploy-account-a@example.com, select `doGet` in the
function dropdown, press **Run**, and accept the consent screen (it warns the app is
unverified — *Advanced* → *Go to Kelingkong 2026 ledger*). Authorization is per-account, not
per-deployment, so it survives later `clasp push` / `clasp deploy` cycles.

**Transferring Drive/script ownership to a new account is not enough on its own.** The
consent screen's "developer" identity is tied to the script's underlying GCP project. If you
ever move the deploying account again, also relink the script to a GCP project the new account
owns: editor → Project Settings → "Google Cloud Platform (GCP) Project" → Change project →
paste a project number owned by the new account. Re-deploy and re-consent after relinking.

**Storage is tied to the deploying account, not the folder it writes into.** `Code.gs` writes
photos into `PHOTO_FOLDER_ID` via the deploying account's own Drive API calls
(`executeAs: USER_DEPLOYING`) — the *creating* identity owns the resulting file regardless of
who owns the parent folder. Owning the containing folder does not redirect storage cost. In
practice this means whichever account backs the deployment absorbs the storage of every photo
uploaded all event day — factor that in before ever moving the deploying account to someone's
personal Gmail again.

**Enabling the `drive` OAuth scope is not the same as enabling the Drive API.** Consenting to
`oauthScopes: [..., "https://www.googleapis.com/auth/drive"]` only grants the *scope* — the
**Google Drive API** service must separately be turned on for whichever GCP project backs the
script, in Cloud Console. Without it, every `savePhoto()` call throws and the catch in `doPost`
(around "Photo goes to Drive outside the lock") writes `UPLOAD_FAILED` to the sheet with no
detail — this cost real time to diagnose on 2026-08-22, only found by temporarily changing that
catch block to write `err.message` into the cell, which surfaced: `Izin ditolak saat
mengaktifkan API: drive untuk project GCP ...`. Enable it at
`https://console.cloud.google.com/apis/library/drive.googleapis.com?project=<project-number>`
for the GCP project currently linked (see "Live IDs" above) any time the script is relinked to
a different project.

## Deploy

Requires clasp v3 (`npm i -g @google/clasp`). Deploying account: **deploy-account-c@example.com**
(migrated 2026-09-11 after access to the prior deploying account, deploy-account-b@example.com,
was lost outright — see "Live IDs" above; keep the credential limited to whoever actually
needs to redeploy, not the whole committee, and make sure it's recoverable).

Two prerequisites, both one-off and both easy to forget:

1. **Enable the Apps Script API** for that account at
   <https://script.google.com/home/usersettings>. `clasp push` fails with a bare 403 if it
   is off, and the error does not say which setting is wrong.
2. **The deploying account must own or have edit access to both IDs in `Code.gs`** — the
   spreadsheet and the photo folder. The web app runs as the deployer (`USER_DEPLOYING`),
   so if those were created under a different Google account, every submission fails at
   `openById` with a permission error rather than anything descriptive.
3. **Set Script Properties before the first deploy.** `Code.gs`'s `CONFIG` reads its live
   IDs and secret out of `PropertiesService.getScriptProperties()` rather than hardcoding
   them, so the source can be public. In the Apps Script editor, go to Project Settings >
   Script Properties and add:

   | Property | Value |
   |---|---|
   | `SPREADSHEET_ID` | the ledger Spreadsheet's ID |
   | `PHOTO_FOLDER_ID` | the Drive folder ID for photo/video uploads |
   | `STAFF_KEY` | a random string (e.g. `python3 -c "import secrets; print(secrets.token_urlsafe(24))"`) — the shared secret for the 3 staff `pos.html` stations |

   Missing any of these makes the corresponding `CONFIG` value `null` at runtime rather
   than failing at deploy time, so double-check all three are set before testing.

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
python3 ../scripts/seed_transactions.py --url <exec-url> --keys-csv <team-keys.csv> --all
```

## The deployment settings are load-bearing

`appsscript.json` pins:

- **`executeAs: USER_DEPLOYING`** — the script touches the Sheet and Drive with
  the deployer's authority.
- **`access: ANYONE_ANONYMOUS`** — this is the whole reason the write layer is
  not a Google Form. A Form carrying a file-upload question requires every
  respondent to sign in to a Google account, which would put 25 teams behind a
  login wall at 11:05 on event day.

Re-deploy with `clasp deploy` after any change — `clasp push` alone updates the
code but **not** the live web-app URL's served version.

## Testing the lock

The concurrency case must be tested with genuinely parallel requests. A
sequential loop passes whether or not the lock exists:

```
scripts/seed_transactions.py --url <webapp-url> --keys-csv <team-keys.csv> --concurrent-buy "Man Mo Temple"
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

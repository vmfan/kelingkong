# Participant page

One self-contained HTML file. No build step, no framework, no login. Indonesian, because
participants read it (`CLAUDE.md`).

Open `index.html?tim=7&key=...` — both come from the URL and are remembered in
`localStorage`, so a reopened tab still knows who you are. One QR code per team map.

**`key` is required, added 2026-08-31.** Without it (or with the wrong one), every
submission is rejected server-side (`Code.gs`'s `bad_key` guard) — this stops a team from
guessing/typing another team's number and submitting as them. Generate the 25 keys with
`python3 ../scripts/generate_team_keys.py`, paste its `team,key` output into the Sheet's
`TeamKeys` tab, and use its URL list (not a bare `?tim=N`) to generate the printed QR
codes. See `docs/2026/operations.md` item 25.

## Hosting

Live at **<https://vmfan.github.io/kelingkong/index.html>** — GitHub Pages, private repo
(`vmfan/kelingkong`, GitHub Pro), served from a `gh-pages` branch containing only this
`web/` folder (Pages' folder picker only offers `/` or `/docs` on `main`, not `/web`, so a
dedicated branch is the workaround). Verified end-to-end 2026-08-21: all 6 published CSVs
and the Apps Script `?misi=1` endpoint load with no CORS errors from that origin.

**To redeploy after editing anything under `web/`:** commit on `main`, then run

```
git subtree split --prefix=web -b gh-pages-tmp
git push origin gh-pages-tmp:gh-pages --force
git branch -D gh-pages-tmp
```

from the repo root. GitHub Pages rebuilds automatically within ~1 minute of the
`gh-pages` push.

Local check: `python3 -m http.server 8765` then <http://localhost:8765/index.html?tim=7>.

## CONFIG, at the top of the `<script>` block

| Key | Why you would change it |
|---|---|
| `ENDPOINT` | The Apps Script `/exec` URL. Already set |
| `CSV` | Publish-to-web CSV URLs for `harga` / `milik` / `tim` / `klasemen` / `aktivitas` / `objek`. All six are filled in as of 2026-09-01. If one is ever blanked, that tab degrades (no completion state for `aktivitas`; `CONFIG.OBJECTS` for `objek`) rather than breaking |
| `BACKUP_FORM` | Set this and every action button redirects to the backup Form instead. The mid-event failover — one edit, no redeploy |
| `REFRESH_MS` | CSV poll interval, default 45 s |
| `FAST_POLL_MS` | Live `?data=1` poll, default 3 s. This is the primary read path while the script is healthy |
| `LIVE_TRUST_MS` | How long a live read owns the board, default 20 s. Raise it if the script is slow enough that the CSV keeps taking over |
| `PENDING_TTL_MS` | How long an unconfirmed optimistic patch may survive, default 3 min |
| `READ_TIMEOUT_MS` | Ceiling on every read, default 12 s. See "No fetch may hang" below |
| `WRITE_TIMEOUT_MS` | Ceiling on a submission, default 2 min — a 20 MB video on mobile data is legitimately slow |
| `STALE_SHOW_AFTER_MS` | Nothing has succeeded for this long → level-2 banner, default 90 s |
| `STALE_MIN_SHOW_MS` | Minimum time the banner stays up once shown, default 10 s |
| `LIVE_FAIL_STREAK` | Consecutive failed live reads before the level-1 banner, default 3 |
| `MISI_POLL_MS` | Surprise-mission poll interval, default 8 s. Always a live `?misi=1` read, never `CONFIG.CSV` — see the comment above `CSV.objek` in the script for why |
| `OBJECTS` | Fallback `[name, KD]` list used only while `CSV.objek` is blank. Not finalized — the sheet-driven `objek` tab is the intended source of truth, this is just what the page shows before that tab is published |

### Publishing a tab, if one ever needs redoing

The Sheets API cannot publish tabs, so this is manual. In `Kelingkong Ledger`:
**File ▸ Share ▸ Publish to web**, pick the sheet, choose **CSV**, publish, copy the URL, paste
it into the matching `CONFIG.CSV` key. Publishing a single sheet does **not** make the document
link-viewable, so the operator tabs stay private.

### `?data=1` does not serve `objek`

`readParticipantTabs()` in `Code.gs` returns five tabs — `harga`, `milik`, `tim`, `klasemen`,
`aktivitas`. **Not `objek`.** So `loadFast()` merges the tabs it receives into `DATA` instead of
replacing `DATA` wholesale; a wholesale assignment would wipe the objects list every 3 s and
silently drop the page back to the `CONFIG.OBJECTS` fallback. If you add a tab to
`readParticipantTabs`, add it to `LIVE_TABS` in `index.html` too, and take it out of
`CSV_ONLY_TABS`.

### The `objek` tab's shape

Two columns, header row then one row per object: `nama, harga`. `harga` is the KD value paid
on submission (defaults to 5 if blank/missing when parsed client-side, but the live value used
to actually credit a team's balance comes from `doPost`, same as every other action — the CSV
only drives what the page *displays*). Not finalized — add, remove, or reprice rows any time;
the page picks up the change on its next 45 s poll, no redeploy.

## Three things that are deliberate

**The action button is disabled for the whole round trip.** A submission takes ~3 s, most of
it Apps Script container start-up. Without the lockout teams double-tap; the idempotency key
is what makes that harmless, and this is what stops them needing it.

**Photos are downscaled to 1200 px / JPEG 0.7 on the phone.** A 4 MB original over mobile
data is the slowest part of a submission. Across ~550 submissions this is the difference
between ~3 GB and ~150 MB of Drive.

**The board never goes blank.** The last successful fetch is cached in `localStorage`; if
the network fails the page shows that with a staleness banner rather than nothing. The
printed price list is the fallback below that. The cache is written *before* the optimistic
patch is applied, so it stores what the Sheet said, not what the page was predicting.

**The live poll owns the board; the CSV poll is the fallback.** Two readers run at once — a
3 s `?data=1` read of the Sheet, and the 45 s published-CSV baseline that recaches on Google's
schedule (minutes). While a live read is younger than `LIVE_TRUST_MS` the CSV cycle takes only
the tabs the live route cannot serve (`objek`), because letting minutes-old CSV values
overwrite seconds-old live ones makes numbers visibly change and then revert. When the script
is down, `LAST_LIVE` goes stale and the CSV baseline resumes owning everything — the
degrade-not-break path in `docs/2026/ledger-system.md`.

**Optimistic patches are bounded.** A submission the fetched board has not caught up with yet
is queued in `kk.pending.v2` and reapplied on each fetch, so a purchase never appears to undo
itself. Three rules keep that from drifting: a live payload is one atomic read, so table
presence alone retires an entry; nothing survives `PENDING_TTL_MS` regardless; and the patch
itself is idempotent, so replaying it cannot invent a landmark. The storage keys are
**versioned** — bump them if the entry shape ever changes again, because a stale entry sitting
in a participant's `localStorage` is not something a redeploy would otherwise clear.

**No fetch may hang.** `fetch()` has no timeout of its own — a socket that never answers leaves
the promise pending forever. Observed live on 2026-09-02: one published-CSV tab (`milik`) hung
past 13 s while the other five answered in under a second. Because every poll sits behind a
reentrancy guard, one pending request latched that guard on and disabled the CSV path for the
rest of the session. Everything therefore goes through `fetchT()`, which adds an `AbortController`
deadline **and** rejects non-2xx responses — `fetch` resolves happily on a 404, and Publish-to-web
answers with a real HTML error page when a tab is unpublished or quota is hit, which `parseCSV`
would otherwise accept as board data and render as a garbled but authoritative-looking board.
The six CSV tabs also fail independently now: one hung tab keeps its previous value and the cycle
carries on, and only `harga` failing counts as a failed cycle.

**The staleness banner has two levels, and is keyed on time since *any* path succeeded.** Level 1
(`LIVE_FAIL_STREAK` consecutive live-read failures) means the CSV baseline is carrying the board:
the numbers are right but we no longer know how far behind Google's recache is. Level 2
(`STALE_SHOW_AFTER_MS` with nothing succeeding at all) points at the printed price list. It is
keyed on failure *count* rather than clock age deliberately — a merely-hidden tab also leaves
`LAST_LIVE` stale, and an age test would flash a warning on every phone unlock, which is the
fastest way to teach teams to ignore it. `STALE_MIN_SHOW_MS` stops it strobing at the threshold.

**The page refreshes on wake.** While a tab is hidden `loadFast` returns early by design and the
browser throttles the timers besides (measured at 24 s against a nominal 3 s interval), so a
just-unlocked phone would otherwise sit on minutes-old prices until the next tick.
`visibilitychange` and `pageshow`/`persisted` (the mobile bfcache restore) fire a live read, a
mission read, and — only if the live path is actually failing — a CSV cycle.

**The buy dialog's background price check is display-only.** It updates the title and
deliberately does **not** touch `pending.expectedCost`. That field is the price the team actually
tapped, and `Code.gs` refuses to charge anything else without an explicit second tap. Moving it
re-points the guard at the new price, so a ladder step landing in that window was charged
silently — the exact thing `expectedCost` exists to prevent.

**Districts collapse, and the collapse state is sticky.** 51 landmarks under 13 headers is an
unpleasant scroll on a phone. Districts default open only if the team already holds a landmark
there; everything else starts collapsed. A manual tap survives the 45s poll (state lives in a
module-level `Set`, not recomputed from scratch each render) — searching auto-expands whatever
matches without touching that Set, so clearing the search reverts to whatever the team had open.

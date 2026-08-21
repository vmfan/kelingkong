# Participant page

One self-contained HTML file. No build step, no framework, no login. Indonesian, because
participants read it (`CLAUDE.md`).

Open `index.html?tim=7` — the team number comes from the URL and is remembered in
`localStorage`, so a reopened tab still knows who you are. One QR code per team map.

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
| `CSV` | Publish-to-web CSV URLs for `harga` / `milik` / `tim` / `klasemen` / `aktivitas` / `objek`. The first four are filled in; `aktivitas` (task/object completion, added 2026-08-19) and `objek` (Objects to Find list, added 2026-08-20) are **still blank** — while `aktivitas` is blank the page shows no completion state; while `objek` is blank the page falls back to `CONFIG.OBJECTS`. Neither falls back to the script for the other four |
| `BACKUP_FORM` | Set this and every action button redirects to the backup Form instead. The mid-event failover — one edit, no redeploy |
| `REFRESH_MS` | Poll interval, default 45 s |
| `MISI_POLL_MS` | Surprise-mission poll interval, default 8 s. Always a live `?misi=1` read, never `CONFIG.CSV` — see the comment above `CSV.objek` in the script for why |
| `OBJECTS` | Fallback `[name, KD]` list used only while `CSV.objek` is blank. Not finalized — the sheet-driven `objek` tab is the intended source of truth, this is just what the page shows before that tab is published |

### Fill in `CSV.aktivitas` and `CSV.objek` before the event

While `CSV.aktivitas` is blank, task/object buttons never gray out — the page has no way to
know what a team has already done, so it always shows a live button, and a resubmit is just
rejected server-side as a `duplicate` with no visual warning beforehand. While `CSV.objek` is
blank, the "Objects to Find" list is whatever `CONFIG.OBJECTS` says in the code, not what the
committee most recently decided. The Sheets API cannot publish tabs, so both are manual, same
as the other four were:

In `Kelingkong Ledger`: **File ▸ Share ▸ Publish to web**, pick the `aktivitas` sheet (or the
`objek` sheet — same steps), choose **CSV**, publish, copy the URL, paste it into
`CONFIG.CSV.aktivitas` (or `CONFIG.CSV.objek`). Publishing a single sheet does **not** make the
document link-viewable, so the operator tabs stay private.

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
printed price list is the fallback below that.

**Districts collapse, and the collapse state is sticky.** 51 landmarks under 13 headers is an
unpleasant scroll on a phone. Districts default open only if the team already holds a landmark
there; everything else starts collapsed. A manual tap survives the 45s poll (state lives in a
module-level `Set`, not recomputed from scratch each render) — searching auto-expands whatever
matches without touching that Set, so clearing the search reverts to whatever the team had open.

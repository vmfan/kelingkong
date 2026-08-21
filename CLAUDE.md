# Working in this repo

This is a planning repo for the Kelingkong orientation event, not a software project.
It holds documents and data files that the organizing committee works from.

## Conventions

**Language.** Internal planning docs are English. Anything a participant reads — rules,
mission cards, briefings, signage — is Indonesian. Files that are participant-facing say
so at the top.

**`Old Kelingkong (2025)/` is a read-only archive.** Never edit the xlsx. If something in
it is wrong, record the correction in `docs/2025/data-audit.md` and fix it in `data/`.
The archive is what lets us tell "the spreadsheet said X" from "we decided Y".

**`data/*.csv` is the single source of truth for the board.** Landmark names, districts,
and prices come from there. Docs may quote those numbers, but if a doc and the CSV
disagree, the CSV wins and the doc is stale.

**Use canonical names.** The 2025 sheets spell the same place several ways
(`DeDo Bear` / `DoDo bear`, `Elements` / `Elementals`). `data/landmarks.csv` has a
`canonical_name` column and an `aliases` column. Always write the canonical name; add new
spellings to `aliases` rather than renaming.

**Don't silently fix inherited data.** Where the 2025 sheets contradict each other, the
contradiction is recorded in `docs/2025/data-audit.md` along with which way we resolved
it. Preserve that record — it explains numbers that would otherwise look arbitrary.

## Things that are easy to get wrong

- **Base prices encode travel time.** Far landmarks cost and score more precisely so teams
  will leave Hong Kong Island. Any repricing must preserve that gradient.
- **Set bonuses are the only source of score growth.** A first buyer pays face value for
  face value, so an isolated purchase is score-neutral by design. Don't "fix" this.
- **The price cap at 2.5× base is load-bearing.** Without it, late buyers of popular
  landmarks are priced out and the non-exclusive design collapses into a land grab.
- **Volunteers are the binding constraint**, not participants. Team count follows leader
  recruitment. This was true in 2025 and is still true — but **narrow it as of 2026-08-19**:
  enough people are recruited to staff a standby banker pool, so *review and operations*
  capacity is no longer scarce. It is **leader** recruitment specifically that still gates
  team count. Don't reject a design for costing volunteer time without checking which pool.

## Verifying data changes

After editing anything in `data/`, run:

```
python3 scripts/verify.py
```

It checks CSV integrity, district sizes, the distance/price gradient, that no landmark
from the 2025 archive has been dropped, and that the archive itself is unmodified.

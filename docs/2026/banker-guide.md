# Banker guide — D-Day

Internal. For the standby banker pool working photo review on event day. Answers item 22
in `operations.md`.

## What you're doing

Submissions post and score the instant a team sends them — nothing waits on you. Your job is
to look at the photo *after the fact* and catch the rare bad one, not to approve anything
before it counts. See `ledger-system.md` for why it works this way.

## What you can see and touch

The `Kelingkong Ledger` sheet now shows only two tabs during the event — everything else
(`Board`, `Ref`, `Ledger`, `Standings`, `Missions`, and the published participant tabs) is
hidden and locked to organizers, so don't go looking for them.

- **`Kontrol`** — your work queue. Fully editable.
- **`Transactions`** — you only ever touch two columns: **`K`** (type `void` to reverse a row)
  and **`M`**, `diperiksa` (tick after you've reviewed the photo). Every other column is
  locked — you shouldn't be able to edit them, and if you can, stop and flag it rather than
  typing over a formula.

**Never bulk-fill column M.** Tick individual checkboxes as you clear them. Pasting a value
into the whole column touches all ~2000 rows and leaves the tab full of false ticks.

## Working the queue

Open `Kontrol`, block 7, **`ANTRIAN VERIFIKASI`**. It lists every `ok` transaction whose
`diperiksa` box is still unticked, oldest first, with a link to the photo. The header shows
how many are backlogged.

For each row:

1. Open the photo.
2. **A good photo shows the whole team at the landmark** — recognizable people, recognizable
   location. If you can't tell it's this team at this landmark, it's not good enough to pass
   silently.
3. **Ticking `diperiksa` only means "I looked at this."** It does not undo anything. If the
   photo is fine (or borderline but plausible), tick it and move to the next row.
4. **If the photo is clearly wrong** — wrong landmark, no team visible, reused/duplicate
   photo, or obviously staged — void the row instead of ticking it.

## Voiding a bad transaction

Type `void` into `Transactions!K` for that row. This is immediate and automatic:

- Refunds the cash to the team
- Removes the landmark from their portfolio and recomputes their multiplier
- Releases the ladder slot — the next buyer takes the freed position at the lower price
- If it was the first buy on that landmark, moves the titleholder to buyer #2

**The team sees this on the live board immediately.** Tell their leader directly when you
void something — don't let them discover a missing landmark or a changed score on their own.
Earlier buyers of the same landmark keep the price they paid; voiding never retroactively
recharges anyone. A team can buy the same landmark again after a void.

## Also watch on `Kontrol`

You're mainly working block 7, but the other six blocks surface things worth a glance if
you have spare capacity: negative balances, a team silent for 90+ minutes, stuck `pending`
rows, failed photo uploads, rejected submissions with their reason, and physically
impossible travel between two consecutive submissions. None of these need action from you
beyond flagging to committee/floaters — `Kontrol` is empty when everything's fine, so
anything showing there is worth a look.

## When in doubt

If a photo is ambiguous, or you're unsure whether to void, don't guess — flag it to
committee/floaters rather than voiding on a hunch. A wrongful void is visible to the team
immediately and is confusing to explain after the fact.

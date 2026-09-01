# 2025 spreadsheet — data audit

Contradictions and errors found in `Old Kelingkong (2025)/Kelingkong 2025.xlsx` while
extracting it into `data/`. **The archive is not corrected** — this file is the record of
what was wrong and how each item was resolved for 2026.

## 1. Game post points disagree between tabs

- *Rules & Point System* (T3:V3): 10 points at Tamar, 15 at M+, 20 at Kai Tak — total 45.
- *Score Sheet* (C4:C6): Post 1 = 15, Post 2 = 20, Post 3 = 25 — total 60.

**Resolution:** the Score Sheet values are what appear to have been tallied on the day, so
they are treated as the 2025 record. Moot for 2026, which pays currency rather than
points.

## 2. Kai Tak region total is wrong

The Rules tab states `Total: 54` for the Kai Tak region (P46). The per-tier values on the
same tab sum to **70**:

| Points | Landmarks | Subtotal |
|---|---|---|
| 3 | Sneakers Street, Argyle Centre, Ladies Market | 9 |
| 4 | Kadorar et Levain, Dragon Centre, DeDo Bear, Kam Wah | 16 |
| 5 | AIRSIDE, Petite First Kai Tak | 10 |
| 6 | Kai Tak Stadium | 6 |
| 7 | Kowloon Walled City Park, Choi Hung Rainbow, Nan Lian Garden | 21 |
| 8 | Kwun Tong Promenade | 8 |
| | **14 landmarks** | **70** |

The Score Sheet tab independently confirms the same tier assignments. **`Total: 54` is an
arithmetic error.**

**Resolution:** 70 is correct. Recorded in `retrospective.md` as part of the zone
imbalance finding.

## 3. Region totals were never balanced

| Region | Landmarks | Total points |
|---|---|---|
| HK Island | 17 | 33 |
| TST | 17 | 44 (never stated on the sheet) |
| Kai Tak | 14 | 70 |

**Resolution:** not an error — the weighting compensates for travel distance. Preserved
deliberately in the 2026 base prices. See `../2026/economy.md`.

## 4. The two tabs use different region schemes

The *Rules* tab sorts landmarks into three scoring regions; the *Landmarks* tab sorts the
same landmarks into MTR districts under three zones. They disagree:

- **Mongkok and Sham Shui Po** landmarks (Sneakers Street, Ladies Market, Argyle Centre,
  Dragon Centre, DeDo Bear, Kam Wah) are Zone 1 (M+ post) on the *Landmarks* tab but
  scored under the **Kai Tak** region in *Rules*.
- **Whampoa and Kowloon Station** landmarks (Hung Hom Promenade, Aeon, Paper Stone,
  Shanxi, Elements, M+, West Kowloon Park) are scored under **TST** in *Rules* but sit in
  Zone 3 / Kowloon on the *Landmarks* tab.

**Resolution:** `data/landmarks.csv` carries **both** schemes in separate columns
(`region_rules_2025`, `zone_landmarks_2025`) so the conflict stays visible. 2026 uses
neither — it uses the finer MTR districts, rebalanced. See `../2026/economy.md`.

## 5. "Objects to Find" list differs between tabs

- *Rules* tab (W36:AD36): 7 items — Cha Chaan Teng, DimSum, Bolo Bun, Egg Waffle, Mango
  Mochi, **Dai Pai Dong, Milk Tea**.
- *Landmarks* tab (D20:H20): 5 items — the same list without the last two.

**Resolution:** the 7-item Rules version is treated as authoritative. Preserved in
`data/objects-to-find-2025.md`.

## 6. Score Sheet was only built for 3 of 21 groups

Columns exist for Group 1, Group 2 and Group 3. Groups 4–21 have no scoring columns.

**Resolution:** not recoverable. Recorded as the operational failure that motivates the
2026 Google Sheet + Form ledger.

## 7. Landmark name variants

The same place is spelled differently across tabs. Canonical forms chosen for 2026 are in
`data/landmarks.csv`; every variant below is preserved in that file's `aliases` column.

| Canonical | Variants found |
|---|---|
| DeDo Bear | `DeDo Bear`, `DoDo bear` |
| Kadorar Bakery | `Kadorar et Levain`, `Kadorar Bakery`, `Kadorar bakery` |
| Shanxi Cut Noodles | `Ming Hing Shanxi`, `Shanxi Cut Noodles` |
| Hong Kong Museum of Art | `MOA`, `Museum of Arts`, `HKMoA` |
| Elements | `Elements`, `Elementals` |
| Bruce Lee Statue | `Bruce Lee`, `Brucelee`, `Bruce lee statue` |
| AIA Ferris Wheel | `Hong Kong Observation`, `AIA Ferris Wheel + Pier`, `HK observatory wheel` |
| West Kowloon Art Park | `west Kowloon park`, `West kowloon art park` |
| Mister Softee | `Mister Softie`, `Mister Softee` |
| Kowloon Walled City Park | `Kowloon walled City Park` |
| Vission Bakery | `Vission` |

### Previously unresolved

**`Vission`** (Rules tab, C47, HK Island, 4 points) was carried with a `notes` flag because
the intended spelling was unknown — possibly "The Vision," possibly a venue name that had
since changed. **Resolved 2026-08-31**: confirmed by a committee member who was there in
2025 to be **Vission Bakery**. `data/landmarks.csv` now uses that canonical name with
`Vission` as an alias.

## 8. Landmarks brainstormed but never scored

The *Landmarks* tab lists ~12 places that never made it into the scoring tables:

Mister Softee · The Langham · Lee Tung Avenue · Southorn Playground · Mid-Level Escalator
· Kennedy Town Seaside · Forbes Street ("Hong Kong be happy" sign) · Toko Wijaya ·
Legoland Discovery Centre · Chagee · Twin Tower · AIA Ferris Wheel

**Resolution:** preserved in `data/landmark-candidates.csv`. These are free content for
filling out thin districts in 2026.

## 9. Kowloon Walled City Park is filed under Lok Fu

The *Landmarks* tab assigns the park to **Lok Fu** in both places it appears — the zone
table (C14:D14) and the MTR table (H38:H39). `data/landmarks.csv` files it under **Sung
Wong Toi**, a 14-minute walk.

Not an error in the archive. Sung Wong Toi opened on the Tuen Ma line in 2021 and is now
the nearer station; Lok Fu was the reasonable answer when the 2025 sheet was written. Both
stations sit on opposite sides of the park.

**Resolution:** 2026 uses Sung Wong Toi. The Lok Fu provenance is retained in
`data/districts.csv`, which is why the East Kowloon note names a station no 2026 landmark
uses.

## 10. Kwun Tong Promenade never had an MTR district

It is scored at 8 points on the *Rules* tab — the highest value on the board — but does
not appear anywhere on the *Landmarks* tab, so it was never assigned to a zone or an MTR
district. Every other scored landmark appears on both tabs.

This means it sat outside the finer district structure that the 2026 board is built on,
and the "East Kowloon" grouping it was placed into for 2026 was an inference, not
something the 2025 sheets recorded.

**Resolution:** dropped from the 2026 board for travel time (45 minutes from base, the
furthest point) and preserved in `data/landmark-candidates.csv`. See
`../2026/economy.md`.

# Surprise missions — 2026 content

The four missions ready to paste into the live `Missions` tab. Mechanic, schedule, and
open decisions are all documented in `docs/2026/missions-build-spec.md` — this file is
purely the content that spec left open (mission text, per-row `penalty_kd`, and whether
any mission is location-gated). Nothing here changes the mechanic.

**Not yet applied to the live Sheet.** Same convention as every other Sheet/`Code.gs`
change referenced from this repo — someone with Sheet access still needs to paste the
four rows below into the `Missions` tab before 2026-09-12.

| Mission | `issued_at` | `deadline` | `penalty_kd` | `text` |
|---|---|---|---|---|
| M1 — Bintang Kelingkong | 11:29 | 11:49 | 10 | 🚨 RAZIA PAJAK — Misi 1: Kumpulkan minimal 8 dari 10 anggota tim kalian, lalu bentuk formasi BINTANG bersama (berbaring atau berdiri, bebas!). Foto dari jarak yang menunjukkan seluruh formasi dan seluruh anggota yang ikut. Batas waktu: 11:49. |
| M2 — Sapa Orang Baru | 13:44 | 14:04 | 10 | 🚨 RAZIA PAJAK — Misi 2: Ajak SATU orang yang bukan anggota tim kalian (bisa warga lokal, turis, atau anggota tim lain) untuk berfoto bersama sambil melakukan pose bebas. Batas waktu: 14:04. |
| M3 — Aksara Kanton | 14:44 | 15:04 | 10 | 🚨 RAZIA PAJAK — Misi 3: Cari papan nama, plang jalan, atau tulisan apa pun beraksara Tionghoa (Kanton) di sekitar kalian. Foto tim kalian di depannya, tulisannya harus terlihat jelas. Batas waktu: 15:04. |
| M4 — Seni Jalanan | 15:44 | 16:04 | 10 | 🚨 RAZIA PAJAK — Misi 4: Foto tim kalian bersama karya seni jalanan (mural, grafiti, atau patung publik) yang kalian temukan. Karya harus terlihat jelas di foto bersama anggota tim. Batas waktu: 16:04. |

## Design notes

- **M1 and M4 carry over from 2025** (`docs/2025/format.md:61`: forming a star, street art)
  — both are photogenic, need no travel, and were already proven to work logistically.
- **M2 and M4 need no lookup at all**: one non-teammate in frame (M2) or street art visible
  with the team (M4) — a banker judges the photo alone, no ledger cross-reference.
- **M2 asks for only one other person**, not another Kelingkong team specifically. An
  earlier draft required identifying a second team by number, which assumed one would be
  nearby within the 20-minute window — not guaranteed. "Any one person" keeps the social
  goal (freshmen meeting people) while staying completable from anywhere.
- **M3 avoids money and travel on purpose.** Two earlier drafts were dropped: a
  district-relative anti-farming gate (would have required a banker to cross-reference each
  team's last purchase against the district in the submitted photo — real per-submission
  lookup overhead for a problem that isn't confirmed yet) and a convenience-store purchase
  task (dropped because it ties a mission to spending KD, and missions are meant to only
  ever cost KD via the flat penalty — never touch a team's cash or purchases otherwise).
  Chinese signage is everywhere in Hong Kong, so this version is completable from any street,
  costs nothing, and needs no lookup.
- **None of the four are location-gated** — `missions-build-spec.md` leaves that option
  open for a future mission, but all four here stay location-agnostic like 2025's set.
- **`penalty_kd: 10` for all four**, per the spec's working default (≈ the cheapest landmark
  on the board; four misses ≈ a quarter of the 150 KD starting allowance). Not varied
  per-mission, since none of the four differs meaningfully in effort from the 2025 baseline
  that number was sized against.

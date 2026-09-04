# Operations

## Rundown

**Confirmed against venue availability 2026-09-04** — see item 1, closed below.

| Time | What |
|---|---|
| 08:00 | Committee and post staff on site; posts set up |
| 09:45 | Participants assemble; opening and other talks before the game starts |
| 11:05 | Briefing ends, teams disperse |
| 11:30 | First heats fire |
| 11:30–12:30 | Heats run every 15 min |
| ~12:00–13:30 | Lunch, taken wherever teams happen to be — **heats paused within this window** (new for 2026; 2025's heats ran straight through lunch) |
| 13:45 | Heats resume |
| 16:30 | Last heats (run until 16:45) |
| **16:45** | **Submission deadline — Form closes** |
| 16:45–17:15 | Regroup, standings finalised |
| 17:15 | Closing and results |

Live exploration is roughly 11:05–16:45 minus lunch ≈ **4h10m** (down from the 4.5h the
pacing model was built against — a ~7% compression from the confirmed venue times, 2026-09-04).
If the schedule compresses, the 6-landmark target and the prices derived from it need
revisiting — see `economy.md`, and open item 27 below.

Base and regroup point in 2025 was BNI Admiralty; all travel times in
`../../data/landmarks.csv` are measured from there.

## Starting district assignment

Each team is given a different starting district, to stop 250 people converging on the
same landmarks in the first 20 minutes. That congestion fix creates a fairness problem
of its own if it draws from all 13 districts: mean travel time from base ranges from 7
minutes (Admiralty) to 35 (East Kowloon), so a team assigned a far district would lose
up to half an hour just reaching their first landmark — an imposed cost the
distance-compensating prices in `economy.md` assume is always a **chosen** one.

**The starting pool is restricted to the 8 nearest districts**, capped at 18.6 min mean
ETA — everything up to and including TST Waterfront:

Admiralty · Wan Chai · Causeway Bay · TST Central · Central · Mongkok · Sheung Wan ·
TST Waterfront

The five excluded — Sham Shui Po–Prince Edward, Whampoa–Hung Hom, West Kowloon, Kai Tak,
East Kowloon — stay fully on the board at full value. Teams are free to travel to any of
them; nobody is assigned the trip. See `economy.md` for why these five are priced as
deliberate expeditions rather than default choices.

**Assign by round-robin, not random draw.** Cycle the 21 teams through the 8-district
list in order, wrapping back to the start — team 1 gets Admiralty, team 2 gets Wan Chai,
… team 9 gets Admiralty again. At 21 teams this lands unevenly by one: Admiralty, Wan
Chai, Causeway Bay, TST Central and Central (the first 5 in the list) get 3 teams each,
Mongkok, Sheung Wan and TST Waterfront get 2 each — still a tight ~2–3-teams-per-district
spread. A random draw from 8 options across 21 teams does not guarantee that; nothing
stops 5 of 21 landing on the same district by chance, which would recreate the congestion problem
the assignment exists to prevent.

## People

| Role | Count | Notes |
|---|---|---|
| Participants | 210 | 21 teams of 10 (fixed 2026-09-01 — item 26) |
| Group leaders | ~42 | 2 per team, from helpers / ranting / PPI HK |
| Post staff | 9 | 3 per post, separate pool |
| Bankers (photo review) | standby pool, recruited | Work the `Kontrol` verification queue; void bad submissions |
| Committee / floaters | TBD | Ledger monitoring, surprise missions, contingency. Missions add no headcount either way: entered live, it's populating a `Missions` tab row and sending a chat message; pre-scheduled, it's pasting a pre-written message into chat at the scheduled minute (`missions-build-spec.md`) |

**Leader recruitment is the critical path.** Team count follows leader count, not
participant count. This was 2025's finding and it has not changed. If recruitment falls
short, the fallback is fewer, larger teams — which makes the "groups too crowded"
complaint worse, so it is a real cost, not a free adjustment.

### Briefing the leaders

The two leaders travelling with each team are the **only real-time feedback the design
has**. Scores land at 17:15, far too late to change how a team spent its afternoon, so
anything that needs correcting during the day has to come from them.

Five things they must know, in this order:

1. **Two landmarks per district, then move on.** Three districts held is the top
   multiplier (×1.8). A team that sweeps one district and stops is on ×1.4 — it has used a
   third of the scoring system and seen a third as much of Hong Kong.
2. **A landmark on its own scores nothing extra**, and does not make its district count.
   Teams will strand single purchases by accident and wonder why their score did not move.
   This is the one idea that has to land in the briefing.
3. **A stranded team should do on-site tasks, not buy.** A team that has spent everything
   still scores 1:1 on cash, and tasks are self-service and need no purchase. Farming tasks
   at four landmarks is worth more than any purchase it can afford (+70 against +24), and
   it is the option that keeps them moving. See the single-district endgame in `economy.md`.
4. **If the team has a pair in a district and it is before 15:00, move them on.** A third
   district is worth more than a third landmark. This is a judgement call the leader has to
   make, and nobody else is positioned to make it.
5. **A team that plans to spend the whole day in one far district (Kai Tak or East
   Kowloon) and stop is playing a legitimate but losing strategy — say so.** It's a real
   choice, not a mistake to be corrected by rule, but simulation (`simulated-playtest.md`)
   shows it can score competitively with far better strategies purely because a single-stop
   plan never runs out of time the way a multi-district one can. If a team commits to this
   early, the leader's job is to make sure they know the tradeoff, not to steer them off it.
6. **Surprise missions cost money now, they don't earn it.** Every mission broadcast in the
   leader chat starts with `🚨 RAZIA PAJAK` — 2026's mechanic switch from a bonus to a
   penalty means missing that message costs a team, so leaders should know to watch for
   the prefix and check the page's countdown box the moment they see it (`economy.md`,
   Surprise missions).

The **`Live board` tab is the other mid-day signal** — a team that can see other teams
pulling ahead at 13:00 still has time to act on it. Worth making sure it is genuinely
published and refreshing, not just built.

## The ledger

Three layers, deliberately on separate failure domains. Full evaluation and the rejected
alternatives are in `ledger-system.md`; this section is the build spec. It replaces 2025's
hand-tallied score sheet, which was only ever built out for 3 of 21 groups.

| Layer | What | Fails how |
|---|---|---|
| **Write** | Apps Script web app (`../../apps-script/Code.gs`), one `doPost` | Writes stop; reads and the board keep working; failover is a pre-built unlisted Form |
| **Compute** | Sheet formulas | Soft — a wrong number is a cell someone can fix at 14:00 |
| **Read** | Four published tabs → static participant page | Page dies; the Sheet is unaffected and still authoritative |

**Submission** — one per action: team ID · action (`buy` / `task` / `object` / `post` /
`mission`) · landmark, object or mission id · photo or video. The write layer resolves the
ladder price, checks affordability, rejects duplicates and post-deadline submissions, and
tells the team what it paid on the spot.

**Apps Script rather than a Google Form, for one decisive reason:** a Form carrying a
file-upload question forces every respondent to sign in to a Google account, with no
anonymous option. Since photo/video proof is required on every action (below), the Form
design walks 25 teams into a login wall at 11:30. See `ledger-system.md`.

**Photo or video proof is required on every action, including `buy`.** `buy` and `task` are logged as
independent submissions, so without this a team could earn task money at one landmark and
buy a different one it never visited — undercutting `event-brief.md`'s goal of getting teams
to see parts of Hong Kong they wouldn't find on their own. Requiring proof on `buy`
itself closes that gap directly, rather than adding a separate no-gain "presence" task:
it costs zero new concepts in `rules.md` and doesn't add a second Form submission per
purchase for volunteers to review — volunteers, not participants, are this event's binding
constraint (root `CLAUDE.md`).

**Sheet tabs.** Built 2026-08-19 in `Kelingkong Ledger`.

| Tab | Contents |
|---|---|
| `Transactions` | Append-only journal. 12 columns are the write layer's contract; column M (`diperiksa`) is added for bankers and is never touched by the script |
| `Board` | 51 landmarks: district, side, base price, aliases, task income, buyer count, current price, titleholder. Task income is 30% of base price board-wide, **except Kai Tak's 4 landmarks at 50%** (`economy.md` calibration log, 2026-08-19) — rounded to 5, so Kai Tak's is a flat 20 KD each. **Applied 2026-08-19** to both `Board!F5:F8` and `Code.gs` (see open item 20) |
| `Ref` | The 13 districts with their `side`, plus the multiplier table. What the same-side cap reads |
| `Ledger` | Cash per team, broken into allowance / task / object / post / spend |
| `Standings` | Face value → districts held → sides → multiplier → property value → score |
| `Kontrol` | Operator exceptions and the banker verification queue. Empty unless something needs handling |
| `TeamKeys` | team \| key. One random key per team, generated by `scripts/generate_team_keys.py` and pasted in once before the event — never edited live. `Code.gs`'s `bad_key` guard checks every submission against this, so guessing/typing another team's number isn't enough to submit as them. A team with no row here has every submission rejected (fails closed) |
| `harga` `milik` `tim` `klasemen` | Published read-only, participant-facing, Indonesian |

The participant tabs carry only derived, participant-safe columns and are exposed with
**Publish to web ▸ specific sheet ▸ CSV**, which mints a standalone URL without making the
document link-viewable. The operator/participant split is structural, not a convention.

Current price formula: `base × MIN(2.5, 1 + 0.25 × prior_buyers)`.

**Every formula uses full-column references** (`Transactions!$C:$C`, never `$C$2:$C`).
Inserting a row rewrites absolute references that point below it — this was found the hard
way while building the Sheet, when seeding 18 rows silently rewrote `$C$2:$C` to `$C$20:$C`
across `Board`, `Ledger` and `Standings` and every score quietly read zero. Full-column refs
are immune. Do not "tidy" them back.

**`Kontrol` surfaces seven conditions**, and shows nothing when all is well: negative balance ·
team with no submission in 90 minutes · `pending` rows where the script died mid-transaction ·
failed media uploads · rejected submissions with their reason · **physically impossible travel** ·
**the photo/video-verification queue**. The 90-minute check is the only mid-day signal that a team has
stalled, which the design otherwise cannot detect.

### Photo/video verification and voiding

Photos and videos are stored but were never looked at, and until 2026-08-19 a written
transaction could not be undone. Both are now addressed — **after the fact, not as an
approval gate**. A submission still posts and scores the instant it arrives; nothing waits
on a human. See `ledger-system.md` for why gating on approval is incompatible with the
price ladder.

**Block 7, `ANTRIAN VERIFIKASI`,** lists every `ok` row whose `diperiksa` checkbox
(`Transactions!M`) is unticked, oldest first, with a link to the photo or video. Bankers work
the queue and tick as they go; the header carries the backlog count. The checkbox is the
*only* column an operator writes in `Transactions`.

**Block 6, `PERPINDAHAN TIDAK MUNGKIN`,** flags a team whose two most recent landmark
submissions are further apart than the elapsed time allows, using `|eta_a − eta_b|` from
`Board!H` as a lower bound on travel time. It cannot produce a false positive, which is what
makes it safe to act on. It is deliberately *weak*: two far districts near each other — Kai Tak
and East Kowloon, one minute apart by this measure — will not trip it. It catches the obvious
cheat, not every cheat; the queue is the real coverage.

**To reverse a transaction, set `Transactions!K` to `void`.** Every formula in the workbook
filters `status = "ok"`, so a void immediately refunds the cash, removes the landmark from the
team's portfolio, recomputes the multiplier, **releases the ladder slot** (the next buyer takes
the freed position at the lower price) and, if the voided row was the first buy, moves the
titleholder to buyer #2. Teams who bought *before* the voided row keep the price they paid —
voiding never retroactively recharges anyone, so `ladder_pos` in older rows is an audit record
rather than a live index and two rows may legitimately show the same value. A team whose buy is
voided may buy that landmark again.

**Never bulk-fill column M.** Writing values into the whole column (rather than ticking
individual rows) puts data in all ~2000 rows. The append position is measured from column A
alone precisely so that a stray tick cannot move it, but a bulk fill still leaves the tab
littered with false checkboxes.

**Build and test `Standings` first.** Since the 2026-08-17 revision this is much simpler
than it was: count the districts where a team owns **2 or more** landmarks, look up the
multiplier (1.4 / 1.6 / 1.8 for 1 / 2 / 3+), **then apply the same-side cap**, and multiply
the result against the team's total face value. One count, one lookup, one cap check, one
multiplication — no best-two selection.

**Do not omit the cap.** Count the distinct `side` values (`../../data/districts.csv`:
Hong Kong Island / Kowloon / East Kowloon) among the districts the team *holds*. If that
count is less than 2, **the multiplier is ×1.4 regardless of how many districts are held**.
This is the 2026-08-17 rule in `concept.md` and `rules.md` §3; an earlier revision of this
section specified the district count alone, and a `Standings` built from it scores every
same-side team **29% high**.

Verify it by hand-computing a team that owns 2 in one district, 2 in another, 2 in a third,
and 1 stray, **with the three districts spanning at least two sides** — say Sheung Wan and
Causeway Bay (Hong Kong Island) plus TST Central (Kowloon): **3 districts, 2 sides → ×1.8**,
applied to all seven landmarks including the stray. Then run three more cases:

| Case | Expected |
|---|---|
| Remove one landmark from the third district | ×1.6 — that district is no longer held |
| Move the third district to Admiralty, so all three are Hong Kong Island | **×1.4 — capped, not ×1.8** |
| Hold two districts, one Kowloon and one East Kowloon | ×1.6 — the cap needs 2 sides, not 2 *specific* sides |

The middle case is the one the earlier spec got wrong. It is also the exact scenario the
same-side cap exists to discourage (`economy.md`, calibration log 2026-08-17), so it will
occur on the day.

## Rain plan

**September is typhoon and rainstorm season.** 2025 had no documented contingency; this is
the fourth complaint from the retro and the last one still open.

### Decision points

| Signal | Action |
|---|---|
| T8 or above, or Black rainstorm | **Event cancelled.** Announce by 07:00. |
| T3, or Red rainstorm | **Indoor board only** (below). Announce by 08:00. |
| Amber rainstorm | Proceed; brief teams on indoor substitutes |
| Rain during the day | Teams switch to indoor landmarks at their own discretion |

Decisions are made against the Hong Kong Observatory's published warnings, by a **named
person**, by the stated time. Assign that person before the day — an unassigned decision
does not get made.

### The indoor board

These landmarks are sheltered and MTR-connected, and are already on the board:

| District | Indoor landmarks |
|---|---|
| Admiralty | United Centre, Pacific Place, The Henderson |
| Causeway Bay | Times Square |
| Sham Shui Po–Prince Edward | Dragon Centre |
| TST Central | K11 Art Mall, The Peninsula |
| TST Waterfront | K11 Musea, Hong Kong Museum of Art |
| West Kowloon | Elements, M+ |
| Whampoa–Hung Hom | Aeon Supermarket, Paper Stone Bakery, Toko Wijaya |
| Mongkok | Argyle Centre |
| Kai Tak | AIRSIDE |

Note that **Admiralty is the only district that is fully indoors**, and it is also the
cheapest. In a wet-weather run the set-bonus maths shifts toward Admiralty and TST — flag
this to teams rather than pretending the board is unchanged.

Game posts in wet weather: Post 1 (Tamar Park) and Post 3 (Kai Tak Stadium) are outdoors
and need indoor substitutes identified in advance. Post 2 (M+) is already sheltered.

## Closed since the last revision

| Date | Item | Outcome |
|---|---|---|
| 2026-08-16 | **East Kowloon walkability** | Decided. Kwun Tong Promenade dropped to `landmark-candidates.csv`; district 4→3, worst ETA 45→37 min. Not fully fixable — there is no walkable cluster in the east — so East Kowloon is now explicitly the expedition district and `rules.md` warns teams about the travel cost. See `economy.md`. |
| 2026-08-16 | **Multiplier balance — analysis** | Analysis closed, *fix still open* (item 7). The earlier "balanced within 3%" finding was wrong: leftover cash is not a counterweight, and the far/near gap is a structural **+42** invariant to income. A corrected price table is pre-computed and staged in `economy.md`. |

The board is now **51 landmarks across 13 districts**. Treat it as frozen for the Aug 17–23
mechanics freeze; the only change still contemplated is the price table under item 11.

## Open items

Ordered by deadline.

| # | Item | Deadline | Notes |
|---|---|---|---|
| 1 | Confirm event timings against venue | Week 1 | **Closed 2026-09-04.** Confirmed rundown: committee 08:00, assemble 09:45, disperse 11:05, first heat 11:30, heats paused 12:30–13:45 for lunch (new — 2025's heats ran through lunch), last heat 16:30 (ends 16:45), submission deadline 16:45, closing 17:15. Live exploration drops from the assumed 4.5h to ~4h10m — see the Rundown section above and item 27 |
| 2 | Leader recruitment to ~50 | Week 1 | Critical path; gates team count |
| 3 | Build the ledger | Week 1 | **Done 2026-08-19.** Sheet (10 tabs), Apps Script write layer deployed, and the participant page (`../../web/index.html`) built and tested end-to-end against the live endpoint. Lock, idempotency and price cap all verified; a 120-submission 25-team day matched an independent recomputation exactly. **Remaining: publish the 4 CSV tabs (see `../../web/README.md`) and build the backup Form.** See `ledger-system.md` |
| 4 | Assign the rain-decision owner | Week 1 | One named person, not "the committee" |
| 5 | Design 3 post games to the 15-min / 20-person / solo-par spec | Week 2 | See `game-posts.md` |
| 6 | Write 51 on-site landmark tasks | Week 2 | Largest content job. One per row in `landmarks.csv` |
| 7 | Economy validation | Week 2 | **No field run and no design interview** — committee away for the summer. Replaced by desk analysis (done) plus a Monte Carlo simulation of the 25-team day (`scripts/simulate_playtest.py`, results in `docs/2026/simulated-playtest.md`). Dwell time and comprehension rate stay unmeasured into event day; both were swept as sensitivity parameters instead, not measured — that risk is recorded there |
| 8 | Verify the `Vission` spelling | Week 2 | Cannot go on a printed map unresolved |
| 9 | Indoor substitutes for Posts 1 and 3 | Week 3 | Part of the rain plan |
| 10 | Print maps, price lists, timetables | Week 3 | Hard dependency on 6, 7 and 11. QR codes on each team's map point to `https://vmfan.github.io/kelingkong/index.html?tim=N&key=...` — **live and verified 2026-08-21** (see `../../web/README.md` Hosting section). `key` added 2026-08-31 to stop team-spoofed submissions (item 25); `TeamKeys` populated and team count fixed at 21 (item 26). **QR images generated 2026-09-01** — `print/qr/tim-01.png`…`tim-21.png`, built by `scripts/generate_team_qr.py` from `scripts/team-keys.csv` (a checked-in snapshot of the live, deployed `TeamKeys` values — not a fresh key regeneration). Ready to place on the printed maps; still needed: the maps/price lists/timetables themselves |
| 11 | **Apply or discard the compressed price table** | Week 3 | **Applied 2026-08-18.** Simulation showed the same-side cap alone left a 90–105 point residual far/near gap under realistic 25-team price-ladder contention — wider than the 2026-08-17 desk estimate assumed. Top-only compression applied at ratio 0.45 (`scripts/apply_price_compression.py`): narrowed the simulated gap by 25–37% across every scenario tested without touching near-crossing's affordability. Full record in `economy.md`'s calibration log and `simulated-playtest.md` |
| 12–15 | ×2.2 ambiguity · restate pace · cap multiplier at 3 · cut best-2 cap | — | **CLOSED 2026-08-17.** All four are superseded by the set-bonus revision, which removes the depth tier table and the best-2 cap outright. See the calibration log in `economy.md` |
| 16 | **Print task income in KD, not as "30%"** | Week 3, with printing | **Done in `rules.md`**, which now says the figure is on the price list. Remaining work is putting the number on the printed list and map |
| 17 | **Drop +25% / 2.5× from the participant rules** | Week 1 | **Done.** `rules.md` now says prices rise once others buy and directs teams to the board. Mechanic unchanged in the Sheet |
| 18 | **Re-test `Standings` against the new multiplier** | Week 1 | **Spec corrected 2026-08-19** — it had specified district count alone and omitted the same-side cap, which scores every same-side team 29% high. "The ledger" above now carries four verification cases, including the 3-districts-one-side case the old spec got wrong. Hand-verify all four before trusting any score |
| 19 | **Watch the thin-portfolio price penalty** | Week 2 | The multiplier now varies by team, so a team holding one district (×1.4) loses money buying at ladder position 3+, where a three-district team (×1.8) still profits to position 4. Pushes narrow teams to broaden, which is intended — but it is the trailing team that pays. Bounded by the 2.5× cap |
| 20 | **Apply the Kai Tak task-income exception to the built Sheet** | Week 3, before printing | **CLOSED — applied to the live `Board` tab 2026-08-19.** Kai Tak's 4 landmarks (AIRSIDE, Petite First Kai Tak, Kai Tak Stadium, Twin Tower) now pay 50% task income instead of 30%, i.e. 20 KD flat instead of 10. Scoped to just those 4 rows; `Standings`, `Ref`, and every other landmark's task income were confirmed untouched, per item 18's hand-verification precedent |
| 21 | **Watch the farm-and-leave gap at Kai Tak** | Ongoing, from event day 1 | Simulation found that visiting Kai Tak, doing all 4 tasks, and buying nothing already outscores the taught ×1.8 near-crossing build even before item 20's boost (240 vs. 180), and the boost widens it further (→280). No mechanical fix was adopted — see `economy.md` calibration log, 2026-08-19 decision entries, and `simulated-playtest.md`'s "Farm-and-leave, quantified" section. Unlike item 19, this is not bounded by an existing cap; if it's visibly happening on the day, it needs a same-day call, not a wait-and-see |
| 22 | **Brief the bankers on the verification queue** | Week 3 | Added 2026-08-19 with photo review. They need: how to read `Kontrol` block 7, what a good photo looks like (whole team, at the landmark), that ticking `diperiksa` only marks it seen, and that voiding is done by typing `void` into `Transactions!K`. Also that a void is visible to the team immediately — so tell the team's leader, don't let them discover it on the board |
| 23 | **Publish the `objek` CSV tab and paste the URL into `web/index.html`'s `CONFIG.CSV.objek`** | Week 3 | Added 2026-08-20 with surprise missions. Seeded with 2025's 7 objects at 5 KD each; until published the page falls back to its hardcoded `CONFIG.OBJECTS` list, which already matches |
| 24 | **Apply the widened mission window and retimed broadcast schedule to the live Sheet** | Week 3, before printing | **Reopened 2026-09-04 — not yet re-closed.** Previously reopened 2026-08-31, re-closed same day against a four-mission schedule (`M1`–`M4`: 10:59 / 13:44 / 14:29 / 15:14, all 2026-09-12). Reopened again now that item 1's venue-time confirmation moved the rundown (11:05 disperse / 11:30 first heat / heats paused 12:30–13:45 / 16:30 last heat / 16:45 deadline): the schedule is re-derived to `M1`–`M4` = 11:29 / 13:44 / 14:44 / 15:44 (`missions-build-spec.md`, "Broadcast schedule"; `economy.md`, 2026-09-04 calibration log entry). Live `Missions` tab still holds the 2026-08-31 values (`M1` 10:59, `M3` 14:29) and needs `M1`, `M3` and `M4`'s `issued_at` retimed to match — `M2` (13:44) is unchanged. `Code.gs`'s `CONFIG.DEADLINE` also needs redeploying at the new `16:45` value (updated in this repo, not yet pushed live — see `apps-script/Code.gs`) |
| 25 | **Stop team-spoofed submissions** | Week 3, before printing | Added 2026-08-31, **closed 2026-09-01**. `team` was previously a self-asserted number with nothing checking it — anyone reading the endpoint URL out of the page source could POST as any team. `Code.gs` now rejects any submission whose `key` doesn't match that team's row in `TeamKeys` (see "The ledger" above), checked before `Transactions` is touched. `TeamKeys` is populated (21 rows, matching item 26) and deployed live; verified end-to-end — wrong key, missing key and cross-team key reuse all rejected before any Sheet write. QR images generated (see item 10) |
| 26 | **Finalize the team count everywhere "25" is assumed** | Before Aug 31 printing window | Added 2026-08-31, **closed 2026-09-01 — fixed at 21 teams of 10**, matching 2025's actual count rather than growing to the 25 originally targeted (`concept.md`). All three groups resolved: (1) **Mechanical:** `Code.gs`'s `CONFIG.TEAMS` set to 21 and redeployed live; `TeamKeys` trimmed to 21 rows (teams 22–25 removed); `--teams` defaults on `generate_team_keys.py`/`seed_transactions.py` updated to 21; `web/index.html`'s prompt fallback updated to "(1-21)?". Verified live: team 22 now rejected `bad_team`, team 21 still submits normally. (2) **Judgement call — re-ran the simulation, no repricing needed:** set `simulate_playtest.py`'s `TEAMS = 21` and re-ran `--compare-crossing --runs 200 --seed 42` against the same board this repo ships. The far/near gap **widened slightly, not narrowed**, at 21 vs. 25 teams (dwell20/25: 49.9→53.0; dwell35: 58.1→60.4 — a ~6–10% shift, same direction as before). Fewer teams means less price-ladder contention, which if anything makes far-crossing marginally more attainable, not less — item 11's 0.45 compression ratio is not invalidated by the count change and stays as applied. Full context in `economy.md`'s calibration log, 2026-09-01 entry. (3) **Prose:** `concept.md` and this file's People table and round-robin section updated to 21/210/~42. `economy.md`'s dated calibration-log entries (historical record of decisions made under the 25-team assumption at the time) are deliberately left as-is; only forward-looking/current-state text was updated |
| 27 | **Re-validate the pacing model against the confirmed venue times** | Before printing | Added 2026-09-04 with item 1's closure. Live exploration drops from the assumed 4.5h to ~4h10m (~7% compression) — the Rundown section's own standing warning is that a compressed schedule means "the 6-landmark target and the prices derived from it need revisiting." `simulated-playtest.md`'s Monte Carlo run was built on a 270-minute budget and is now stale; rerun `scripts/simulate_playtest.py` with the new budget before trusting its far/near-gap findings for any further pricing decision. Not attempted as part of this retime — judgement call for the committee, same as item 7 |

**Anything unresolved by 24 August should default to 2025 behaviour rather than stay
open.**

Item 11 is now **closed** — applied 2026-08-18, see above.

## Timeline

| Window | Must land |
|---|---|
| **Aug 17–23** | Mechanics freeze — **set bonus rekeyed to districts held, 2026-08-17**; `rules.md` redrafted. Sheet + Form built to the new `Standings` formula. Leader recruitment opens (~50). Rain-decision owner named |
| **Aug 24–30** | Re-derive the far/near comparison under the new multiplier, then **decide the price table (item 11 — likely discard)**. Design interview against the redrafted rules. Sheet load test. One trial run per post game. Write 51 landmark tasks. Participant signup opens. |
| **Aug 31–Sep 6** | Print maps, price lists, timetables — prices must be final before this window opens. Site recon at 3 posts. Brief the 9 post staff. Rain plan finalised. |
| **Sep 7–11** | Final headcount → team assignments and starting districts. Leader briefing. End-to-end dry run of the Sheet. |
| **Sep 12** | Event day. |

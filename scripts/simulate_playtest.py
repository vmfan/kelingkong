#!/usr/bin/env python3
"""Monte Carlo simulation standing in for the cancelled field playtest.

There is no field run this year (committee is away for the summer, see
docs/2026/simulated-playtest.md) and the design-interview fallback in playtest.md also
did not happen. This script answers the *economic* pre-registered questions in
economy.md ("What the playtest must measure") and playtest.md (Part 3) by simulating
21 teams competing over the board in data/landmarks.csv and data/districts.csv.

It does NOT answer the comprehension questions (playtest.md Stages 1-3) — those test
whether a human reads rules.md and discovers clustering/crossing unprompted, which no
simulated agent can stand in for. The "naive" archetype below is an explicit, labelled
GUESS at what low-comprehension play looks like, not a measurement of comprehension.

Read-only against data/*.csv. Writes nothing back into data/ or the archive.

Run from the repo root:
    python3 scripts/simulate_playtest.py --sanity
    python3 scripts/simulate_playtest.py --runs 200 --out /path/to/summary.json
"""

import argparse
import csv
import json
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDMARKS = ROOT / "data" / "landmarks.csv"
DISTRICTS = ROOT / "data" / "districts.csv"

ALLOWANCE = 150
BUDGET_MIN = 270  # 10:30-16:30 minus lunch, per operations.md
ESCALATION_PER_BUYER = 0.25
PRICE_CAP_MULTIPLE = 2.5
SIDES_REQUIRED = 2  # of 3 sides in data/districts.csv; economy.md "Same-side cap"
SIDES_BONUS_THRESHOLD = 3  # all 3 sides; only value that means anything with 3 sides total
SIDES_BONUS_MULTIPLIER = None  # e.g. 2.0 to enable a bonus tier layered on the 2-sides floor
TASK_INCOME_RATE = 0.3  # rules.md: "30% of that landmark's base price", the live board rate
KAI_TAK_TASK_RATE = None  # e.g. 0.6 to test a Kai Tak-only task-income boost, Board-only
TEAMS = 21
STARTING_DISTRICTS = [
    "Admiralty", "Wan Chai", "Causeway Bay", "TST Central",
    "Central", "Mongkok", "Sheung Wan", "TST Waterfront",
]
POST_ANCHOR_DISTRICTS = {"Admiralty": "Post 1", "West Kowloon": "Post 2", "Kai Tak": "Post 3"}
INTRA_HOP_MEAN = 8
INTER_HOP_FLOOR = 15
OBJECT_BONUS_MEAN, OBJECT_BONUS_CAP = 20, 35


# --------------------------------------------------------------------------- data model

@dataclass
class Landmark:
    name: str
    district: str
    base_price: int
    eta: int


@dataclass
class District:
    name: str
    side: str
    landmarks: list = field(default_factory=list)

    @property
    def mean_eta(self):
        return sum(l.eta for l in self.landmarks) / len(self.landmarks)

    def cheapest(self, n):
        return sorted(self.landmarks, key=lambda l: l.base_price)[:n]


def load_board(kai_tak_discount=1.0):
    """kai_tak_discount is an in-memory experiment only -- it never touches
    data/landmarks.csv. 1.0 = no change (the live board); e.g. 0.7 = 30% off Kai Tak's
    base_price, rounded to the nearest 5 to match the board's existing price granularity."""
    landmarks_by_name = {}
    districts = {}
    with open(DISTRICTS, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            districts[row["district_2026"]] = District(row["district_2026"], row["side"])
    with open(LANDMARKS, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            price = int(row["base_price"])
            if row["district_2026"] == "Kai Tak" and kai_tak_discount != 1.0:
                price = max(5, round(price * kai_tak_discount / 5) * 5)
            lm = Landmark(
                row["canonical_name"], row["district_2026"],
                price, int(row["eta_from_bni_min"]),
            )
            landmarks_by_name[lm.name] = lm
            districts[lm.district].landmarks.append(lm)
    return landmarks_by_name, districts


# --------------------------------------------------------------------------- archetypes

def near_crossing(districts):
    """2+2+2, cheap end, spans HK Island + Kowloon. Mirrors economy.md's worked example."""
    picks = [("Sheung Wan", 2), ("Causeway Bay", 2), ("TST Central", 2)]
    return [lm for d, n in picks for lm in districts[d].cheapest(n)]


def far_crossing(districts):
    """2+2+2 including expensive far districts, still spans 2 sides."""
    picks = [("Kai Tak", 2), ("East Kowloon", 2), ("TST Central", 2)]
    return [lm for d, n in picks for lm in districts[d].cheapest(n)]


def three_side_crossing(districts):
    """2+2+2, deliberately spans all 3 sides via Sheung Wan (HK Island) + TST Central
    (Kowloon) + Kai Tak (East Kowloon) -- tests a sides_required=3 threshold and doubles
    as a Post 3 exposure check, since Kai Tak is a POST_ANCHOR_DISTRICTS entry."""
    picks = [("Sheung Wan", 2), ("TST Central", 2), ("Kai Tak", 2)]
    return [lm for d, n in picks for lm in districts[d].cheapest(n)]


def kai_tak_task_farm(districts):
    """Visits every Kai Tak landmark to do the on-site task and collect the Post 3
    anchor-district bonus -- buys nothing. Models the purchase-decoupled farming risk
    flagged for a Kai Tak task-income boost (economy.md calibration log, 2026-08-19).
    simulate_one_run() special-cases this archetype to skip the purchase_attempt event."""
    d = districts["Kai Tak"]
    return d.cheapest(len(d.landmarks))


def same_side_cluster(districts):
    """3 districts, all Hong Kong Island - the discoverability failure mode."""
    picks = [("Sheung Wan", 2), ("Causeway Bay", 2), ("Admiralty", 2)]
    return [lm for d, n in picks for lm in districts[d].cheapest(n)]


def single_district_sweep(districts):
    """Sweep one far district and stop."""
    d = districts["East Kowloon"]
    return d.cheapest(len(d.landmarks))


def greedy_adaptive(districts, rng, start_district, budget_hint):
    """No fixed list: repeatedly buy the cheapest pair in the nearest un-held district,
    preferring a district on a new side once one district is already held."""
    order = []
    held_sides = set()
    used = {start_district}
    candidates = sorted(
        (d for d in districts.values() if d.name != start_district),
        key=lambda d: d.mean_eta,
    )
    # start district itself is a candidate too, often cheapest to open first
    candidates = [districts[start_district]] + candidates
    spent_estimate = 0
    for d in candidates:
        if spent_estimate > budget_hint or len(order) >= 10:
            break
        pair = d.cheapest(min(2, len(d.landmarks)))
        if len(pair) < 2:
            continue
        # once one district is held, mildly prefer crossing to a new side
        if held_sides and d.side in held_sides and rng.random() < 0.4:
            continue
        order.extend(pair)
        held_sides.add(d.side)
        spent_estimate += sum(l.base_price for l in pair)
    return order


def naive(districts, rng, start_district):
    """Picks landmarks by raw proximity, no deliberate pairing - a stand-in guess for a
    team the rules text failed to reach, NOT a measurement of comprehension."""
    all_lm = sorted(
        (l for d in districts.values() for l in d.landmarks),
        key=lambda l: l.eta,
    )
    rng.shuffle(all_lm[:20])  # jitter among the nearer half so it's not deterministic
    return all_lm[:8]


ARCHETYPES = [
    "near_crossing", "far_crossing", "three_side_crossing", "same_side_cluster",
    "single_district_sweep", "greedy_adaptive", "naive", "kai_tak_task_farm",
]

# Archetypes that visit landmarks purely to collect task/post income and never attempt a
# purchase -- simulate_one_run() skips the purchase_attempt event for these.
TASK_FARM_ARCHETYPES = {"kai_tak_task_farm"}

POPULATION_MIXES = {
    "optimistic": {
        "near_crossing": 0.30, "far_crossing": 0.20, "greedy_adaptive": 0.30,
        "same_side_cluster": 0.10, "single_district_sweep": 0.05, "naive": 0.05,
    },
    "base": {
        "near_crossing": 0.20, "far_crossing": 0.15, "greedy_adaptive": 0.20,
        "same_side_cluster": 0.20, "single_district_sweep": 0.10, "naive": 0.15,
    },
    "pessimistic": {
        "near_crossing": 0.10, "far_crossing": 0.05, "greedy_adaptive": 0.10,
        "same_side_cluster": 0.30, "single_district_sweep": 0.15, "naive": 0.30,
    },
}


def build_shopping_list(archetype, districts, rng, start_district):
    if archetype == "near_crossing":
        return near_crossing(districts)
    if archetype == "far_crossing":
        return far_crossing(districts)
    if archetype == "three_side_crossing":
        return three_side_crossing(districts)
    if archetype == "same_side_cluster":
        return same_side_cluster(districts)
    if archetype == "single_district_sweep":
        return single_district_sweep(districts)
    if archetype == "greedy_adaptive":
        return greedy_adaptive(districts, rng, start_district, budget_hint=260)
    if archetype == "naive":
        return naive(districts, rng, start_district)
    if archetype == "kai_tak_task_farm":
        return kai_tak_task_farm(districts)
    raise ValueError(archetype)


# --------------------------------------------------------------------------- scoring

def score_team(owned_names, landmarks_by_name, districts, cash, sides_required=SIDES_REQUIRED,
                sides_bonus_multiplier=SIDES_BONUS_MULTIPLIER,
                sides_bonus_threshold=SIDES_BONUS_THRESHOLD):
    by_district = {}
    for name in owned_names:
        lm = landmarks_by_name[name]
        by_district.setdefault(lm.district, []).append(lm)
    held = {d: lms for d, lms in by_district.items() if len(lms) >= 2}
    sides = {districts[d].side for d in held}
    n_held = len(held)
    multiplier = {0: 1.0, 1: 1.4, 2: 1.6}.get(n_held, 1.8)
    if n_held >= 1 and len(sides) < sides_required:
        multiplier = min(multiplier, 1.4)
    # Bonus tier: layered ON TOP of the existing 2-sides floor, never lowers it -- a team
    # that reaches sides_bonus_threshold sides gets bumped up, nobody else is affected.
    if sides_bonus_multiplier is not None and len(sides) >= sides_bonus_threshold:
        multiplier = max(multiplier, sides_bonus_multiplier)
    total_value = sum(lm.base_price for lms in by_district.values() for lm in lms)
    score = cash + total_value * multiplier
    return {
        "score": score, "districts_held": n_held, "sides_touched": len(sides),
        "multiplier": multiplier, "landmarks_owned": len(owned_names),
        "total_value": total_value,
    }


def sanity_check():
    """Checks the scoring engine reproduces economy.md's mechanic, not its exact figures
    (that worked example hand-picks specific landmarks, not cheapest-2-per-district)."""
    landmarks_by_name, districts = load_board()

    near = near_crossing(districts)
    spend = sum(l.base_price for l in near)
    result = score_team({l.name for l in near}, landmarks_by_name, districts, cash=0)
    assert result["districts_held"] == 3 and result["sides_touched"] == 2, result
    assert result["multiplier"] == 1.8, result
    assert result["score"] == spend * 1.8, result

    same_side = same_side_cluster(districts)
    spend2 = sum(l.base_price for l in same_side)
    result2 = score_team({l.name for l in same_side}, landmarks_by_name, districts, cash=0)
    assert result2["districts_held"] == 3 and result2["sides_touched"] == 1, result2
    assert result2["multiplier"] == 1.4, result2  # capped despite holding 3 districts
    assert result2["score"] == spend2 * 1.4, result2

    # economy.md's literal worked example, by name (prices are live from landmarks.csv,
    # so this checks the mechanic, not a specific price table)
    named = ["Man Mo Temple", "PMQ", "KJRI Hong Kong", "Victoria Park",
             "United Centre", "Pacific Place"]
    named_spend = sum(landmarks_by_name[n].base_price for n in named)
    r3 = score_team(set(named), landmarks_by_name, districts, cash=0)
    assert r3["score"] == named_spend * 1.4, r3  # all HK Island -> capped at x1.4

    named[4:6] = ["K11 Art Mall", "The Peninsula"]  # swap Admiralty for TST Central
    named_spend2 = sum(landmarks_by_name[n].base_price for n in named)
    r4 = score_team(set(named), landmarks_by_name, districts, cash=0)
    assert r4["score"] == named_spend2 * 1.8, r4  # now crosses to Kowloon -> x1.8

    print("Sanity check passed: scoring engine matches economy.md's worked example "
          f"({named_spend} KD -> {r3['score']:.0f} same-side / {named_spend2} KD -> "
          f"{r4['score']:.0f} crossing) and the district/side logic holds for the "
          "near-crossing and same-side-cluster archetypes.")


# --------------------------------------------------------------------------- simulation

def sample_dwell(rng, mode):
    low, high = max(10, mode - 7), mode + 10
    return rng.triangular(low, high, mode)


def simulate_one_run(rng, dwell_mode, mix, landmarks_by_name, districts,
                      sides_required=SIDES_REQUIRED,
                      sides_bonus_multiplier=SIDES_BONUS_MULTIPLIER,
                      kai_tak_task_rate=KAI_TAK_TASK_RATE):
    names, weights = zip(*mix.items())

    events = []  # (t, kind, team_id, payload)
    team_start = {}
    time_bound = {}
    time_used = {}
    for i in range(TEAMS):
        archetype = rng.choices(names, weights=weights, k=1)[0]
        start_district = STARTING_DISTRICTS[i % len(STARTING_DISTRICTS)]
        team_start[i] = archetype
        shopping_list = build_shopping_list(archetype, districts, rng, start_district)

        t = 0.0
        current_district = start_district
        visited_districts_this_run = set()
        # object bonus lands at a random point in the first half of the day
        events.append((rng.uniform(20, BUDGET_MIN * 0.5), "object_bonus", i,
                        min(OBJECT_BONUS_CAP, round(rng.gauss(OBJECT_BONUS_MEAN, 6)))))

        time_bound[i] = False
        for lm in shopping_list:
            if lm.district != current_district:
                if current_district in districts:
                    hop = max(INTER_HOP_FLOOR,
                              abs(lm.eta - districts[current_district].mean_eta))
                else:
                    hop = lm.eta
                current_district = lm.district
            else:
                hop = max(2, rng.gauss(INTRA_HOP_MEAN, 2))
            t += hop
            t += sample_dwell(rng, dwell_mode)
            if t > BUDGET_MIN:
                time_bound[i] = True  # the plan had more items the clock didn't allow
                break
            rate = (kai_tak_task_rate if (kai_tak_task_rate is not None
                                           and lm.district == "Kai Tak")
                    else TASK_INCOME_RATE)
            events.append((t, "task_income", i, round(lm.base_price * rate / 5) * 5))
            if archetype not in TASK_FARM_ARCHETYPES:
                events.append((t + 0.001, "purchase_attempt", i, lm))
            if lm.district in POST_ANCHOR_DISTRICTS and lm.district not in visited_districts_this_run:
                visited_districts_this_run.add(lm.district)
                win = rng.random() < 0.5
                events.append((t + 0.002, "post_income", i, 40 if win else 20))
        time_used[i] = t

    events.sort(key=lambda e: e[0])

    cash = {i: float(ALLOWANCE) for i in range(TEAMS)}
    owned = {i: set() for i in range(TEAMS)}
    money_bound = {i: False for i in range(TEAMS)}
    got_post_income = {i: False for i in range(TEAMS)}
    spend_actual = {i: 0.0 for i in range(TEAMS)}
    buyer_count = {}

    for t, kind, i, payload in events:
        if kind == "post_income":
            cash[i] += payload
            got_post_income[i] = True
        elif kind in ("task_income", "object_bonus"):
            cash[i] += payload
        elif kind == "purchase_attempt":
            lm = payload
            n = buyer_count.get(lm.name, 0)
            price = lm.base_price * min(PRICE_CAP_MULTIPLE, 1 + ESCALATION_PER_BUYER * n)
            if cash[i] >= price:
                cash[i] -= price
                spend_actual[i] += price
                buyer_count[lm.name] = n + 1
                owned[i].add(lm.name)
            else:
                money_bound[i] = True

    results = []
    for i in range(TEAMS):
        r = score_team(owned[i], landmarks_by_name, districts, cash[i],
                        sides_required=sides_required,
                        sides_bonus_multiplier=sides_bonus_multiplier)
        r["archetype"] = team_start[i]
        r["cash_left"] = cash[i]
        r["money_bound"] = money_bound[i]
        r["time_bound"] = time_bound[i]
        r["plan_completed"] = not money_bound[i] and not time_bound[i]
        r["got_post_income"] = got_post_income[i]
        r["spend_actual"] = round(spend_actual[i], 1)
        r["time_used"] = round(time_used[i], 1)
        results.append(r)
    return results


def run_scenario(dwell_mode, mix_name, n_runs, seed, landmarks_by_name, districts,
                  sides_required=SIDES_REQUIRED, sides_bonus_multiplier=SIDES_BONUS_MULTIPLIER,
                  kai_tak_task_rate=KAI_TAK_TASK_RATE):
    return run_scenario_with_mix(dwell_mode, POPULATION_MIXES[mix_name], n_runs, seed,
                                  landmarks_by_name, districts, sides_required,
                                  sides_bonus_multiplier, kai_tak_task_rate)


def run_scenario_with_mix(dwell_mode, mix, n_runs, seed, landmarks_by_name, districts,
                           sides_required=SIDES_REQUIRED,
                           sides_bonus_multiplier=SIDES_BONUS_MULTIPLIER,
                           kai_tak_task_rate=KAI_TAK_TASK_RATE):
    rng = random.Random(seed)
    all_results = []
    for _ in range(n_runs):
        all_results.extend(simulate_one_run(rng, dwell_mode, mix, landmarks_by_name,
                                             districts, sides_required,
                                             sides_bonus_multiplier, kai_tak_task_rate))
    return all_results


def summarize(results):
    by_archetype = {}
    for r in results:
        by_archetype.setdefault(r["archetype"], []).append(r)
    summary = {}
    for arch, rs in by_archetype.items():
        scores = [x["score"] for x in rs]
        landmarks = [x["landmarks_owned"] for x in rs]
        districts_held = [x["districts_held"] for x in rs]
        cash_left = [x["cash_left"] for x in rs]
        money_bound_frac = sum(1 for x in rs if x["money_bound"]) / len(rs)
        time_bound_frac = sum(1 for x in rs if x["time_bound"]) / len(rs)
        plan_completed_frac = sum(1 for x in rs if x["plan_completed"]) / len(rs)
        got_post_income_frac = sum(1 for x in rs if x["got_post_income"]) / len(rs)
        sides_touched_frac = {
            str(n): round(sum(1 for x in rs if x["sides_touched"] == n) / len(rs), 2)
            for n in range(4)
        }
        time_used = [x["time_used"] for x in rs]
        # total income earned (spent + banked, above the starting allowance) per minute
        # spent -- comparable across any archetype, farming or buying alike.
        kd_per_min = [(x["cash_left"] + x["spend_actual"] - ALLOWANCE) / x["time_used"]
                      if x["time_used"] > 0 else 0.0 for x in rs]
        summary[arch] = {
            "n": len(rs),
            "score_mean": round(statistics.mean(scores), 1),
            "score_median": round(statistics.median(scores), 1),
            "landmarks_mean": round(statistics.mean(landmarks), 2),
            "landmarks_5_to_6_frac": round(
                sum(1 for x in landmarks if 5 <= x <= 6) / len(landmarks), 2),
            "districts_held_mean": round(statistics.mean(districts_held), 2),
            "cash_left_mean": round(statistics.mean(cash_left), 1),
            "cash_left_median": round(statistics.median(cash_left), 1),
            "money_bound_frac": round(money_bound_frac, 2),
            "time_bound_frac": round(time_bound_frac, 2),
            "plan_completed_frac": round(plan_completed_frac, 2),
            "got_post_income_frac": round(got_post_income_frac, 2),
            "sides_touched_frac": sides_touched_frac,
            "time_used_mean": round(statistics.mean(time_used), 1),
            "kd_per_min_mean": round(statistics.mean(kd_per_min), 2),
        }
    return summary


def sides_gap(results, threshold):
    """Mean score gap between teams whose held districts span >= threshold sides vs
    fewer -- formalizes the 'crossed vs not-crossed' comparison used in
    simulated-playtest.md finding 5."""
    crossed = [r["score"] for r in results if r["sides_touched"] >= threshold]
    not_crossed = [r["score"] for r in results if r["sides_touched"] < threshold]
    return {
        "threshold": threshold,
        "crossed_frac": round(len(crossed) / len(results), 2),
        "crossed_mean": round(statistics.mean(crossed), 1) if crossed else None,
        "not_crossed_mean": round(statistics.mean(not_crossed), 1) if not_crossed else None,
        "gap": (round(statistics.mean(crossed) - statistics.mean(not_crossed), 1)
                if crossed and not_crossed else None),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sanity", action="store_true")
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--sides-required", type=int, default=SIDES_REQUIRED)
    ap.add_argument("--kai-tak-discount", type=float, default=1.0,
                     help="In-memory experiment only, never touches data/landmarks.csv. "
                          "1.0 = no change; e.g. 0.7 = 30%% off Kai Tak's base_price.")
    ap.add_argument("--sides-bonus", type=float, default=None,
                     help="Enable a bonus multiplier for teams spanning all 3 sides, "
                          "layered on top of the existing sides_required floor (does not "
                          "lower anyone's multiplier). E.g. 2.0")
    ap.add_argument("--kai-tak-task-rate", type=float, default=None,
                     help="Override the task-income rate (default 0.3, rules.md's '30%% of "
                          "base price') for Kai Tak landmarks only. Cash-only -- does not "
                          "touch base_price or the Standings face-value/multiplier logic. "
                          "E.g. 0.6")
    ap.add_argument("--compare-crossing", action="store_true",
                     help="Also run a standalone near_crossing vs three_side_crossing "
                          "50/50 comparison, written to <out-stem>_crossing_comparison.json")
    ap.add_argument("--farm-check", action="store_true",
                     help="Also run kai_tak_task_farm (visits Kai Tak, collects task/post "
                          "income, buys nothing) as a standalone 100%% archetype, reporting "
                          "kd_per_min_mean, to <out-stem>_farm_check.json")
    args = ap.parse_args()

    sanity_check()
    if args.sanity:
        return

    landmarks_by_name, districts = load_board(kai_tak_discount=args.kai_tak_discount)
    full = {}
    for dwell_mode in (20, 25, 35):
        for mix_name in POPULATION_MIXES:
            key = f"dwell{dwell_mode}_{mix_name}"
            results = run_scenario(dwell_mode, mix_name, args.runs, args.seed,
                                    landmarks_by_name, districts,
                                    sides_required=args.sides_required,
                                    sides_bonus_multiplier=args.sides_bonus,
                                    kai_tak_task_rate=args.kai_tak_task_rate)
            full[key] = {
                "dwell_mode": dwell_mode, "population_mix": mix_name,
                "summary": summarize(results),
                "sides_gap_2": sides_gap(results, 2),
            }
            if args.sides_required == 3:
                full[key]["sides_gap_3"] = sides_gap(results, 3)
            print(f"-- {key} --")
            for arch, s in full[key]["summary"].items():
                print(f"  {arch:22s} score={s['score_mean']:6.1f} "
                      f"landmarks={s['landmarks_mean']:.2f} "
                      f"5-6frac={s['landmarks_5_to_6_frac']:.2f} "
                      f"districts={s['districts_held_mean']:.2f} "
                      f"cash_left={s['cash_left_mean']:6.1f} "
                      f"money_bound={s['money_bound_frac']:.2f} "
                      f"time_bound={s['time_bound_frac']:.2f} "
                      f"plan_completed={s['plan_completed_frac']:.2f}")

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(full, indent=2))
        print(f"\nWrote {out_path}")

    if args.compare_crossing:
        crossing_mix = {"near_crossing": 0.5, "three_side_crossing": 0.5}
        crossing_full = {}
        for dwell_mode in (20, 25, 35):
            key = f"dwell{dwell_mode}_crossing_comparison"
            results = run_scenario_with_mix(dwell_mode, crossing_mix, args.runs, args.seed,
                                             landmarks_by_name, districts,
                                             sides_required=args.sides_required,
                                             sides_bonus_multiplier=args.sides_bonus,
                                             kai_tak_task_rate=args.kai_tak_task_rate)
            crossing_full[key] = {
                "dwell_mode": dwell_mode, "sides_required": args.sides_required,
                "sides_bonus": args.sides_bonus,
                "kai_tak_task_rate": args.kai_tak_task_rate,
                "summary": summarize(results),
            }
            print(f"-- {key} (sides_required={args.sides_required}, "
                  f"sides_bonus={args.sides_bonus}) --")
            for arch, s in crossing_full[key]["summary"].items():
                print(f"  {arch:22s} score={s['score_mean']:6.1f} "
                      f"plan_completed={s['plan_completed_frac']:.2f} "
                      f"money_bound={s['money_bound_frac']:.2f} "
                      f"time_bound={s['time_bound_frac']:.2f} "
                      f"got_post_income={s['got_post_income_frac']:.2f}")

        if args.out:
            comparison_path = Path(args.out).with_name(
                Path(args.out).stem + "_crossing_comparison.json")
            comparison_path.write_text(json.dumps(crossing_full, indent=2))
            print(f"\nWrote {comparison_path}")

    if args.farm_check:
        farm_mix = {"kai_tak_task_farm": 1.0}
        farm_full = {}
        for dwell_mode in (20, 25, 35):
            key = f"dwell{dwell_mode}_farm_check"
            results = run_scenario_with_mix(dwell_mode, farm_mix, args.runs, args.seed,
                                             landmarks_by_name, districts,
                                             sides_required=args.sides_required,
                                             sides_bonus_multiplier=args.sides_bonus,
                                             kai_tak_task_rate=args.kai_tak_task_rate)
            farm_full[key] = {
                "dwell_mode": dwell_mode, "kai_tak_task_rate": args.kai_tak_task_rate,
                "summary": summarize(results),
            }
            print(f"-- {key} (kai_tak_task_rate={args.kai_tak_task_rate}) --")
            for arch, s in farm_full[key]["summary"].items():
                print(f"  {arch:22s} cash_left={s['cash_left_mean']:6.1f} "
                      f"time_used={s['time_used_mean']:6.1f} "
                      f"kd_per_min={s['kd_per_min_mean']:.2f} "
                      f"got_post_income={s['got_post_income_frac']:.2f}")

        if args.out:
            farm_path = Path(args.out).with_name(Path(args.out).stem + "_farm_check.json")
            farm_path.write_text(json.dumps(farm_full, indent=2))
            print(f"\nWrote {farm_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Drive the deployed ledger endpoint hard enough to find the bugs that only appear on the day.

This is the load test `playtest.md` (item 3) and `simulated-playtest.md` both call for and
neither could run, because until 2026-08-19 there was no ledger to test against.

It answers correctness questions about the *implementation*, not the economy. The economy
was covered by `simulate_playtest.py`, whose board loader and scoring engine this reuses —
deliberately, so the expected standings are computed by code that was written before the
Sheet existed and cannot inherit its bugs.

    python3 scripts/seed_transactions.py --url <webapp-url> --keys-csv <team-keys.csv> --all

`--keys-csv` is required once `TeamKeys` exists in the Sheet (added 2026-08-31 to stop
team-spoofed submissions, operations.md item 25) -- every submission is otherwise rejected
as `bad_key` before it ever reaches these checks. Point it at
`scripts/generate_team_keys.py`'s stdout redirected to a file; it skips that file's
comment lines and stops parsing at its URL block automatically.

The four checks, in order of how badly they fail in production:

  --concurrent-buy  Two teams buy the same landmark at the same instant. Both must not be
                    charged the same price. THIS IS THE ONE THAT MATTERS: it passes
                    trivially if you test sequentially, and a missing LockService lock
                    produces no error at all — just quietly wrong prices all day.
  --idempotency     The same submission_id twice (double-tap, network retry). One charge.
  --cap             12 buyers of one landmark. Price stops at 2.5x, titleholder unchanged.
  --load            A full simulated 21-team day, then compare the Sheet's standings against
                    a local recomputation of the same transaction log.

Does NOT cover: append-first ordering (needs a fault injected between the append and the
pricing — verify by reading `doPost`, and by confirming Kontrol block 3 surfaces a row whose
status is left at `pending`), and the 16:29/16:31 deadline pair, which needs the server clock
rather than ours.

Nothing here writes to data/ or the archive.
"""

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate_playtest import (  # noqa: E402
    ALLOWANCE, ESCALATION_PER_BUYER, PRICE_CAP_MULTIPLE,
    load_board, score_team,
)

# A 1x1 transparent GIF. Enough to exercise the Drive write path without turning the
# load test into a bandwidth test.
TINY_PHOTO = ("data:image/gif;base64,"
              "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


def post(url, payload, timeout=60):
    """One submission. text/plain deliberately: it is what the browser sends, because an
    application/json POST triggers a CORS preflight that Apps Script does not answer."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        # Apps Script answers a POST with a 302 to a content URL. urllib follows it by
        # converting POST -> GET (per RFC), and intermittently lands back on /exec, so we
        # read doGet's reply instead of doPost's. The submission itself went through fine —
        # only our view of the result is lost. A browser's fetch() follows the redirect
        # correctly and does not hit this. Flag it rather than scoring it as a failure:
        # reporting a phantom lock bug is worse than reporting an unreadable response.
        if "service" in parsed:
            return {"ok": None, "error": "response_lost_to_redirect"}
        return parsed
    except urllib.error.HTTPError as err:
        return {"ok": False, "error": "http", "status": err.code,
                "message": err.read().decode("utf-8", "replace")[:200]}
    except Exception as err:                                   # noqa: BLE001
        return {"ok": False, "error": "transport", "message": str(err)}


TEAM_KEYS = {}  # populated from --keys-csv; empty means every submission fails bad_key


def action(team, act, item, photo=False, **extra):
    p = {"submissionId": str(uuid.uuid4()), "team": team, "key": TEAM_KEYS.get(team, ""),
         "action": act, "item": item}
    if photo:
        p["photo"] = TINY_PHOTO
    p.update(extra)
    return p


def ladder_price(base, prior_buyers):
    return round(base * min(PRICE_CAP_MULTIPLE, 1 + ESCALATION_PER_BUYER * prior_buyers))


# --------------------------------------------------------------------------- checks

def check_concurrent_buy(url, landmark, n, photo):
    """N teams buy one landmark simultaneously. Ladder positions must be a permutation of
    1..N. If the lock is missing, positions collide and prices repeat."""
    print(f"\n=== concurrent buy: {n} teams, '{landmark}', fired together ===")
    payloads = [action(t, "buy", landmark, photo) for t in range(1, n + 1)]
    with ThreadPoolExecutor(max_workers=n) as pool:
        results = list(pool.map(lambda p: post(url, p), payloads))

    positions, prices = [], []
    for team, r in enumerate(results, start=1):
        pos, cost = r.get("ladderPos"), r.get("cost")
        positions.append(pos)
        prices.append(cost)
        print(f"  team {team:>2}  ok={str(r.get('ok')):<5} pos={pos}  cost={cost}  "
              f"{r.get('message') or r.get('error') or ''}")

    lost = sum(1 for r in results if r.get("error") == "response_lost_to_redirect")
    # Only SUCCESSFUL buys consume a ladder slot. A rejected buy (insufficient funds)
    # reports the position it would have taken, so several rejects legitimately share a
    # number - counting those as a collision is how this check cried wolf the first time.
    won = sorted(r["ladderPos"] for r in results
                 if r.get("ok") and r.get("ladderPos") is not None)
    rejected = sum(1 for r in results if r.get("ok") is False)
    distinct = len(won) == len(set(won))
    contiguous = won == list(range(1, len(won) + 1)) if not lost else distinct
    passed = distinct and contiguous and bool(won)
    if rejected:
        print(f"  {rejected} rejected (no ladder slot consumed); "
              f"{len(won)} successful buys hold positions {won}")

    print(f"  positions={sorted(positions, key=lambda x: (x is None, x))}  prices={prices}")
    if lost:
        print(f"  {lost} response(s) lost to the POST->GET redirect; those submissions still")
        print(f"  landed. Confirm the full ladder in Board!I (buyers) for '{landmark}'.")
    verdict(passed, "ladder positions distinct - no two teams charged the same price",
            "COLLISION - two teams got the same position: the lock is missing or "
            "not held across the append")
    return passed


def check_idempotency(url, landmark, photo):
    """The same submission_id twice. The replay must not charge again."""
    print("\n=== idempotency: one submission_id, sent twice ===")
    p = action(21, "buy", landmark, photo)  # last real team -- also exercises the TEAMS boundary
    first = post(url, p)
    second = post(url, dict(p))
    print(f"  first : ok={first.get('ok')} cost={first.get('cost')} bal={first.get('balance')}")
    print(f"  replay: ok={second.get('ok')} replay={second.get('replay')} "
          f"bal={second.get('balance')}")
    passed = bool(second.get("replay")) and first.get("balance") == second.get("balance")
    verdict(passed, "replay recognised, balance unchanged",
            "DOUBLE CHARGE - the submission_id lookup is not finding the earlier row")
    return passed


def check_cap(url, landmark, base, photo):
    """Sequential buyers past the cap. Price stops at 2.5x; titleholder never changes."""
    n = 12
    print(f"\n=== price cap: {n} sequential buyers of '{landmark}' (base {base}) ===")
    costs, first_holder = [], None
    for team in range(1, n + 1):
        r = post(url, action(team, "buy", landmark, photo))
        costs.append(r.get("cost"))
        if r.get("titleholder"):
            first_holder = team
    capped = round(base * PRICE_CAP_MULTIPLE)
    tail = [c for c in costs[7:] if c is not None]
    print(f"  costs={costs}")
    print(f"  cap should be {capped}; tail={tail}; titleholder claimed by team {first_holder}")
    passed = bool(tail) and all(c == capped for c in tail) and first_holder == 1
    verdict(passed, f"price stops at {capped}, titleholder stays team 1",
            "cap not binding, or titleholder reassigned")
    return passed


def check_load(url, teams, photo, landmarks_by_name, districts):
    """A full day's traffic, then compare the Sheet against a local recomputation.

    The expected figures come from simulate_playtest.score_team, which predates the Sheet.
    If the two disagree, at least one is wrong and neither gets the benefit of the doubt.
    """
    print(f"\n=== load: simulated day, {teams} teams ===")
    plan = _shopping_plan(teams, districts)
    sent, started = [], time.time()

    with ThreadPoolExecutor(max_workers=8) as pool:
        for team, names in plan.items():
            for name in names:
                sent.append((team, name, pool.submit(
                    post, url, action(team, "buy", name, photo))))

    owned, spent = {}, {}
    for team, name, fut in sent:
        r = fut.result()
        if r.get("ok"):
            owned.setdefault(team, []).append(name)
            spent[team] = spent.get(team, 0) + (r.get("cost") or 0)

    elapsed = time.time() - started
    print(f"  {len(sent)} submissions in {elapsed:.1f}s "
          f"({len(sent) / max(elapsed, 0.01):.1f}/s)")

    print(f"\n  {'team':>4} {'owned':>6} {'spent':>6} {'cash':>6} {'mult':>5} {'score':>7}")
    expected = {}
    for team in sorted(owned):
        cash = ALLOWANCE - spent.get(team, 0)
        s = score_team(owned[team], landmarks_by_name, districts, cash)
        expected[team] = s
        print(f"  {team:>4} {len(owned[team]):>6} {spent.get(team, 0):>6} "
              f"{cash:>6} {s['multiplier']:>5} {s['score']:>7.0f}")

    print("\n  Compare these against the Sheet's `Standings` / `tim` tab. Any mismatch is a")
    print("  Sheet formula bug: these numbers were computed by simulate_playtest.py.")
    return expected


def _shopping_plan(teams, districts):
    """Spread teams across the archetypes so the ladder actually contends. A plan where
    every team buys different landmarks would never exercise the price escalation."""
    picks = {
        "near": [("Sheung Wan", 2), ("Causeway Bay", 2), ("TST Central", 2)],
        "same_side": [("Sheung Wan", 2), ("Causeway Bay", 2), ("Admiralty", 2)],
        "far": [("Kai Tak", 2), ("TST Central", 2)],
        "sweep": [("Mongkok", 3)],
    }
    order = ["near", "same_side", "far", "sweep"]
    plan = {}
    for team in range(1, teams + 1):
        shape = picks[order[(team - 1) % len(order)]]
        plan[team] = [lm.name for d, n in shape for lm in districts[d].cheapest(n)]
    return plan


def verdict(passed, good, bad):
    print(f"  {'PASS' if passed else 'FAIL'}: {good if passed else bad}")


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="deployed Apps Script web app /exec URL")
    ap.add_argument("--keys-csv", help="team,key CSV (scripts/generate_team_keys.py's first "
                    "output block) -- required against a live TeamKeys tab, since every "
                    "submission is otherwise rejected as bad_key")
    ap.add_argument("--all", action="store_true", help="run every check")
    ap.add_argument("--concurrent-buy", metavar="LANDMARK")
    ap.add_argument("--idempotency", action="store_true")
    ap.add_argument("--cap", metavar="LANDMARK")
    ap.add_argument("--load", action="store_true")
    ap.add_argument("--n", type=int, default=4, help="parallel buyers (default 4)")
    ap.add_argument("--teams", type=int, default=21)
    ap.add_argument("--with-photo", action="store_true",
                    help="attach a 1x1 GIF so the Drive write path is exercised too")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan without posting anything")
    args = ap.parse_args()

    if args.keys_csv:
        # Tolerates generate_team_keys.py's raw stdout piped straight to a file: skips its
        # leading "# Paste into..." comment and stops at the blank line before the URL block.
        with open(args.keys_csv) as f:
            lines = [l for l in f if l.strip() and not l.startswith("#")]
        for row in csv.DictReader(lines):
            if row.get("team", "").strip().isdigit():
                TEAM_KEYS[int(row["team"])] = row["key"].strip()

    landmarks_by_name, districts = load_board()

    if args.dry_run:
        plan = _shopping_plan(args.teams, districts)
        total = sum(len(v) for v in plan.values())
        print(f"{total} buy submissions across {len(plan)} teams")
        for team in list(plan)[:4]:
            print(f"  team {team}: {', '.join(plan[team])}")
        print("  ...")
        return 0

    if not args.url:
        ap.error("--url is required unless --dry-run")

    default_lm = "Man Mo Temple"
    results = []
    if args.all or args.concurrent_buy:
        results.append(check_concurrent_buy(
            args.url, args.concurrent_buy or default_lm, args.n, args.with_photo))
    if args.all or args.idempotency:
        results.append(check_idempotency(args.url, "Tsim Chai Kee", args.with_photo))
    if args.all or args.cap:
        name = args.cap or default_lm
        results.append(check_cap(
            args.url, name, landmarks_by_name[name].base_price, args.with_photo))
    if args.all or args.load:
        check_load(args.url, args.teams, args.with_photo, landmarks_by_name, districts)

    if not results and not (args.all or args.load):
        ap.error("nothing to do - pass --all or one of the checks")

    print("\n" + "=" * 60)
    if results:
        print(f"{sum(results)}/{len(results)} checks passed")
    print("Clear the Transactions tab before the event. These are test rows.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

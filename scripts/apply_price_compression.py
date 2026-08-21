#!/usr/bin/env python3
"""Apply the price-table compression to data/landmarks.csv, softening the expensive end
of the board without touching the cheap end.

APPLIED 2026-08-18 at the defaults below (ratio=0.45, threshold=30). See
docs/2026/economy.md's calibration log for the full decision record. Three ratios were
tried:

- 0.75 across the WHOLE range (economy.md's original staged proposal) — reverted after
  simulation showed it raised every 10-KD landmark to 20 KD (a 100% increase) with the
  allowance untouched, collapsing near-crossing's plan-completion rate from 85-98% to
  15-27% while leaving far-crossing's own cost roughly flat. The score gap widened, not
  narrowed.
- 0.6, top-only (p' = p for p<=30, else 30+0.6*(p-30)) — worked, but produces byte-identical
  far/near/sweep simulation results to 0.45, since neither archetype touches the specific
  landmarks the two ratios disagree on.
- 0.35, top-only — narrowed the sweep-vs-far residual further than 0.45, but collapsed
  East Kowloon and Kai Tak's most expensive landmarks to the same price, erasing a
  distinction the board intentionally preserves (see "East Kowloon is still not walkable"
  in economy.md). Rejected on that basis.

**0.45 was chosen**: identical simulated outcome to 0.6 for the metrics that matter, while
preserving more of the board's price gradient. See docs/2026/simulated-playtest.md for the
full simulation results this decision rests on.

Transform:

    p' = p                          for p <= 30
    p' = 30 + 0.45 * (p - 30)       for p > 30   (rounded half-up to the nearest 10)

which maps 40->30, 50->40, 60->40, 70->50.

Adds `base_price_precompression` (the prior 2025-points*10 value) so the derivation in
`points_2025` stays traceable, then overwrites `base_price` with the compressed value —
`base_price` remains the single source of truth the board reads from.

Run once from the repo root:  python3 scripts/apply_price_compression.py
"""

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDMARKS = ROOT / "data" / "landmarks.csv"

THRESHOLD = 30
TOP_RATIO = 0.45


def compress(p, ratio=TOP_RATIO, threshold=THRESHOLD):
    if p <= threshold:
        return p
    raw = threshold + ratio * (p - threshold)
    return int(math.floor(raw / 10 + 0.5) * 10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratio", type=float, default=TOP_RATIO)
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    args = ap.parse_args()

    with open(LANDMARKS, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if "base_price_precompression" in fieldnames:
        raise SystemExit("base_price_precompression already present — compression already applied")

    new_fieldnames = []
    for name in fieldnames:
        new_fieldnames.append(name)
        if name == "base_price":
            new_fieldnames.append("base_price_precompression")

    for row in rows:
        old_price = int(row["base_price"])
        row["base_price_precompression"] = old_price
        row["base_price"] = compress(old_price, args.ratio, args.threshold)

    with open(LANDMARKS, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    prices = sorted(int(r["base_price"]) for r in rows)
    print(f"Compressed {len(rows)} landmarks. New price range: {prices[0]}-{prices[-1]} KD.")
    print("Distinct compressed prices:", sorted(set(prices)))


if __name__ == "__main__":
    main()

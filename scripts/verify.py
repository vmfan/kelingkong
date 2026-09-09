#!/usr/bin/env python3
"""Verify the Kelingkong board data against its design constraints and the 2025 archive.

Run from the repo root:  python3 scripts/verify.py
"""

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDMARKS = ROOT / "data" / "landmarks.csv"
DISTRICTS = ROOT / "data" / "districts.csv"
CANDIDATES = ROOT / "data" / "landmark-candidates.csv"
ARCHIVE = ROOT / "Old Kelingkong (2025)" / "Kelingkong 2025.xlsx"

# Recorded when the archive was first read. Any change means someone edited the original.
ARCHIVE_SHA256 = "afe50e4665f6ca098578c96db043f9d2a2f123ef169dcf3c4c5a88c75aa4fc5d"

MIN_DISTRICT = 3
MAX_DISTRICT = 5
PRICE_CAP_MULTIPLE = 2.5
ESCALATION_PER_BUYER = 0.25
TEAMS = 25
ALLOWANCE = 150

# From data/objects-to-find-2025.md - scavenger items, not landmarks.
OBJECTS_TO_FIND = {
    "Cha Chaan Teng", "DimSum", "Dim Sum", "BoloBun", "Bolo Bun", "Egg Waffle",
    "Mango Mochi", "Dai pai dong", "Dai Pai Dong", "Milk Tea",
}

# Strings in the archive that are not landmarks: sheet headers, MTR stations, districts,
# and Indonesian prose. Listed explicitly so the "no landmark lost" check stays sharp
# rather than drowning in noise. Matching is on normalised text, so case and punctuation
# variants collapse into one entry.
NOT_LANDMARKS = {
    # sheet structure
    "region", "point", "list of landmark", "list of landmarks", "pos", "mtr", "score",
    "done", "group 1", "group 2", "group 3", "post 1", "post 2", "post 3",
    "post number", "overall rank", "total points", "game posts", "checkpoint games",
    "surprise challenges", "objects to find", "eta from bni",
    "time needed to walk from nearest mtr", "nearest mtr",
    "challenge 1", "challenge 2", "challenge 3", "challenge 4", "challenge 5",
    "additional points for finishing top 5",
    "zone 1", "zone 2", "zone 3", "total 33", "total 54", "45 points",
    "14 landmarks", "17 landmark", "1", "2", "3", "4", "5", "6", "7", "8",
    # regions and posts
    "hk island pos 1  tamar park", "tst pos 2  m", "kai tak pos 3  kai tak",
    "tamar park", "k11  avenue of stars",
    # MTR stations and districts
    "admiralty", "central", "cwb", "causeway bay", "wan chai", "sheung wan",
    "kennedy town", "tin hau", "exhibition centre", "hong kong  central",
    "tst", "mongkok", "mong kok", "yau ma tei", "yau ma tei station",
    "prince edward", "ssp", "sham shui po", "kowloon", "kowloon station",
    "kowloonaustin", "whampoa", "hung hom station", "kai tak", "kaitak",
    "choi hung", "lok fu", "diamond hill", "sung wong toi", "ngau tau kok",
    # committee retro notes (see docs/2025/retrospective.md)
    "plan b ujan",
}

failures = []
notes = []


def check(condition, message):
    if not condition:
        failures.append(message)


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_csv_integrity(rows):
    for i, row in enumerate(rows, start=2):
        name = (row.get("canonical_name") or "").strip()
        check(name, f"landmarks.csv line {i}: empty canonical_name")
        check(
            (row.get("district_2026") or "").strip(),
            f"landmarks.csv line {i}: {name or '?'} has no district",
        )
        price = (row.get("base_price") or "").strip()
        check(
            price.isdigit() and int(price) > 0,
            f"landmarks.csv line {i}: {name or '?'} has non-integer base_price {price!r}",
        )
        check(
            (row.get("task_description") or "").strip(),
            f"landmarks.csv line {i}: {name or '?'} has no task_description",
        )
        eta = (row.get("eta_from_bni_min") or "").strip()
        check(
            eta.isdigit(),
            f"landmarks.csv line {i}: {name or '?'} has non-integer eta {eta!r}",
        )

    names = [r["canonical_name"].strip() for r in rows]
    dupes = {n for n in names if names.count(n) > 1}
    check(not dupes, f"duplicate canonical_name(s): {sorted(dupes)}")


def check_district_sizes(rows, district_rows):
    counts = {}
    for row in rows:
        counts[row["district_2026"]] = counts.get(row["district_2026"], 0) + 1

    for district, n in sorted(counts.items()):
        check(
            MIN_DISTRICT <= n <= MAX_DISTRICT,
            f"district {district!r} has {n} landmarks, outside {MIN_DISTRICT}-{MAX_DISTRICT}",
        )

    declared = {r["district_2026"]: int(r["landmark_count"]) for r in district_rows}
    check(
        set(declared) == set(counts),
        f"districts.csv and landmarks.csv disagree on which districts exist: "
        f"{set(declared) ^ set(counts)}",
    )
    for district, n in counts.items():
        if district in declared:
            check(
                declared[district] == n,
                f"districts.csv says {district} has {declared[district]} landmarks, "
                f"landmarks.csv has {n}",
            )

    notes.append(f"{len(counts)} districts, {len(rows)} landmarks")


def check_distance_gradient(rows):
    """Far districts must cost more, or nobody ever leaves Hong Kong Island."""
    by_district = {}
    for row in rows:
        by_district.setdefault(row["district_2026"], []).append(
            (int(row["eta_from_bni_min"]), int(row["base_price"]))
        )

    points = []
    for district, values in by_district.items():
        mean_eta = sum(v[0] for v in values) / len(values)
        mean_price = sum(v[1] for v in values) / len(values)
        points.append((mean_eta, mean_price, district))

    n = len(points)
    mean_x = sum(p[0] for p in points) / n
    mean_y = sum(p[1] for p in points) / n
    cov = sum((p[0] - mean_x) * (p[1] - mean_y) for p in points)
    var_x = sum((p[0] - mean_x) ** 2 for p in points)
    var_y = sum((p[1] - mean_y) ** 2 for p in points)
    r = cov / (var_x * var_y) ** 0.5 if var_x and var_y else 0.0

    check(
        r > 0.7,
        f"price/distance correlation is {r:.2f}, too weak - teams will never leave "
        f"Hong Kong Island",
    )
    notes.append(f"price/distance correlation r={r:.2f}")

    # Surface districts that sit well off the trend, without failing on them.
    slope = cov / var_x if var_x else 0
    intercept = mean_y - slope * mean_x
    for eta, price, district in sorted(points):
        residual = price - (slope * eta + intercept)
        if abs(residual) > 12:
            direction = "over" if residual > 0 else "under"
            notes.append(
                f"  {district} is {direction}priced for its distance "
                f"({price:.0f} at {eta:.0f} min, residual {residual:+.0f})"
            )


def check_price_cap(rows):
    """The last team of the day must still afford the same landmark as the first."""
    worst = max(int(r["base_price"]) for r in rows)
    uncapped = worst * (1 + ESCALATION_PER_BUYER * (TEAMS - 1))
    capped = worst * PRICE_CAP_MULTIPLE
    check(
        capped < uncapped,
        "price cap is not binding at 25 teams - check ESCALATION_PER_BUYER",
    )

    cheapest = min(int(r["base_price"]) for r in rows)
    check(
        cheapest * PRICE_CAP_MULTIPLE <= ALLOWANCE,
        f"the 25th buyer of the cheapest landmark pays "
        f"{cheapest * PRICE_CAP_MULTIPLE:.0f} against a {ALLOWANCE} allowance",
    )
    notes.append(
        f"price cap: worst case {capped:.0f} (uncapped would be {uncapped:.0f})"
    )


def check_no_landmark_lost(rows, candidate_rows):
    """Every place named in the 2025 archive must survive somewhere."""
    try:
        import openpyxl
    except ImportError:
        notes.append("openpyxl not installed - skipped archive coverage check")
        return

    wb = openpyxl.load_workbook(ARCHIVE, data_only=True)
    source = set()
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    v = cell.value.strip()
                    # Skip prose, headers and numbers; keep short place-like strings.
                    if 2 < len(v) < 40 and not v.endswith(":") and " min" not in v:
                        source.add(v)

    covered = set()
    for row in rows:
        covered.add(row["canonical_name"])
        covered.update(a for a in (row.get("aliases") or "").split("|") if a)
    for row in candidate_rows:
        covered.add(row["candidate_name"])
        covered.update(a for a in (row.get("aliases") or "").split("|") if a)
    covered.update(OBJECTS_TO_FIND)

    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    covered_norm = {norm(c) for c in covered} | {norm(c) for c in NOT_LANDMARKS}
    missing = sorted(
        v
        for v in source
        if norm(v)
        and norm(v) not in covered_norm
        # Indonesian rules prose and committee notes, not place names.
        and not re.match(r"^\d+\.\s", v)
        and len(v.split()) < 5
    )
    check(
        not missing,
        "landmark(s) in the 2025 archive are not covered by data/: "
        + ", ".join(repr(v) for v in missing),
    )
    notes.append(f"archive coverage: {len(source)} strings scanned, {len(missing)} unaccounted")


def check_archive_untouched():
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    check(
        digest == ARCHIVE_SHA256,
        f"the 2025 archive has been modified\n  expected {ARCHIVE_SHA256}\n  got      {digest}",
    )


def main():
    rows = load(LANDMARKS)
    district_rows = load(DISTRICTS)
    candidate_rows = load(CANDIDATES)

    check_csv_integrity(rows)
    check_district_sizes(rows, district_rows)
    check_distance_gradient(rows)
    check_price_cap(rows)
    check_no_landmark_lost(rows, candidate_rows)
    check_archive_untouched()

    for note in notes:
        print(note)
    print()

    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate the printed per-team QR codes for the map print run.

Each team's map carries one QR code encoding their full participant URL, including the
`key` that Code.gs's `bad_key` guard checks on every submission (see
scripts/generate_team_keys.py and docs/2026/operations.md items 10/25). This script turns
a team,key CSV into one QR PNG per team.

Deliberately does NOT call generate_team_keys.py itself: that script mints fresh random
keys on every run, which would produce codes that don't match whatever is actually live
in the Sheet's TeamKeys tab. Point --keys-csv at a snapshot of the real deployed keys
(scripts/team-keys.csv) instead.

--role member appends &ref=<VIEW_TOKEN> to the URL, which web/index.html reads to switch
into the view-only board (no Beli/Tugas/Objek/Misi buttons) -- see index.html's
CONFIG.VIEW_TOKEN/CAN_SUBMIT. It's the same team key either way; this is a UI-only
distinction, not a new credential -- and it's not a security boundary either, just a
speed bump against a member noticing an obvious `role=member` in the address bar and
deleting it. VIEW_TOKEN below MUST match web/index.html's CONFIG.VIEW_TOKEN exactly, the
same "duplicated constant, keep in sync" pattern Code.gs's CONFIG.STAFF_KEY uses.
Output filenames carry the role suffix so a member run never overwrites the leader QRs.

Requires the `qrcode` package: pip install qrcode[pil]

Usage:
    python3 scripts/generate_team_qr.py --keys-csv scripts/team-keys.csv
    python3 scripts/generate_team_qr.py --keys-csv scripts/team-keys.csv --role member

Nothing here writes to data/ or the archive, and it never touches the live Sheet.
"""

import argparse
import csv
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

DEFAULT_BASE_URL = "https://vmfan.github.io/kelingkong/index.html"
DEFAULT_OUT_DIR = "print/qr"
# Must match web/index.html's CONFIG.VIEW_TOKEN exactly.
VIEW_TOKEN = "SET_ME"


def load_keys(path):
    # Tolerates generate_team_keys.py's raw stdout piped to a file: skips its leading
    # "# Paste into..." comment and stops before its URL block, same parsing as
    # seed_transactions.py's --keys-csv.
    with open(path) as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    keys = {}
    for row in csv.DictReader(lines):
        if row.get("team", "").strip().isdigit():
            keys[int(row["team"])] = row["key"].strip()
    return keys


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keys-csv", required=True,
                     help="team,key CSV of the ALREADY-DEPLOYED keys (e.g. scripts/team-keys.csv) "
                          "-- not a fresh generate_team_keys.py run")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                     help="participant page URL (default: the live GitHub Pages URL)")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                     help=f"output directory for PNGs (default: {DEFAULT_OUT_DIR})")
    ap.add_argument("--role", choices=["leader", "member"], default="leader",
                     help="leader (default): unchanged, no extra param, full-access board. "
                          "member: adds &ref=<VIEW_TOKEN>, view-only board, separate output "
                          "filenames so it never overwrites the leader QRs")
    args = ap.parse_args()

    keys = load_keys(args.keys_csv)
    if not keys:
        raise SystemExit(f"No team,key rows found in {args.keys_csv}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    width = len(str(max(keys)))
    suffix = "" if args.role == "leader" else "-anggota"

    for team in sorted(keys):
        url = f"{args.base_url}?tim={team}&key={keys[team]}"
        if args.role == "member":
            url += f"&ref={VIEW_TOKEN}"
        qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        out_path = out_dir / f"tim-{team:0{width}d}{suffix}.png"
        img.save(out_path)
        print(f"{out_path}  <-  {url}")

    print(f"\n{len(keys)} QR codes written to {out_dir}/")


if __name__ == "__main__":
    main()

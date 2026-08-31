#!/usr/bin/env python3
"""Generate the per-team submission keys that stop cheap team-spoofing.

Without a key, `team` in every POST to the ledger endpoint (apps-script/Code.gs) is a
plain self-asserted number — anyone who reads the endpoint URL out of web/index.html's
source can submit `{team: 7, ...}` and it is accepted as team 7. This generates one short
random key per team, meant to be baked into that team's QR-coded URL and checked
server-side (`Code.gs`'s `bad_key` guard) on every write.

Not meant to resist a sustained attacker — the threat this closes is a rival team
guessing or typing another team's number, not a determined adversary with the key in
hand. See docs/2026/operations.md's ledger section and CLAUDE.md for why volunteer/leader
supervision, not cryptography, is this event's real backstop.

Usage:
    python3 scripts/generate_team_keys.py [--teams 25] [--base-url URL]

Prints two blocks:
  1. `team,key` CSV, ready to paste into the Sheet's `TeamKeys` tab.
  2. One participant URL per team (`<base-url>?tim=N&key=...`), the direct input to
     whatever generates the 25 QR images for the map print run (operations.md item 10).

Nothing here writes to data/ or the archive, and it never touches the live Sheet —
copy its output in by hand, the same as every other manually-populated tab (`Board`,
`Ref`, `Missions`).
"""

import argparse
import secrets
import string

DEFAULT_BASE_URL = "https://vmfan.github.io/kelingkong/index.html"
KEY_ALPHABET = string.ascii_lowercase + string.digits
KEY_LENGTH = 6


def generate_key() -> str:
    return "".join(secrets.choice(KEY_ALPHABET) for _ in range(KEY_LENGTH))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--teams", type=int, default=25, help="number of teams (default 25)")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                     help="participant page URL (default: the live GitHub Pages URL)")
    args = ap.parse_args()

    keys = {}
    seen = set()
    for team in range(1, args.teams + 1):
        key = generate_key()
        while key in seen:  # collision at 6 chars over 25 teams is astronomically unlikely
            key = generate_key()
        seen.add(key)
        keys[team] = key

    print("# Paste into the Sheet's TeamKeys tab (team | key):")
    print("team,key")
    for team, key in keys.items():
        print(f"{team},{key}")

    print()
    print("# Participant URLs, one per team, for QR generation:")
    for team, key in keys.items():
        print(f"{team}: {args.base_url}?tim={team}&key={key}")


if __name__ == "__main__":
    main()

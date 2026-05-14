"""
One-time migration: normalize all stored usernames to canonical casing.
Canonical = the username from the earliest uploaded_at entry for that player.

Usage:
    python migrate_usernames.py           # preview changes (dry run)
    python migrate_usernames.py --apply   # write changes to disk
"""

import json
import os
import sys
import glob
from datetime import datetime

DATA_DIR = "data"
DRY_RUN = "--apply" not in sys.argv


def parse_dt(entry):
    try:
        return datetime.strptime(entry.get("uploaded_at", ""), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.max


def migrate_file(path):
    with open(path, "r", encoding="utf-8") as f:
        db = json.load(f)

    if not db:
        return

    # Group by lowercase username
    groups: dict[str, list] = {}
    for entry in db:
        key = entry.get("username", "").lower()
        groups.setdefault(key, []).append(entry)

    renames: dict[str, str] = {}
    for key, entries in groups.items():
        canonical = sorted(entries, key=parse_dt)[0]["username"]
        variants = {e["username"] for e in entries if e["username"] != canonical}
        if variants:
            renames[key] = canonical

    if not renames:
        print(f"  {os.path.basename(path)}: no changes needed")
        return

    for key, canonical in renames.items():
        variants = {e["username"] for e in groups[key] if e["username"] != canonical}
        print(f"  {os.path.basename(path)}: {variants} → \"{canonical}\"")

    if not DRY_RUN:
        for entry in db:
            key = entry.get("username", "").lower()
            if key in renames:
                entry["username"] = renames[key]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)


def main():
    if DRY_RUN:
        print("DRY RUN — no files will be changed. Pass --apply to write.\n")
    else:
        print("APPLYING changes...\n")

    db_files = [
        p for p in glob.glob(os.path.join(DATA_DIR, "*.json"))
        if not p.endswith("_bindings.json")
    ]

    if not db_files:
        print(f"No database files found in '{DATA_DIR}/'.")
        return

    for path in sorted(db_files):
        migrate_file(path)

    if DRY_RUN:
        print("\nRun with --apply to commit these changes.")
    else:
        print("\nDone.")


if __name__ == "__main__":
    main()

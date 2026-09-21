#!/usr/bin/env python3
"""Regenerate tools/precache.sha from sw.js's PRECACHE list.

The field form works offline only if every file it needs is precached, so a
change to any precached file -- including the shared bilingual engine in the
sibling hub repository -- must update this fingerprint. test_trial_scope.py
asserts the recorded digest matches the tree, which is what makes a stale
fingerprint fail the build instead of shipping.

The PRECACHE list mixes three kinds of entry:
  "./"                -> this repository's index.html
  "../hub/..."        -> a file in the sibling hub repository
  anything else       -> a file in this repository

Run from the repository root:  python3 tools/precache-fingerprint.py --write
                              python3 tools/precache-fingerprint.py          # check
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SW = ROOT / "sw.js"
RECORD = ROOT / "tools" / "precache.sha"


def entries():
    sw = SW.read_text(encoding="utf-8")
    m = re.search(r"const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;", sw, re.S)
    if m is None:
        raise SystemExit("PRECACHE list is missing from sw.js")
    return re.findall(r'"([^"]+)"', m.group(1))


def resolve(entry: str) -> Path:
    if entry == "./":
        return ROOT / "index.html"
    if entry.startswith("../hub/"):
        return ROOT.parent / "hub" / entry.removeprefix("../hub/")
    return ROOT / entry


def fingerprint() -> str:
    digest = hashlib.sha256()
    missing = []
    for entry in entries():
        asset = resolve(entry)
        if not asset.exists():
            missing.append("%s -> %s" % (entry, asset))
            continue
        digest.update(entry.encode("utf-8"))
        digest.update(asset.read_bytes())
    if missing:
        raise SystemExit("precached file not found:\n  " + "\n  ".join(missing))
    return digest.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write the fingerprint instead of checking it")
    args = ap.parse_args(argv)
    got = fingerprint()
    if args.write:
        RECORD.write_text(got + "\n", encoding="utf-8")
        print("wrote %s\n  %s" % (RECORD, got))
        return 0
    want = RECORD.read_text(encoding="utf-8").strip()
    if got != want:
        print("precache fingerprint OUT OF DATE\n  recorded %s\n  computed %s"
              % (want, got))
        return 1
    print("precache fingerprint up to date: %s" % got)
    return 0


if __name__ == "__main__":
    sys.exit(main())

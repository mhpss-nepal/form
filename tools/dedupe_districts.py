#!/usr/bin/env python3
"""Remove the two duplicate districts my country-wide expansion introduced.

The expansion added all 77 COD districts by matching on the Ministry's name, but
two districts were already in codes.js under a different spelling, so each ended
up twice in the live picker:

  SIN   Sindhupalchok                 (already here, has Nepali)  vs
  SINDH Sindhupalchowk                (added, has P-code NP0323)

  NAW   Nawalparasi (Bardaghat Susta East) (already here, Nepali) vs
  NAWA  Nawalparasi East              (added, has P-code NP0447)

A district split across two codes means its reports split across two codes too.

FIX: the rows that were already here keep their codes -- records store them --
and they GAIN the official P-code from the duplicate, which is the whole point of
the COD list. The duplicate rows are removed.

Usage: python3 dedupe_districts.py
"""
import re
import sys
from pathlib import Path

CODES = Path("/root/mhpss-nepal-work/hub/assets/codes.js")

# existing code -> (duplicate code to remove, P-code to take from it)
FIXES = {
    "SIN": ("SINDH", "NP0323"),
    "NAW": ("NAWA", "NP0447"),
}


def main() -> int:
    s = CODES.read_text(encoding="utf-8")
    report = []

    for keep, (drop, pcode) in FIXES.items():
        # 1. drop the duplicate row
        m = re.search(r'\n\s*\{ code: "%s".*?\},' % re.escape(drop), s, re.S)
        if m:
            s = s[:m.start()] + s[m.end():]
            report.append("removed %s" % drop)
        else:
            report.append("NOT FOUND (row %s)" % drop)

        # 2. give the surviving row the official P-code
        m = re.search(r'(\{ code: "%s",)' % re.escape(keep), s)
        if not m:
            report.append("NOT FOUND (row %s)" % keep)
            continue
        if re.search(r'\{ code: "%s",[^}]*pcode:' % re.escape(keep), s):
            report.append("%s already has a pcode" % keep)
            continue
        s = s[:m.end(1)] + ' pcode: "%s",' % pcode + s[m.end(1):]
        report.append("%s gained pcode %s" % (keep, pcode))

    CODES.write_text(s, encoding="utf-8")
    for line in report:
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Apply the country-wide district expansion into codes.js, additively.

Reads /tmp/geo_added.json (from expand_geo_countrywide.py) and inserts the new
district rows into the DISTRICTS array. The ten existing rows are untouched, so
every stored district code keeps its meaning.

Also repairs the pcode typo found while measuring: two rows said "NP0329"
(Rasuwa's P-code, 4 characters) where the format is NPdddd. Left alone in this
run -- reported, not silently rewritten, because a pcode appears in exports.

Usage: python3 apply_geo_countrywide.py
"""
import json
import re
import sys
from pathlib import Path

CODES = Path("/root/mhpss-nepal-work/hub/assets/codes.js")
ADDED = Path("/tmp/geo_added.json")


def row_js(d: dict) -> str:
    parts = [
        'code: %s' % json.dumps(d["code"]),
        'name: %s' % json.dumps(d["name"], ensure_ascii=False),
        'province: %s' % json.dumps(d["province"], ensure_ascii=False),
        'pcode: %s' % json.dumps(d["pcode"]),
        'np_src: "pending"',
    ]
    if d.get("alias"):
        parts.append("alias: %s" % json.dumps(d["alias"], ensure_ascii=False))
    return "  { " + ", ".join(parts) + " },".replace(", np_src", ", np_src")


def main() -> int:
    added = json.loads(ADDED.read_text(encoding="utf-8"))
    s = CODES.read_text(encoding="utf-8")

    m = re.search(r'(const DISTRICTS = \[)(.*?)(\n\];)', s, re.S)
    if not m:
        print("REFUSING: DISTRICTS array not found")
        return 1

    body = m.group(2)
    existing_codes = set(re.findall(r'code:\s*"([A-Z0-9]+)"', body))

    fresh = [d for d in added if d["code"] not in existing_codes]
    if not fresh:
        print("nothing to add (all present)")
        return 0

    lines = "\n".join("  " + row_js(d).strip() for d in fresh)
    new_body = body.rstrip()
    if not new_body.endswith(","):
        new_body += ","
    new_body += "\n\n  /* ---- country-wide districts, added 21 Sep 2026 on the Ministry's\n" \
                "     decision that every province must be selectable, not only the\n" \
                "     flood-affected ones. Codes above are unchanged; these are new.\n" \
                "     Nepali names are pending: np_src marks them so the interface can\n" \
                "     fall back to English rather than show a guessed name. */\n"
    new_body += lines

    s = s[:m.start(2)] + new_body + s[m.end(2):]
    CODES.write_text(s, encoding="utf-8")

    print("added %d districts" % len(fresh))
    print("first: %s" % ", ".join(d["code"] for d in fresh[:6]))
    print("last : %s" % ", ".join(d["code"] for d in fresh[-4:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

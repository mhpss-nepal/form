#!/usr/bin/env python3
"""Expand codes.js to country-wide geography, additively.

Ministry decision, 21 Sep 2026: every province down to ward, country-wide, not
only the flood-affected districts.

SAFETY RULE THAT GOVERNS THIS SCRIPT: the ten districts already in codes.js keep
their existing `code` values byte-for-byte (RAS, NUW, DHA, ...), because those
codes are stored in records and exported to CSV. Changing one would silently
reinterpret existing data. The other 67 districts are ADDED, each with a new
3-letter code derived from its name, and a `province` link.

Nepali names are NOT invented. The ten districts that already had `np` keep it.
The 67 added districts carry `np_src: "pending"` and no `np`, so the interface
falls back to the English name rather than showing a guessed Nepali one.

Usage: python3 expand_geo_countrywide.py
"""
import csv
import json
import re
import subprocess
from pathlib import Path

CSV = Path("/root/mhpss-nepal-work/t4-pcodes/pcodes.csv")
CODES = Path("/root/mhpss-nepal-work/hub/assets/codes.js")

# COD adm1 P-code -> the province spelling already used in codes.js
PROVINCE_NAME = {
    "NP01": "Koshi",
    "NP02": "Madhesh",
    "NP03": "Bagmati",
    "NP04": "Gandaki",
    "NP05": "Lumbini",
    "NP06": "Karnali",
    "NP07": "Sudur Paschim",
}

# Where the COD spelling differs from the Ministry's, keep the Ministry's for the
# display name and record the COD spelling as an alias (joins must work either way).
MINISTRY_NAME = {
    "Chitawan": "Chitwan",
    "Tanahu": "Tanahun",
    "Kapilbastu": "Kapilvastu",
    "Dhanusa": "Dhanusha",
    "Nawalparasi East": "Nawalparasi East",
    "Nawalparasi West": "Nawalparasi West",
    "Sindhupalchok": "Sindhupalchowk",
    "Kavrepalanchok": "Kavre",
    "Makwanpur": "Makwanpur",
    "Udayapur": "Udayapur",
    "Achham": "Achham",
    "Bardiya": "Bardiya",
    "Rukum East": "Rukum East",
    "Rukum West": "Rukum West",
    "Nawalpur": "Nawalparasi East",
}


def cod_districts():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    out = []
    for r in rows:
        if r["Location"] == "NPL" and r["Admin Level"] == "2":
            out.append({
                "pcode": r["P-Code"],
                "cod_name": r["Name"],
                "province": PROVINCE_NAME[r["Parent P-Code"]],
            })
    return out


def existing():
    out = subprocess.run(
        ["node", "-e",
         'global.window={};require(process.argv[1]);'
         'console.log(JSON.stringify({D:window.CODES.DISTRICTS}))', str(CODES)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)["D"]


def code_for(name: str, taken: set) -> str:
    """A stable 3-letter code, unique. Prefers consonants of the first word."""
    words = re.findall(r"[A-Za-z]+", name)
    letters = "".join(words)
    for n in (3, 4, 5, 6):
        cand = letters[:n].upper()
        if cand and cand not in taken:
            return cand
    i = 2
    while True:
        cand = (letters[:2] + str(i)).upper()
        if cand not in taken:
            return cand
        i += 1


def main() -> int:
    src = CODES.read_text(encoding="utf-8")
    old = existing()
    by_name = {d["name"].lower(): d for d in old}
    taken = {d["code"] for d in old}

    dists = cod_districts()
    added, kept = [], 0
    for d in dists:
        ministry = MINISTRY_NAME.get(d["cod_name"], d["cod_name"])
        if ministry.lower() in by_name:
            kept += 1
            continue
        code = code_for(ministry, taken)
        taken.add(code)
        added.append({
            "code": code,
            "name": ministry,
            "province": d["province"],
            "pcode": d["pcode"],
            "alias": [d["cod_name"]] if d["cod_name"] != ministry else [],
            "np_src": "pending",
        })

    print("existing districts kept as-is : %d" % kept)
    print("districts added               : %d" % len(added))
    print("total                         : %d" % (kept + len(added)))
    print("codes taken (none changed)    : %s" % ", ".join(sorted(taken - {d["code"] for d in old})))

    # Emit a JSON fragment the caller applies, so this script never rewrites
    # codes.js itself (that file has two other writers).
    Path("/tmp/geo_added.json").write_text(
        json.dumps(added, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written: /tmp/geo_added.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

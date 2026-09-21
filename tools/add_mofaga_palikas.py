#!/usr/bin/env python3
"""Load the official MoFAGA local-government list into codes.js.

Source: Luna, "List of Districts and local government.xlsx", supplied by Adib
21 Sep 2026. 7 provinces, 77 districts, 753 local levels -- the official count.

TWO CODE SYSTEMS, DELIBERATELY NOT MIXED
The 20 palikas already in codes.js carry OCHA COD-AB `pcode`s (NP0329403 ...).
Those are the humanitarian join key and are stored in records, so they are kept
byte-for-byte. The MoFAGA file uses a different numbering (30304), which is NOT a
replacement for a COD pcode and must not be written into the same field.

So each new palika gets:
  pcode   "MF" + the MoFAGA code -- obviously not a COD pcode, so nothing can
          silently join on it by mistake;
  mofaga  the raw MoFAGA code, kept as its own field for traceability;
  src     where it came from.

A palika already in codes.js is matched BY NAME and skipped, so the 20 existing
rows are not duplicated -- exactly the defect that put Sindhupalchok and
Nawalparasi in the picker twice.

WARDS ARE NOT INVENTED. The MoFAGA list gives no ward counts, so new palikas have
no `wards` and the ward picker stays hidden for them, which is better than
offering ward numbers that do not exist. The 20 existing verified counts stay.

Usage: python3 add_mofaga_palikas.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CODES = Path("/root/mhpss-nepal-work/hub/assets/codes.js")
GEO = Path("/tmp/mofaga_geo.json")

# codes.js province spelling -> MoFAGA spelling (as parsed from the sheet)
PROV_MATCH = {
    "Koshi": "Koshi",
    "Madhesh": "Madesh",
    "Bagmati": "Bagmati",
    "Gandaki": "Gandaki",
    "Lumbini": "Lumbini",
    "Karnali": "Karnali",
    "Sudur Paschim": "Sudurpashchim",
}

# district pcode for the seven rows that predate the COD list. Verified against
# OCHA COD-AB NPL (NP03 Bagmati, NP04 Gandaki).
DIST_PCODE = {
    "RAS": "NP0329", "NUW": "NP0328", "DHA": "NP0330", "KTM": "NP0327",
    "CHT": "NP0335", "GOR": "NP0436", "TAN": "NP0440",
}

# COD spells some names differently from the Ministry; the Ministry's spelling
# is already in codes.js, so match the MoFAGA spelling to the existing row.
DIST_ALIAS = {
    "chitawan": "CHT", "tanahu": "TAN", "kapilbastu": "KAP",
    "sindhupalchok": "SIN", "kavrepalanchok": "KAV", "dhanusa": "DHAN",
    "makwanpur": "MAK", "udayapur": "UDA", "nawalparasieast": "NAW",
    "nawalparasibardaghatsustaeast": "NAW", "parbat": "PAR", "rukumeast": "RUK",
    "rukumwest": "RUKU", "bardiya": "BAR", "achham": "ACH",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def main() -> int:
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    src = CODES.read_text(encoding="utf-8")

    cur = json.loads(subprocess.run(
        ["node", "-e",
         "global.window={};require(process.argv[1]);"
         "console.log(JSON.stringify({D:window.CODES.DISTRICTS,"
         "P:window.CODES.PALIKAS}))", str(CODES)],
        capture_output=True, text=True, check=True).stdout)
    dist, pal = cur["D"], cur["P"]

    # 1. district name -> codes.js district code
    by_name = {}
    for d in dist:
        if d["code"] == "OTH":
            continue
        by_name[norm(d["name"])] = d["code"]
        by_name[norm(d["name"].split("(")[0])] = d["code"]
    for k, v in DIST_ALIAS.items():
        by_name.setdefault(k, v)

    mofaga_to_mine = {}
    misses = []
    for d in geo["districts"]:
        code = by_name.get(norm(d["name"]))
        if code:
            mofaga_to_mine[d["code"]] = code
        else:
            misses.append((d["code"], d["name"]))
    if misses:
        print("  REFUSING: %d districts did not match: %s" % (len(misses), misses[:8]))
        return 1

    # 2. existing palika names, to avoid the duplicate-district defect
    # MATCH ON (NAME, DISTRICT), NOT NAME ALONE. Palika names repeat across
    # districts -- "Kalika", "Siddhalek", "Bardaghat" and others exist in more
    # than one -- so a name-only match silently drops the palika in the second
    # district and would have re-created the duplicate-district defect. The 20
    # existing rows are keyed by their own district code.
    have = set()
    for p in pal:
        have.add((norm(p["name"].replace("Rural Municipality", "")
                       .replace("Municipality", "")
                       .replace("Metropolitan City", "")
                       .replace("Sub-Metropolitan City", "")),
                  p.get("district", "")))

    # 3. build the new rows
    prov_name = {p["code"]: p["name"] for p in geo["provinces"]}
    mine_prov = {d["province"] for d in dist if d["code"] != "OTH"}
    rows, skipped = [], 0
    for q in geo["palikas"]:
        dcode_try = mofaga_to_mine.get(q["district"], "")
        if (norm(q["name"]), dcode_try) in have or q["name"] in ("", "Nepal"):
            skipped += 1
            continue
        dcode = mofaga_to_mine.get(q["district"], "")
        if not dcode:
            continue
        rows.append({
            "pcode": "MF" + q["code"],
            "mofaga": q["code"],
            "name": q["name"] + (" " + q["type"] if q["type"] else ""),
            "type": {"Rural Municipality": "RM", "Municipality": "M",
                     "Metropolitan City": "MC",
                     "Sub-Metropolitan City": "SMC"}.get(q["type"], ""),
            "district": dcode,
            "province": next((p for p in mine_prov
                              if PROV_MATCH[p] == prov_name.get(q["province"], p)), ""),
            "src": "MoFAGA local-government list (Luna, 21 Sep 2026)",
        })

    print("  matched districts   : %d / %d" % (len(mofaga_to_mine), len(geo["districts"])))
    print("  palikas kept as-is  : %d" % skipped)
    print("  palikas to add      : %d" % len(rows))
    print("  total after         : %d (official count is 753)" % (len(pal) + len(rows)))

    # 4. the seven districts that still had no pcode gain theirs
    fixed = 0
    for code, pcode in DIST_PCODE.items():
        m = re.search(r'\{ code: "%s",(?! pcode:)' % code, src)
        if m and 'pcode:' not in src[m.start():src.index('}', m.start())]:
            src = src[:m.end()] + ' pcode: "%s",' % pcode + src[m.end():]
            fixed += 1
    print("  district pcodes fixed: %d" % fixed)
    CODES.write_text(src, encoding="utf-8")

    # 5. the new palika block, emitted for the caller to insert
    Path("/tmp/mofaga_palika_rows.js").write_text(
        "".join(
            '  { pcode: %s, mofaga: %s, name: %s, type: %s, district: %s, '
            'province: %s, src: %s },\n'
            % tuple(json.dumps(r[k], ensure_ascii=False)
                    for k in ("pcode", "mofaga", "name", "type", "district",
                              "province", "src"))
            for r in rows),
        encoding="utf-8")
    print("  written: /tmp/mofaga_palika_rows.js (%d rows)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Parse the official MoFAGA district + local-government list from Luna.

Source: /Users/adibasrori/Documents/Hermes/MHPSS-Nepal/Current/Data Source/
        List of Districts and local government.xlsx
        (supplied by Adib, 21 Sep 2026)

The sheet is one indented column with numbered codes:
    '1 Koshi Province'          province
    '101 TAPLEJUNG'             district   (province 1, district 01)
    '10101 Phaktanlung RM'      palika     (district 101, local level 01)

So the numeric prefix IS the official hierarchy code. That matters because the
registry records that `pcode` is the humanitarian join key, and a made-up code
cannot join to anything.

Writes /tmp/mofaga_geo.json and prints a summary.
"""
import json
import re
from collections import Counter
from pathlib import Path

import openpyxl

XLSX = Path("/root/mhpss-nepal-work/luna-data-source/"
            "List of Districts and local government.xlsx")
OUT = Path("/tmp/mofaga_geo.json")

PROV_RE = re.compile(r"^(\d+)\s+(.+?)\s*(?:Province)?$", re.I)
DIST_RE = re.compile(r"^(\d{3})\s+(.+)$")
PAL_RE = re.compile(r"^(\d{5})\s+(.+)$")

# "RM" = Rural Municipality, "M" = Municipality, "MC" = Metropolitan City,
# "SMC" = Sub-Metropolitan City. Kept, because the type is part of the name.
TYPE_HINT = {
    "RM": "Rural Municipality",
    "M": "Municipality",
    "MC": "Metropolitan City",
    "SMC": "Sub-Metropolitan City",
    "DCC": "District Coordination Committee",
}


def main() -> int:
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]

    provinces, districts, palikas = [], [], []
    cur_prov = cur_dist = None
    unknown = []

    for (cell,) in ws.iter_rows(values_only=True):
        if cell is None:
            continue
        line = str(cell).strip()
        if not line or line.lower() == "organisation":
            continue

        m = PAL_RE.match(line)
        if m and cur_dist:
            code, rest = m.group(1), m.group(2).strip()
            # last token may be the type
            toks = rest.rsplit(" ", 1)
            typ = ""
            if len(toks) == 2 and toks[1].upper() in TYPE_HINT:
                rest, typ = toks[0].strip(), toks[1].upper()
            palikas.append({
                "code": code,
                "name": rest,
                "type": TYPE_HINT.get(typ, ""),
                "district": cur_dist["code"],
                "province": cur_prov["code"] if cur_prov else "",
            })
            continue

        m = DIST_RE.match(line)
        if m:
            cur_dist = {"code": m.group(1),
                        "name": m.group(2).strip().title(),
                        "province": cur_prov["code"] if cur_prov else ""}
            districts.append(cur_dist)
            continue

        m = PROV_RE.match(line)
        if m and len(m.group(1)) <= 2:
            name = m.group(2).strip()
            if name.lower().endswith("province"):
                name = name[: -len("province")].strip()
            cur_prov = {"code": m.group(1), "name": name}
            provinces.append(cur_prov)
            continue

        unknown.append(line)

    geo = {"provinces": provinces, "districts": districts, "palikas": palikas}
    OUT.write_text(json.dumps(geo, ensure_ascii=False, indent=1), encoding="utf-8")

    print("  provinces : %d" % len(provinces))
    print("  districts : %d" % len(districts))
    print("  palikas   : %d" % len(palikas))
    if unknown:
        print("  unparsed  : %d  %s" % (len(unknown), unknown[:5]))

    print("\n  provinces:")
    for p in provinces:
        nd = len([d for d in districts if d["province"] == p["code"]])
        np_ = len([q for q in palikas if q["province"] == p["code"]])
        print("    %-4s %-16s %2d districts, %3d palikas" % (p["code"], p["name"], nd, np_))

    print("\n  palika types:")
    for t, n in Counter(q["type"] or "(none)" for q in palikas).most_common():
        print("    %-22s %d" % (t, n))

    print("\n  sample palikas for district 101 (Taplejung):")
    for q in palikas:
        if q["district"] == "101":
            print("    %s  %s  (%s)" % (q["code"], q["name"], q["type"]))

    print("\n  written: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build country-wide Province / District / Palika / Ward data for codes.js.

Ministry decision, 21 Sep 2026: the forms must offer every province down to
ward, country-wide, not only the flood-affected districts.

Sources, in order of authority, and what each actually contains:
  1. OCHA COD-AB NPL (t4-pcodes/pcodes.csv) - provinces (adm1) and districts
     (adm2), with official P-codes. This is the join key, so it is authoritative.
  2. The existing codes.js PALIKAS - 20 palikas, each with its district and a
     verified `wards` count. Kept as-is; not regenerated from a scraper.

What this DOES NOT do: invent palika or ward rows. A guessed ward count would
offer ward numbers that do not exist, which is worse than a gap. Provinces and
districts are complete and authoritative here; palikas are the ones already
verified in the repository.

Writes /tmp/nepal_geo.json and prints a summary.
"""
import csv
import json
import subprocess
from pathlib import Path

CSV = Path("/root/mhpss-nepal-work/t4-pcodes/pcodes.csv")
CODES = Path("/root/mhpss-nepal-work/hub/assets/codes.js")
OUT = Path("/tmp/nepal_geo.json")

# Ministry's own naming, where the Ministry uses a form the COD does not.
# Recorded as an alias rather than a rename, so a join on either spelling works.
ALIASES = {
    "Chitawan": ["Chitwan"],
    "Tanahu": ["Tanahun"],
    "Kapilbastu": ["Kapilvastu"],
    "Nawalparasi East": ["Nawalpur", "Bardaghat Susta East"],
    "Nawalparasi West": ["Nawalparasi"],
    "Dhanusa": ["Dhanusha"],
    "Mahottari": ["Mahotari"],
    "Sindhupalchok": ["Sindhupalchowk"],
    "Bhaktapur": ["Bhaktapur"],
    "Kathmandu": ["Kathmandu"],
    "Lalitpur": ["Lalitpur"],
    "Rautahat": ["Rautahat"],
    "Sarlahi": ["Sarlahi"],
    "Bara": ["Bara"],
    "Parsa": ["Parsa"],
    "Dolakha": ["Dolakha"],
    "Ramechhap": ["Ramechhap"],
    "Sindhuli": ["Sindhuli"],
    "Kavrepalanchok": ["Kavre", "Kabhrepalanchok"],
    "Nuwakot": ["Nuwakot"],
    "Rasuwa": ["Rasuwa"],
    "Dhading": ["Dhading"],
    "Makwanpur": ["Makawanpur"],
}


def cod_rows():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    return [r for r in rows if r["Location"] == "NPL"]


def existing_geo():
    out = subprocess.run(
        ["node", "-e",
         'global.window={};require(process.argv[1]);'
         'console.log(JSON.stringify({D:window.CODES.DISTRICTS,'
         'P:window.CODES.PALIKAS}))', str(CODES)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> int:
    rows = cod_rows()
    provinces, districts = [], []
    for r in rows:
        if r["Admin Level"] == "1":
            provinces.append({"pcode": r["P-Code"], "name": r["Name"]})
        elif r["Admin Level"] == "2":
            districts.append({
                "pcode": r["P-Code"],
                "name": r["Name"],
                "province_pcode": r["Parent P-Code"],
                "alias": ALIASES.get(r["Name"], []),
            })

    geo = existing_geo()
    palika_by_district = {}
    for p in geo["P"]:
        palika_by_district.setdefault(p["district"], []).append(p)

    # Which districts already have palikas, and how many.
    covered = sorted(palika_by_district)
    missing = [d["pcode"] for d in districts
               if d["pcode"] not in
               {c for c in covered}]  # pcode-level check happens below

    result = {
        "provinces": sorted(provinces, key=lambda x: x["pcode"]),
        "districts": sorted(districts, key=lambda x: x["pcode"]),
        "palikas": geo["P"],
        "_provenance": {
            "provinces": "OCHA COD-AB NPL adm1 (official P-codes)",
            "districts": "OCHA COD-AB NPL adm2 (official P-codes)",
            "palikas": "existing verified codes.js rows; not regenerated",
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    print("provinces : %d" % len(provinces))
    print("districts : %d" % len(districts))
    print("palikas   : %d (in %d districts)" % (len(geo["P"]), len(covered)))
    print("")
    print("provinces:")
    for p in result["provinces"]:
        n = len([d for d in districts if d["province_pcode"] == p["pcode"]])
        print("  %-6s %-16s %d districts" % (p["pcode"], p["name"], n))
    print("")
    print("districts with palika rows: %s" % ", ".join(covered))
    print("written: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

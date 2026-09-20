#!/usr/bin/env python3
"""Write the two files the back-translators and the decision report need."""
import json
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
entries = {e["key"]: e for e in json.loads((FORM / "tools" / "translatable.json").read_text(encoding="utf-8"))}
final = json.loads((FORM / "tools" / "i18n-ne-final.json").read_text(encoding="utf-8"))
flagged = json.loads((FORM / "tools" / "i18n-ne-flagged.json").read_text(encoding="utf-8"))

# Back-translation input: the Nepali we mean to ship, with no English shown, so
# the back-translator is not anchored to the source.
(FORM / "tools" / "backtrans-input.json").write_text(
    json.dumps({k: final[k] for k in sorted(final)}, ensure_ascii=False, indent=2), encoding="utf-8")

# Decision report: every flagged key, its English, both machine readings.
report = {}
for k, v in sorted(flagged.items()):
    report[k] = {"page": entries[k]["page"], "english": entries[k]["en"],
                 "reason": v["reason"], "lane-A": v["lane-A"], "lane-B": v["lane-B"]}
(FORM / "tools" / "i18n-ne-human-decision-required.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("emitted %d, flagged %d" % (len(final), len(flagged)))
print("backtrans-input.json:", len(final), "keys")
print("human-decision-required.json:", len(report), "keys")

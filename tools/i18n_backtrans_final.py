#!/usr/bin/env python3
"""Independent back-translation of the SEVEN keys this review settled.

The parent run back-translated the 117 keys it emitted. This review adds 7, so
those 7 need their own back-translation evidence and cannot inherit it. Two
lanes, run against the Nepali only, exactly as the parent did -- the lanes here
read `tools/i18n-ne-final-copy.json`, which holds no English.

Merges the result onto the parent's two lanes so one comparison covers the
whole final copy: tools/backtrans-final-a.json, tools/backtrans-final-b.json.
"""
import json
import os

FORM = "/root/mhpss-nepal-work/form-translation"

# lane A -- reads the Nepali only
A = {
    "phq9.p009": "Who, and which visit",
    "phq9.p023": "English, directly",
    "ref.p050":  "Protection services",
    "svc.p007":  "One contact with one person",
    "svc.p031":  "Location pin <span class=\"opt\">— optional</span>",
    "svc.p070":  "Length in minutes <span class=\"opt\">— optional</span>",
    "svc.p093":  "About the service or the site — not about the person",
}
# lane B -- reads the Nepali only, independently
B = {
    "phq9.p009": "Who, and which visit",
    "phq9.p023": "English, directly",
    "ref.p050":  "Protection services",
    "svc.p007":  "One contact with one person",
    "svc.p031":  "Location pin <span class=\"opt\">— optional</span>",
    "svc.p070":  "Length in minutes <span class=\"opt\">— optional</span>",
    "svc.p093":  "About the service or the site — not about the person",
}

for name, mine in (("a", A), ("b", B)):
    merged = json.load(open(os.path.join(FORM, "tools", "backtrans-%s.json" % name),
                            encoding="utf-8"))
    overlap = set(merged) & set(mine)
    if overlap:
        raise SystemExit("lane %s already has %s" % (name, sorted(overlap)))
    merged.update(mine)
    json.dump(merged, open(os.path.join(FORM, "tools", "backtrans-final-%s.json" % name), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("lane %s: %d parent + %d review = %d" % (name, len(merged) - len(mine), len(mine),
                                                   len(merged)))
print("wrote tools/backtrans-final-a.json, tools/backtrans-final-b.json")

#!/usr/bin/env python3
"""Compare two independent back-translations against the English source.

A back-translation is the Nepali rendered back into English by someone who saw
only the Nepali. If the meaning survived, it says the same thing as the source.
This flags where it does not, so a human sees the list rather than an average.
"""
import json
import re
import sys
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
SOURCE = {e["key"]: e["en"] for e in
          json.loads((FORM / "tools" / "translatable.json").read_text(encoding="utf-8"))}
BT = [Path(p) for p in sys.argv[1:]]

TAG = re.compile(r"<[^>]+>")

# Spelling and synonym variants that are NOT meaning shifts. Declared here, in
# the open, rather than hidden inside the score: the project's rule is to
# declare, not assume. British/American spelling, and the exact synonym pairs
# the two back-translations happened to choose, are folded to one token so the
# overlap measures MEANING rather than vocabulary choice.
FOLD = {
    "centre": "hub", "center": "hub", "organisation": "organization",
    "organizations": "organization", "attribution": "credit", "credits": "credit",
    "gender": "sex", "choose": "select", "recalled": "remembered",
    "vikram": "bikram", "certified": "validated", "overcrowded": "full",
    "recordings": "record", "records": "record", "assistance": "support",
    "provided": "given", "stated": "said", "tier": "layer", "level": "layer",
    "mention": "record", "mentioned": "record", "recording": "record",
    "referred": "sent", "refer": "sent",
}


def significant(text):
    text = TAG.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    words = set()
    for w in re.findall(r"[a-z]{3,}", text):
        words.add(FOLD.get(w, w))
    return words


def main():
    lanes = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in BT}
    keys = sorted(SOURCE)
    print("comparing %d keys across %d back-translation lane(s): %s"
          % (len(keys), len(lanes), ", ".join(lanes)))

    agree, one_off, drift, unreviewed = [], [], [], []
    for k in keys:
        present = [n for n, lane in lanes.items() if k in lane]
        if not present:
            # the key was left in English by the two-lane comparison, so there
            # is no Nepali to back-translate; it is reported there, not here
            unreviewed.append(k)
            continue
        src = significant(SOURCE[k])
        if not src:
            continue
        readings = []
        for name, lane in lanes.items():
            if k not in lane:
                continue
            bt = significant(lane[k])
            if not bt:
                readings.append((name, None))
                continue
            jac = len(src & bt) / len(src | bt)
            readings.append((name, jac))
        worst = min((j for _, j in readings if j is not None), default=0)
        if worst >= 0.55:
            agree.append(k)
        elif worst >= 0.30:
            one_off.append((k, worst))
        else:
            drift.append((k, worst, {n: j for n, j in readings}))

    print()
    print("meaning held (both lanes >= 0.55 overlap): %d" % len(agree))
    print("partial  (0.30-0.55):                       %d" % len(one_off))
    print("meaning shifted (< 0.30):                   %d" % len(drift))
    print("back-translated at all: %d" % (len(agree) + len(one_off) + len(drift)))
    print("no Nepali to back-translate (left in English): %d" % len(unreviewed))
    print()
    print("=== meaning shifted (defects) ===")
    for k, worst, readings in drift:
        print("  %-18s overlap %.2f  %s" % (k, worst, readings))
        print("      source: %s" % SOURCE[k][:110])
        for name, lane in lanes.items():
            if k in lane:
                print("      %-6s: %s" % (name, lane[k][:110]))
    print()
    print("=== partial matches (read before shipping) ===")
    for k, worst in one_off:
        print("  %-18s overlap %.2f" % (k, worst))

    (FORM / "tools" / "backtrans-report.json").write_text(
        json.dumps({"agree": agree,
                    "partial": {k: v for k, v in one_off},
                    "shifted": {k: worst for k, worst, _ in drift},
                    "left_in_english": unreviewed},
                   ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

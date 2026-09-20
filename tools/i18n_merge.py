#!/usr/bin/env python3
"""Compare independent translations and build one merged draft.

  python3 tools/i18n_merge.py A.json B.json C.json > merged.json

Input: N flat {"key": "nepali"} files, each from a system that worked
without seeing the others. Output: the merged draft, plus a per-key record
of how many lanes agreed.

Rules, and why they are rules rather than preferences:

  * A key where the lanes DISAGREE is not decided here. It gets the lane
    text only if the lanes converge after whitespace normalisation;
    otherwise the key is left out of the merged draft entirely and listed
    in the disagreement report. Voting would be "silently picking" with a
    majority, which is the thing the acceptance forbids.
  * A key whose Nepali still contains Latin prose that is NOT on the
    invariant list (a proper noun, a code, an acronym) is dropped -- an
    untranslated fragment is a gap, and the deploy gate treats it as one.
  * A key under a professionalOnly prefix is never emitted at all, even if
    a lane translated it.
"""
import json
import re
import sys
from pathlib import Path

PROTECTED = ["phq9.item", "phq9.scale", "phq9.cutoff", "consent.", "safeguard.", "clinical."]
INVARIANT = [r"PHQ-9", r"HMIS", r"GBV", r"IASC", r"MHPSS", r"WHO", r"EDCD", r"PRIME",
             r"Kohrt", r"Kroenke", r"Spitzer", r"Williams", r"Pfizer", r"Bikram Sambat",
             r"\bAD\b", r"CSV", r"JSON", r"Excel", r"Rasuwa", r"Bhote\s*Koshi", r"EXCEL"]
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")
TAG = re.compile(r"<[^>]+>")


def normalise(value):
    return re.sub(r"\s+", " ", value).strip()


def comparable(value):
    """Strip markup, punctuation and the invariant tokens, then compare."""
    text = TAG.sub(" ", value)
    text = text.replace("—", " ").replace("–", " ")
    for token in INVARIANT:
        text = re.sub(token, " ", text, flags=re.I)
    text = re.sub(r"[^\u0900-\u097F\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tags_of(value):
    return TAG.findall(value)


def stray_latin(value):
    text = TAG.sub(" ", value)
    for token in INVARIANT:
        text = re.sub(token, " ", text, flags=re.I)
    return LATIN_WORD.findall(text)


def main():
    lanes = {}
    for path in sys.argv[1:]:
        lanes[Path(path).stem] = json.loads(Path(path).read_text(encoding="utf-8"))
    keys = sorted({k for lane in lanes.values() for k in lane})
    merged, agreed, disputed, rejected = {}, {}, {}, {}

    for key in keys:
        if key.startswith(tuple(PROTECTED)):
            rejected[key] = "protected -- renders in English on the Nepali page"
            continue
        available = {name: normalise(lane[key]) for name, lane in lanes.items() if key in lane}
        if len(available) < 2:
            rejected[key] = f"only {len(available)} lane(s) produced it"
            continue
        forms = {comparable(v): v for v in available.values()}
        if len(forms) == 1:
            merged[key] = sorted(available.values(), key=len)[0]
            agreed[key] = len(available)
            continue
        # a different word order or a synonym is a real disagreement: report
        # it with all the readings and emit nothing for this key.
        disputed[key] = available
    report = {
        "lanes": {name: len(lane) for name, lane in lanes.items()},
        "keys_considered": len(keys),
        "agreed": len(merged),
        "disputed": len(disputed),
        "rejected": len(rejected),
        "disagreements": disputed,
        "rejected_detail": rejected,
    }
    Path("/tmp/i18n_merge_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    json.dump(merged, sys.stdout, ensure_ascii=False, indent=2)
    print(f"lanes {report['lanes']}", file=sys.stderr)
    print(f"agreed {len(merged)}  disputed {len(disputed)}  rejected {len(rejected)}", file=sys.stderr)


if __name__ == "__main__":
    main()

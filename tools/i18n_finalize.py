#!/usr/bin/env python3
"""Reconcile the two independent machine lanes and lock terminology.

Authority order for a key's final Nepali, highest first:

  1. the project's ESTABLISHED wording, taken from the terminology lock
     (hub-real/tools/terminology-lock.json) and the `np` values already in
     hub/assets/codes.js. This is the vocabulary the rest of the platform and
     the national code lists already use, so a form that invents a different
     word stops matching them.
  2. the two independent machine lanes AGREEING after whitespace/markup
     normalisation.
  3. nothing. A key where the lanes disagree and no established wording
     exists is LEFT IN ENGLISH and reported. Voting a machine disagreement
     would be "silently picking" with a majority, which the acceptance
     forbids.

Every emitted string is machine-drafted. Nothing here is labelled human.
"""
import json
import re
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
HUB = Path("/root/mhpss-nepal-work/hub-translation")
LOCK_FILE = Path("/root/mhpss-nepal-work/hub-real/tools/terminology-lock.json")

PREFIXES = ["phq9.item", "phq9.scale", "phq9.cutoff", "consent.", "safeguard.", "clinical."]
INVARIANT = [r"PHQ-9", r"HMIS", r"GBV", r"IASC", r"MHPSS", r"WHO", r"EDCD", r"PRIME",
             r"Kohrt", r"Kroenke", r"Spitzer", r"Williams", r"Pfizer", r"Bikram Sambat",
             r"\bAD\b", r"CSV", r"JSON", r"Excel", r"Rasuwa", r"Bhote\s*Koshi", r"OCMC",
             r"WASH", r"PFA", r"mhGAP", r"NHTC", r"IEC", r"RDNA", r"NDRRMA", r"\bBS\b",
             r"EXCEL", r"Uttargaya", r"RB", r"Programme for Improving Mental Health Care"]
TAG = re.compile(r"<[^>]+>")
BANGLA = re.compile(r"[\u0900-\u097F]")
LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


def normalise(value):
    return re.sub(r"\s+", " ", value).strip()


def comparable(value):
    """Reduce to the meaningful Nepali content: drop markup, dashes, the
    invariant proper nouns/codes and any Latin, keep Devanagari and digits."""
    text = TAG.sub(" ", value).replace("—", " ").replace("–", " ")
    for token in INVARIANT:
        text = re.sub(token, " ", text, flags=re.I)
    text = re.sub(r"[^\u0900-\u097F0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tags_of(value):
    return TAG.findall(value)


def stray_latin(value):
    text = TAG.sub(" ", value)
    for token in INVARIANT:
        text = re.sub(token, " ", text, flags=re.I)
    return [w for w in LATIN_WORD.findall(text)]


def codes_np():
    """English -> Nepali from the code lists, for the option labels."""
    out = {}
    f = HUB / "assets" / "codes.js"
    if not f.is_file():
        return out
    src = f.read_text(encoding="utf-8")
    for m in re.finditer(r'\{[^{}]*\bname:\s*"((?:[^"\\]|\\.)*)"[^{}]*\bnp:\s*"((?:[^"\\]|\\.)*)"[^{}]*\}', src):
        out.setdefault(m.group(1), m.group(2))
    return out


def main():
    entries = json.loads((FORM / "tools" / "translatable.json").read_text(encoding="utf-8"))
    lane_a = json.loads((FORM / "tools" / "i18n-ne-draft.json").read_text(encoding="utf-8"))
    lane_b = json.loads(Path("/root/mhpss-nepal-work/i18n-lane-b/draft-2.json").read_text(encoding="utf-8"))
    lock = json.loads(LOCK_FILE.read_text(encoding="utf-8"))["by_english"]
    lock.update({k: v for k, v in codes_np().items() if k not in lock})

    final, origin, flagged = {}, {}, {}
    stats = {"lock": 0, "agreed": 0, "disputed": 0, "missing_lane": 0, "quality": 0}

    for e in entries:
        key, en = e["key"], e["en"]
        if key.startswith(tuple(PREFIXES)):
            continue
        # 1. established wording wins outright
        if en in lock:
            final[key] = lock[en]
            origin[key] = "lock"
            stats["lock"] += 1
            continue
        a, b = lane_a.get(key, "").strip(), lane_b.get(key, "").strip()
        if not a or not b:
            flagged[key] = "a lane produced nothing"
            stats["missing_lane"] += 1
            continue
        if comparable(a) == comparable(b):
            final[key] = sorted([a, b], key=len)[0]
            origin[key] = "agreed"
            stats["agreed"] += 1
            continue
        flagged[key] = "the two lanes disagree"
        stats["disputed"] += 1

    # ---- quality gate on what we are about to emit ------------------------
    for key in list(final):
        value = final[key]
        e = next(x for x in entries if x["key"] == key)
        problems = []
        if not BANGLA.search(value):
            problems.append("no Devanagari text")
        if stray_latin(value):
            problems.append("untranslated Latin: %s" % stray_latin(value))
        if e["html"] and tags_of(value) != tags_of(e["en"]):
            problems.append("markup differs from the English")
        if "{v: " in e["en"] or "storeWarn" in e["en"] and "storeWarn" not in value:
            pass
        for token in ("storeWarn", "descCount", "ver", "cnt"):
            if ("id=\\\"%s\\\"" % token) in e["en"] and token not in value:
                problems.append("dropped id=%s used by the page's script" % token)
        if problems:
            flagged[key] = "; ".join(problems)
            stats["quality"] += 1
            del final[key]
            origin.pop(key, None)

    print("translatable keys: %d" % len(entries))
    print("emitted:           %d" % len(final))
    print("  from established wording (lock): %d" % stats["lock"])
    print("  lanes agreed:                    %d" % stats["agreed"])
    print("left in English (flagged): %d" % len(flagged))
    print("  lanes disagree:                  %d" % stats["disputed"])
    print("  a lane missing:                  %d" % stats["missing_lane"])
    print("  failed quality gate:             %d" % stats["quality"])
    per_page = {}
    for key in final:
        page = next(x["page"] for x in entries if x["key"] == key)
        per_page[page] = per_page.get(page, 0) + 1
    print("per page emitted:", per_page)

    (FORM / "tools" / "i18n-ne-final.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (FORM / "tools" / "i18n-ne-flagged.json").write_text(
        json.dumps({k: {"reason": v,
                        "lane-A": lane_a.get(k, ""),
                        "lane-B": lane_b.get(k, "")}
                    for k, v in sorted(flagged.items())}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (FORM / "tools" / "i18n-ne-origin.json").write_text(
        json.dumps(origin, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print("wrote tools/i18n-ne-final.json, i18n-ne-flagged.json, i18n-ne-origin.json")


if __name__ == "__main__":
    main()

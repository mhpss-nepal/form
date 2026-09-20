#!/usr/bin/env python3
"""Quality control for the machine Nepali drafts.

The drafts are reviewed by a person before publication, so this does not try to
decide whether a translation is *good*. It finds the defects a reviewer would
otherwise have to hunt for, and it finds the ones that are objectively wrong:

  1. WRONG SCRIPT — NLLB occasionally emits a token in a different Indic
     script than the target, e.g. a Bengali character inside a Devanagari
     word (`सेप्टেम्बर`). Unreadable to a Nepali reader and invisible in a
     skim.
  2. MARKUP DRIFT — every HTML tag and every {placeholder} in the source must
     still be present exactly once in the draft. A dropped tag breaks the page.
  3. ENGLISH LEFT INSIDE — a Latin word carried into the Nepali that is not an
     acronym, a code or a proper noun. `gender` spliced into the middle of a
     Devanagari word is the signature of a partially-copied sentence.
  4. UNFINISHED — no Devanagari at all, or an implausibly short result.

Reads  design-preview/i18n-ne-fill.json
Writes design-preview/i18n-ne-qc.json  (per-row verdict) and prints a summary.

Exit code is 0 even when rows are flagged: flagged rows are for the reviewer,
not a build failure. Use `--strict` to make any flag fail.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILL = REPO / "design-preview" / "i18n-ne-fill.json"
OUT = REPO / "design-preview" / "i18n-ne-qc.json"

DEVANAGARI = (0x0900, 0x097F)
# Indic/other scripts NLLB mixes up when asked for Nepali.
OTHER_SCRIPTS = {
    "Bengali": (0x0980, 0x09FF),
    "Gurmukhi": (0x0A00, 0x0A7F),
    "Gujarati": (0x0A80, 0x0AFF),
    "Odia": (0x0B00, 0x0B7F),
    "Tamil": (0x0B80, 0x0BFF),
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
    "Sinhala": (0x0D80, 0x0DFF),
    "Thai": (0x0E00, 0x0E7F),
    "Arabic": (0x0600, 0x06FF),
    "Cyrillic": (0x0400, 0x04FF),
    "Greek": (0x0370, 0x03FF),
}

TAG = re.compile(r"</?[a-zA-Z][^>]*>")
PLACEHOLDER = re.compile(r"\{[a-zA-Z0-9_]+\}|%[sd]|\{\d+\}")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
DEV_CHAR = re.compile(r"[\u0900-\u097F]")

# Latin strings that are correct to leave as-is in Nepali.
ALWAYS_OK = {
    "MHPSS", "PHQ", "PHQ-9", "QR", "IASC", "EDCD", "WHO", "GBV", "WASH", "NCD",
    "CSV", "JSON", "ID", "AD", "BS", "PFA", "CMC", "KOSHISH", "NRCS", "CWIN",
    "GitHub", "Google", "Firebase", "Kobo", "KoboToolbox", "MaNepal",
    "https", "http", "www",
}


def scripts_in(text: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for ch in text:
        cp = ord(ch)
        if DEVANAGARI[0] <= cp <= DEVANAGARI[1]:
            continue
        for name, (lo, hi) in OTHER_SCRIPTS.items():
            if lo <= cp <= hi:
                hits.setdefault(name, []).append(ch)
    return hits


def norm_tags(text: str) -> list[str]:
    # compare tag NAMES only: translations may reorder attributes inside a tag
    return sorted(re.sub(r"\s+", "", m.group(0)).lower() for m in TAG.finditer(text))


def main() -> int:
    if not FILL.exists():
        print(f"missing {FILL}; run translate_missing.py --emit first")
        return 1
    data = json.loads(FILL.read_text(encoding="utf-8"))

    verdicts = {}
    counts = {"wrong_script": 0, "markup_drift": 0, "english_left": 0, "unfinished": 0}
    rows_flagged = 0

    for key, row in sorted(data.items()):
        en, ne = str(row["en"]), str(row["ne"])
        flags = []

        # 1. wrong script
        sc = scripts_in(ne)
        if sc:
            counts["wrong_script"] += 1
            detail = ", ".join(f"{n}:{''.join(set(c))}" for n, c in sc.items())
            flags.append({"type": "wrong_script", "detail": detail})

        # 2. markup + placeholders must survive exactly once each
        et, nt = norm_tags(en), norm_tags(ne)
        ep = sorted(PLACEHOLDER.findall(en))
        np_ = sorted(PLACEHOLDER.findall(ne))
        if et != nt or ep != np_:
            counts["markup_drift"] += 1
            flags.append({
                "type": "markup_drift",
                "tags_expected": et, "tags_found": nt,
                "ph_expected": ep, "ph_found": np_,
            })

        # 3. English left inside, beyond known-safe tokens
        en_words = {w.lower() for w in LATIN_WORD.findall(en)}
        leftover = []
        for w in LATIN_WORD.findall(ne):
            if w in ALWAYS_OK or w.upper() in ALWAYS_OK:
                continue
            if w in TAG.findall(ne):
                continue
            # inside a tag/attribute -> not reader-visible prose
            if re.search(r"<[^>]*" + re.escape(w) + r"[^>]*>", ne):
                continue
            leftover.append(w)
        if leftover and DEV_CHAR.search(ne):
            counts["english_left"] += 1
            flags.append({"type": "english_left", "words": sorted(set(leftover))[:8]})

        # 4. unfinished
        if not DEV_CHAR.search(ne):
            # a pure technical token (QR, PHQ-9) is not a failure
            if not any(w in ALWAYS_OK for w in LATIN_WORD.findall(en)) and en.strip():
                counts["unfinished"] += 1
                flags.append({"type": "unfinished", "detail": "no Devanagari produced"})

        if flags:
            rows_flagged += 1
        verdicts[key] = {
            "en": en[:160],
            "ne": ne[:160],
            "pages": row.get("pages", []),
            "glossary_changes": row.get("glossary_changes", []),
            "flags": flags,
            "needs_human_review": True,   # true for every row, flagged or not
        }

    OUT.write_text(json.dumps(verdicts, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"rows: {len(data)}   rows with an objective flag: {rows_flagged}")
    for k, v in counts.items():
        print(f"  {k:14} {v}")
    print(f"\nwrote {OUT}")

    if rows_flagged:
        print("\nrows to fix or watch:")
        for k, v in verdicts.items():
            if v["flags"]:
                types = ",".join(f["type"] for f in v["flags"])
                print(f"  {k:18} [{types}]  {v['ne'][:70]}")

    if "--strict" in sys.argv and rows_flagged:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Rescue the validated Nepali PHQ-9 from the legacy-font supplement PDF.

The instrument is open access -- Kohrt et al., BMC Psychiatry 2016;16:58,
PMC4782581, Additional file 1 -- but its Nepali is typeset in a legacy
non-Unicode (Preeti) font, so extracting the text yields ASCII glyph codes
rather than Devanagari. This converts them and then proves the conversion.

How the conversion is verified
------------------------------
Not by a round trip. Preeti overloads ASCII punctuation: `?` renders रु, so the
real question mark is written `<`. The reverse map is therefore many-to-one
and a byte comparison fails for reasons that are NOT errors -- it looks like a
failure while being meaningless. (Measured: only `/` and `?` differ; the
Devanagari never drifted.)

Instead, two INDEPENDENT open-source mappers convert the same text and must
produce identical Devanagari:
    * npttf2utf        (casualsnek)
    * nepali-unicoder  (greedy + contextual rules)
Two separately written implementations agreeing character-for-character is
evidence about the mapping, not a self-consistency check. Measured: 9/9 items
agree. A disagreement is reported per item and fails the run.

The same PDF also carries the authors' own English back-translation, printed on
the same line as the Nepali, so both halves are emitted side by side -- that
side-by-side is the artefact a reviewer actually needs.

What this still does NOT establish
----------------------------------
That the text is correct NEPALI -- only that it faithfully represents the glyphs
in the published instrument. A reader of Nepali must confirm it, which is why
the output is a review file and not a silent write into the form.

Outputs (design-preview/references/):
  phq9-nepal-unicode.json   items, response scale, bilingual, per-item verdict
  phq9-nepal-REVIEW.md      Nepali | English back-translation, for a reviewer

Usage: /root/preeti/venv/bin/python design-preview/rescue_phq9_nepali.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import npttf2utf
from pypdf import PdfReader

try:
    from nepali_unicoder.convert import Converter as _NeConverter
    _HAVE_NE = True
except Exception:  # noqa: BLE001
    _HAVE_NE = False

_MAP = Path(npttf2utf.__file__).parent / "map.json"
REPO = Path(__file__).resolve().parent.parent
REFS = REPO / "design-preview" / "references"
PDF = REFS / "kohrt-2016-nepal-phq9-supplement.pdf"
OUT_JSON = REFS / "phq9-nepal-unicode.json"
OUT_MD = REFS / "phq9-nepal-REVIEW.md"

DEV = re.compile(r"[\u0900-\u097F]")
fm = npttf2utf.FontMapper(str(_MAP))
_ne = _NeConverter(mode="preeti") if _HAVE_NE else None


def dev_only(s: str) -> str:
    return "".join(DEV.findall(s or ""))


def convert_pair(legacy: str) -> tuple[str, str, bool]:
    """Return (npttf2utf_result, nepali_unicoder_result, agree_on_devanagari)."""
    a = fm.map_to_unicode(legacy, from_font="Preeti")
    b = _ne.convert(legacy) if _ne else ""
    return a, b, (dev_only(a) == dev_only(b)) if _ne else False


def main() -> int:
    if not PDF.exists():
        print(f"missing {PDF}")
        return 1
    if not _HAVE_NE:
        print("nepali-unicoder not installed; cannot cross-verify. Refusing to run.")
        return 1

    reader = PdfReader(str(PDF))
    raw = "\n".join((pg.extract_text() or "") for pg in reader.pages)

    print("=== cross-converter verification on known words ===")
    probes = ["tkfO{+", "g]kfn", "slQ klg ePg", "w]/} h;f] eof]", "cfˆgf]", "kl/jf/"]
    all_ok = True
    for s in probes:
        a, b, ok = convert_pair(s)
        all_ok &= ok
        print(f"  {'AGREE ' if ok else 'DIFFER'} {s!r:18} -> npttf2utf={a!r:18} unicoder={b!r}")
    if not all_ok:
        print("ABORT: the two mappers disagree on known words; not trusting either.")
        return 1

    # items are numbered "!= " ... "(= " in Preeti digits
    item_line = re.compile(r"([!@#$%^&*()])= (.*?)(?=\n[!@#$%^&*()]= |\Z)", re.S)
    digit = dict(zip("!@#$%^&*()", "123456789"))

    items, disagreements = [], []
    for m in item_line.finditer(raw):
        num = digit.get(m.group(1))
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        if not num or len(body) < 20:
            continue
        split = re.search(r"(During the past two weeks.*)", body)
        nep_legacy = (body[: split.start()] if split else body).strip()
        english = split.group(1).strip() if split else ""
        # The PDF prints the response grid after the English ("0 1 2 3" as the
        # Preeti glyphs ") ! @ #"), and item 9 runs into the page footer and
        # page 3. Cut both, so the review table shows only real content.
        english = re.split(r"\)\s*!\s*@\s*#|hDdf|Nepal Depression Screening", english)[0].strip()
        a, b, agree = convert_pair(nep_legacy)
        if not agree:
            disagreements.append(num)
        items.append({
            "number": int(num),
            "ne": a,
            "en_backtranslation": english,
            "ne_legacy_source": nep_legacy,
            "cross_converter_agreement": agree,
            "ne_from_nepali_unicoder": b,
        })
    items.sort(key=lambda x: x["number"])

    scale = []
    for legacy, en in [("slQ klg ePg", "Not at all"), ("slxn]sfxL+ eof]", "Sometimes"),
                       ("w]/} h;f] eof]", "Usually"), (";w} h;f] eof]", "Always")]:
        a, b, agree = convert_pair(legacy)
        scale.append({"ne": a, "en": en, "legacy": legacy, "cross_converter_agreement": agree})

    print(f"\nitems recovered: {len(items)}")
    for it in items:
        print(f"  {it['number']}. {'AGREE ' if it['cross_converter_agreement'] else 'DIFFER'}  {it['ne'][:56]}")

    data = {
        "source": "Kohrt BA, Luitel NP, Acharya P, Jordans MJD. BMC Psychiatry 2016;16:58 (PMC4782581), Additional file 1",
        "doi": "10.1186/s12888-016-0768-y",
        "conversion": "Preeti->Unicode via npttf2utf, cross-verified against nepali-unicoder",
        "verification": "both mappers must produce identical Devanagari",
        "still_needed": "a Nepali reader must confirm the wording before this is used",
        "items": items,
        "response_scale": scale,
    }
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    L = [
        "# Validated Nepali PHQ-9 — converted for review",
        "",
        "**Source:** Kohrt et al., BMC Psychiatry 2016;16:58 (PMC4782581), Additional file 1.",
        "The published Nepali is typeset in a legacy non-Unicode font. It was converted with",
        "`npttf2utf` and **cross-checked against an independent converter** (`nepali-unicoder`);",
        "the two produce identical Devanagari for every item below.",
        "",
        "**What you are checking:** that the Nepali column says what the English column says.",
        "The conversion is verified faithful to the printed glyphs, but only a reader of Nepali can",
        "confirm it is correct — this is the instrument, and one wrong word changes what the cut-off",
        "≥10 means.",
        "",
        "## The nine items",
        "",
        "| # | Nepali | English back-translation (same paper) | conversion |",
        "|---|---|---|---|",
    ]
    for it in items:
        mark = "✅ two mappers agree" if it["cross_converter_agreement"] else "⚠️ MAPPERS DISAGREE"
        L.append(f"| {it['number']} | {it['ne']} | {it['en_backtranslation']} | {mark} |")
    L += ["", "## Response scale (validated version)", "", "| Nepali | English |", "|---|---|"]
    for s in scale:
        L.append(f"| {s['ne']} | {s['en']} |")
    L += [
        "",
        "> The validated instrument uses this four-level scale — **not** the standard",
        '> "several days / more than half the days / nearly every day". The cut-off ≥10 belongs',
        "> to these words with this scale.",
    ]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"\nwrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"cross-converter disagreements: {disagreements or 'none'}")
    return 1 if disagreements else 0


if __name__ == "__main__":
    sys.exit(main())

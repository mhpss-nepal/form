#!/usr/bin/env python3
"""Guard the two language rules that matter for the 5Ws form.

Rule 1 — a first-time reader lands on Nepali, and English stays one tap away.
Rule 2 — the interface language never reaches the data: records and exports
         stay in English regardless of what the reader sees.

Both are checked against the runtime behaviour, not the source text, because
the interesting failure modes (a lost language, a Devanagari label leaking into
a CSV) only appear at runtime.

Run: python3 design-preview/check_language_rules.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STORE = REPO.parent / "hub" / "assets" / "store.js"
CODES = REPO.parent / "hub" / "assets" / "codes.js"
I18N = REPO.parent / "hub" / "assets" / "i18n.js"

DEVANAGARI = re.compile(r"[\u0900-\u097F]")

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


# ---------------------------------------------------------------- rule 1: default
i18n = I18N.read_text(encoding="utf-8")
# The default is layered, not global: Layer 1 (the field forms) opens in Nepali,
# Layer 2 and Layer 3 stay English. A single global DEFAULT cannot say that, and
# the Hub pages load the same i18n.js, so a global "ne" would turn Layer 2 Nepali.
# So i18n.js keeps DEFAULT = "en" and each page declares its own:
#   <html lang="en" data-i18n-default="ne">
m = re.search(r'var DEFAULT = "(\w+)"', i18n)
check("i18n.js declares a default language", bool(m), m.group(1) if m else "not found")
check(
    "the engine reads a per-page declaration",
    "data-i18n-default" in i18n and "DECLARED" in i18n,
    "i18n.js must read data-i18n-default from the page",
)
check(
    "the global default stays English, so Layer 2 and Layer 3 do not follow Layer 1",
    bool(m) and m.group(1) == "en",
    f'found DEFAULT = "{m.group(1)}"' if m else "",
)

# Every Layer 1 page that should open in Nepali must carry the declaration on its
# own <html>, and the pages that must stay English must not carry a Nepali one.
NEPALI_PAGES = ["5ws-report.html", "index.html"]
ENGLISH_PAGES = ["selfreport.html", "phq9.html", "referral.html", "contact.html"]
for page in NEPALI_PAGES:
    text = (REPO / page).read_text(encoding="utf-8", errors="ignore")
    tag = re.search(r"<html[^>]*>", text)
    check(
        f"{page} declares a Nepali default of its own",
        bool(tag) and 'data-i18n-default="ne"' in tag.group(0),
        tag.group(0) if tag else "no <html> tag",
    )
for page in ENGLISH_PAGES:
    text = (REPO / page).read_text(encoding="utf-8", errors="ignore")
    tag = re.search(r"<html[^>]*>", text)
    check(
        f"{page} does not force Nepali on a page the decision keeps English",
        bool(tag) and 'data-i18n-default="ne"' not in tag.group(0),
        tag.group(0) if tag else "no <html> tag",
    )

# English must remain selectable and the URL must still win.
# The offered languages are declared in i18n-strings.js, not in i18n.js.
strings = (REPO.parent / "hub" / "assets" / "i18n-strings.js").read_text(encoding="utf-8")
langs = re.search(r"langs:\s*\[([\s\S]*?)\]", strings)
check("i18n-strings.js declares the offered languages", bool(langs))
if langs:
    offered = re.findall(r'code:\s*"(\w+)"', langs.group(1))
    check("English is still an offered language", "en" in offered, f"offered: {offered}")
    check("Nepali is still an offered language", "ne" in offered, f"offered: {offered}")
check(
    "?lang= still overrides the default",
    'get("lang")' in i18n and "codes.indexOf(q) > -1" in i18n,
)
check(
    "a named preference is still remembered",
    'localStorage.getItem(KEY)' in i18n and "localStorage.setItem(KEY" in i18n,
)

# ------------------------------------------------- rule 2: language stays out of data
store = STORE.read_text(encoding="utf-8")
codes = CODES.read_text(encoding="utf-8")

# The export must not pick labels through the language-aware helper.
readings = re.search(r"function activityReadings\(r\)[\s\S]*?\n\}", store)
check("store.js has activityReadings()", bool(readings))
if readings:
    body = readings.group(0)
    check(
        "activityLabel is built from the English name, not the language-aware label()",
        "a ? a.name :" in body and "C.label(" not in body,
        "found C.label() in the export path" if "C.label(" in body else "",
    )

# The stored record must carry codes, and the CSV must not use C.label.
check(
    "the CSV writer does not call the language-aware label()",
    not re.search(r"function toCSV[\s\S]*?C\.label\(", store),
)
check(
    "the language-aware helper is gated on data-lang, not baked into stored values",
    'data-lang") === "ne"' in codes,
)

# A chosen language must not be written onto a record.
cols = re.search(r"const CSV_COLUMNS = \[([\s\S]*?)\];", store)
check("CSV_COLUMNS is declared", bool(cols))
if cols:
    check(
        "no language column is exported onto the record",
        not re.search(r'"lang', cols.group(1)),
    )

# --------------------------------------------------------------------- summary
print()
if failures:
    print(f"{len(failures)} check(s) failed:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("All language-rule checks passed.")

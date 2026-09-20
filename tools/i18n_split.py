#!/usr/bin/env python3
"""Split the extracted keys into the translatable set and the protected set.

Protected = a key under one of the professionalOnly prefixes. Those render in
English on the Nepali page by design, so they get no Nepali entry at all.

Writes tools/translatable.json (key, en, html, page) and
tools/protected.json, and prints the counts the acceptance asks for.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ["phq9.item", "phq9.scale", "phq9.cutoff", "consent.", "safeguard.", "clinical."]


def main():
    entries = json.loads((ROOT / "tools" / "new-i18n-entries.json").read_text(encoding="utf-8"))
    protected = [e for e in entries if e["key"].startswith(tuple(PREFIXES))]
    translatable = [e for e in entries if e not in protected]
    (ROOT / "tools" / "translatable.json").write_text(
        json.dumps(translatable, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "tools" / "protected.json").write_text(
        json.dumps(protected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"keys total {len(entries)}  translatable {len(translatable)}  protected {len(protected)}")
    per_page = {}
    for entry in translatable:
        per_page[entry["page"]] = per_page.get(entry["page"], 0) + 1
    for page, count in sorted(per_page.items()):
        print(f"  {page}: {count} translatable")
    matches = {}
    for prefix in PREFIXES:
        matches[prefix] = sum(1 for e in entries if e["key"].startswith(prefix))
    print("professionalOnly prefixes that match live keys:")
    for prefix in PREFIXES:
        print(f"  {prefix:<16} {matches[prefix]}")
    print(f"  live prefixes {sum(1 for v in matches.values() if v)} of {len(PREFIXES)}, "
          f"{len(protected)} keys held in English")


if __name__ == "__main__":
    main()

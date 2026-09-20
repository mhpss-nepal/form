#!/usr/bin/env python3
"""Add the newly-extracted keys (phq9.item9Instruction) to the hub dictionary."""
import json
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
OUT = Path("/root/mhpss-nepal-work/i18n-apply-input")
OUT.mkdir(exist_ok=True)

entries = json.loads((FORM / "tools" / "new-i18n-entries.json").read_text(encoding="utf-8"))
final = json.loads((FORM / "tools" / "i18n-ne-final.json").read_text(encoding="utf-8"))
(OUT / "en.json").write_text(
    json.dumps([{"key": e["key"], "en": e["en"]} for e in entries], ensure_ascii=False, indent=2),
    encoding="utf-8")
(OUT / "ne.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
print("en offered:", len(entries), " (protected:", sum(
    1 for e in entries if e["key"].startswith(("phq9.item", "phq9.scale", "phq9.cutoff",
                                               "consent.", "safeguard.", "clinical."))), ")")
print("ne drafts:", len(final))
print("item9Instruction en:", next(e["en"] for e in entries
                                   if e["key"] == "phq9.item9Instruction")[:120])

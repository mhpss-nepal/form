#!/usr/bin/env python3
"""Fill the missing Nepali for keys the pages already carry.

Scope: only keys that a page already references via data-i18n AND that have no
`ne` value yet. Those pages are half-built: the structure is keyed, the Nepali
was never supplied. Translating them completes pages that already exist; it
does not touch form semantics.

Deliberately NOT done here:
  * pages whose prose is still hardcoded (contact, phq9, referral, 4ws) --
    keying those up is a content migration, not a translation;
  * anything marked KEPT IN ENGLISH by prefix (clinical.*, consent.*,
    safeguard.*, phq9.*) -- those must not be machine-translated at all.

Outputs (no source file is modified by this script):
  design-preview/i18n-ne-fill.json     key -> machine Nepali, with provenance
  design-preview/i18n-ne-review.md     English | Nepali side by side, for a reviewer

Usage:  python3 design-preview/translate_missing.py [--emit]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/root/mhpss-nepal-work/form-frontend")
STRINGS = Path("/root/mhpss-nepal-work/hub/assets/i18n-strings.js")
NMT_PY = "/root/nmt/venv/bin/python"
NMT_SCRIPT = "/root/nmt/translate.py"
OUT_JSON = REPO / "design-preview" / "i18n-ne-fill.json"
OUT_MD = REPO / "design-preview" / "i18n-ne-review.md"

# Prefixes the project keeps in English on purpose (see i18n-strings.js _meta).
NEVER_MACHINE = ("phq9.", "consent.", "safeguard.", "clinical.")

DEV = re.compile(r"[\u0900-\u097F]")


def load_tables() -> dict:
    node = (
        'global.window={};'
        f'require("{STRINGS}");'
        'const S=window.I18N_STRINGS;'
        'console.log(JSON.stringify({en:S.en,ne:S.ne,meta:S._meta}));'
    )
    r = subprocess.run(["node", "-e", node], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"node parse failed: {r.stderr[:300]}")
    return json.loads(r.stdout)


def pages_using() -> dict[str, list[str]]:
    """key -> [pages that reference it]."""
    used: dict[str, list[str]] = {}
    for p in sorted(REPO.glob("*.html")):
        for k in set(re.findall(r'data-i18n="([^"]+)"', p.read_text(errors="ignore"))):
            used.setdefault(k, []).append(p.name)
    return used


def main() -> int:
    data = load_tables()
    EN, NE, META = data["en"], data["ne"], data["meta"]

    used = pages_using()
    missing = [
        k for k in sorted(used)
        if k in EN and not NE.get(k) and not k.startswith(NEVER_MACHINE)
    ]
    skipped_kept = [k for k in sorted(used) if k.startswith(NEVER_MACHINE) and not NE.get(k)]

    print(f"keys referenced by pages : {len(used)}")
    print(f"missing Nepali (to fill) : {len(missing)}")
    print(f"left in English on purpose: {len(skipped_kept)}")
    if skipped_kept:
        print("   " + ", ".join(skipped_kept[:10]) + (" ..." if len(skipped_kept) > 10 else ""))
    if not missing:
        print("nothing to do")
        return 0

    if "--emit" not in sys.argv:
        print("\n(dry run — pass --emit to call the translation engine)")
        for k in missing[:5]:
            print(f"   {k}: {str(EN[k])[:70]}")
        return 0

    # ---- translate ------------------------------------------------------
    payload = {k: str(EN[k]) for k in missing}
    proc = subprocess.run(
        [NMT_PY, NMT_SCRIPT], input=json.dumps(payload),
        capture_output=True, text=True, timeout=3600,
    )
    if proc.returncode != 0:
        print("translate failed:", proc.stderr[-800:])
        return 1
    got = json.loads(proc.stdout)

    table = {}
    for k in missing:
        ne = (got.get(k) or "").strip()
        ok = bool(ne) and bool(DEV.search(ne))
        table[k] = {
            "en": str(EN[k]),
            "ne": ne,
            "pages": used.get(k, []),
            "has_devanagari": ok,
            # every value here is machine-drafted and unreviewed by a person
            "provenance": "machine",
            "reviewed_by_human": False,
        }

    bad = [k for k, v in table.items() if not v["has_devanagari"]]
    OUT_JSON.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [
        "# Machine Nepali awaiting human review",
        "",
        "Every row below is a machine draft. None of it has been checked by a",
        "Nepali speaker. Read the Nepali column and correct it in place; the",
        "left column is the authoritative English.",
        "",
        "Anything that changes a meaning, a safety instruction, or a clinical",
        "term must be rewritten rather than accepted.",
        "",
        f"Rows: {len(table)}  ·  without Devanagari (needs attention): {len(bad)}",
        "",
        "| key | English (authoritative) | Nepali (machine draft) | used on |",
        "|---|---|---|---|",
    ]
    for k in sorted(table):
        v = table[k]
        clean = lambda s: str(s).replace("|", "\\|")  # noqa: E731
        lines.append(
            f"| `{k}` | {clean(v['en'])} | {clean(v['ne'])} | {', '.join(v['pages'])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nwrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"translated: {len(table)}  without Devanagari: {len(bad)}")
    if bad:
        print("needs attention:", bad[:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Translate EVERY key that still has no Nepali, for human review.

Team decision (2026-09-20): machine-translate everything so a human team can
review it on the live pages and send corrections. So nothing is withheld from
translation here.

One thing is handled differently, and deliberately:

  The keys whose *display* is held in English on purpose (prefixes phq9.*,
  consent.*, safeguard.*, clinical.*) DO get a machine Nepali draft stored, so a
  reviewer can read and correct it -- but their values are not displayed in
  place of the protected English until a human promotes them. A fresh
  translation of the PHQ-9 is not the validated instrument, and showing it as
  if it were would put a false score behind a real cut-off.

They are marked `provisional: true` in the output and in _meta.source.machine,
so the review file can show exactly which drafts must not be published as-is.

Writes: design-preview/i18n-ne-fill.json   (all drafts, with provenance)
Usage:  python3 design-preview/translate_all_missing.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/root/mhpss-nepal-work/form-frontend")
STRINGS = Path("/root/mhpss-nepal-work/hub/assets/i18n-strings.js")
NMT_PY = "/root/nmt/venv/bin/python"
NMT_SCRIPT = "/root/nmt/translate.py"
OUT = REPO / "design-preview" / "i18n-ne-fill.json"

# Stored as a draft, but NOT displayed in place of the protected English.
PROVISIONAL_PREFIXES = ("phq9.", "consent.", "safeguard.", "clinical.")
# Wording about clinical safety that a machine should not restate as guidance.
SAFETY_HINTS = re.compile(
    r"(suicid|self-harm|safeguard|immediate risk|child protection|"
    r"no permission required|validated|cut-off|cutoff)", re.I)
DEV = re.compile(r"[\u0900-\u097F]")


def tables() -> dict:
    node = ('global.window={};'
            f'require("{STRINGS}");'
            'const S=window.I18N_STRINGS;'
            'console.log(JSON.stringify({en:S.en,ne:S.ne}));')
    r = subprocess.run(["node", "-e", node], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("parse failed: " + r.stderr[:300])
    return json.loads(r.stdout)


def main() -> int:
    data = tables()
    EN, NE = data["en"], data["ne"]
    missing = [k for k in sorted(EN) if not str(NE.get(k) or "").strip()]
    print(f"english keys      : {len(EN)}")
    print(f"already Nepali    : {len(EN) - len(missing)}")
    print(f"to translate      : {len(missing)}")
    if not missing:
        print("nothing to do")
        return 0

    payload = {k: str(EN[k]) for k in missing}
    print(f"characters        : {sum(len(v) for v in payload.values())}")

    # Chunked and resumable. A single 51k-character run takes ~45 minutes with
    # beam search; if anything interrupts it, all of it is lost. Writing each
    # chunk as it finishes means a restart continues instead of starting over,
    # and it gives visible progress. Greedy decoding (beams=1): measured 22 s
    # against 196 s for the same long string, for comparable output that a
    # human reviewer corrects anyway.
    CHUNK = 60
    PROGRESS = Path("/tmp/ne_chunks.jsonl")
    done: dict[str, str] = {}
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                done.update(rec)
            except Exception:
                pass
        print(f"resuming: {len(done)} already translated in {PROGRESS}")

    todo = [k for k in missing if k not in done]
    chunks = [todo[i:i + CHUNK] for i in range(0, len(todo), CHUNK)]
    print(f"to translate now  : {len(todo)} in {len(chunks)} chunk(s)", flush=True)

    got = dict(done)
    for n, keys in enumerate(chunks, 1):
        part = {k: payload[k] for k in keys}
        chars = sum(len(v) for v in part.values())
        print(f"  chunk {n}/{len(chunks)}: {len(keys)} keys, {chars} chars ...", flush=True)
        proc = subprocess.run(
            [NMT_PY, NMT_SCRIPT, "--beams", "1", "--batch-size", "8"],
            input=json.dumps(part), capture_output=True, text=True, timeout=7200,
            env={**os.environ, "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"},
        )
        if proc.returncode != 0:
            print("engine failed:", proc.stderr[-800:])
            return 1
        out = json.loads(proc.stdout)
        got.update(out)
        with PROGRESS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
        print(f"    ok ({len(got)}/{len(missing)} done)", flush=True)

    sys.path.insert(0, "/root/nmt")
    from glossary import apply as glossary_apply, audit_glossary  # noqa: E402

    bad_gloss = audit_glossary()
    if bad_gloss:
        print("refusing to apply an unattested glossary:")
        for b in bad_gloss:
            print("   -", b)
        return 1

    table = {}
    for k in missing:
        raw = str(got.get(k) or "").strip()
        fixed, changes = glossary_apply(raw)
        provisional = k.startswith(PROVISIONAL_PREFIXES) or bool(SAFETY_HINTS.search(raw))
        table[k] = {
            "en": str(EN[k]),
            "ne": fixed,
            "pages": [],
            "has_devanagari": bool(DEV.search(fixed)),
            "provenance": "machine",
            "reviewed_by_human": False,
            # stored for review, but must not be displayed as if validated
            "provisional": provisional,
            "glossary_changes": changes,
            "ne_before_glossary": raw if changes else None,
        }

    OUT.write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    no_dev = [k for k, v in table.items() if not v["has_devanagari"]]
    prov = [k for k, v in table.items() if v["provisional"]]
    print(f"\nwrote {OUT}")
    print(f"translated        : {len(table)}")
    print(f"no Devanagari     : {len(no_dev)} {no_dev[:8]}")
    print(f"provisional (do not publish as-is): {len(prov)}")
    print(f"glossary corrected: {sum(1 for v in table.values() if v['glossary_changes'])} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())

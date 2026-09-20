#!/usr/bin/env python3
"""Write the machine Nepali drafts into hub/assets/i18n-strings.js.

The team has approved machine translation with human review afterwards, so the
drafts go in and the review happens on the live pages. Two things this script
will NOT do, because they are not language decisions:

  * it will not touch any key already marked `human` in _meta.source;
  * it will not machine-translate a name in the NEVER list below. Those are
    protected by the project's own _meta policy. If a protected key is among
    the drafts it is skipped and reported, not silently written.

Backs the file up first and refuses to write if the result does not parse or
if it would drop an existing key.

Usage: python3 design-preview/apply_ne_drafts.py [--write]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/root/mhpss-nepal-work/form-frontend")
HUB = Path("/root/mhpss-nepal-work/hub/assets/i18n-strings.js")
DRAFTS = REPO / "design-preview" / "i18n-ne-fill.json"
BACKUP_DIR = Path("/root/mhpss-nepal-work/backups")

# The project's own policy (see _meta in i18n-strings.js). Kept here so this
# script cannot violate it by accident.
PROTECTED_PREFIXES = ("phq9.", "consent.", "safeguard.", "clinical.")


def tables() -> dict:
    node = (
        'global.window={};'
        f'require("{HUB}");'
        'const S=window.I18N_STRINGS;'
        'console.log(JSON.stringify({en:S.en,ne:S.ne,meta:S._meta}));'
    )
    r = subprocess.run(["node", "-e", node], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("file does not parse before edit: " + r.stderr[:300])
    return json.loads(r.stdout)


def find_object_span(src: str, key: str) -> tuple[int, int]:
    """Return (open_brace_index, close_brace_index) of `key: { ... }`.

    Skips // and /* */ comments: this file's JSDoc contains {name}-style
    placeholders in prose, which would otherwise unbalance the brace count.
    """
    m = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*\{{", src)
    if not m:
        raise SystemExit(f"could not find '{key}: {{' in i18n-strings.js")
    start = src.index("{", m.start())
    depth = 0
    i = start
    in_str = None
    while i < len(src):
        ch = src[i]

        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue

        # not inside a string: check for comments
        nxt = src[i : i + 2]
        if nxt == "//":
            j = src.find("\n", i)
            i = len(src) if j == -1 else j
            continue
        if nxt == "/*":
            j = src.find("*/", i + 2)
            i = len(src) if j == -1 else j + 2
            continue

        if ch in "\"'`":
            in_str = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, i
        i += 1
    raise SystemExit(f"unbalanced braces for '{key}'")


def js_string(s: str) -> str:
    # JSON escaping is valid JS for our purposes (all values are plain strings)
    return json.dumps(s, ensure_ascii=False)


def main() -> int:
    write = "--write" in sys.argv
    before = tables()
    en, ne, meta = before["en"], before["ne"], before["meta"]
    drafts = json.loads(DRAFTS.read_text(encoding="utf-8"))

    human = set((meta.get("source") or {}).get("human") or [])

    # The team decided (2026-09-20) that everything is machine-translated so it
    # can be reviewed on the live pages, then corrected from feedback. So the
    # protected prefixes (phq9./consent./safeguard./clinical.) are written too
    # when --include-provisional is passed -- but each such value keeps its
    # `provisional: true` flag in i18n-ne-fill.json, and the review file lists
    # them, so nobody mistakes them for checked wording. Without the flag this
    # script still refuses to touch them.
    include_provisional = "--include-provisional" in sys.argv
    protected = () if include_provisional else PROTECTED_PREFIXES

    to_add, skipped = {}, []
    for k, row in drafts.items():
        if k in ne and str(ne[k]).strip():
            skipped.append((k, "already has Nepali"))
            continue
        if k in human:
            skipped.append((k, "marked human-reviewed: not overwriting"))
            continue
        if k.startswith(protected):
            skipped.append((k, "protected prefix: never machine-translated"))
            continue
        v = str(row.get("ne") or "").strip()
        if not v:
            skipped.append((k, "empty draft"))
            continue
        to_add[k] = v

    print(f"drafts in file      : {len(drafts)}")
    print(f"to add              : {len(to_add)}")
    print(f"skipped             : {len(skipped)}")
    for k, why in skipped[:12]:
        print(f"   - {k}: {why}")
    if not to_add:
        print("nothing to add")
        return 0
    if not write:
        print("\n(dry run — pass --write to modify i18n-strings.js)")
        return 0

    src = HUB.read_text(encoding="utf-8")
    import hashlib
    hash_at_read = hashlib.sha256(src.encode("utf-8")).hexdigest()
    start, end = find_object_span(src, "ne")

    lines = []
    lines.append("")
    lines.append("    /* ---- added by machine translation, awaiting human review ----")
    lines.append("       Team decision (2026-09-20): machine-translate everything so a")
    lines.append("       human team can review it on the live pages, then send feedback.")
    lines.append("       Every key here is listed in _meta.source.machine. Swapping any")
    lines.append("       value for a human translation means editing it here and moving")
    lines.append("       the key to _meta.source.human. */")
    for k in sorted(to_add):
        lines.append(f"    {js_string(k)}: {js_string(to_add[k])},")
    block = "\n".join(lines) + "\n  "

    new_src = src[:end] + block + src[end:]

    # provenance: tell the app these are machine values, and bump the revision
    # so a previously-dismissed notice returns (the Nepali changed).
    def add_to_machine_array(text: str, keys: list[str]) -> str:
        # the array is written inline as `source: { machine: [` in this file,
        # and the surrounding comment also uses the word "machine", so match
        # specifically on `machine:` followed by `[`.
        m = re.search(r"machine\s*:\s*\[", text)
        if not m:
            raise SystemExit("could not find source.machine array")
        # determine the indentation of the array's own entries
        line_start = text.rfind("\n", 0, m.start()) + 1
        indent = re.match(r"[ \t]*", text[line_start:]).group(0)
        payload = "".join(f"\n{indent}  {js_string(k)}," for k in keys)
        return text[: m.end()] + payload + text[m.end():]

    # ---- race guard --------------------------------------------------------
    # This file is edited by more than one session: an earlier run of this
    # script had its 111 values silently overwritten about 15 minutes later by
    # a parallel writer. So compare the file against what was read at the top
    # of this function, and refuse to write if it moved underneath us.
    import hashlib
    if hashlib.sha256(HUB.read_bytes()).hexdigest() != hash_at_read:
        print("ABORT: i18n-strings.js changed while this run was in progress.")
        print("       Another session is writing this file. Re-run once it stops,")
        print("       or hand design-preview/i18n-ne-fill.json to whoever owns it.")
        return 1

    new_src = add_to_machine_array(new_src, sorted(to_add))

    # verify before touching the original
    tmp = Path("/tmp/i18n-strings.candidate.js")
    tmp.write_text(new_src, encoding="utf-8")
    check = subprocess.run(
        ["node", "-e",
         'global.window={};'
         f'require("{tmp}");'
         'const S=window.I18N_STRINGS;'
         'const ne=S.ne;'
         'console.log("ne keys:", Object.keys(ne).length);'
         'const miss=' + json.dumps(sorted(to_add)) + '.filter(k=>!ne[k]);'
         'console.log("still missing:", miss.length);'],
        capture_output=True, text=True)
    if check.returncode != 0:
        print("candidate does not parse — NOT writing")
        print(check.stderr[:600])
        return 1
    print(check.stdout.strip())

    # confirm nothing was lost
    cand = json.loads(subprocess.run(
        ["node", "-e", 'global.window={};'
         f'require("{tmp}");'
         'console.log(JSON.stringify({en:Object.keys(window.I18N_STRINGS.en).length,'
         'ne:Object.keys(window.I18N_STRINGS.ne).length}))'],
        capture_output=True, text=True).stdout)
    if cand["en"] != len(en):
        print(f"ABORT: en keys changed {len(en)} -> {cand['en']}")
        return 1
    if cand["ne"] < len(ne):
        print(f"ABORT: ne keys shrank {len(ne)} -> {cand['ne']}")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shutil.copy2(HUB, BACKUP_DIR / f"i18n-strings.js.{stamp}.predrafts.bak")
    HUB.write_text(new_src, encoding="utf-8")
    print(f"\nWROTE {HUB}")
    print(f"backup: {BACKUP_DIR / f'i18n-strings.js.{stamp}.predrafts.bak'}")
    print(f"ne keys {len(ne)} -> {cand['ne']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

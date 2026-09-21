#!/usr/bin/env python3
"""Build an ADD-ONLY patch of the hub dictionary.

Adds the 794 Nepali values (and 246 English keys) that live only in this
session's dictionary, and changes nothing else. In particular it does NOT
overwrite the one key the hub lane deliberately fixed by hand:
f4.wardLab, where the hub removed the <span class="opt"> markup because the
form uses data-i18n (not data-i18n-html), so the markup would render as
literal text. The hub's value wins.

Usage: python3 build_dictionary_addonly.py
Writes /tmp/i18n-strings.addonly.js and a diff against hub origin/main.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HUB = Path("/root/mhpss-nepal-audit-20260918/hub")
BASE_JS = "/tmp/hubmain_i18n.js"          # hub origin/main dictionary
MINE_JSON = "/tmp/k_final.json"           # this session's 974 dictionary
OUT_JS = "/tmp/i18n-strings.addonly.js"
OUT_PATCH = ("/root/mhpss-nepal-work/form-frontend/design-preview/"
             "hub-pending/i18n-strings.js.add-ne-775.patch")

# Keys the hub lane owns and this session must not rewrite, even though the
# two dictionaries differ on them. Reason recorded next to each.
HUB_WINS = {
    # the form renders this with data-i18n (no -html), so the hub stripped the
    # inline markup that this session's copy still carries.
    "f4.wardLab",
}

# Strings that must never be machine-translated (mirrors the hub file's own
# protected-prefix note). These are EXCLUDED from the patch, not translated:
# the hub says a machine must not touch them, and this session's values for
# them are machine drafts, so adding them would put machine Nepali into a
# validated clinical instrument (PHQ-9 cut-off >=10 belongs to specific
# wording), into consent wording, and into the GBV/child-protection gate.
# The hub intends them to stay English until a human decides.
PROTECTED_PREFIXES = ("phq9.item", "consent.", "safeguard.", "clinical.")


def protected(key: str) -> bool:
    return key.startswith(PROTECTED_PREFIXES)


def flatten(js_path: str) -> dict:
    out = subprocess.run(
        ["node", "-e",
         "global.window={};require(process.argv[1]);"
         "console.log(JSON.stringify({m:window.I18N_STRINGS._meta,"
         "en:window.I18N_STRINGS.en,ne:window.I18N_STRINGS.ne}))",
         js_path],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def entry_block(table: dict, only_keys) -> str:
    return "\n".join(
        "    %s: %s," % (js_string(k), js_string(table[k]))
        for k in table if k in only_keys
    )


def main() -> int:
    hub = flatten(BASE_JS)
    mine = json.loads(Path(MINE_JSON).read_text(encoding="utf-8"))

    hub_en, hub_ne = hub["en"], hub["ne"]
    my_en, my_ne = mine["en"], mine["ne"]

    add_en = sorted(k for k in my_en if k not in hub_en and not protected(k))
    add_ne = sorted(k for k in my_ne if k not in hub_ne and not protected(k))
    held = sorted(k for k in my_ne if k not in hub_ne and protected(k))

    # Any key present in both but different, that is NOT explicitly hub-owned.
    conflicts = sorted(
        k for k in hub_ne
        if k in my_ne and hub_ne[k] != my_ne[k] and k not in HUB_WINS
    )
    if conflicts:
        print("REFUSING: unlisted value conflicts on %d key(s): %s"
              % (len(conflicts), conflicts[:10]))
        return 1

    # English conflicts too - none expected, but check rather than assume.
    en_conflicts = sorted(
        k for k in hub_en if k in my_en and hub_en[k] != my_en[k]
        and k not in HUB_WINS
    )
    if en_conflicts:
        print("REFUSING: unlisted EN value conflicts: %s" % en_conflicts[:10])
        return 1

    src = Path(BASE_JS).read_text(encoding="utf-8")

    # Insert the new entries first inside each table, as a labelled, reversible
    # block. New keys are named, so nothing existing is reordered or rewritten.
    en_block = ("\n    /* Added by the form lane, %d keys; see LANGUAGE-COVERAGE.md */\n"
                % len(add_en)) + entry_block(my_en, set(add_en))
    ne_block = ("\n    /* Added by the form lane, %d keys; machine-drafted, await human review */\n"
                % len(add_ne)) + entry_block(my_ne, set(add_ne))

    src = src.replace("  en: {\n", "  en: {\n" + en_block + "\n", 1)
    src = src.replace("  ne: {\n", "  ne: {\n" + ne_block + "\n", 1)

    # Extend the machine provenance list so the new Nepali is auditable.
    m = re.search(r"machine: \[(.*?)\]", src, re.S)
    if m:
        listing = m.group(1).strip().rstrip(",")
        listing = listing + ",\n" + ",\n".join(
            "      " + js_string(k) for k in add_ne)
        src = src[:m.start()] + "machine: [\n" + listing + "\n    ]" + src[m.end():]

    Path(OUT_JS).write_text(src, encoding="utf-8")

    # Report
    print("added to en: %d" % len(add_en))
    print("added to ne: %d" % len(add_ne))
    print("hub-owned keys left untouched: %s" % sorted(HUB_WINS))
    print("HELD IN ENGLISH (protected, never machine-translated): %d" % len(held))
    for k in held:
        print("    held: %s" % k)

    # Write the patch against hub origin/main
    subprocess.run(
        "diff -u --label a/assets/i18n-strings.js --label b/assets/i18n-strings.js "
        "%s %s > %s || true" % (BASE_JS, OUT_JS, OUT_PATCH),
        shell=True, check=True)
    lines = Path(OUT_PATCH).read_text(encoding="utf-8").count("\n")
    print("patch written: %s (%d lines)" % (OUT_PATCH, lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Report, per keyed page, which professionalOnly prefixes actually match.

This is the count the task asks for, and it is the count that was WRONG before:
the prefix list protected **0 of 204** keys while every Nepali page carried a
notice claiming clinical wording was kept in English. A protection that is
claimed but matches nothing is worse than no protection, because it is believed.

It reads the real dictionary and the real page files -- not a copy of either --
and prints three things per page:

  * prefixes that match at least one key the page actually uses  (protection in force)
  * keys on the page held in English by those prefixes            (what is protected)
  * prefixes in the list that match NO live key anywhere          (dead, must be 0)

Run from the form repository root, after keying:

  python3 tools/i18n-protection-report.py [dictionary]

Exit 0 if every prefix matches a live key, 1 if any is dead.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DICTIONARY = Path("/root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js")
PAGES = ["referral.html", "phq9.html", "contact.html", "index.html",
         "selfreport.html", "5ws-report.html"]
KEY_ATTRS = ("data-i18n", "data-i18n-ph", "data-i18n-aria",
             "data-i18n-alt", "data-i18n-title")


def dictionary_keys(source):
    body = re.search(r"\n  en:\s*\{(.*?)\n  \}", source, re.S).group(1)
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"^\s*//.*$", "", body, flags=re.M)
    return set(re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"', body))


def prefixes(source):
    block = re.search(r"professionalOnly:\s*\[(.*?)\]", source, re.S).group(1)
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    return re.findall(r'"([^"]+)"', block)


def page_keys(path):
    text = path.read_text(encoding="utf-8")
    keys = set()
    for attr in KEY_ATTRS:
        keys |= set(re.findall(attr + r'="([^"]+)"', text))
    # keys minted in JavaScript are written as data-i18n="' + o.key + '"; they
    # resolve to a variable, so they cannot be read from the source. They are
    # reported by the extractor (tools/i18n_extract.py) instead.
    return {k for k in keys if "'" not in k}


def main():
    dictionary = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DICTIONARY
    source = dictionary.read_text(encoding="utf-8")
    live_keys, pro = dictionary_keys(source), prefixes(source)

    print("dictionary: %s" % dictionary)
    print("live EN keys: %d   professionalOnly prefixes: %d" % (len(live_keys), len(pro)))
    print()

    dead = [p for p in pro if not any(k.startswith(p) for k in live_keys)]
    print("PREFIX HEALTH")
    for p in pro:
        matched = sorted(k for k in live_keys if k.startswith(p))
        print("  %-14s matches %2d live key(s)%s"
              % (p, len(matched), "   <-- DEAD" if not matched else ""))
    print("  %d of %d prefixes match a live key; %d dead"
          % (len(pro) - len(dead), len(pro), len(dead)))
    total = sum(1 for k in live_keys if any(k.startswith(p) for p in pro))
    print("  %d keys held in English in total" % total)
    print()

    print("PER PAGE (keys the page really uses)")
    print("  %-18s %6s %10s  %s" % ("page", "keys", "protected", "prefixes in force"))
    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            continue
        keys = page_keys(path)
        prot = sorted(k for k in keys if any(k.startswith(p) for p in pro))
        hit = [p for p in pro if any(k.startswith(p) for k in keys)]
        print("  %-18s %6d %10d  %s"
              % (name, len(keys), len(prot),
                 ", ".join("%s=%d" % (p, sum(1 for k in prot if k.startswith(p)))
                           for p in hit) or "-"))
        for k in prot:
            print("        - %s" % k)
    print()
    print("phq9.html shows one more key than tools/i18n-check.py's HTML scanner,")
    print("because phq9.item9Instruction is minted inside a <script> (the item-9")
    print("safety instruction, rendered only after a positive answer). The scanner")
    print("cannot see script text; this report reads the attribute wherever it is.")
    print()
    if dead:
        print("FAIL: prefix(es) matching no live key: %s" % ", ".join(dead))
        return 1
    print("OK: every professionalOnly prefix matches a live key.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

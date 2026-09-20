#!/usr/bin/env python3
"""Fail if the dictionary the bilingual gate reads is not the canonical one.

tools/i18n-check.py reads the shared dictionary from a SIBLING `hub/`
directory (`../hub/assets/i18n-strings.js`), because in the deployed layout the
form repo is served at `/form/` and the hub at `/hub/` and they really are
siblings. On this host that sibling is an untracked staging copy, so it can be
older than the tracked dictionary in the hub worktree.

That is not a cosmetic difference. On 20 Sep 2026 the staging copy sat at the
pre-keying revision while `referral.html`, `phq9.html` and `contact.html` were
already keyed against the new dictionary. The gate then failed all three pages
with "keys used here with no English string" -- and, worse, it reported the six
professionalOnly prefixes as matching NO key, i.e. the historic 0-of-204 bug
appeared to have come back. It had not: the gate was reading the wrong file.
A gate that silently reads a stale dictionary reports the opposite of the truth
in both directions -- it invents failures and it hides the real protection
count.

So the rule this enforces: whichever dictionary the gate reads must be
byte-identical to the canonical one, or the run must say so out loud.

  python3 tools/i18n-dictionary-sync-check.py [CANONICAL]

With no argument it compares, in order of preference:
  * /root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js  (the tracked
    worktree for this task), else
  * ../hub-real/assets/i18n-strings.js relative to this repository.

Exit 0 identical / 1 drifted / 2 cannot compare.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_DICTIONARY = os.path.join(ROOT, "..", "hub", "assets", "i18n-strings.js")
CANDIDATES = [
    "/root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js",
    os.path.join(ROOT, "..", "hub-real", "assets", "i18n-strings.js"),
]


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    canonical = sys.argv[1] if len(sys.argv) > 1 else None
    if not canonical:
        for candidate in CANDIDATES:
            if os.path.isfile(candidate):
                canonical = candidate
                break
    if not canonical or not os.path.isfile(canonical):
        print("cannot find a canonical dictionary to compare against")
        return 2
    if not os.path.isfile(GATE_DICTIONARY):
        print("the gate's dictionary is missing: %s" % GATE_DICTIONARY)
        return 2

    gate, canon = digest(GATE_DICTIONARY), digest(canonical)
    print("gate dictionary      %s  %s" % (gate[:16], GATE_DICTIONARY))
    print("canonical dictionary %s  %s" % (canon[:16], canonical))
    if gate == canon:
        print("IN SYNC")
        return 0
    print("DRIFT: the gate is reading a different dictionary than the canonical one.")
    print("       Every count the gate prints -- including the professionalOnly")
    print("       protection count -- describes the file it read, not the change.")
    print("       Copy the canonical file over the gate's path before trusting a run.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

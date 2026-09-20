#!/usr/bin/env python3
"""Turn the 100 held keys into a minimal human-decision worksheet.

The parent run left 100 keys in English with both machine readings recorded.
All 100 remain in English: published vocabulary may inform a human reviewer,
but it cannot itself adjudicate a disagreement. The worksheet groups repeated
term choices so one human decision can settle every key it blocks.

A key is counted under "one term" only if, after aligning the two readings word
for word, exactly one aligned position differs -- no word added or dropped
anywhere. A key that needs more than that is listed separately.

Output: tools/i18n-ne-review-worksheet.json

This script is self-contained: it does not import the adjudicator, so changing
the adjudicator's policy cannot silently change what the worksheet claims.
"""
import collections
import difflib
import json
import os
import re

FORM = "/root/mhpss-nepal-work/form-translation"

DEV = re.compile(r"[\u0900-\u097F]+")
TAG = re.compile(r"<[^>]+>")
SUFFIX = ["हरूलाई", "हरूबाट", "हरूको", "हरूमा", "हरूले", "हरू", "बारे", "सँग", "लाई", "बाट",
          "को", "का", "की", "मा", "ले", "पछि", "भित्र", "सम्म", "तिर"]


def dev_words(v):
    return DEV.findall(TAG.sub(" ", v))


def base_letters(t):
    return sum(1 for ch in t if "\u0900" <= ch <= "\u093d")


def stem(t):
    changed = True
    while changed and base_letters(t) >= 3:
        changed = False
        for s in SUFFIX:
            if t.endswith(s) and base_letters(t[: -len(s)]) >= 3:
                t = t[: -len(s)]
                changed = True
                break
    return t


def stems(v):
    return [stem(t) for t in dev_words(v)]


def single_term_difference(a, b):
    """(term_A, term_B) if the only difference is one aligned position, else
    None -- with the added/dropped case reported separately."""
    sa, sb = stems(a), stems(b)
    if sa == sb:
        return None
    sm = difflib.SequenceMatcher(a=sa, b=sb, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    if len(ops) != 1 or ops[0][0] != "replace":
        return None
    _, i1, i2, j1, j2 = ops[0]
    if (i2 - i1) != (j2 - j1) or (i2 - i1) != 1:
        return None
    return sa[i1], sb[j1]


def main():
    hdr = json.load(open(os.path.join(FORM, "tools", "i18n-ne-human-decision-required.json"),
                         encoding="utf-8"))
    held = json.load(open(os.path.join(FORM, "tools", "i18n-ne-authority-held.json"),
                          encoding="utf-8"))

    one_term = collections.defaultdict(list)
    multi = {}
    for k in sorted(held):
        a, b = hdr[k].get("lane-A", ""), hdr[k].get("lane-B", "")
        pair = single_term_difference(a, b)
        if pair:
            one_term[pair].append(k)
        else:
            multi[k] = held[k].get("reason", "")

    decisions = []
    for (ta, tb), keys in sorted(one_term.items(), key=lambda kv: -len(kv[1])):
        decisions.append({
            "reading_A_term": ta,
            "reading_B_term": tb,
            "keys_settled_by_this_one_decision": keys,
            "count": len(keys),
            "question": ("which is the Ministry's word, %s or %s?" % (ta, tb)),
        })

    out = {
        "note": ("Keys left in English because the two independent machine lanes disagree "
                 "and no human adjudication was obtained. Published project vocabulary is "
                 "context, not a decision. These are the questions for a Nepali speaker or "
                 "the Ministry terminology owner. Every key settled by one answer is "
                 "listed under it, so one word decided once clears a whole batch."),
        "single_term_decisions": decisions,
        "needs_sentence_level_review": multi,
        "counts": {
            "held": len(held),
            "settled_by_one_term_decision": sum(len(d["keys_settled_by_this_one_decision"])
                                                for d in decisions),
            "distinct_term_decisions": len(decisions),
            "sentence_level": len(multi),
        },
    }
    json.dump(out, open(os.path.join(FORM, "tools", "i18n-ne-review-worksheet.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)

    c = out["counts"]
    print("held keys: %d" % c["held"])
    print("  settled by deciding ONE term: %d, across %d distinct decisions"
          % (c["settled_by_one_term_decision"], c["distinct_term_decisions"]))
    print("  need sentence-level review:   %d" % c["sentence_level"])
    print()
    print("%-4s %-18s %-18s %s" % ("n", "reading A", "reading B", "keys"))
    for d in decisions:
        print("%-4d %-18s %-18s %s" % (d["count"], d["reading_A_term"], d["reading_B_term"],
                                       ", ".join(d["keys_settled_by_this_one_decision"][:6])))
    print()
    print("wrote tools/i18n-ne-review-worksheet.json")


if __name__ == "__main__":
    main()

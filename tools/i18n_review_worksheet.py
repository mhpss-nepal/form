#!/usr/bin/env python3
"""Turn the held keys into a minimal human-decision worksheet.

The parent run left 100 keys in English with both machine readings recorded.
This review settled 7 against the project's own published vocabulary and held
93. Those 93 are not 93 separate questions: most turn on one term the two lanes
chose differently, and deciding that term once settles every key it blocks.

The alignment used is the same one the adjudicator uses, so a key is counted
here as "one term" only if, after aligning the two readings word for word,
exactly one aligned position differs -- no word added or dropped anywhere. A
key that needs more than that is not one decision and is listed separately.

Output: tools/i18n-ne-review-worksheet.json
"""
import collections
import importlib.util
import json
import os

FORM = "/root/mhpss-nepal-work/form-translation"

spec = importlib.util.spec_from_file_location(
    "adj", os.path.join(FORM, "tools", "i18n_review_adjudicate.py"))
adj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adj)


def single_term_difference(a, b):
    """(term_A, term_B) if the only difference is one aligned position, else
    None -- with the added/dropped case reported separately."""
    import difflib
    sa, sb = adj.stems(a), adj.stems(b)
    if sa == sb:
        return None
    sm = difflib.SequenceMatcher(a=sa, b=sb, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    if len(ops) != 1 or ops[0][0] != "replace":
        return None
    tag, i1, i2, j1, j2 = ops[0]
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
        "note": ("Keys left in English because no authority in the project's own material "
                 "settles the difference between the two independent machine lanes. This "
                 "run decided nothing here; these are the questions for a Nepali speaker or "
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

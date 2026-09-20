#!/usr/bin/env python3
"""Record every machine-lane disagreement, and settle none of them.

The parent run left 100 keys in English because two independent machine lanes
disagreed, and the project rule forbids deciding a disagreement by a vote.

An earlier revision of this script also settled 7 of them "by the project's own
published vocabulary". That was withdrawn: it was a second automated heuristic,
not a human decision, and one of its routes (R4) picked the shorter reading
among genuine Nepali grammatical variants. The task permits a disagreement to
leave English only after a HUMAN decision.

Published material remains useful CONTEXT for the reviewer, but this script
does not decide anything with it. It therefore settles zero keys, leaves all
100 in English, and writes the audit dumps the worksheet and the evidence doc
read.

Context material a reviewer may consult (read-only):
  * hub-real/tools/terminology-lock.json      (approved sentence + code pairs)
  * hub-translation/assets/codes.js           (`np`, `help_np` fields)
  * hub-translation/assets/i18n-strings.js    (shipped placeholders + `ne`)
"""

import json
import os

FORM = "/root/mhpss-nepal-work/form-translation"


def main():
    hdr = json.load(open(os.path.join(FORM, "tools",
                                      "i18n-ne-human-decision-required.json"),
                         encoding="utf-8"))
    if len(hdr) != 100:
        raise SystemExit("expected the parent's 100 flagged keys, found %d" % len(hdr))

    # Nothing is settled here: every disagreement is a question for a person.
    settled = {}
    held = {
        key: {
            "page": item.get("page", ""),
            "english": item["english"],
            "reason": "two machine lanes disagree; a human decision is required",
        }
        for key, item in sorted(hdr.items())
    }

    print("flagged keys:                                 %d" % len(hdr))
    print("settled by an automated rule:                  %d" % len(settled))
    print("left in English -- human decision required:   %d" % len(held))
    print()

    # Audit dump: both machine readings stay visible for every held key, so a
    # reviewer reads the evidence rather than prose.
    audit = {"settled": {}, "held": {}}
    for k in sorted(held):
        audit["held"][k] = dict(held[k], lane_A=hdr[k].get("lane-A", ""),
                                lane_B=hdr[k].get("lane-B", ""))
    for k in sorted(settled):
        audit["settled"][k] = dict(settled[k], lane_A=hdr[k].get("lane-A", ""),
                                   lane_B=hdr[k].get("lane-B", ""))

    json.dump(audit, open(os.path.join(FORM, "tools", "i18n-review-evidence.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump(settled, open(os.path.join(FORM, "tools", "i18n-ne-authority-resolved.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump(held, open(os.path.join(FORM, "tools", "i18n-ne-authority-held.json"), "w",
                         encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()

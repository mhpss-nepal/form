#!/usr/bin/env python3
"""Print every form on the Layer 1 landing page, in both languages.

Ministry decision, 21 Sep 2026: the live site must show all the forms that have
been built, not just the 5Ws. This restores the full card grid that was reduced
to one card by bf6c121, keeping the trial marking as a label rather than as a
removal.

Usage: python3 restore_all_form_cards.py <path-to-index.html>
"""
import re
import sys
from pathlib import Path

# The order the ministry saw them in, and the key each card's text comes from.
# Text is NOT written here: every string is an i18n key so both languages come
# from the dictionary, which is what keeps the page bilingual by construction.
CARDS = [
    ("svc",   "ml.p010", "ml.p048", "ml.p029", "ml.p028", "5ws-report.html",       "5ws"),
    ("svc",   "ml.p009", "ml.p047", "ml.p027", "ml.p026", "contact.html",          "contact"),
    ("clin",  "ml.p008", "ml.p046", "ml.p025", "ml.p024", "phq9.html",             "phq9"),
    ("ref",   "ml.p007", "ml.p045", "ml.p023", "ml.p022", "referral.html",         "referral"),
    ("selfr", "ml.p006", "ml.p044", "ml.p021", "ml.p020", "selfreport.html",       "self"),
]

CARD = """    <div class="ml-card {cls}">
      <div class="tag" data-i18n="{tag}"></div>
      <h3 data-i18n="{head}"></h3>
      <p data-i18n="{body}" data-i18n-html></p>
      <p class="src" data-i18n="{src}"></p>
      <div class="ml-actions">
        <a href="{form}" data-i18n="ml.act.open"></a>
        <button class="sec" data-url="{form}" onclick="COPY(this)" data-i18n="ml.p074"></button>
        <button class="sec" data-qr="{qr}" onclick="QRT(this)" data-i18n="ml.act.qr"></button>
      </div>
      <div class="qrbox" hidden></div>
    </div>
"""


def main() -> int:
    p = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
    s = p.read_text(encoding="utf-8")

    grid = re.search(r'  <div class="ml-grid">\n.*?\n  </div>\n', s, re.S)
    if not grid:
        print("REFUSING: could not find the ml-grid block")
        return 1

    want = [c[5] for c in CARDS]
    have = re.findall(r'href="([a-z0-9-]+\.html)"', grid.group(0))
    if have == want:
        print("already correct: %s" % have)
        return 0

    cards = "".join(
        CARD.format(cls=c[0], tag=c[1], head=c[2], body=c[3], src=c[4],
                    form=c[5], qr=c[6])
        for c in CARDS
    )
    new_grid = '  <div class="ml-grid">\n\n' + cards + '\n  </div>\n'
    s = s[:grid.start()] + new_grid + s[grid.end():]

    # The QR matrices live in qr-trial.js, which for the trial carried only
    # master and 5ws. If the other matrices are absent, the page must not claim
    # a QR it cannot draw -- QRT() already handles a missing key, but the
    # button should not be offered. Check and report rather than assume.
    p.write_text(s, encoding="utf-8")
    print("cards now: %s" % re.findall(r'href="([a-z0-9-]+\.html)"', new_grid))
    return 0


if __name__ == "__main__":
    sys.exit(main())

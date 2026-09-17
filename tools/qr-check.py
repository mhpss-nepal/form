#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHPSS Nepal -- the QR integrity check
=====================================
The QR codes in assets/qr.js are PRE-COMPUTED BIT MATRICES, on purpose: no CDN
library, so they render on a phone with no signal. The consequence is easy to
miss and expensive.

    The address is baked into the matrix. The "url" field beside it is only a
    label. Editing that label changes NOTHING about where the QR points.

So if the site address ever moves -- a renamed repo, a custom domain, a new
path -- every matrix has to be REGENERATED (tools/qr-build.py). A QR printed on
a wall at a holding centre cannot be corrected later, and the failure is
silent: a field worker points a camera and lands on a dead page.

This decodes every matrix and asserts two things:
  1. it decodes to exactly the url label sitting next to it
  2. that url begins with the site's declared base

Exit 0 all consistent / 1 a QR points somewhere it should not / 2 cannot run.

Usage: qr-check.py [base-url]        default base: tools/site.conf
"""
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the matrices are shared code, in the hub repository one folder over
QRJS = os.path.join(ROOT, "..", "hub", "assets", "qr.js")
CONF = os.path.join(ROOT, "tools", "site.conf")

ENTRY = re.compile(
    r'"([A-Za-z0-9_-]+)":\s*\{\s*"n":\s*(\d+)\s*,'
    r'\s*"url":\s*"([^"]+)"\s*,'
    r'(?:\s*"sha":\s*"([0-9a-f]*)"\s*,)?'
    r'\s*"m":\s*"([01,]+)"'
)


def declared_base(argv):
    if len(argv) > 1 and argv[1].strip():
        return argv[1].strip().rstrip("/")
    if os.path.isfile(CONF):
        for line in io.open(CONF, encoding="utf-8"):
            line = line.strip()
            if line.startswith("base"):
                return line.split("=", 1)[1].strip().rstrip("/")
    return None


def main(argv):
    if not os.path.isfile(QRJS):
        print("  cannot read ../hub/assets/qr.js")
        return 2

    base = declared_base(argv)
    src = io.open(QRJS, encoding="utf-8").read()
    entries = ENTRY.findall(src)

    # The strong check decodes the matrix and needs numpy + opencv. The Mac's
    # python3 has neither, and a check that only runs on one machine is a check
    # that does not run. So there are two real modes -- never a skip:
    #
    #   decode  the matrix is decoded and compared to its label
    #   digest  the sha written at generation time is recomputed, which proves
    #           the url and the matrix have not been changed since they were
    #           generated together (and generation DID decode them)
    #
    # Both also require every label to sit inside the declared base, which is
    # what catches a moved address.
    try:
        import numpy as np
        import cv2
        mode = "decode"
    except ImportError:
        np = cv2 = None
        mode = "digest"

    print("MHPSS Nepal -- QR integrity  [%s mode]" % mode)
    print("  declared base: %s" % (base or "(none set)"))
    print("  matrices: %d" % len(entries))
    if not entries:
        print("  no matrices found -- the file format changed; check the regex")
        return 2

    problems = []
    det = cv2.QRCodeDetector() if cv2 else None

    for key, n, url, sha, m in entries:
        n = int(n)
        rows = m.split(",")
        if len(rows) != n or any(len(r) != n for r in rows):
            problems.append((key, "matrix is not %dx%d" % (n, n), url, ""))
            continue

        if base and not url.startswith(base + "/"):
            problems.append((key, "points outside the declared base", url, ""))
            continue

        if mode == "decode":
            grid = np.array([[0 if c == "1" else 255 for c in r] for r in rows],
                            dtype=np.uint8)
            q = 4
            big = np.full((n + 2 * q, n + 2 * q), 255, dtype=np.uint8)
            big[q:q + n, q:q + n] = grid
            img = cv2.resize(big, None, fx=8, fy=8,
                             interpolation=cv2.INTER_NEAREST)
            data, _, _ = det.detectAndDecode(img)
            if not data:
                problems.append((key, "does not decode at all", url, ""))
                continue
            if data != url:
                problems.append((key, "points somewhere else", url, data))
                continue
        else:
            if not sha:
                problems.append((key, "has no digest -- regenerate with "
                                      "tools/qr-build.py so it can be checked "
                                      "without a QR decoder", url, ""))
                continue
            got = hashlib.sha256((url + "|" + m).encode("utf-8")).hexdigest()[:32]
            if got != sha:
                problems.append((key, "url or matrix edited since generation",
                                 url, "digest %s, expected %s" % (got, sha)))
                continue

        print("    %-10s OK   %s" % (key, url))

    if not problems:
        if mode == "decode":
            print("\n  Consistent: every QR decodes to its own label, inside the base.")
        else:
            print("\n  Consistent: every url+matrix matches the digest written when it")
            print("  was generated (and generation decoded it), inside the base.")
        return 0

    print("\n  QR MISMATCH -- these would send a phone to the wrong place:")
    for key, why, url, got in problems:
        print("    %-10s %s" % (key, why))
        print("        label  : %s" % url)
        if got:
            print("        %s" % got)
    print("\n  A QR cannot be fixed by editing its url label -- the address is")
    print("  inside the bit matrix. Regenerate with:")
    print("      python3 tools/qr-build.py <base-url> --write")
    print("  and remember any QR already PRINTED still points to the old address.")
    return 1


def cards():
    """Every QR the printable card sheet asks for must exist in qr.js.

    The sheet is the thing a field worker is handed, so a missing key there is
    a card with a blank square on it. The full test -- render the sheet to A4
    and decode each card back with OpenCV -- needs a browser and cannot run on
    the deploy machine; it is done from the cloud workspace before a deploy and
    passed 6 of 6 at 150 dpi and above on 16 September 2026. This is the part
    that can run anywhere.
    """
    import os, re
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    card = os.path.join(root, "cards.html")
    if not os.path.exists(card):
        return 0, "no card sheet"
    html = open(card, encoding="utf-8").read()
    want = re.findall(r'data-qr="([a-z0-9]+)"', html)
    qr = open(os.path.join(root, "..", "hub", "assets", "qr.js"), encoding="utf-8").read()
    have = set(re.findall(r'^"([a-z0-9]+)":\{', qr, re.M))
    missing = [k for k in want if k not in have]
    if missing:
        return 1, "the card sheet asks for %s, which assets/qr.js does not hold" % ", ".join(missing)
    return 0, "the card sheet's %d codes all exist" % len(want)

if __name__ == "__main__":
    rc = main(sys.argv)
    crc, cmsg = cards()
    print("  card sheet: %s" % cmsg)
    sys.exit(rc or crc)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHPSS Nepal -- regenerate the pre-computed QR matrices
======================================================
Run this whenever the site address changes. It rewrites assets/qr.js with
matrices that actually encode the new address, then verifies every one of them
by decoding it back -- because the whole failure mode here is a QR that LOOKS
right and points somewhere dead.

Usage:  qr-build.py https://new-address.example        [--write]
Without --write it is a dry run and prints what would change.

The paths are declared here, once. Add a form to this list and it gets a QR.
"""
import hashlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QRJS = os.path.join(ROOT, "..", "hub", "assets", "qr.js")
CONF = os.path.join(ROOT, "tools", "site.conf")

# key -> path under the base. The key is what form/index.html asks for.
TARGETS = [
    ("master",   "/form/"),
    ("4ws",      "/form/4ws-report.html"),
    ("contact",  "/form/contact.html"),
    ("phq9",     "/form/phq9.html"),
    ("referral", "/form/referral.html"),
    ("self",     "/form/selfreport.html"),
]

HEADER = """/* Pre-computed QR matrices (ECC level M).
   Each entry decodes back to its own URL -- verified with OpenCV
   QRCodeDetector by tools/qr-build.py, and re-verified on every deploy by
   tools/qr-check.py.

   PRE-COMPUTED ON PURPOSE: no CDN library, so a QR renders on a phone with no
   signal.

   THE ADDRESS IS INSIDE THE MATRIX. The "url" field is only a label -- editing
   it changes nothing about where the QR points. If the site address moves, run
   tools/qr-build.py, do not hand-edit this file.

   Generated for base: %s
*/
window.QR = {
%s
};
window.QR._base = "%s";
"""


def build(base, write):
    try:
        import qrcode
        import numpy as np
        import cv2
    except ImportError as e:
        print("cannot run: %s (need qrcode, numpy, opencv-python)" % e)
        return 2

    base = base.rstrip("/")
    blocks = []
    det = cv2.QRCodeDetector()
    print("MHPSS Nepal -- rebuilding QR matrices")
    print("  base: %s" % base)

    for key, path in TARGETS:
        url = base + path
        q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                          border=0)
        q.add_data(url)
        q.make(fit=True)
        mod = q.get_matrix()          # list of rows of True/False
        n = len(mod)
        rows = ["".join("1" if c else "0" for c in r) for r in mod]

        # verify by decoding what we just made
        grid = np.array([[0 if c == "1" else 255 for c in r] for r in rows],
                        dtype=np.uint8)
        pad = 4
        big = np.full((n + 2 * pad, n + 2 * pad), 255, dtype=np.uint8)
        big[pad:pad + n, pad:pad + n] = grid
        img = cv2.resize(big, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
        got, _, _ = det.detectAndDecode(img)
        if got != url:
            print("    %-10s FAILED verification -- decoded %r" % (key, got))
            print("    nothing written.")
            return 1
        print("    %-10s n=%-3d verified  %s" % (key, n, url))

        matrix = ",".join(rows)
        # The digest covers url + matrix together, so neither can be changed
        # without the other. A machine with no QR decoder (the Mac's python3
        # has no cv2) can still verify this, which is what lets the deploy
        # guard run the check everywhere instead of skipping it.
        sha = hashlib.sha256((url + "|" + matrix).encode("utf-8")).hexdigest()[:32]
        blocks.append('"%s":{\n"n":%d,\n"url":"%s",\n"sha":"%s",\n"m":"%s"\n}'
                      % (key, n, url, sha, matrix))

    out = HEADER % (base, ",\n".join(blocks), base)

    if not write:
        print("\n  DRY RUN -- pass --write to replace assets/qr.js")
        print("  (%d bytes would be written)" % len(out.encode("utf-8")))
        return 0

    io.open(QRJS, "w", encoding="utf-8").write(out)
    io.open(CONF, "w", encoding="utf-8").write("base=%s\n" % base)
    print("\n  assets/qr.js rewritten, tools/site.conf updated.")
    print("  REMEMBER: any QR already printed still points to the old address.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(build(sys.argv[1], "--write" in sys.argv))

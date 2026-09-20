#!/usr/bin/env python3
"""Failing-first check: the keying contract tests must FAIL on the base pages.

Restores the three pages to their pre-keying base, runs the unittest, records
the result, then puts the keyed pages back. Nothing is left modified.
"""
import shutil
import subprocess
import sys
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
BASE = FORM / "tools" / "fixtures" / "keying-base"
PAGES = ["referral.html", "phq9.html", "contact.html"]

backup = FORM / "tools" / "_keyed-backup"
backup.mkdir(exist_ok=True)
for p in PAGES:
    shutil.copy2(FORM / p, backup / p)
    shutil.copy2(BASE / p, FORM / p)

try:
    result = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_i18n_keying"],
                            cwd=FORM, capture_output=True, text=True)
    tail = result.stderr.strip().splitlines()
    print("AT BASE: exit=%d" % result.returncode)
    print("\n".join(tail[-6:]))
    print()
    fails = sum(1 for line in tail if line.startswith("FAIL:") or line.startswith("ERROR:"))
    print("base: %d failing test(s)" % fails)
finally:
    for p in PAGES:
        shutil.copy2(backup / p, FORM / p)
    shutil.rmtree(backup)

result = subprocess.run([sys.executable, "-m", "unittest", "test_i18n_keying"],
                        cwd=FORM, capture_output=True, text=True)
print("AT HEAD: exit=%d  %s" % (result.returncode, result.stderr.strip().splitlines()[-1]))

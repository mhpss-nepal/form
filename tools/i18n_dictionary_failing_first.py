"""Failing-first demonstration for the DictionaryIntegrity tests.

Proves that the two new checks really do catch the two conditions they were
written for, by reproducing each condition and re-running them:

  A. the gate's dictionary is stale (pre-keying) -> sync check FAILS
  B. professionalOnly holds a dead prefix      -> protection report FAILS

Nothing is left changed at the end.
"""
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
STAGE = FORM.parent / "hub" / "assets" / "i18n-strings.js"
CANON = FORM.parent / "hub-translation" / "assets" / "i18n-strings.js"
BASE = Path("/tmp/base-dict.js")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def run(*args, cwd=FORM):
    r = subprocess.run([sys.executable, *args], cwd=cwd,
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def unit(pattern):
    r = subprocess.run([sys.executable, "-m", "unittest", "test_i18n_keying",
                        "-k", pattern, "-v"],
                       cwd=FORM, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


print("=" * 74)
print("BASELINE (head): both new instruments must pass")
print("=" * 74)
rc, out = run("tools/i18n-dictionary-sync-check.py")
print("sync-check exit=%d  %s" % (rc, out.splitlines()[-1]))
rc2, out2 = run("tools/i18n-protection-report.py")
print("protection-report exit=%d  %s" % (rc2, out2.splitlines()[-1]))
rc3, out3 = unit("DictionaryIntegrity")
print("unittest DictionaryIntegrity exit=%d  %s"
      % (rc3, out3.splitlines()[-1]))
assert rc == 0 and rc2 == 0 and rc3 == 0, "baseline is not green"

print()
print("=" * 74)
print("A. gate's dictionary reverted to the pre-keying revision (ff2d4e2)")
print("=" * 74)
try:
    shutil.copyfile(BASE, STAGE)
    print("staged dictionary sha256=%s (was %s)" % (digest(STAGE), digest(CANON)))
    rc, out = run("tools/i18n-dictionary-sync-check.py")
    print("sync-check exit=%d" % rc)
    print("\n".join("   " + line for line in out.splitlines()))
    rc_u, out_u = unit("DictionaryIntegrity.test_gate_dictionary_is_the_canonical")
    print("unittest->%s" % ("FAILED (caught)" if rc_u != 0 else "PASSED (missed!)"))
    assert rc == 1 and rc_u != 0, "the stale-dictionary condition was not caught"
finally:
    shutil.copyfile(CANON, STAGE)
    print("restored canonical dictionary sha256=%s" % digest(STAGE))

print()
print("=" * 74)
print("B. a DEAD prefix added to _meta.professionalOnly")
print("=" * 74)
source = CANON.read_text(encoding="utf-8")
saved = source
# plant a prefix that matches no key -- the historic 0-of-204 condition
patched = source.replace('"clinical."\n    ],', '"clinical.",\n      "dead.prefix.sentinel"\n    ],', 1)
assert patched != source, "could not plant the dead prefix"
# patch BOTH the canonical and the gate's copy, or the sync check fires first
for target in (CANON, STAGE):
    target.write_text(patched, encoding="utf-8")
try:
    rc, out = run("tools/i18n-protection-report.py")
    print("protection-report exit=%d" % rc)
    print("\n".join("   " + line for line in out.splitlines() if "DEAD" in line or "dead" in line))
    rc_u, out_u = unit("DictionaryIntegrity.test_every_professional_only_prefix")
    print("unittest->%s" % ("FAILED (caught)" if rc_u != 0 else "PASSED (missed!)"))
    assert rc == 1 and rc_u != 0, "the dead-prefix condition was not caught"
finally:
    CANON.write_text(saved, encoding="utf-8")
    STAGE.write_text(saved, encoding="utf-8")
    print("restored both dictionaries: canonical=%s staged=%s"
          % (digest(CANON), digest(STAGE)))

print()
print("=" * 74)
print("RESTORED -- re-running the baseline")
print("=" * 74)
rc, out = run("tools/i18n-dictionary-sync-check.py")
rc2, _ = run("tools/i18n-protection-report.py")
rc3, out3 = unit("DictionaryIntegrity")
print("sync-check=%d  protection-report=%d  unittest=%d  %s"
      % (rc, rc2, rc3, out3.splitlines()[-1]))
assert rc == 0 and rc2 == 0 and rc3 == 0, "did not restore cleanly"
print("FAILING-FIRST PROVEN: both conditions are caught, both clear at head.")

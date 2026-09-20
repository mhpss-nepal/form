"""Capture the exact acceptance outputs for this reconciliation run.

Writes each command and its full output into the evidence file, so the file
cannot drift from what was actually run.
"""
import datetime
import subprocess
import sys
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")

COMMANDS = [
    ("Gate: the dictionary names itself",
     ["python3", "tools/i18n-check.py"]),
    ("Reconciliation: gate dictionary vs canonical, by sha256",
     ["python3", "tools/i18n-dictionary-sync-check.py"]),
    ("professionalOnly prefix health + per-page protection count",
     ["python3", "tools/i18n-protection-report.py"]),
    ("Keying contract tests (10)",
     ["python3", "-m", "unittest", "test_i18n_keying"]),
    ("Keying failing-first: pinned pre-keying fixtures",
     ["python3", "tools/i18n_failing_first.py"]),
    ("Rendered Stage-B proof: protected wording is English on the Nepali page",
     ["python3", "tools/i18n_safety_proof_file_url.py"]),
    ("Failing-first for the two new instruments",
     ["python3", "tools/i18n_dictionary_failing_first.py"]),
    ("Offline completeness (keyed pages need the dictionary precached)",
     ["python3", "tools/sw-precache-check.py"]),
    ("Text setting", ["python3", "tools/text-setting-check.py"]),
    ("QR payload consistency", ["python3", "tools/qr-check.py"]),
]

chunks = []
for title, argv in COMMANDS:
    print("running: %s" % " ".join(argv))
    r = subprocess.run(argv, cwd=FORM, capture_output=True, text=True, timeout=900)
    body = (r.stdout + r.stderr).strip()
    chunks.append("### %s\n\n```\n$ cd /root/mhpss-nepal-work/form-translation\n$ %s\n\n%s\n\n(exit %d)\n```\n"
                  % (title, " ".join(argv), body, r.returncode))
    print("  exit=%d  (%d bytes)" % (r.returncode, len(body)))

header = """# Keying evidence — `referral.html`, `phq9.html`, `contact.html`

MHPSS Nepal · task `t_2cfc3bab` · reconciliation run · %s

Revised scope for this run: reconcile the two worktrees, get the three keyed
pages clean through `tools/i18n-check.py`, and report the verified
`professionalOnly` count **after** keying. Translation to a reviewed standard is
the next ticket and is **not attempted here** (see the follow-on note at the
end).

Every command below was run from `/root/mhpss-nepal-work/form-translation` and
its output is reproduced verbatim, including the dictionary's sha256 — because
the previous evidence recorded a gate run whose result depended on a file the
command never named, and that file later went stale.

""" % datetime.date.today().isoformat()

out = FORM / "TRANSLATION-KEYING-EVIDENCE.md"
out.write_text(header + "\n---\n\n".join(chunks), encoding="utf-8")
print("\nwrote %s (%d bytes)" % (out, out.stat().st_size))

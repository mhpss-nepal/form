#!/usr/bin/env python3
"""Diagnose the pre-existing precache-fingerprint drift (not caused by this task)."""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path("/root/mhpss-nepal-work/form-frontend")
HUB = ROOT.parent / "hub"

sw = (ROOT / "sw.js").read_text(encoding="utf-8")
block = re.search(r"const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;", sw, re.DOTALL).group(1)
entries = re.findall(r'"([^"]+)"', block)

recorded = (ROOT / "tools" / "precache.sha").read_text(encoding="utf-8").strip()
total = hashlib.sha256()
per = {}
for entry in entries:
    if entry == "./":
        asset = ROOT / "index.html"
    elif entry.startswith("../hub/"):
        asset = HUB / entry.removeprefix("../hub/")
    else:
        asset = ROOT / entry
    h = hashlib.sha256()
    h.update(entry.encode("utf-8"))
    h.update(asset.read_bytes())
    per[entry] = h.hexdigest()[:16]
    total.update(entry.encode("utf-8"))
    total.update(asset.read_bytes())

print("recorded :", recorded)
print("computed :", total.hexdigest())
print("entries  :", len(entries))
print()
print("committed precache.sha history:")
print(subprocess.run(["git", "log", "--oneline", "-5", "--", "tools/precache.sha"],
                     cwd=ROOT, capture_output=True, text=True).stdout)
print("committed value at HEAD:", subprocess.run(
    ["git", "show", "HEAD:tools/precache.sha"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
print("committed value at 11bff2f:", subprocess.run(
    ["git", "show", "11bff2f:tools/precache.sha"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
print("sw.js changed since 11bff2f?", subprocess.run(
    ["git", "diff", "--stat", "11bff2f", "HEAD", "--", "sw.js"], cwd=ROOT,
    capture_output=True, text=True).stdout.strip() or "(no change)")
print("index.html changed since 11bff2f?", subprocess.run(
    ["git", "diff", "--stat", "11bff2f", "HEAD", "--", "index.html"], cwd=ROOT,
    capture_output=True, text=True).stdout.strip() or "(no change)")
print()
print("hub asset mtimes (untracked in this repo, shared with other worktrees):")
for name in sorted(p.name for p in HUB.joinpath("assets").iterdir()):
    p = HUB / "assets" / name
    print("   %-22s %s  %d bytes" % (name, p.stat().st_mtime_ns, p.stat().st_size))
print()
print("recompute excluding ../hub entries:")
h2 = hashlib.sha256()
for entry in entries:
    if entry.startswith("../hub/"):
        continue
    asset = ROOT / ("index.html" if entry == "./" else entry)
    h2.update(entry.encode("utf-8"))
    h2.update(asset.read_bytes())
print("  form-only digest:", h2.hexdigest())

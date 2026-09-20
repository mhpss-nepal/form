#!/usr/bin/env python3
"""Re-stamp content hashes on the B2 preview asset URLs.

Run after editing 5ws-preview-core.js, 5ws-preview.css or 5ws-preview-status.js
so a browser can never serve a stale preview asset.
"""
from pathlib import Path
import hashlib, re, sys

root = Path(__file__).resolve().parent.parent
dp = root / "design-preview"
page = root / "5ws-report-b2.html"

def stamp(name):
    h = hashlib.sha256((dp / name).read_bytes()).hexdigest()[:10]
    return f"design-preview/{name}?h={h}"

html = page.read_text(encoding="utf-8")
for name in ("5ws-preview.css", "5ws-preview-core.js", "5ws-preview-status.js"):
    html = re.sub(re.escape(f"design-preview/{name}") + r"\?h=[0-9a-f]*", stamp(name), html)
page.write_text(html, encoding="utf-8")
print("stamped:", re.findall(r"5ws-preview[^\"']*", html))

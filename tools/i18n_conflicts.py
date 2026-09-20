#!/usr/bin/env python3
"""Explain the 15 English conflicts i18n_apply.py reported."""
import json
import re
from pathlib import Path

FORM = Path("/root/mhpss-nepal-work/form-translation")
HUB = Path("/root/mhpss-nepal-work/hub-translation")
CONFLICT = ["phq9.p015", "ref.p016", "ref.p021", "ref.p054", "ref.p063", "ref.p064",
            "ref.p070", "svc.p008", "svc.p010", "svc.p023", "svc.p028", "svc.p031",
            "svc.p061", "svc.p070", "svc.p078"]


def unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def block(src, name):
    m = re.search(r"\n  " + name + r":\s*\{(.*?)\n  \}", src, re.S)
    b = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    b = re.sub(r"^\s*//.*$", "", b, flags=re.M)
    return {k: v for k, v in
            ((unescape(a), unescape(c)) for a, c in
             re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', b))}


hub = block((HUB / "assets" / "i18n-strings.js").read_text(encoding="utf-8"), "en")
page = {e["key"]: e["en"] for e in json.loads((FORM / "tools" / "new-i18n-entries.json").read_text(encoding="utf-8"))}
real = 0
print("key            | equal after unescaping?  | value")
for k in CONFLICT:
    h, p = hub.get(k, ""), page.get(k, "")
    same = h == p
    if not same:
        real += 1
    print("%-14s | %-8s | %s" % (k, "YES" if same else "NO", p[:66]))
print()
print("real (non-escaping) conflicts: %d of %d" % (real, len(CONFLICT)))

#!/usr/bin/env python3
"""Provenance audit: no machine draft may be labelled human, and a key may not
be in both lists."""
import re
from pathlib import Path

HUB = Path("/root/mhpss-nepal-work/hub-translation")
src = (HUB / "assets" / "i18n-strings.js").read_text(encoding="utf-8")


def block(name):
    m = re.search(r"\n  " + name + r":\s*\{(.*?)\n  \}", src, re.S)
    b = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    b = re.sub(r"^\s*//.*$", "", b, flags=re.M)
    return dict(re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', b))


def meta_list(name):
    m = re.search(name + r"\s*:\s*\[(.*?)\]", src, re.S)
    if not m:
        return []
    b = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    b = re.sub(r"//[^\n]*", "", b)
    return re.findall(r'"((?:[^"\\]|\\.)*)"', b)


ne = {k for k, v in block("ne").items() if v.strip()}
machine = set(meta_list("machine"))
human = set(meta_list("human"))
pro = meta_list("professionalOnly")
en = block("en")

print("ne keys with text:        %d" % len(ne))
print("_meta.source.machine:     %d" % len(machine))
print("_meta.source.human:       %d" % len(human))
print()
print("machine keys that have NO Nepali (should be 0): %d"
      % len([k for k in machine if k not in ne]))
print("Nepali keys missing from machine (unlabelled drafts): %d"
      % len([k for k in ne if k not in machine]))
print("keys in BOTH machine and human: %d" % len(machine & human))
print()
print("professionalOnly prefixes: %d, of which match live English keys: %d"
      % (len(pro), sum(1 for p in pro if any(k.startswith(p) for k in en))))
print("keys held in English: %d" % len([k for k in en if any(k.startswith(p) for p in pro)]))
print()
# protected keys must have NO Nepali at all
bad = [k for k in ne if any(k.startswith(p) for p in pro)]
print("protected keys that WRONGLY have Nepali: %d %s" % (len(bad), bad))
print()
# the honest notice
notice = [k for k in en if "automatic" in en[k].lower() or "authoritative" in en[k].lower()]
print("honest reader-notice keys present: %s" % notice)

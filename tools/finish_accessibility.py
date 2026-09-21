#!/usr/bin/env python3
"""Finish the accessibility pass: main landmark, table captions, named groups.

Continues tools/add_accessibility.py. Split out because the earlier step edits
(scope, skip link) had to land first and be verified on their own.

  1. <main id="main"> so the skip link has a target, wrapped around the page
     content only -- never around the header or footer navigation;
  2. <caption> on each data table, taken from that table's own first header
     cell, so a screen reader announces the table by name;
  3. <fieldset>/<legend> around the two grouped count blocks, so the group of
     inputs has a name rather than being a run of loose numbers.

Usage: python3 finish_accessibility.py
"""
import re
import sys
from pathlib import Path

BASE = Path("/root/mhpss-nepal-work/form-frontend")
FORMS = ["5ws-report.html", "contact.html", "referral.html", "selfreport.html",
         "phq9.html", "index.html"]


def add_main(s: str) -> tuple:
    if 'id="main"' in s:
        return s, False
    m = re.search(r'<div class="wrap[^"]*">\n', s)
    if not m:
        return s, False
    s = s[:m.end()] + '  <main id="main">\n' + s[m.end():]
    # close it immediately before the first <script that follows body content
    tail = re.search(r"\n<script", s[m.end():])
    if tail:
        at = m.end() + tail.start()
        s = s[:at] + "\n  </main>\n" + s[at:]
        return s, True
    return s, False


def add_captions(s: str) -> tuple:
    added = 0

    def one(m):
        nonlocal added
        body = m.group(0)
        if "<caption" in body:
            return body
        th = re.search(r"<th[^>]*>\s*(?:<[^>]+>)*\s*([^<]{2,70}?)\s*(?:<[^>]+>)*\s*</th>", body)
        if not th:
            return body
        label = re.sub(r"\s+", " ", th.group(1)).strip()
        if not label or label in ("—", "-"):
            return body
        added += 1
        return body.replace(
            "<table",
            '<table', 1).replace(
            ">",
            '>\n      <caption class="sr-only">%s</caption>' % label, 1)

    s = re.sub(r"<table\b[\s\S]*?</table>", one, s)
    return s, added > 0


def add_fieldset(s: str) -> tuple:
    """Give each grouped count block a name, without moving its content."""
    changed = False
    # the "of whom" group and the disability group both have a heading <p> then
    # a run of <div><label><input></div>
    for cls in ("ofwhom",):
        m = re.search(r'<div class="%s"' % cls, s)
        if not m:
            continue
        end = s.find("\n      </div>\n", m.start())
        if end == -1:
            continue
        block = s[m.start():end]
        if "<fieldset" in block:
            continue
        # the heading paragraph becomes the legend
        h = re.search(r'<p class="ofw-h"[^>]*>', block)
        if not h:
            continue
        # replace the opening div with a fieldset, and the closing div with the
        # fieldset close; the heading paragraph becomes a legend with a
        # visually-hidden-able span kept as-is for layout
        new = block
        new = new.replace('<div class="%s"' % cls, '<fieldset class="%s"' % cls, 1)
        new = new[:new.rfind("</div>")] + "</fieldset>"
        new = new.replace('<p class="ofw-h"', '<legend class="ofw-h"', 1)
        new = new.replace("</p>", "</legend>", 1)
        s = s[:m.start()] + new + s[end:]
        changed = True
    return s, changed


def main() -> int:
    for name in FORMS:
        p = BASE / name
        if not p.exists():
            print("  skip (absent): %s" % name)
            continue
        s = p.read_text(encoding="utf-8")
        before = s
        notes = []
        s, did_main = add_main(s)
        if did_main:
            notes.append("main")
        n0 = s
        s, did_cap = add_captions(s)
        if did_cap:
            notes.append("captions")
        if name == "5ws-report.html":
            s, did_fs = add_fieldset(s)
            if did_fs:
                notes.append("fieldset")
        if s != before:
            p.write_text(s, encoding="utf-8")
        print("  %-20s %s" % (name, ", ".join(notes) or "no change"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

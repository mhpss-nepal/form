#!/usr/bin/env python3
"""Render the trial's only form and prove it still works, in a real browser.

Run the site root first (the page loads ../hub/assets/*):
    python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
    python3 tools/5ws-still-works.py http://127.0.0.1:8791

The interface language is whatever the shared engine resolves (per-surface
default, remembered choice, or ?lang=), so this probe never matches on English
button TEXT -- it matches on the stable `name=` contract taken from the committed
page itself, plus the ids and structure a regression would actually break.

Exit 0 the form loads and holds its contract, 1 a regression, 2 cannot run.
"""
import json
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "5ws-report.html"
SHEET_IDS = ("f", "expCsv", "expJson", "wipe", "reset", "problems", "tgs")
SELECT_IDS = ("org", "cadre", "district", "site", "palika", "modality", "activity", "status")

PROBE = """(() => {
  const q = id => document.getElementById(id);
  const f = q('f');
  const named = f ? [...f.querySelectorAll('[name]')].map(e => e.name) : [];
  return JSON.stringify({
    title: document.title,
    lang: document.documentElement.lang,
    hasForm: !!f,
    names: named,
    controlsInForm: f ? f.querySelectorAll('input,select,textarea').length : 0,
    controlsInDoc: document.querySelectorAll('input,select,textarea').length,
    selects: f ? [...f.querySelectorAll('select')].map(s => s.id) : [],
    submits: [...document.querySelectorAll('[type=submit], button[form=f]')].length,
    checkboxes: f ? f.querySelectorAll('input[type=checkbox]').length : 0,
    numbers: f ? f.querySelectorAll('input[type=number]').length : 0,
    idsPresent: %s.reduce((a, id) => (a[id] = !!q(id), a), {}),
    hrefs: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
    i18nMounted: !!document.querySelector('#i18nbar'),
    toggle: (() => {
      const b = [...document.querySelectorAll('#i18nbar button, #i18nbar a')]
        .map(x => (x.textContent || '').trim()).filter(Boolean);
      return b;
    })(),
    notice: document.body.innerText.replace(/\\s+/g, ' ').slice(0, 150),
  });
})()""" % json.dumps(list(SHEET_IDS))


def expected_names(src):
    match = re.search(r'<form id="f"[\s\S]*?</form>', src)
    if match is None:
        raise SystemExit("cannot find <form id=f> in 5ws-report.html")
    block = match.group(0)
    return sorted(set(re.findall(r'\bname="([^"]+)"', block)))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print("cannot run: %s (need playwright)" % exc)
        return 2

    src = PAGE.read_text(encoding="utf-8")
    want_names = expected_names(src)
    want_selects = [i for i in SELECT_IDS]

    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []

        def on_console(m):
            if m.type == "error":
                errors.append(m.text)

        page.on("console", on_console)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("%s/form-frontend/5ws-report.html" % root, wait_until="load")
        page.wait_for_timeout(900)
        data = json.loads(page.evaluate(PROBE))

        if not data["hasForm"]:
            problems.append("the 5Ws <form id=f> is missing")
        if sorted(set(data["names"])) != want_names:
            missing = [n for n in want_names if n not in data["names"]]
            extra = [n for n in data["names"] if n not in want_names]
            problems.append("name= contract drifted; missing %s extra %s" % (missing, extra))
        for cid, present in data["idsPresent"].items():
            if not present:
                problems.append("control/element #%s is gone" % cid)
        if data["selects"] != want_selects:
            problems.append("the agreed select ids changed: %s" % data["selects"])
        if data["submits"] < 1:
            problems.append("no submit control: a report could not be saved")
        if data["checkboxes"] < 8:
            problems.append("only %d target-group checkboxes" % data["checkboxes"])
        if data["numbers"] < 15:
            problems.append("only %d numeric count fields" % data["numbers"])
        for href in data["hrefs"]:
            if href and any(bad in href for bad in ("contact.html", "phq9.html", "referral.html", "selfreport.html")):
                problems.append("the 5Ws page links an unapproved form: %s" % href)
        if not data["i18nMounted"]:
            problems.append("the bilingual notice/switch did not mount")
        if errors:
            problems.append("console errors: %s" % "; ".join(errors[:3]))

        print("  title        : %s" % data["title"])
        print("  lang         : %s   i18n switch: %s   toggle: %s"
              % (data["lang"], data["i18nMounted"], data["toggle"]))
        print("  name= in form: %d (source expects %d) -> %s"
              % (len(set(data["names"])), len(want_names),
                 "match" if sorted(set(data["names"])) == want_names else "MISMATCH"))
        print("  controls     : %d in form / %d in document" % (data["controlsInForm"], data["controlsInDoc"]))
        print("  selects      : %s" % data["selects"])
        print("  counts       : %d checkboxes, %d numeric, %d submit" % (data["checkboxes"], data["numbers"], data["submits"]))
        print("  ids present  : %s" % ", ".join(k for k, v in data["idsPresent"].items() if v))
        print("  .html hrefs  : %s" % sorted({h for h in data["hrefs"] if h and h.endswith(".html")}))
        print("  notice       : %s" % data["notice"])
        page.close()
        browser.close()

    if problems:
        print("\n  5WS REGRESSION:")
        for row in problems:
            print("    %s" % row)
        return 1
    print("\n  The trial's only form still loads with its full name= contract, its eight")
    print("  agreed pickers, its count and target-group controls, its save path and its")
    print("  bilingual chrome -- and it links no unapproved form.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

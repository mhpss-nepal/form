#!/usr/bin/env python3
"""Rendered evidence for the per-layer language default, in a real browser.

The declaration `data-i18n-default="ne"` on 5ws-report.html is read by the
shared engine at ../hub/assets/i18n.js. A source-text check ("the attribute is
present") is NOT evidence the page opens in Nepali: the engine decides, at
runtime, from URL -> remembered choice -> browser preference -> the declared
page default. This drives the actual DOM and reads what the engine resolved.

Run the site root first, with the form worktree and the durable hub repo side by
side so `../hub/assets/*` resolves to the repo the pages actually load:

    python3 -m http.server 8931 --bind 127.0.0.1 --directory /tmp/t83-serve
    python3 tools/per-layer-default-render-check.py http://127.0.0.1:8931

Cases required by the task (t_83eec40f section 2):
  1. 5ws-report.html, no ?lang=       -> Nepali on first load
  2. 5ws-report.html?lang=en          -> still English (a shared link stays shareable)
  3. a Hub page (hub/index.html)      -> English
  4. index.html                       -> English (the not-fully-translated guard)

Each case is opened in a FRESH browser context, so the remembered-choice
localStorage key from a previous case cannot leak into the next one -- which is
exactly how a reader arrives the first time.

The engine exposes the language as a FUNCTION, `window.I18N.lang()`. Reading
`window.I18N.lang` as a property yields a function object (never the code) and
is the trap the task warns about.

Exit 0 all four cases as required / 1 a case is wrong / 2 cannot run.
"""
from __future__ import annotations

import json
import sys

CASES = [
    # label,                       path,                             want, devanagari?, kind
    ("5ws report, no ?lang=",      "form-frontend/5ws-report.html",  "ne", True, "engine"),
    ("5ws report ?lang=en",        "form-frontend/5ws-report.html?lang=en", "en", False, "engine"),
    ("Hub home",                   "hub/index.html",                 "en", False, "engine"),
    ("form landing (index.html)",  "form-frontend/index.html",       "en", False, "engine"),
    # Defensive: every OTHER form page must keep declaring nothing -> English.
    ("b2 derived preview",         "form-frontend/5ws-report-b2.html", "en", False, "engine"),
    ("contact",                    "form-frontend/contact.html",     "en", False, "engine"),
    ("phq9",                       "form-frontend/phq9.html",        "en", False, "engine"),
    ("referral",                   "form-frontend/referral.html",    "en", False, "engine"),
    ("selfreport",                 "form-frontend/selfreport.html",  "en", False, "engine"),
    # The 4Ws stub is a redirect, not a page with a language: it must land on
    # the 5Ws report and inherit whatever THAT resolves to (Nepali).
    ("4ws redirect stub",          "form-frontend/4ws-report.html",  "ne", True, "redirect"),
    # cards.html loads no i18n engine at all and is not a form; it must simply
    # keep declaring nothing (its printed Devanagari is a design constant).
    ("cards sheet (no engine)",    "form-frontend/cards.html",       None, False, "noengine"),
]

PROBE = """(() => {
  const fn = window.I18N && typeof window.I18N.lang === 'function';
  const declared = document.documentElement.getAttribute('data-i18n-default');
  const body = document.body ? document.body.innerText.replace(/\\s+/g, ' ').trim() : '';
  const devanagari = (body.match(/[\\u0900-\\u097F]/g) || []).length;
  return JSON.stringify({
    i18n_present: !!window.I18N,
    lang_fn_is_function: fn,
    resolved: fn ? window.I18N.lang() : null,
    data_lang: document.documentElement.getAttribute('data-lang'),
    html_lang: document.documentElement.lang,
    declared: declared,
    title: document.title,
    devanagari_chars: devanagari,
    final_url: window.location.href,
    first_text: body.slice(0, 160),
  });
})()"""


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

    problems = []
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, path, want, expect_devanagari, kind in CASES:
            # a fresh context = a first-time reader: no remembered choice,
            # no cache from a previous case.
            ctx = browser.new_context(viewport={"width": 390, "height": 844})
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))

            page.goto("%s/%s" % (root, path), wait_until="load")
            page.wait_for_timeout(800)
            data = json.loads(page.evaluate(PROBE))

            if kind == "redirect":
                if "/5ws-report.html" not in data["final_url"]:
                    problems.append((label, "did not land on 5ws-report.html: %s"
                                     % data["final_url"]))
            elif kind == "noengine":
                if data["declared"] is not None:
                    problems.append((label, "declares %r; a page with no engine must declare nothing"
                                     % data["declared"]))
            else:  # engine
                if not data["i18n_present"]:
                    problems.append((label, "window.I18N never mounted"))
                elif not data["lang_fn_is_function"]:
                    problems.append((label, "window.I18N.lang is not a function"))
                if data["resolved"] != want:
                    problems.append((label, "resolved %r, wanted %r" % (data["resolved"], want)))
                if data["data_lang"] != want:
                    problems.append((label, "data-lang %r, wanted %r" % (data["data_lang"], want)))
                if expect_devanagari and data["devanagari_chars"] == 0:
                    problems.append((label, "no Devanagari in the rendered text"))
                if not expect_devanagari and data["devanagari_chars"] > 0:
                    problems.append((label, "%d Devanagari chars on an English page"
                                     % data["devanagari_chars"]))
            if errors and kind != "noengine":
                problems.append((label, "console errors: %s" % "; ".join(errors[:3])))

            rows.append((label, path, data, kind))
            ctx.close()
        browser.close()

    print("  %-26s %-34s %-8s %-6s %-6s %-5s %s"
          % ("case", "path", "I18N", "data-", "html-", "deva", "declared"))
    for label, path, d, kind in rows:
        print("  %-26s %-34s %-8s %-6s %-6s %-5s %s"
              % (label, path,
                 str(d["resolved"]), str(d["data_lang"]), str(d["html_lang"]),
                 d["devanagari_chars"], repr(d["declared"])))
        print("      text: %s" % d["first_text"][:100])

    hub = [r for r in rows if r[1].startswith("hub/")]
    if hub:
        print("  hub page renders:", repr(hub[0][2]["first_text"][:60]))
    red = [r for r in rows if r[3] == "redirect"]
    if red:
        print("  4ws stub lands on:", red[0][2]["final_url"])

    if problems:
        print("\n  PER-LAYER DEFAULT CHECK FAILED:")
        for row in problems:
            print("    %s" % (row,))
        return 1
    print("\n  The 5Ws report opens in Nepali with no ?lang=; ?lang=en still gives")
    print("  English; the Hub and every other form page stay English.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

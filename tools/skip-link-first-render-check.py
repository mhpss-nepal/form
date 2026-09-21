#!/usr/bin/env python3
"""Rendered-browser check that the SKIP LINK IS THE FIRST TAB STOP.

The skip link is the only control a keyboard or screen-reader user has for
getting past the page's header, so it has to be the first thing Tab reaches.
Markup order alone does not decide that: two scripts inject a strip at the FRONT
of <body> at runtime -- the bilingual engine's machine-translation notice
(../hub/assets/i18n.js) and pwa.js's connection / offline strip (#pwabar) -- and
whichever runs last would otherwise end up in front of the skip link.

That was a real, measured regression (task t_e504a356): in the ENGLISH view on
all six form pages the first Tab stop was #pwabar's dismiss button
(BUTTON.x, aria-label="Dismiss", 44x44 at 332,10) and the skip link was second.
The re-ordering that was supposed to prevent it lived inside mountNotice(), a
function that returns early when lang === "en", so it only ever ran in Nepali.
Nepali was right, English was wrong, and nothing in the source showed it.

So this drives the actual DOM, in BOTH languages, with the offline strip forced
VISIBLE -- the field case, where a phone has no signal and the strip is on
screen -- and presses Tab once.

Run the site root first, because the pages load ../hub/assets/*:
    python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
    python3 tools/skip-link-first-render-check.py http://127.0.0.1:8791

Exit 0 every page passes / 1 a page failed / 2 cannot run.
"""
import json
import sys

# The six pages the field build serves, in the order the trial scope lists them.
PAGES = (
    "5ws-report.html",
    "contact.html",
    "referral.html",
    "phq9.html",
    "selfreport.html",
    "index.html",
)
# The Nepali DEFAULT view (no ?lang) and the English one. Both must pass: the
# bug this check exists for passed in Nepali and failed in English.
CASES = (("ne", ""), ("en", "?lang=en"))

# Force the offline strip visible first, exactly as a phone with no signal has
# it, and then report the first Tab stop.
PROBE = """(() => {
  const bar = document.getElementById('pwabar');
  if (bar) bar.hidden = false;
  const a = document.activeElement;
  const skip = document.querySelector('.a11y-skip');
  const body = document.body;
  return JSON.stringify({
    first_stop_is_skip: !!(a && a.classList && a.classList.contains('a11y-skip')),
    first_stop_tag: a ? a.tagName : null,
    first_stop_id: a ? a.id : null,
    first_stop_class: a ? a.className : null,
    first_stop_aria: a ? a.getAttribute('aria-label') : null,
    first_stop_text: a ? (a.innerText || a.value || '').trim().slice(0, 30) : null,
    in_pwabar: !!(a && a.closest && a.closest('#pwabar')),
    in_mtnote: !!(a && a.closest && a.closest('#mtnote')),
    pwabar_present: !!bar,
    pwabar_visible: !!(bar && !bar.hidden),
    skip_is_first_element: !!(skip && body.firstElementChild === skip),
    body_order: Array.from(body.children).slice(0, 4).map(e => e.id || e.className || e.tagName)
  });
})()"""


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    base = argv[1].rstrip("/")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print("cannot run: %s (need playwright)" % exc)
        return 2

    results = []
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for page_name in PAGES:
            for lang, qs in CASES:
                # A fresh context per measurement: no saved language, no
                # dismissed notice carried in from the previous page.
                ctx = browser.new_context(viewport={"width": 390, "height": 844},
                                          locale="en-US")
                page = ctx.new_page()
                errors = []
                page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                # cache-busted, so a cached engine cannot answer for the tree
                url = "%s/form/%s%s%scb=%s" % (base, page_name, qs,
                                               "&" if qs else "?", "skipcheck")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3500)   # i18n.js, pwa.js, fb.js settle
                # force the offline strip visible (the field case), then Tab
                page.evaluate(
                    "() => { const b = document.getElementById('pwabar'); if (b) b.hidden = false; }")
                page.keyboard.press("Tab")
                page.wait_for_timeout(200)
                first = json.loads(page.evaluate(PROBE))
                row = dict(page=page_name, lang=lang, **first)
                row["errors"] = errors
                results.append(row)
                ok = first["first_stop_is_skip"] and not errors
                label = "%s [%s]" % (page_name, lang)
                if ok:
                    print("PASS  %-26s first stop: .a11y-skip %r"
                          % (label, first["first_stop_text"]))
                else:
                    print("FAIL  %-26s first stop: %s.%s %r (in #pwabar=%s, in #mtnote=%s)"
                          % (label, first["first_stop_tag"], first["first_stop_class"],
                             first["first_stop_text"], first["in_pwabar"],
                             first["in_mtnote"]))
                    if label not in problems:
                        problems.append(label)
                if not first["skip_is_first_element"]:
                    print("      .a11y-skip is not the first element child: %s"
                          % first["body_order"])
                    if label not in problems:
                        problems.append(label)
                if errors:
                    print("      page errors: %s" % errors)
                ctx.close()
        browser.close()

    print("\n%d measurements, %d failing" % (len(results), len(problems)))
    if problems:
        print("skip link is NOT the first tab stop on: %s" % ", ".join(problems))
        return 1
    print("the skip link is the first tab stop on every page, in both languages, "
          "with the offline strip visible")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

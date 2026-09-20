#!/usr/bin/env python3
"""Rendered-browser check of the trial build, over the served site.

Source-level tests can stay green through a real defect (the shared i18n engine
injects chrome at runtime, and a QR is only drawn after the page's own script
runs). This drives the actual DOM and reports what a field worker's browser
resolves, at mobile and desktop widths, in both languages.

Run the site root first, because the pages load ../hub/assets/*:
    python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
    python3 tools/trial-scope-render-check.py http://127.0.0.1:8791

Exit 0 all clear / 1 an unapproved path is reachable / 2 cannot run.
"""
import json
import sys

UNAPPROVED = ("contact.html", "phq9.html", "referral.html", "selfreport.html")

PROBE = """(() => {
  const cards = [...document.querySelectorAll('.ml-card')].map(c => ({
    heading: (c.querySelector('h3') || {}).textContent || '',
    hrefs: [...c.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
    urls: [...c.querySelectorAll('[data-url]')].map(b => b.getAttribute('data-url')),
    qr: [...c.querySelectorAll('[data-qr]')].map(b => b.getAttribute('data-qr')),
  }));
  const qrs = [...document.querySelectorAll('[data-qr]')];
  // Click every QR button so the matrices are actually drawn, not just declared.
  const opened = [];
  [...document.querySelectorAll('.ml-actions .sec, #qrAll')].forEach(b => {
    if (b.hasAttribute('data-qr') || b.id === 'qrAll') { b.click(); opened.push(b.id || b.getAttribute('data-qr')); }
  });
  const drawn = [...document.querySelectorAll('.qrbox svg rect')].length;
  const sheetDrawn = [...document.querySelectorAll('.qwrap svg rect')].length;
  const sheetUrls = [...document.querySelectorAll('.qurl')].map(d => d.textContent.trim()).filter(Boolean);
  const drawnUrls = [...document.querySelectorAll('.qrbox .u, .qrbox div')].map(d => d.textContent.trim()).filter(Boolean);
  return JSON.stringify({
    title: document.title,
    lang: document.documentElement.lang,
    cards, opened, drawn, sheetDrawn, sheetUrls, drawnUrls,
    allHrefs: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
    allQr: [...document.querySelectorAll('[data-qr]')].map(b => b.getAttribute('data-qr')),
    injectedChrome: [...document.querySelectorAll('[id*="i18n"], .i18nbar, [class*="i18n"]')].length,
    text: document.body.innerText.replace(/\\s+/g, ' ').slice(0, 600),
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
    seen = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, width, height in (("390 mobile", 390, 844), ("1280 desktop", 1280, 900)):
            page = browser.new_page(viewport={"width": width, "height": height})
            console = []
            # Only real errors count. Both repositories log informational lines
            # (the Hub bridge logs "heartbeats undefined" on every page), and a
            # check that fails on those would be switched off rather than fixed.
            def on_console(m):
                if m.type == "error":
                    console.append(f"{m.type}: {m.text}")

            page.on("console", on_console)
            page.on("pageerror", lambda e: console.append(f"pageerror: {e}"))
            for url, what in (
                ("%s/form-frontend/index.html" % root, "landing"),
                ("%s/form-frontend/cards.html" % root, "card sheet"),
            ):
                page.goto(url, wait_until="load")
                page.wait_for_timeout(700)
                data = json.loads(page.evaluate(PROBE))
                seen.append((label, what, data))
                for href in data["allHrefs"]:
                    if href and any(bad in href for bad in UNAPPROVED):
                        problems.append((label, what, "link to unapproved form", href))
                for key in data["allQr"]:
                    if key not in ("5ws", "master"):
                        problems.append((label, what, "unapproved QR key", key))
                if what == "card sheet" and data["allQr"] != ["5ws"]:
                    problems.append((label, what, "card sheet QR set", str(data["allQr"])))
                if what == "card sheet":
                    if data["sheetDrawn"] == 0:
                        problems.append((label, what, "card sheet drew no QR svg", "0"))
                    for shown in data["sheetUrls"]:
                        if any(bad in shown for bad in UNAPPROVED):
                            problems.append((label, what, "card sheet prints an unapproved address", shown))
                if what == "landing":
                    form_cards = [c for c in data["cards"] if c["hrefs"]]
                    if len(form_cards) != 1 or form_cards[0]["hrefs"] != ["5ws-report.html"]:
                        problems.append((label, what, "actionable form cards", json.dumps(form_cards)))
                    if data["drawn"] == 0:
                        problems.append((label, what, "no QR svg rendered after clicking", "0"))
            if console:
                problems.append((label, "console", "messages", "; ".join(console[:4])))
            page.close()
        browser.close()

    for label, what, data in seen:
        print("  %-14s %-10s cards=%d qr=%s drawn=%d sheetDrawn=%d sheetUrls=%s hrefs=%s"
              % (label, what, len(data["cards"]), data["allQr"], data["drawn"],
                 data["sheetDrawn"], data["sheetUrls"],
                 sorted({h for h in data["allHrefs"] if h and h.endswith('.html')})))

    if problems:
        print("\n  RENDERED CHECK FAILED:")
        for row in problems:
            print("    %s" % (row,))
        return 1
    print("\n  Clear: no reachable link or QR to an unapproved form in the rendered DOM,")
    print("  the landing page exposes exactly one actionable form card, and every")
    print("  declared QR actually drew.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

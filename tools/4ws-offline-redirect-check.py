#!/usr/bin/env python3
"""Prove the already-distributed 4Ws QR reaches the 5Ws form offline.

Run the site root first (the form loads ../hub/assets/*):
    python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
    python3 tools/4ws-offline-redirect-check.py http://127.0.0.1:8791

The browser installs the real service worker while online, then a fresh page
navigates to 4ws-report.html for the first time with the network disabled.
Exit 0 redirected to the form with query/hash intact / 1 regression / 2 cannot run.
"""
import json
import re
import sys
from urllib.parse import parse_qs, urlparse


QUERY = "qr=distributed-4ws&lang=ne"
HASH = "field-copy"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")
    scope = "%s/form-frontend/" % root
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print("cannot run: %s (need playwright)" % exc)
        return 2

    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 390, "height": 844})
        install = context.new_page()
        errors = []

        def on_console(message):
            if message.type == "error":
                errors.append(message.text)

        install.on("console", on_console)
        install.on("pageerror", lambda error: errors.append(str(error)))
        install.goto(scope + "index.html", wait_until="load")
        install.evaluate("navigator.serviceWorker.ready.then(() => true)")
        install.wait_for_function("navigator.serviceWorker.controller !== null")

        # The redirect stub must not have been requested before offline mode.
        cache_name = re.search(
            r'const\s+CACHE\s*=\s*"([^"]+)"',
            (install.evaluate("fetch('sw.js').then(r => r.text())")),
        )
        if cache_name is None:
            print("cannot find CACHE name in served sw.js")
            context.close()
            browser.close()
            return 2
        cached_before = install.evaluate("""async (name) => {
          const cache = await caches.open(name);
          return (await cache.keys()).map(request => request.url);
        }""", cache_name.group(1))
        if not any(urlparse(url).path.endswith("/4ws-report.html") for url in cached_before):
            problems.append("4ws-report.html was not precached before the first offline navigation")

        context.set_offline(True)
        page = context.new_page()
        page.on("console", on_console)
        page.on("pageerror", lambda error: errors.append(str(error)))
        requested = scope + "4ws-report.html?" + QUERY + "#" + HASH
        responses = []
        page.on("response", lambda item: responses.append(item))
        page.goto(requested, wait_until="load")
        page.wait_for_url("**/5ws-report.html?" + QUERY + "#" + HASH)
        page.locator("#f").wait_for(state="attached")

        parsed = urlparse(page.url)
        data = page.evaluate("""() => JSON.stringify({
          controlled: navigator.serviceWorker.controller !== null,
          hasForm: !!document.getElementById('f'),
          formNames: document.querySelectorAll('#f [name]').length,
          search: location.search,
          hash: location.hash,
          path: location.pathname,
          title: document.title
        })""")
        data = json.loads(data)
        if not parsed.path.endswith("/5ws-report.html"):
            problems.append("offline navigation did not reach 5ws-report.html: %s" % page.url)
        if parse_qs(parsed.query) != parse_qs(QUERY):
            problems.append("redirect did not preserve query: %s" % data["search"])
        if parsed.fragment != HASH:
            problems.append("redirect did not preserve hash: %s" % data["hash"])
        if not data["controlled"]:
            problems.append("the fresh offline page was not controlled by a service worker")
        navigations = [item for item in responses if item.request.is_navigation_request()]
        served_paths = [urlparse(item.url).path for item in navigations if item.from_service_worker]
        for expected in ("/4ws-report.html", "/5ws-report.html"):
            if not any(path.endswith(expected) for path in served_paths):
                problems.append("%s was not served by the service worker" % expected.lstrip("/"))
        if not data["hasForm"] or data["formNames"] == 0:
            problems.append("redirect target did not render the 5Ws form")
        if errors:
            problems.append("console errors: %s" % "; ".join(errors[:3]))

        print("  requested : %s" % requested)
        print("  resolved  : %s" % page.url)
        print("  worker    : controlled=%s served=%s" %
              (data["controlled"], [path.rsplit("/", 1)[-1] for path in served_paths]))
        print("  form      : %s (%d named controls)" % (data["hasForm"], data["formNames"]))
        print("  query/hash: %s %s" % (data["search"], data["hash"]))
        context.close()
        browser.close()

    if problems:
        print("\n  4WS OFFLINE REDIRECT FAILED:")
        for problem in problems:
            print("    %s" % problem)
        return 1
    print("\n  The distributed 4Ws address was available before first use, redirected")
    print("  offline to the 5Ws form, and preserved its query string and hash.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

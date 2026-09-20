#!/usr/bin/env python3
"""Rendered evidence for preview isolation (task t_d1360320).

Drives a real Chromium over the served site and reports what a REVIEWER's
browser actually resolves:

  · every review page carries the bilingual DEMO / REVIEW banner, at the top,
    legible and not overflowing, at 390 px and 1280 px;
  · the real committed form renders inside the frame (the 5Ws form's own
    controls, its pickers filled, its language switch mounted);
  · a real submit inside the review frame is directed ONLY at the staging
    collection. Network requests to Firestore are intercepted and ABORTED, so
    this proves the write path WITHOUT committing any document to the project
    (we cannot see the security rules, so nothing is left to chance).

    python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
    python3 tools/preview-isolation-render-check.py http://127.0.0.1:8791

Exit 0 all clear / 1 a boundary failed / 2 cannot run.
"""
import json
import re
import sys
import urllib.parse

REVIEW_PAGES = ("5ws-report.html", "5ws-report-b2.html", "4ws-report.html", "contact.html",
                "phq9.html", "referral.html", "selfreport.html")
WRITING = ("5ws-report.html", "5ws-report-b2.html", "contact.html", "phq9.html",
           "referral.html", "selfreport.html")
PREVIEW_COLLECTION = "submissions_preview"
LIVE_COLLECTIONS = ("submissions", "public_stats")

BANNER_MUST_CONTAIN = ("DEMO", "REVIEW", "not real data", "not counted anywhere",
                       "समीक्षा", "वास्तविक डेटा होइन")

BANNER_PROBE = """(() => {
  const b = document.getElementById('preview-mode-banner');
  if (!b) return JSON.stringify({ present: false });
  const cs = getComputedStyle(b);
  const rect = b.getBoundingClientRect();
  const lines = [...b.querySelectorAll('.pm-en, .pm-ne, .pm-note')].map(e => ({
    cls: e.className, text: e.textContent.trim(),
    fontPx: parseFloat(getComputedStyle(e).fontSize),
    width: Math.round(e.getBoundingClientRect().width)
  }));
  return JSON.stringify({
    present: true, role: b.getAttribute('role'), position: cs.position,
    top: cs.top, zIndex: cs.zIndex, bg: cs.backgroundColor, fg: cs.color,
    offsetTop: Math.round(b.offsetTop), scrollY: Math.round(window.scrollY),
    isFirst: document.body.firstElementChild === b,
    stickyTopPx: Math.round(rect.top),
    width: Math.round(rect.width), viewport: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    text: b.innerText.replace(/\\s+/g, ' '), lines: lines
  });
})()"""


FORM_PROBE = """(() => {
  const root = document.getElementById('shell-page');
  return JSON.stringify({
    hasForm: !!document.querySelector('#f'),
    controls: root ? root.querySelectorAll('#f input, #f select, #f textarea').length : 0,
    selectsFilled: root ? [...root.querySelectorAll('#f select')].filter(s => s.options.length > 1).length : 0,
    lang: document.documentElement.getAttribute('data-lang'),
    i18nToggle: !!document.querySelector('#i18nbar, [data-i18n-toggle]'),
    pwabar: !!document.querySelector('#pwabar'),
    fbbar: !!document.querySelector('#fbbar'),
    collection: window.FB_COLLECTION,
    previewMode: !!window.FB_PREVIEW_MODE,
    url: location.pathname + location.search,
    bodyText: document.body.innerText.replace(/\\s+/g, ' ').slice(0, 160)
  });
})()"""


SUBMIT_PROBE = """(async () => {
  const root = document.getElementById('shell-page') || document;
  const set = (id, v) => {
    const el = root.querySelector('#' + id);
    if (!el) return;
    el.value = v;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };
  const pick = (id, value) => {
    const sel = root.querySelector('#' + id);
    if (!sel) return;
    const opt = [...sel.options].find(o => o.value === value) || sel.options[1];
    if (opt) { sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); }
  };
  set('dateAD', '2026-09-20');
  set('sessionTime', '09:30');
  set('reachedTotal', '7');
  set('focalName', 'Reviewer (synthetic)');
  set('focalPhone', '9800000000');
  pick('org', 'CMC'); pick('cadre', 'HW'); pick('district', 'NUW');
  pick('site', 'NUW-02'); pick('palika', 'NP10101');
  pick('activity', '1.1'); pick('modality', 'HC'); pick('status', 'ONG');

  const tg = root.querySelector('#tgs input[type=checkbox]');
  if (tg) { tg.checked = true; tg.dispatchEvent(new Event('change', { bubbles: true })); }
  set('f04', '7');
  const form = root.querySelector('#f');
  if (!form) return JSON.stringify({ error: 'no form rendered' });
  form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  await new Promise(r => setTimeout(r, 3000));

  const out = {
    queued: (window.FB && window.FB.queue) ? window.FB.queue().length : null,
    rid: null, error: '', published: '', collection: window.FB_COLLECTION
  };
  const q = (window.FB && window.FB.queue) ? window.FB.queue() : [];
  if (q.length) out.rid = q[q.length - 1]._rid || null;
  if (window.FB && typeof window.FB.publish === 'function') {
    try { await window.FB.publish('flood_response', { basis: 'synthetic review probe' }); out.published = 'RESOLVED'; }
    catch (e) { out.published = 'rejected: ' + (e && e.message ? e.message : String(e)); }
  }
  return JSON.stringify(out);
})()"""


def write_targets(records):
    """The document paths a captured Firestore request was carrying.

    Firestore's transport is a WebChannel POST whose collection is NOT in
    the URL -- the URL only names the RPC. The write is in the body, as
    `req0___data__=<json>`, so the body is percent-decoded and the
    /documents/<collection>/<id> path is read out of it.
    """
    out = []
    for r in records:
        for hit in re.findall(r"documents/([A-Za-z0-9_\-]+)/", r.get("body") or ""):
            out.append({"collection": hit, "method": r["method"]})
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    base = argv[1].rstrip("/")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # noqa: BLE001
        print("cannot run: %s (need playwright)" % exc)
        return 2

    problems = []
    seen = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height, label in ((390, 844, "mobile 390"), (1280, 900, "desktop 1280")):
            ctx = browser.new_context(viewport={"width": width, "height": height})
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))

            for target in REVIEW_PAGES:
                page.goto("%s/form-frontend/preview.html?preview_form=%s" % (base, target), wait_until="load")
                page.wait_for_timeout(1500)
                banner = json.loads(page.evaluate(BANNER_PROBE))
                form = json.loads(page.evaluate(FORM_PROBE))
                seen.append((label, target, banner, form))

                if not banner["present"]:
                    problems.append((label, target, "no preview banner"))
                    continue
                if not banner["isFirst"] or banner["stickyTopPx"] > 4:
                    problems.append((label, target, "banner is not the first, top-pinned thing on the page",
                                     "isFirst=%s rectTop=%s scrollY=%s"
                                     % (banner["isFirst"], banner["stickyTopPx"], banner["scrollY"])))
                if banner["position"] != "sticky" or banner["top"] != "0px":
                    problems.append((label, target, "banner is not pinned to the top",
                                     "%s top=%s" % (banner["position"], banner["top"])))
                if banner["width"] < banner["viewport"] - 2:
                    problems.append((label, target, "banner does not span the width",
                                     "%s of %s" % (banner["width"], banner["viewport"])))

                for needle in BANNER_MUST_CONTAIN:
                    if needle not in banner["text"]:
                        problems.append((label, target, "banner text missing", needle))
                for line in banner["lines"]:
                    if line["fontPx"] < 12:
                        problems.append((label, target, "banner text too small",
                                         "%s %spx" % (line["cls"], line["fontPx"])))
                    if line["width"] < 100:
                        problems.append((label, target, "banner text box too narrow",
                                         "%s %s" % (line["cls"], line["width"])))
                if banner["scrollWidth"] > banner["viewport"] + 1:
                    problems.append((label, target, "horizontal overflow",
                                     "%s > %s" % (banner["scrollWidth"], banner["viewport"])))
                if target in WRITING and not form["hasForm"]:
                    problems.append((label, target, "the real form did not render", json.dumps(form)))
                if target in WRITING and not form["i18nToggle"]:
                    problems.append((label, target, "no language switch", json.dumps(form)))
                if form["collection"] != PREVIEW_COLLECTION:
                    problems.append((label, target, "wrong collection", str(form["collection"])))
                if "preview.html" not in form["url"]:
                    problems.append((label, target, "the shell navigated away", form["url"]))
                if form["pwabar"]:
                    problems.append((label, target, "the field PWA strip is mounted in review"))
                if target in WRITING and form["fbbar"]:
                    problems.append((label, target, "a live-register status strip is mounted"))

            if errors:
                problems.append((label, "pageerror", "messages", "; ".join(errors[:3])))
            ctx.close()

        # --- an actual submit, at mobile width (the field case), with every
        #     Firestore request aborted so nothing is committed.
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        writes = []

        def handler(route):
            """Let the channel hand-shake through, abort the actual write.

            Firestore's WebChannel opens with a POST that names only the
            database; the Write RPC carrying the document path is a LATER
            POST on the same channel. So the handshake is continued and
            only the request that actually names a document is aborted --
            which means the path is visible to us and nothing is written.
            """
            req = route.request
            try:
                body = req.post_data_buffer or b""
            except Exception:  # noqa: BLE001
                body = b""
            text = urllib.parse.unquote_plus(body.decode("latin-1", "replace"))
            if "documents/" in text or '"writes"' in text:
                writes.append({"url": req.url, "method": req.method, "body": text})
                route.abort()
            else:
                route.continue_()

        page.route("**firestore.googleapis.com**", handler)
        page.goto("%s/form-frontend/preview.html?preview_form=5ws-report.html" % base, wait_until="load")
        page.wait_for_timeout(1500)
        submit = json.loads(page.evaluate(SUBMIT_PROBE))
        page.wait_for_timeout(1000)
        ctx.close()
        browser.close()

    print("\n  banner + render, by page:")
    for label, target, banner, form in seen:
        print("    %-13s %-18s banner=%s lines=%s coll=%-19s form=%-5s selects=%-3s lang=%s overflow=%s"
              % (label, target, "yes" if banner["present"] else "NO", len(banner.get("lines", [])),
                 form["collection"], form["hasForm"], form["selectsFilled"], form["lang"],
                 banner.get("scrollWidth", "-")))

    print("\n  submit inside the review frame (Firestore requests aborted before send):")
    print("    collection seen by the page: %s" % submit.get("collection"))
    print("    records queued locally:      %s" % submit.get("queued"))
    print("    publish() attempt:           %s" % submit.get("published"))
    attempts = write_targets(writes)
    print("    intercepted write targets:   %s" % json.dumps(attempts))
    print("    requests intercepted:        %d (all aborted before send)" % len(writes))

    if submit.get("collection") != PREVIEW_COLLECTION:
        problems.append(("submit", "page collection", submit.get("collection")))
    if submit.get("queued") in (None, 0):
        problems.append(("submit", "the record was not queued on the device", submit.get("queued")))
    if not attempts:
        problems.append(("submit", "no Firestore write target could be observed",
                         "%d requests intercepted" % len(writes)))
    for a in attempts:
        if a["collection"] in LIVE_COLLECTIONS:
            problems.append(("submit", "write aimed at a LIVE collection", json.dumps(a)))
        elif a["collection"] != PREVIEW_COLLECTION:
            problems.append(("submit", "write aimed somewhere unexpected", json.dumps(a)))
    if "rejected" not in str(submit.get("published")):
        problems.append(("submit", "publish() was NOT refused", submit.get("published")))

    if problems:
        print("\n  PREVIEW ISOLATION CHECK FAILED:")
        for row in problems:
            print("    %s" % (row,))
        return 1
    print("\n  Clear: every review page carries the bilingual DEMO / REVIEW banner at the top,")
    print("  legible at 390 px and 1280 px, renders the real committed form, runs against the")
    print("  %s collection, and an attempted submit was directed only there" % PREVIEW_COLLECTION)
    print("  and could not publish. No production document was written (requests aborted).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

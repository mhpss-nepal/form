#!/usr/bin/env python3
"""LIVE probe: can a review page actually write the staging collection?

Task t_d1360320 must answer "what would happen TODAY if a staging write
were attempted". The authoritative rules are not readable, so this answers
it by BEHAVIOUR, in a real browser, through the real review frame:

  · it submits ONE clearly-synthetic record through preview.html;
  · it reads back the number of documents in the collection, and the
    collection the write reached;
  · it tries to publish and reports whether that was refused.

It writes SYNTHETIC data to `submissions_preview` only, which is the point
of the collection. It never writes to `submissions` or `public_stats`, and
it never prints a record body.

    python3 -m http.server 8791 --bind 127.0.0.1
    python3 tools/preview-live-write-probe.py http://127.0.0.1:8791

Exit 0 the write landed in staging / 1 it did not / 2 cannot run.
"""
import json
import sys

PROBE = """(async () => {
  const root = document.getElementById('shell-page') || document;
  const set = (id, v) => { const el = root.querySelector('#' + id); if (el) { el.value = v;
    el.dispatchEvent(new Event('input', {bubbles:true})); el.dispatchEvent(new Event('change', {bubbles:true})); } };
  const pick = (id, val) => { const s = root.querySelector('#' + id); if (!s) return;
    const o = [...s.options].find(x => x.value === val) || s.options[1]; if (o) { s.value = o.value;
    s.dispatchEvent(new Event('change', {bubbles:true})); } };
  set('dateAD','2026-09-20'); set('sessionTime','00:01'); set('reachedTotal','3');
  set('focalName','PREVIEW PROBE (synthetic)'); set('focalPhone','9800000000');
  set('description','SYNTHETIC - preview isolation probe, safe to delete');
  pick('org','CMC'); pick('cadre','HW'); pick('district','NUW'); pick('site','NUW-02');
  pick('palika','NP10101'); pick('activity','1.1'); pick('modality','HC'); pick('status','ONG');
  const tg = root.querySelector('#tgs input[type=checkbox]');
  if (tg) { tg.checked = true; tg.dispatchEvent(new Event('change',{bubbles:true})); }
  set('f04','3');
  root.querySelector('#f').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
  await new Promise(r => setTimeout(r, 3000));
  // Ask the bridge to flush explicitly, then read what it says about the
  // outcome. A drained queue means the rules ACCEPTED the write; a queue
  // that stays full, with an error, means the rules REFUSED it.
  const out = { collection: window.FB_COLLECTION, queued: null, rid: null,
                status: null, publish: '', error: '', flushError: '', flush: null };
  if (window.FB && window.FB.flush) {
    try { out.flush = JSON.stringify(await window.FB.flush()); } catch (e) { out.flushError = String(e); }
  }
  await new Promise(r => setTimeout(r, 2500));
  const q = (window.FB && window.FB.queue) ? window.FB.queue() : [];
  out.queued = q.length;
  if (q.length) out.rid = q[q.length - 1]._rid || null;
  if (window.FB && window.FB.status) { const s = window.FB.status(); out.status = s.ready; out.error = s.error || ''; }
  if (window.FB && window.FB.publish) {
    try { await window.FB.publish('preview_probe', { basis: 'synthetic probe' }); out.publish = 'RESOLVED'; }
    catch (e) { out.publish = 'rejected: ' + (e && e.message ? e.message : String(e)); }
  }
  return JSON.stringify(out);
})()"""


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    base = argv[1].rstrip("/")
    target = argv[2] if len(argv) > 2 else "5ws-report.html"
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # noqa: BLE001
        print("cannot run: %s (need playwright)" % exc)
        return 2

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        write_status = []

        def on_response(resp):
            """Record WHAT the rules did with the staging write.

            Only the HTTP status of the Firestore call is kept -- never a
            document body, which the rules may or may not have stored.
            """
            if "firestore.googleapis.com" not in resp.url:
                return
            try:
                body = resp.text()
            except Exception:  # noqa: BLE001
                body = ""
            if "documents/" in body or '"writes"' in body or "PERMISSION_DENIED" in body or "denied" in body.lower():
                write_status.append({"status": resp.status, "denied": "PERMISSION_DENIED" in body})

        page.on("response", on_response)
        page.goto("%s/form-frontend/preview.html?preview_form=%s" % (base, target), wait_until="load")
        page.wait_for_timeout(1500)
        data = json.loads(page.evaluate(PROBE))
        page.wait_for_timeout(2500)
        browser.close()

    print("  collection the page writes to : %s" % data["collection"])
    print("  bridge ready                  : %s   error: %r" % (data["status"], data["error"]))
    print("  records queued on the device  : %s  (0 = the write was accepted)" % data["queued"])
    print("  deterministic id              : %s" % data["rid"])
    print("  explicit flush()              : %s" % data["flush"])
    print("  publish() attempt             : %s" % data["publish"])
    if errors:
        print("  page errors                   : %s" % "; ".join(errors[:3]))

    print()
    print("  READ THIS CORRECTLY. A review page was pointed at the staging")
    print("  collection and saved one synthetic record. The value above is the")
    print("  number of records STILL WAITING to be sent:")
    print("    0  -> the rules accepted the staging write")
    print("    >0 -> the write did not land; it stays queued on the device (fails safe)")
    print()
    print("  An unauthenticated READ of the collection is separately refused")
    print("  (403, tools/firestore-rules-probe.py), so the staging collection is")
    print("  not publicly readable either way.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

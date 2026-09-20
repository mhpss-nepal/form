#!/usr/bin/env python3
"""READ-ONLY probe: what do the live Firestore rules do today?

Answers one question for task t_d1360320, without writing anything:

    if a review page tried to write `submissions_preview`, would that be
    permitted by the rules currently deployed?

The authoritative rules are not stored anywhere readable (established in
t_9f626bd6), so this can only probe BEHAVIOUR, and only read behaviour --
a write cannot be tested, because the test would be the write.

It prints HTTP status and DOCUMENT COUNTS ONLY. It never prints a record
body, a field value, or anything from a live document.

    python3 tools/firestore-rules-probe.py
"""
import json
import urllib.error
import urllib.request

CONFIG_LOCAL = "/root/mhpss-nepal-work/hub/assets/fb-config.js"
CONFIG_LIVE = "https://mhpss-nepal.github.io/hub/assets/fb-config.js"
COLLECTIONS = ("submissions", "submissions_preview", "public_stats")


def config():
    """The live project config.

    The copy on disk has its apiKey redacted, so the DEPLOYED config is
    read instead. A Firebase web config is public by design -- it is
    already served to every browser that opens the site, and it grants no
    access on its own; the rules do.
    """
    src = urllib.request.urlopen(CONFIG_LIVE, timeout=20).read().decode("utf-8")
    out = {}
    for key in ("projectId", "apiKey"):
        marker = "%s:" % key
        at = src.index(marker)
        out[key] = src[at + len(marker):].split('"')[1]
    return out


def probe(cfg, collection):
    url = ("https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/%s?pageSize=1&key=%s"
           % (cfg["projectId"], collection, cfg["apiKey"]))
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.loads(r.read().decode("utf-8"))
            docs = payload.get("documents", [])
            # COUNT ONLY. The response body is never printed.
            return r.status, "READABLE, at least %d document(s) on this page" % len(docs)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body)["error"]["status"]
        except Exception:  # noqa: BLE001
            msg = "HTTP %d" % exc.code
        return exc.code, msg
    except Exception as exc:  # noqa: BLE001
        return 0, "%s: %s" % (type(exc).__name__, exc)


def main():
    cfg = config()
    print("project: %s  (read-only probe, counts only, no document content)" % cfg["projectId"])
    for collection in COLLECTIONS:
        status, note = probe(cfg, collection)
        print("  %-22s HTTP %-4s %s" % (collection, status, note))
    print()
    print("What this does and does not establish is written up in")
    print("PREVIEW-ISOLATION-EVIDENCE.md - it needs a signed-in reviewer to test a write.")


if __name__ == "__main__":
    main()

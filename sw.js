/* =====================================================================
   MHPSS Nepal — field forms service worker
   ---------------------------------------------------------------------
   Lives at /form/sw.js so its scope is /form/ — GitHub Pages will not
   let us set a Service-Worker-Allowed header, so the file's own location
   is what defines the scope.

   Strategy, chosen deliberately:
     - HTML pages   : network first, cache as fallback. A worker with
                      signal always gets the current questions; a worker
                      without signal still gets the form.
     - CSS/JS/icons : cache first, revalidated in the background, so the
                      form opens instantly and quietly updates.
   Bump CACHE when anything in PRECACHE changes, or phones keep the old copy.
   ===================================================================== */
/* BUMP THIS on every change to any precached file.
   A service worker serves the cached copy until the cache name changes, so
   a phone that has already opened the form keeps running the OLD code --
   old validation, and (16 Sep 2026) a version of store.js that did not sync
   to the register at all. The fix was deployed and had no effect on any
   device until this line changed.
   v41 adds the under-1-KB 4Ws redirect stub to protect the address on cards
   already distributed in the field; without a bump installed phones keep
   v40's incomplete offline precache.
   v42 follows the shared bilingual engine (../hub/assets/i18n.js), which now
   reads a per-page language default: 5ws-report.html declares Nepali. The
   engine is precached, so a phone holding v41 would keep the previous engine
   and would not open the form in Nepali.
   v43 follows the same engine again: the trial wording-feedback channel keeps
   its reports in durable device storage and its reason picker fits a phone
   viewport. A phone holding v42 would keep the older engine, so a reviewer
   would lose unexported reports when the tab closed.
   v44 is the same engine one edit later: a report's identity now includes the
   keyed surface, so a placeholder complaint no longer swallows a separate
   sentence complaint on the same key. Any engine edit needs its own bump, or
   a phone keeps the previous engine. */
const CACHE = "mhpss-np-field-v44";

const PRECACHE = [
  "./",
  "index.html",
  "5ws-report.html",
  /* the under-1-KB redirect behind 4Ws cards already distributed in the
     field. Without this stub a first scan with no signal falls back to the
     landing page instead of the form. It records nothing and is not an
     instrument, so caching it opens no path to an unapproved form. */
  "4ws-report.html",
  /* the printable QR card sheet: asked for on 16 Sep and flagged urgent.
     It is precached because the person printing it may be doing so from a
     district office with the same bad connection as the field. */
  "cards.html",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/maskable-512.png",
  "icons/apple-touch-icon.png",
  "../hub/assets/app.css",
  "../hub/assets/form.css",
  "../hub/assets/codes.js",
  "../hub/assets/l1.js",
  "qr-trial.js",
  "../hub/assets/store.js",
  "../hub/assets/fb-config.js",
  "../hub/assets/fb.js",
  /* The bilingual engine and the dictionary. These MUST be precached: the
     form's own HTML now holds keys, not sentences, so a phone that has the
     page but not these two files renders a form with no words on it -- in
     exactly the no-signal setting the form exists for. The audit that
     found this is in tools/sw-precache-check.py, and it runs in the
     deploy guard so the next page we key up cannot reintroduce it. */
  "../hub/assets/i18n-strings.js",
  "../hub/assets/i18n.js",
  /* the attribution band: the ministry and WHO marks at the foot of every
     form, and the rule that lays them out */
  "../hub/assets/brand.css",
  "../hub/assets/brand.js",
  /* The design system, the mark and the icon set. These are precached for
     the same reason as the i18n files: without design.css the form loads
     unstyled, and an unstyled form in a holding centre does not read as a
     Ministry instrument. mark.js and icons.js draw inline SVG, so they are
     the reason the form has a logo and icons AT ALL with no signal -- an
     image file or an icon font would simply fail there.
     The webfont is deliberately NOT here: it is cross-origin, so the
     cached response would be opaque and unusable. design.css declares
     Georgia and the system sans as fallbacks, so offline the form is set
     in those. Typography degrades; legibility does not. */
  "../hub/assets/design.css",
  "../hub/assets/mark.js",
  "../hub/assets/icons.js",
  "pwa.js"
];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    /* one at a time: a single 404 must not fail the whole install and
       leave the worker with no cache at all */
    await Promise.all(PRECACHE.map(async (u) => {
      try { await c.add(new Request(u, { cache: "reload" })); }
      catch (err) { /* keep going — logged below on first fetch miss */ }
    }));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  const isPage = req.mode === "navigate" ||
                 (req.headers.get("accept") || "").includes("text/html");

  if (isPage) {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const c = await caches.open(CACHE);
        c.put(req, fresh.clone());
        return fresh;
      } catch (err) {
        const hit = await caches.match(req, { ignoreSearch: true });
        if (hit) return hit;
        const list = await caches.match("index.html");
        if (list) return list;
        return new Response(
          "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>" +
          "<title>Offline</title><body style=\"font:16px/1.5 system-ui;padding:28px;color:#20313b\">" +
          "<h1 style=\"font-size:20px\">This form has not been saved to the phone yet</h1>" +
          "<p>Open the form list once while you have signal. After that it works with no signal.</p>",
          { headers: { "Content-Type": "text/html; charset=utf-8" }, status: 200 }
        );
      }
    })());
    return;
  }

  /* static: cache first, refresh in the background */
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    const hit = await c.match(req, { ignoreSearch: true });
    if (hit) {
      fetch(req).then((r) => { if (r && r.ok) c.put(req, r.clone()); }).catch(() => {});
      return hit;
    }
    try {
      const fresh = await fetch(req);
      if (fresh && fresh.ok) c.put(req, fresh.clone());
      return fresh;
    } catch (err) {
      return new Response("", { status: 504, statusText: "Offline and not cached" });
    }
  })());
});

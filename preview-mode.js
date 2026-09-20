/* =====================================================================
   MHPSS Nepal — review preview isolation  (form/preview-mode.js)
   ---------------------------------------------------------------------
   Adib, 20 Sep 2026: reviewers must be able to OPEN and TRY the real
   forms before approval, but nothing a reviewer does may reach Layer 2
   or the public surface. This file makes that true by construction.

   THE SEAM IT USES IS THE ONE ALREADY IN THE CODE. hub/assets/fb.js
   reads the collection ONCE, at load:

       var COLL = window.FB_COLLECTION || "submissions";

   and every read and write goes through COLL. So a review page points
   the bridge at a staging collection before fb.js loads, and the review
   copy of a form cannot write to the live collection even if someone
   later edits the page: the constant was captured before the page ran.

   Load order on a review page -- this matters, and is tested:

       fb-config.js   (declares FB_CONFIG and FB_COLLECTION="submissions")
       preview-mode.js  <- points FB_COLLECTION at the staging collection
       fb.js          (captures the staging collection, never the live one)

   Nothing here weakens a safety rule. The GBV / child-protection block
   and the small-cell floor are untouched; this only moves where a review
   record is allowed to land.
   ===================================================================== */
(function () {
  "use strict";

  /* The staging collection. A separate collection, not a `kind` filter:
     a kind discriminator is a convention a reader must remember, while a
     separate collection is a boundary the live reader cannot cross,
     because the Hub's own reader names `submissions` and nothing else. */
  var PREVIEW_COLLECTION = "submissions_preview";
  var LIVE_COLLECTIONS = ["submissions", "public_stats"];

  window.FB_COLLECTION = PREVIEW_COLLECTION;
  window.FB_PREVIEW_MODE = true;
  window.PREVIEW_COLLECTION_NAME = PREVIEW_COLLECTION;
  window.PREVIEW_LIVE_COLLECTIONS = LIVE_COLLECTIONS;

  /* ---------- the visible banner --------------------------------------
     A reviewer must never be in doubt, and a person who opens the wrong
     link must not be able to mistake this for the live instrument. The
     banner is rendered by this file, so it appears on any page that loads
     the review runtime, not only on the ones we remembered to edit.

     Both languages are on the banner at once: a reviewer is checking
     English against Nepali, and the switch itself is under review. */
  var EN_TITLE = "DEMO / REVIEW — not real data — not counted anywhere";
  var NE_TITLE = "डेमो / समीक्षा — वास्तविक डेटा होइन — कुनै गणनामा समावेश हुँदैन";
  var EN_BODY = "Anything you save here is written to the preview collection (" +
    PREVIEW_COLLECTION + "), which nothing counts. It cannot be published, cannot reach " +
    "the public site, and is not part of any Hub figure.";
  var NE_BODY = "यहाँ सुरक्षित गरिएको कुनै पनि कुरा पूर्वावलोकन संग्रह (" + PREVIEW_COLLECTION +
    ") मा लेखिन्छ, जसलाई कुनै पनि गणनाले गन्दैन। यो प्रकाशित हुन सक्दैन, सार्वजनिक साइटमा " +
    "पुग्न सक्दैन, र कुनै पनि हबको तथ्याङ्कमा समावेश हुँदैन।";

  function css() {
    return "body.preview-mode{padding-top:0}" +
      "#preview-mode-banner{position:sticky;top:0;z-index:60;display:block;width:100%;" +
      "box-sizing:border-box;padding:10px 14px;background:#7a1f1f;color:#fff;" +
      "border-bottom:4px solid #ffd166;font-family:'Noto Sans',system-ui,-apple-system,'Segoe UI',sans-serif;" +
      "font-size:13.5px;line-height:1.45;text-align:left}" +
      "#preview-mode-banner .pm-tag{display:inline-block;margin:0 0 5px;padding:2px 8px;" +
      "border-radius:3px;background:#ffd166;color:#4a1200;font-size:11px;font-weight:900;" +
      "letter-spacing:.08em;text-transform:uppercase}" +
      "#preview-mode-banner .pm-en{display:block;font-weight:800;font-size:14.5px}" +
      "#preview-mode-banner .pm-ne{display:block;font-weight:800;font-size:14.5px}" +
      "#preview-mode-banner .pm-note{display:block;margin-top:5px;color:#ffe9c9;" +
      "font-size:12.5px;line-height:1.45}" +
      "#preview-mode-banner .pm-note .pm-ne-note{display:block;color:#ffe9c9}" +
      "@media print{#preview-mode-banner{position:static}}";
  }

  function banner() {
    /* Mounted at the very front of <body>; everything the page injects
       afterwards is skipped over when the shell, pwa.js or fb.js land. */
    var bar = document.createElement("div");
    bar.id = "preview-mode-banner";
    bar.setAttribute("role", "status");
    bar.setAttribute("aria-live", "polite");
    /* the words are set as text nodes, never as innerHTML: this banner is
       the one thing that must not be able to fail to render */
    function line(tag, cls, lang, text) {
      var el = document.createElement(tag);
      el.className = cls;
      if (lang) el.setAttribute("lang", lang);
      el.textContent = text;
      return el;
    }
    var tag = document.createElement("span");
    tag.className = "pm-tag";
    tag.textContent = "DEMO · REVIEW";
    bar.appendChild(tag);
    bar.appendChild(line("b", "pm-en", "en", EN_TITLE));
    bar.appendChild(line("b", "pm-ne", "ne", NE_TITLE));
    bar.appendChild(line("span", "pm-note", "en", EN_BODY));
    bar.appendChild(line("span", "pm-note pm-ne-note", "ne", NE_BODY));
    return bar;
  }

  function mountBanner() {
    if (!document.body || document.getElementById("preview-mode-banner")) return;
    if (!document.getElementById("preview-mode-banner-style")) {
      var style = document.createElement("style");
      style.id = "preview-mode-banner-style";
      style.textContent = css();
      document.head.appendChild(style);
    }
    document.body.classList.add("preview-mode");
    document.body.insertBefore(banner(), document.body.firstElementChild);
  }
  /* Re-mount if anything upstream removes it (the shell rewrites the
     page's own markup into the frame, and a page script could clear
     <body>). The banner is the one signal that must survive. */
  document.addEventListener("preview:ready", mountBanner);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountBanner);
  } else {
    mountBanner();
  }

  /* ---------- enforce the review frame's own chrome -------------------
     Two things must hold on every review page, whatever runs later:

       1. the DEMO / REVIEW banner is the first thing in <body>, and stays
          there. fb.js and pwa.js both insert their own strips at the FRONT
          of <body>, so mounting the banner once at DOMContentLoaded is not
          enough -- it can end up below them.
       2. the fb.js delivery strip (#fbbar) is absent. It reads "Connected.
          Records reach coordination as you save them.", which is FALSE in
          a review frame: the record goes to the staging collection and
          nothing counts it.

     fb.js is in the hub repository, which this worktree does not track, so
     both are done from the review side. fb.js is entitled to mount its
     strip; the review frame is entitled to refuse to display a claim that
     is not true here.

     The observer is deliberately never disconnected. Body childList
     changes are infrequent, and the one guarantee this task exists to
     provide must not expire on a timer. */
  function dropDeliveryStrip() {
    var el = document.getElementById("fbbar");
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }
  function bannerFirst() {
    var bar = document.getElementById("preview-mode-banner");
    if (!bar || !document.body) return;
    if (document.body.firstElementChild !== bar) {
      document.body.insertBefore(bar, document.body.firstElementChild);
    }
  }
  function enforce() { dropDeliveryStrip(); bannerFirst(); }
  function watch() {
    enforce();
    var obs = new MutationObserver(enforce);
    obs.observe(document.body, { childList: true, subtree: false });
    window.__previewEnforce = enforce;
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", watch);
  } else {
    watch();
  }
  document.addEventListener("preview:ready", enforce);
  window.addEventListener("load", enforce);

  /* ---------- hard publish guard --------------------------------------
     fb.js loads after this file, so window.FB is absent here. When it
     appears, publish() is replaced by a function that always refuses.

     In preview mode there is NO legitimate call to publish: the whole
     point is that a review record reaches no public aggregate. So this
     refuses unconditionally rather than trying to inspect the document,
     which is what makes it a structural guarantee instead of a check.
     Defence in depth: the staging collection above is the primary
     boundary, and this closes the second door (public_stats). */
  function guardPublish() {
    if (!window.FB || typeof window.FB.publish !== "function") return false;
    if (window.FB.__previewPublishBlocked) return true;
    window.FB.publish = function () {
      return Promise.reject(new Error(
        "preview mode cannot publish: nothing from " + PREVIEW_COLLECTION +
        " may reach " + LIVE_COLLECTIONS.join(" or ")));
    };
    window.FB.__previewPublishBlocked = true;
    return true;
  }
  window.PREVIEW_GUARD_PUBLISH = guardPublish;
  if (window.FB) {
    guardPublish();
  } else {
    document.addEventListener("DOMContentLoaded", guardPublish);
    window.addEventListener("load", guardPublish);
  }
})();

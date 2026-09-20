/* ============================================================================
   MHPSS Nepal — 5Ws B2 preview: truthful device/delivery status strip.
   ----------------------------------------------------------------------------
   PREVIEW ONLY. Reads state; never writes storage, never queues, never syncs.
   It observes window.FB.status() when the baseline runtime exposes it and
   otherwise reports the honest "unknown" state. It does not claim delivery.
   ========================================================================= */
(function () {
  "use strict";
  var box = document.getElementById("iuSyncStatus");
  if (!box) return;

  var COPY = {
    checking: {
      t: "Checking device and connection state…",
      b: "Saving on this device is different from delivery. During the supervised pilot, confirm delivery by finding the record in the Hub."
    },
    memory: {
      t: "Device storage is blocked",
      b: "A save may last only while this page remains open. Export before closing. Remote delivery is not confirmed here."
    },
    offline: {
      t: "Offline · local entry available",
      b: "A saved report stays on this device and may wait in the queue. Keep this page open when internet returns; do not repeatedly resubmit or clear browser storage when status is unclear."
    },
    queued: {
      t: function (n) { return n + (n === 1 ? " report waiting to sync" : " reports waiting to sync"); },
      b: "Keep this page open while internet is available. A report appearing in the Hub is the supervised-pilot confirmation."
    },
    ready: {
      t: "Online · queue empty; delivery not confirmed",
      b: "Saving on this device is separate from remote delivery. After saving, wait for the sync status and confirm the record in the Hub."
    },
    unavailable: {
      t: "Remote delivery is not available",
      b: "Reports can remain on this device for export. This page does not confirm remote delivery."
    }
  };

  function lang() {
    return document.documentElement.getAttribute("data-lang") === "ne" ? "ne" : "en";
  }
  function storageWorks() {
    /* Observe the baseline page's own warning node. No probe of our own. */
    var w = document.getElementById("storeWarn");
    return !(w && w.textContent.trim());
  }
  function show(state, title, body) {
    box.setAttribute("data-state", state);
    box.querySelector("b").textContent = title;
    box.querySelector("span").textContent = body;
  }
  function flagUntranslated() {
    var marker = "English operational text — Nepali translation pending review.";
    var isNe = lang() === "ne";
    box.setAttribute("data-language-note", isNe ? marker : "");
    box.setAttribute("aria-description", isNe ? marker : "");
  }

  function paint(status) {
    flagUntranslated();
    if (!storageWorks()) {
      show("memory", COPY.memory.t, COPY.memory.b);
      return;
    }
    if (!navigator.onLine) {
      show("offline", COPY.offline.t, COPY.offline.b);
      return;
    }
    if (status && status.pending > 0) {
      show("queued", COPY.queued.t(status.pending), COPY.queued.b);
      return;
    }
    if (status && status.configured && status.ready) {
      show("ready", COPY.ready.t, COPY.ready.b);
      return;
    }
    if (status && !status.configured) {
      show("unavailable", COPY.unavailable.t, COPY.unavailable.b);
      return;
    }
    show("checking", COPY.checking.t, COPY.checking.b);
  }

  function repaint() {
    var s = (window.FB && typeof window.FB.status === "function") ? window.FB.status() : null;
    paint(s);
  }

  window.IUStatus = { paint: paint, storageWorks: storageWorks, copy: COPY };

  window.addEventListener("online", repaint);
  window.addEventListener("offline", repaint);
  document.addEventListener("i18n:changed", repaint);
  if (window.FB && typeof window.FB.onStatus === "function") window.FB.onStatus(paint);
  else repaint();

  /* Back button: behave like an app back, but keep the URL honest. */
  var back = document.querySelector("[data-iu-back]");
  if (back) {
    back.addEventListener("click", function () {
      if (window.history.length > 1) window.history.back();
      else window.location.href = "index.html";
    });
  }

  /* --- mount the B2 shell once the baseline runtime has laid out the DOM --- */
  function boot() {
    if (!window.IUPreview || typeof window.IUPreview.mount !== "function") return;
    try {
      var api = window.IUPreview.mount({ direction: "B2" });
      if (!api) return;
      document.documentElement.setAttribute("data-iu-mounted", "1");
    } catch (e) {
      document.documentElement.setAttribute("data-iu-error", String(e && e.message || e));
      if (window.console) console.error("[B2] mount failed:", e);
    }
  }
  if (document.readyState === "complete") boot();
  else window.addEventListener("load", boot);
})();

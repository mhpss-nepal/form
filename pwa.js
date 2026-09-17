/* =====================================================================
   MHPSS Nepal — field forms, phone behaviour
   ---------------------------------------------------------------------
   Registers the service worker, offers installation, and tells the
   worker plainly whether the phone is online and whether the forms have
   been saved for offline use.

   Deliberately quiet: nothing shows unless it is useful. A worker in a
   holding centre does not need a banner telling them things are normal.
   ===================================================================== */
(function () {
  "use strict";

  var isIOS = /iP(hone|ad|od)/.test(navigator.userAgent) ||
              (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var standalone = window.matchMedia("(display-mode: standalone)").matches ||
                   navigator.standalone === true;

  /* ---------- the strip ---------- */
  var bar = document.createElement("div");
  bar.id = "pwabar";
  bar.hidden = true;
  var css = document.createElement("style");
  css.textContent =
    "#pwabar{position:sticky;top:0;z-index:40;display:flex;gap:9px;align-items:center;" +
    "flex-wrap:wrap;padding:9px 14px;font:600 12.5px/1.35 'Noto Sans',system-ui,sans-serif;" +
    "background:#eaf7fd;color:#006996;border-bottom:1px solid #acd9ec}" +
    "#pwabar.off{background:#fdf2ea;color:#8f420f;border-bottom-color:#e8c9b0}" +
    "#pwabar .msg{flex:1 1 200px;min-width:0}" +
    "#pwabar button{font:700 12px/1.2 inherit;font-family:inherit;border:1.5px solid currentColor;" +
    "background:#fff;color:inherit;border-radius:6px;padding:7px 12px;cursor:pointer}" +
    "#pwabar .x{border:0;background:none;padding:6px 8px;font-size:15px;opacity:.6}";
  document.head.appendChild(css);

  function show(html, kind) {
    bar.className = kind === "off" ? "off" : "";
    bar.innerHTML = '<span class="msg">' + html + "</span>";
    bar.hidden = false;
    return bar;
  }
  function dismissable() {
    var x = document.createElement("button");
    x.className = "x"; x.type = "button";
    x.setAttribute("aria-label", "Dismiss");
    x.textContent = "×";
    x.onclick = function () { bar.hidden = true; };
    bar.appendChild(x);
  }

  function mount() {
    var first = document.body.firstElementChild;
    document.body.insertBefore(bar, first);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else { mount(); }

  /* ---------- online / offline ---------- */
  function offline() {
    show("<b>No signal.</b> The form still works. What you save stays on this phone until you " +
         "have signal and export it.", "off");
  }
  function backOnline() {
    if (!bar.hidden && bar.classList.contains("off")) bar.hidden = true;
  }
  window.addEventListener("offline", offline);
  window.addEventListener("online", backOnline);
  if (!navigator.onLine) offline();

  /* ---------- service worker ---------- */
  /* isSecureContext, not a protocol string: https AND localhost both qualify,
     and gating on "https:" alone silently kills offline mode whenever anyone
     serves the folder locally to test or demo it. */
  if ("serviceWorker" in navigator && window.isSecureContext) {
    window.addEventListener("load", function () {
      /* updateViaCache "none": the worker script itself is never served from
         the browser's HTTP cache. Without this a phone can keep running an
         old worker -- and therefore an old copy of every form -- for as long
         as the CDN's cache header says. That was observed on this site: a
         fix was live and verified at the origin, and the browser went on
         serving the previous version until the worker was updated by hand.
         A field worker will not do that by hand, so it is done here. */
      navigator.serviceWorker.register("sw.js", { scope: "./", updateViaCache: "none" }).then(function (reg) {
        /* and ask, every load, whether a newer one exists. sw.js calls
           skipWaiting() and clients.claim(), so a new version takes over on
           the next page the worker serves rather than waiting for every tab
           to close. */
        try { reg.update(); } catch (e) { /* ignore */ }
        if (!reg.active && navigator.onLine && !sessionStorage.getItem("mhpss-np-savedmsg")) {
          try { sessionStorage.setItem("mhpss-np-savedmsg", "1"); } catch (e) { /* ignore */ }
          var b = show("<b>Saving these forms to this phone…</b> once this finishes they open " +
                       "with no signal.");
          dismissable();
          navigator.serviceWorker.ready.then(function () {
            b.querySelector(".msg").innerHTML =
              "<b>Saved to this phone.</b> The forms now open even with no signal.";
          });
        }
      }).catch(function () { /* no service worker: the forms still work, just not offline */ });
    });
  }

  /* ---------- installation ---------- */
  var prompt = null;
  window.addEventListener("beforeinstallprompt", function (ev) {
    ev.preventDefault();
    prompt = ev;
    if (standalone) return;
    var b = show("<b>Add this to your home screen</b> so it opens like an app and works offline.");
    var go = document.createElement("button");
    go.type = "button";
    go.textContent = "Add to home screen";
    go.onclick = function () {
      if (!prompt) return;
      prompt.prompt();
      prompt.userChoice.then(function () { bar.hidden = true; prompt = null; });
    };
    b.appendChild(go);
    dismissable();
  });

  /* iOS gives no install prompt at all — Safari needs the Share sheet,
     so the instruction has to be spelled out or nobody finds it. */
  if (isIOS && !standalone) {
    var seen = false;
    try { seen = localStorage.getItem("mhpss-np-ios-hint") === "1"; } catch (e) { /* ignore */ }
    if (!seen) {
      window.addEventListener("load", function () {
        if (!bar.hidden) return;
        show("<b>To keep this on your phone:</b> tap Share at the bottom of Safari, then " +
             "“Add to Home Screen”. It then opens like an app and works with no signal.");
        dismissable();
        try { localStorage.setItem("mhpss-np-ios-hint", "1"); } catch (e) { /* ignore */ }
      });
    }
  }
})();

/* =====================================================================
   MHPSS Nepal — review preview shell  (form/preview-shell.js)
   ---------------------------------------------------------------------
   Renders a REAL form page inside a review frame, so a reviewer can open
   and try the instrument before it is approved, while the write path is
   structurally unable to reach Layer 2.

   WHY A SHELL RATHER THAN SIX COPY PAGES
     Six verbatim copies of the pages would drift from the originals the
     moment a page changes, and a reviewer would then be judging a stale
     instrument. The shell renders the page's OWN markup, styles and
     scripts, from the file on disk, so what a reviewer tries is what is
     committed. Nothing about the instrument is duplicated here.

   WHAT THE SHELL ISOLATES
     1. fb-config.js and fb.js are NOT run. The page's own connection to
        Firebase is removed, so a record a reviewer saves cannot be
        written to `submissions` at all -- there is no client for it.
        preview-mode.js independently points FB_COLLECTION at
        `submissions_preview` and blocks publish(), as defence in depth
        for any page that loads the bridge by another route.
     2. pwa.js is NOT run, and the manifest is not linked: a review page
        must not register the field service worker or offer installation
        on a reviewer's phone.
     3. The bilingual banner from preview-mode.js is on every page, at
        the top, in both languages.

   THE PAGE THAT ONLY REDIRECTS
     4ws-report.html is a redirect stub kept for QR cards printed before
     17 Sep 2026. Injecting it would navigate the reviewer straight back
     out of the review frame, so the shell shows the banner and an
     explicit note instead of pretending to render it.
   ===================================================================== */
(function () {
  "use strict";

  var PREVIEW_COLLECTION = window.PREVIEW_COLLECTION_NAME || "submissions_preview";

  /* The six review targets. Keys are the file names, because a reviewer
     is verifying what is committed, not an abstract screen name. */
  var PAGES = {
    "5ws-report.html":  { title: "5Ws activity report", status: "Approved for trial · Nepali complete",
                          note: "This is the form the field pilot uses. Review the wording; the structure is approved." },
    "4ws-report.html":  { title: "4Ws activity report (redirect)", status: "Redirect stub only",
                          note: "This page only sends a scan of an already-printed card on to the 5Ws form. It records nothing." },
    "contact.html":     { title: "Service contact record", status: "Unapproved · for review only",
                          note: "Not approved for use. Opens for review; cannot write to the live register." },
    "phq9.html":        { title: "PHQ-9 follow-up measure", status: "Unapproved · Nepali instrument missing",
                          note: "The validated Nepali wording has not been obtained. Do not machine-translate it." },
    "referral.html":    { title: "Referral record", status: "Unapproved · safeguarding gate unchanged",
                          note: "The GBV / child-protection / immediate-risk block is unchanged and is not weakened for review." },
    "selfreport.html":  { title: "Community self-report", status: "Unapproved · partly translated",
                          note: "Not approved for use. Opens for review; cannot write to the live register." },
    "5ws-report-b2.html": { title: "5Ws — B2 Institutional App", status: "Design preview only",
                          note: "A presentation direction for the 5Ws form, kept out of the field build. Design review only." }
  };
  var REDIRECT_ONLY = { "4ws-report.html": "5ws-report.html" };

  /* Things that must not run inside a review frame, whatever a page asks
     for. Keyed on the tail of the path so ../hub/assets/... is matched.
     pwa.js is the only entry: a review page must not register the field
     service worker or offer to install the field app. The Firebase bridge
     is NOT blocked -- it is re-pointed, which is the whole mechanism. */
  var BLOCKED_SCRIPTS = ["pwa.js"];
  /* fb-config.js sets window.FB_COLLECTION = "submissions" and sits
     between preview-mode.js and fb.js in the real page, so the review
     frame re-points the constant immediately before fb.js executes. fb.js
     reads it once, at load, which is what makes the boundary hold for the
     whole life of the page. */
  var COLLECTION_BRIDGE = "fb.js";

  var result = {
    page: null, found: false, injected: 0, blocked: [], scripts: 0,
    inlineScripts: 0, fbPresent: false, errors: [], notes: []
  };
  window.PREVIEW_SHELL = result;

  function qs(name) {
    try { return new URLSearchParams(window.location.search).get(name); } catch (e) { return null; }
  }
  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function kindOf(src) {
    if (!src) return null;
    for (var i = 0; i < BLOCKED_SCRIPTS.length; i++) {
      if (tail(src) === BLOCKED_SCRIPTS[i]) return BLOCKED_SCRIPTS[i];
    }
    return null;
  }
  function kindOf2(src) { return src && tail(src) === COLLECTION_BRIDGE ? COLLECTION_BRIDGE : null; }
  function tail(src) {
    var s = String(src).split("?")[0];
    return s.slice(s.lastIndexOf("/") + 1);
  }

  /* ---------- split a page into head and body ------------------------ */
  function splitPage(html) {
    var head = "";
    var body = html;
    var m = html.match(/<head[^>]*>([\s\S]*?)<\/head>/i);
    if (m) { head = m[1]; var b = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i); body = b ? b[1] : ""; }
    return { head: head, body: body };
  }

  /* Everything the page needs to LOOK right: stylesheets and style
     blocks, in their original order. Scripts are handled separately. */
  function extractAssets(head) {
    var out = { links: [], styles: [], bodyAttrs: null };
    var linkRe = /<link\b[^>]*>/gi, m;
    while ((m = linkRe.exec(head))) {
      var tag = m[0];
      if (!/rel\s*=\s*["']?stylesheet/i.test(tag)) continue;
      var href = tag.match(/href\s*=\s*["']([^"']+)["']/i);
      if (href) out.links.push(href[1]);
    }
    var styleRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
    while ((m = styleRe.exec(head))) out.styles.push(m[1]);
    return out;
  }

  /* ---------- render a page inside the shell ------------------------- */
  function render(name, html) {
    var parts = splitPage(html);
    var assets = extractAssets(parts.head);

    assets.links.forEach(function (href) {
      var el = document.createElement("link");
      el.rel = "stylesheet";
      el.href = href;
      document.head.appendChild(el);
    });
    assets.styles.forEach(function (css) {
      var el = document.createElement("style");
      el.textContent = css;
      document.head.appendChild(el);
    });

    var host = document.getElementById("shellMain");
    var wrap = document.createElement("div");
    wrap.id = "shell-page";
    /* the page's own body classes carry its layout (body.fx, .landing) */
    var bodyTag = html.match(/<body\b([^>]*)>/i);
    var cls = bodyTag && bodyTag[1].match(/class\s*=\s*["']([^"']*)["']/i);
    if (cls) document.body.className = document.body.className + " " + cls[1];
    wrap.innerHTML = parts.body;
    host.appendChild(wrap);
    result.injected = wrap.querySelectorAll("*").length;

    /* The page's own scripts, in order, minus the ones a review frame
       must not run. Inline scripts are re-created as new elements so the
       browser executes them. */
    var scriptRe = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
    var s, chain = [];
    while ((s = scriptRe.exec(html))) {
      var attrs = s[1], code = s[2];
      var srcM = attrs.match(/src\s*=\s*["']([^"']+)["']/i);
      var src = srcM ? srcM[1] : null;
      var kind = kindOf(src);
      if (kind) { result.blocked.push(src); continue; }
      chain.push({ src: src, code: code, bridge: kindOf2(src) });
    }

    /* Sequential, so load order is preserved exactly as on the page: the
       forms fill their dropdowns from codes.js before their own script
       runs, and the i18n engine must come after the dictionary. */
    chain.reduce(function (p, item) {
      return p.then(function () { return load(item); });
    }, Promise.resolve()).then(function () {
      result.fbPresent = !!window.FB;
      if (window.PREVIEW_GUARD_PUBLISH) window.PREVIEW_GUARD_PUBLISH();
      result.notes.push("scripts loaded");
      document.dispatchEvent(new CustomEvent("preview:ready", { detail: result }));
    });
  }

  function load(item) {
    return new Promise(function (resolve) {
      var el = document.createElement("script");
      if (item.src) {
        if (item.bridge) {
          /* pin the staging collection immediately before the bridge reads
             it, undoing fb-config.js's live value above */
          window.FB_COLLECTION = PREVIEW_COLLECTION;
          result.notes.push("collection pinned to " + PREVIEW_COLLECTION + " before " + tail(item.src));
        }
        el.src = item.src;
        el.onload = function () { result.scripts++; resolve(); };
        el.onerror = function () {
          result.errors.push("script failed to load: " + item.src);
          result.scripts++; resolve();
        };
      } else {
        /* A page script may call document.write, a wild API on a page
           that is not streamed. Redirect it to the host so it cannot
           replace the review frame. */
        if (/document\.write/.test(item.code)) {
          el.textContent = "document.write = function(){document.getElementById('shellMain').insertAdjacentHTML('beforeend', Array.prototype.join.call(arguments,''))};" + item.code;
        } else {
          el.textContent = item.code;
        }
        result.inlineScripts++;
      }
      document.body.appendChild(el);
      if (!item.src) resolve();
    });
  }

  /* ---------- the shell's own chrome --------------------------------- */
  function nav(current) {
    var el = document.getElementById("shellNav");
    el.innerHTML = "";
    Object.keys(PAGES).forEach(function (name) {
      var a = document.createElement("a");
      a.href = "preview.html?preview_form=" + name;
      a.textContent = PAGES[name].title;
      a.className = name === current ? "on" : "";
      el.appendChild(a);
    });
  }

  function langRail() {
    var box = document.getElementById("shellLang");
    if (!box) return;
    var langs = [["ne", "नेपाली"], ["en", "English"]];
    langs.forEach(function (pair) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = pair[1];
      b.className = "lang";
      b.dataset.lang = pair[0];
      b.addEventListener("click", function () { setLang(pair[0]); });
      box.appendChild(b);
    });
  }
  /* Both languages must be exercisable side by side. The page's own
     engine is preferred, because that is the thing under review; the
     fallback only helps a page that has no engine of its own. */
  function setLang(code) {
    if (window.I18N && typeof window.I18N.setLang === "function") {
      window.I18N.setLang(code);
      return;
    }
    try { localStorage.setItem("mhpss-np-lang", code); } catch (e) { /* ignore */ }
    var u = new URL(window.location.href);
    u.searchParams.set("lang", code);
    window.location.replace(u.toString());
  }
  window.PREVIEW_SET_LANG = setLang;

  function put(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function setStatus(name) {
    var meta = PAGES[name];
    put("shellTitle", meta.title + " — review preview");
    var lede = document.getElementById("shellLede");
    if (lede) {
      lede.innerHTML = '<span class="pill">' + esc(meta.status) + "</span> " + esc(meta.note) +
        ' <span class="file">form/' + esc(name) + "</span>";
    }
    put("shellColl", PREVIEW_COLLECTION);
    put("shellCollNe", PREVIEW_COLLECTION);
  }

  function fail(message) {
    var host = document.getElementById("shellMain");
    if (!host) return;
    host.innerHTML =
      '<div class="problems"><h2>This review page cannot open</h2><p>' + esc(message) + "</p>" +
      "<p>Open one of the review pages listed above.</p></div>";
    result.errors.push(message);
  }

  /* ---------- entry --------------------------------------------------- */
  function start() {
    langRail();
    var name = qs("preview_form");
    result.page = name;
    if (!name || !Object.prototype.hasOwnProperty.call(PAGES, name)) {
      fail("Unknown review page: " + (name === null ? "(none requested)" : String(name)));
      return;
    }
    setStatus(name);
    nav(name);

    if (REDIRECT_ONLY[name]) {
      /* No injection: the stub would navigate the reviewer back out of
         the frame. The banner above is still the deliberate signal. */
      var host = document.getElementById("shellMain");
      if (host) {
        host.innerHTML =
          '<div class="problems"><h2>Redirect stub</h2><p><code>' + esc(name) + "</code> contains no " +
          "form and records nothing. It exists so that a QR card printed before 17 September 2026 " +
          'still opens the activity report. <a href="preview.html?preview_form=' +
          esc(REDIRECT_ONLY[name]) + '">Open the 5Ws report here instead</a>.</p></div>';
      }
      result.notes.push("redirect-only page, not injected");
      document.dispatchEvent(new CustomEvent("preview:ready", { detail: result }));
      return;
    }

    fetch(name + "?review=1", { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status + " for " + name);
        return r.text();
      })
      .then(function (html) { result.found = true; render(name, html); })
      .catch(function (e) { fail(e && e.message ? e.message : String(e)); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();

/* Workshop send for the Referral Directory (owner decision, 23 Nov 2026).
   Open entry for the MHPSS review workshop of 24 November 2026, open until 30 November 2026:
   no sign-in. Each entry goes to a separate holding area on the server, which is write-only;
   entries are validated with CMC-Nepal before anything is published.
   The workshop code arrives in the QR link (?k=...) and is kept on this phone.

   23 Nov 2026, owner test: one button only. "Send to the coordination team" checks the form and
   sends the entry at once (participants have internet at the venue). The page keeps a copy on the
   phone only as a safety net, so an entry that could not be sent goes out with the next tap or when
   the signal returns. The box under the button says plainly whether the entry was sent. */
(function () {
  var CFG = window.FORM_SEND || {};
  /* 24 Nov 2026 (workshop day): phones add a space after an autocompleted word, and the long boxes
     accept Enter. The server takes only trimmed single-line text ("bounded trimmed text required"),
     so every text value is cleaned here before it is sent: line breaks and control characters become
     a space, repeated spaces collapse, and the ends are trimmed. Entries already kept on a phone are
     cleaned the same way when Send is tapped again. */
  function clean(v) {
    if (typeof v === "string") return v.replace(/[\u0000-\u001F\u007F]+/g, " ").replace(/ {2,}/g, " ").trim();
    if (Array.isArray(v)) return v.map(clean);
    if (v && typeof v === "object") { var o = {}; Object.keys(v).forEach(function (k) { o[k] = clean(v[k]); }); return o; }
    return v;
  }

  /* 25 Nov 2026 (QC after the review workshop): the server also refuses a ward written "05", and a
     phone with Nepali digits, a comma between two numbers or words around the number. Saved records
     are corrected here before they are sent, so records already kept on a phone go through too:
     Nepali digits become Latin, a comma or semicolon between numbers becomes " / ", other letters are
     dropped, and a ward loses its leading zeros. */
  function latin(s) { return s.replace(/[\u0966-\u096F]/g, function (d) { return String(d.charCodeAt(0) - 0x966); }); }
  function phoneFix(v, n) {
    return latin(v).replace(/\s*[,;|\/]+\s*/g, " / ").replace(/[^0-9+()\/. -]/g, "").replace(/ {2,}/g, " ")
      .replace(/^[\s\/.-]+|[\s\/-]+$/g, "").slice(0, n).trim();
  }
  function fixFields(o) {
    if (!o || typeof o !== "object" || Array.isArray(o)) return o;
    if (typeof o.ward === "string") o.ward = latin(o.ward).replace(/[^0-9]/g, "").replace(/^0+/, "");
    if (typeof o.refPhone === "string") o.refPhone = phoneFix(o.refPhone, 80);
    if (typeof o.phone === "string") o.phone = phoneFix(o.phone, 40);
    return o;
  }
  var rawPayload = CFG.payload;
  if (rawPayload) CFG.payload = function (r) { return fixFields(clean(rawPayload(r))); };
  var BASE = "https://mhpss5ws-tdp3xtfnsq-as.a.run.app";
  var ROUTE = "/directory/workshop/intake";
  var KEYC = "mhpss-np-workshop-code", RK = "mhpss-np-workshop-receipts-v1";
  function getJ(k, d) { try { return JSON.parse(localStorage.getItem(k) || "") || d; } catch (e) { return d; } }
  function putJ(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  var fromUrl = new URLSearchParams(location.search).get("k");
  if (fromUrl) { try { localStorage.setItem(KEYC, fromUrl); } catch (e) { /* kept in memory */ } }
  var code = fromUrl || (function () { try { return localStorage.getItem(KEYC); } catch (e) { return null; } })();
  var receipts = getJ(RK, {}), busy = false;
  function canon(p) { return JSON.stringify(p); }

  function pending() {
    return (CFG.read ? CFG.read() : []).filter(function (r) { var x = receipts[r.id]; return !x || x.canon !== canon(CFG.payload(r)); });
  }

  /* the status box under the button */
  function box() { return document.getElementById("saved"); }
  function show(html, kind) {
    var sv = box(); if (!sv) return;
    sv.className = "banner " + (kind === "bad" ? "warn" : kind === "ok" ? "ok" : "info");
    sv.style.fontSize = "15px";
    sv.innerHTML = html;
    sv.classList.remove("hidden");
    try { sv.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) { /* old browsers */ }
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  async function sendOne(r) {
    var p = CFG.payload(r);
    var res = await fetch(BASE + ROUTE, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ protocol: "directory-workshop/1", code: code, reportId: r.id, payload: p }) });
    var body = {}; try { body = await res.json(); } catch (e) { /* empty */ }
    if (!res.ok || body.stored !== true || body.reportId !== r.id) {
      var e = new Error((body && body.error) || ("HTTP " + res.status)); e.permanent = [400, 403, 404, 413].indexOf(res.status) >= 0; throw e;
    }
    receipts[r.id] = { canon: canon(p), sha: body.request_sha256, at: new Date().toISOString(), title: CFG.title ? CFG.title(p) : r.id };
    putJ(RK, receipts);
  }
  async function sendAll() {
    if (busy || !code) return { ok: 0, fail: code ? "" : "no-code" };
    var list = pending(), ok = 0, fail = "";
    if (!list.length) return { ok: 0, fail: "" };
    busy = true;
    var btn = document.getElementById("wsSubmit"); if (btn) btn.disabled = true;
    try {
      for (var i = 0; i < list.length; i++) {
        try { await sendOne(list[i]); ok++; }
        catch (e) { fail = e.message || "not sent"; if (!e.permanent) break; }
      }
    } finally { busy = false; if (btn) btn.disabled = false; }
    return { ok: ok, fail: fail };
  }

  window.FORM_SEND_AFTER_SAVE = async function () {
    var name = "", id = "";
    try { var b = box() && box().querySelector("b"); name = b ? b.textContent : ""; } catch (e) { name = ""; }
    try { var m = (box() && box().textContent || "").match(/\((SP[A-Z0-9]+)\)/); id = m ? m[1] : ""; } catch (e) { id = ""; }
    var what = name ? "“" + esc(name) + "”" : "The entry";
    if (!code) { show("<b>Not sent.</b> Open this page from the workshop QR code, then tap <b>Send to the coordination team</b> again.", "bad"); return; }
    show("Sending " + what + "…", "info");
    var r = await sendAll();
    /* judge the entry just tapped, not older entries kept on this phone */
    var waiting = id ? pending().some(function (x) { return x.id === id; }) : pending().length > 0;
    if (!waiting) {
      show("<b>✓ Sent.</b> " + what + " was received by the coordination team. It is checked with CMC-Nepal before it appears in the directory." +
        "<br>Another place? Tap <b>Clear form</b> and fill in the form again.", "ok");
    } else {
      show("<b>Not sent yet.</b> " + (r.fail && r.fail !== "not sent" ? "Reason: " + esc(r.fail) + ". " : "") +
        "Check the internet connection and tap <b>Send to the coordination team</b> again.", "bad");
    }
  };
  /* an entry that could not be sent goes out by itself when the connection is back */
  window.addEventListener("online", function () { if (pending().length) sendAll(); });
  if (navigator.onLine !== false && pending().length) sendAll();
})();

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

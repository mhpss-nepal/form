/* Workshop send card for the Referral Directory (owner decision, 23 Nov 2026).
   Open entry for the MHPSS review workshop of 24 November 2026, open until 30 November 2026:
   no sign-in. Each saved entry is sent to a separate holding area on the server, which is
   write-only; entries are validated with CMC-Nepal before anything is published.
   The workshop code arrives in the QR link (?k=...) and is kept on this phone. */
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
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function canon(p) { return JSON.stringify(p); }

  var card = document.createElement("div");
  card.className = "card"; card.id = "workshopCard";
  card.innerHTML =
    '<h2 style="font-size:17px;margin:0 0 6px">Send to the coordination team</h2>' +
    '<p class="lead">No sign-in is needed on this workshop page. Save each entry, and it is sent automatically when the phone has signal. ' +
    'The coordination team and CMC-Nepal check every entry before anything is published.</p>' +
    '<div class="actions"><button type="button" class="btn" id="wsSend">Send saved entries</button></div>' +
    '<p id="wsMsg" class="lead" style="margin:10px 0 0"></p>' +
    '<details id="wsDone" style="margin-top:10px"><summary>Entries already sent from this phone</summary><div id="wsList" style="margin-top:8px"></div></details>';
  var actions = document.querySelector("#f .actions");
  var host = actions ? actions.closest(".card") : null;
  if (host && host.parentNode) host.parentNode.insertBefore(card, host); else document.body.appendChild(card);
  var $ = function (s) { return card.querySelector(s); };

  function pending() {
    return (CFG.read ? CFG.read() : []).filter(function (r) { var x = receipts[r.id]; return !x || x.canon !== canon(CFG.payload(r)); });
  }
  function msg(t, ok) { var m = $("#wsMsg"); m.textContent = t; m.style.color = ok === false ? "#a3221c" : ok ? "#1a7f37" : ""; }
  function paint() {
    var n = pending().length;
    if (!code) msg("Open this page from the workshop QR code or link to send entries. You can still fill in and save.", false);
    else if (navigator.onLine === false) msg("No signal: entries stay on this phone and are sent when the signal is back." + (n ? " Waiting: " + n : ""));
    else msg(n ? "Entries waiting to be sent: " + n : "Nothing waiting: every saved entry has been sent.", n ? null : true);
    var done = Object.keys(receipts).map(function (k) { return receipts[k]; }).sort(function (a, b) { return (b.at || "").localeCompare(a.at || ""); });
    $("#wsList").innerHTML = done.length ? done.map(function (x) {
      return '<div style="border:1px solid #d6e0ea;border-radius:10px;padding:8px 12px;margin:0 0 6px"><b>' + esc(x.title) + '</b>' +
        '<div style="font-size:12.5px;color:#52647a">' + esc((x.at || "").replace("T", " ").slice(0, 16)) + ' · received, to be validated with CMC-Nepal</div></div>';
    }).join("") : '<p class="lead">Nothing sent from this phone yet.</p>';
  }
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
    if (busy || !code) { paint(); return; }
    var list = pending();
    if (!list.length) { paint(); return; }
    busy = true; $("#wsSend").disabled = true; msg("Sending…");
    var ok = 0, fail = "";
    try {
      for (var i = 0; i < list.length; i++) {
        try { await sendOne(list[i]); ok++; }
        catch (e) { fail = e.message; if (!e.permanent) break; }
      }
    } finally {
      busy = false; $("#wsSend").disabled = false; paint();
      if (fail) msg("Not sent — the entry stays on this phone. Reason: " + fail, false);
      else if (ok) msg("Sent and received by the coordination team: " + ok + ". Thank you.", true);
    }
  }
  $("#wsSend").addEventListener("click", sendAll);
  window.FORM_SEND_AFTER_SAVE = function () { if (navigator.onLine !== false) sendAll(); else paint(); };
  window.addEventListener("online", sendAll);
  window.addEventListener("offline", paint);
  paint();
  if (navigator.onLine !== false) sendAll();
})();

/* =====================================================================
   MHPSS Nepal — sending the grief and referral directory forms to the server
   ---------------------------------------------------------------------
   Every record is saved on the phone first (the page does that). This file
   adds a "Send to the server" card: the worker signs in with the same account
   as the 5Ws form, and each saved record is sent to the Cloud Run receiver
   (mhpss5ws, project mhpss-nepal-hub). A record counts as sent ONLY when the
   server returns its receipt; until then it stays on the phone and is sent
   again with "Send saved records".
     grief      POST /grief/intake                 (organisation grant needed)
     directory  POST /directory/servicepoints2/intake
   The receipt of each record (revision and request_sha256) is kept on the
   phone, so an edited directory entry is sent as the next revision.
   ===================================================================== */
(function () {
  "use strict";
  var BASE = "https://mhpss5ws-tdp3xtfnsq-as.a.run.app";
  var CFG = window.FORM_SEND || null;
  if (!CFG) return;
  var RKEY = "mhpss-np-send-receipts-" + CFG.form;
  var T = function (k, en) { try { return (window.I18N && I18N.t(k)) || en; } catch (e) { return en; } };
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function getJ(k, d) { try { return JSON.parse(localStorage.getItem(k) || "null") || d; } catch (e) { return d; } }
  function putJ(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function canon(v) {
    if (v === null || typeof v !== "object") return JSON.stringify(v);
    if (Array.isArray(v)) return "[" + v.map(canon).join(",") + "]";
    return "{" + Object.keys(v).sort().map(function (k) { return JSON.stringify(k) + ":" + canon(v[k]); }).join(",") + "}";
  }
  var receipts = getJ(RKEY, {});
  var profile = null, busy = false;

  var card = document.createElement("div");
  card.className = "card"; card.id = "sendCard";
  card.innerHTML =
    '<h2 style="font-size:17px;margin:0 0 6px" data-i18n="send.title">Send to the server</h2>' +
    '<p class="lead" data-i18n="send.lead">Records are saved on this phone first. Sign in with your field account to send them; a record counts as sent only when the server confirms it.</p>' +
    '<div id="sendOut"><div class="grid2">' +
    '<div><label class="f" for="sendEmail" data-i18n="send.email">Email</label><input type="email" id="sendEmail" autocomplete="username"></div>' +
    '<div><label class="f" for="sendPass" data-i18n="send.password">Password</label><input type="password" id="sendPass" autocomplete="current-password"></div>' +
    '</div><div class="actions" style="margin-top:10px"><button type="button" class="btn" id="sendIn" data-i18n="send.signin">Sign in</button></div></div>' +
    '<div id="sendInBox" class="hidden"><p id="sendWho" style="margin:0 0 8px"></p>' +
    '<div class="actions"><button type="button" class="btn" id="sendNow" data-i18n="send.now">Send saved records</button><button type="button" class="btn ghost" id="sendOutBtn" data-i18n="send.signout">Sign out</button></div></div>' +
    '<p id="sendMsg" class="lead" style="margin:10px 0 0"></p>';
  var actions = document.querySelector("#f .actions");
  var host = actions ? actions.closest(".card") : null;
  if (host && host.parentNode) host.parentNode.insertBefore(card, host); else document.body.appendChild(card);
  try { window.I18N && I18N.apply(card); } catch (e) { /* engine optional */ }
  var $ = function (s) { return card.querySelector(s); };
  function msg(text, ok) { var m = $("#sendMsg"); m.textContent = text; m.style.color = ok === true ? "#1a7f37" : ok === false ? "#a3221c" : "#52647a"; }

  function pending() {
    return CFG.read().filter(function (r) { var x = receipts[r.id]; return !x || x.canon !== canon(CFG.payload(r)); });
  }
  function paint() {
    var u = window.BaselineAuth && BaselineAuth.currentUser && BaselineAuth.currentUser();
    $("#sendOut").classList.toggle("hidden", !!u); $("#sendInBox").classList.toggle("hidden", !u);
    var n = pending().length;
    if (u) $("#sendWho").textContent = T("send.signedAs", "Signed in as") + " " + (u.email || "") + (profile && profile.org ? " · " + profile.org : "") + " · " + T("send.waiting", "records not sent yet:") + " " + n;
    else msg(n ? T("send.waiting", "records not sent yet:") + " " + n : "");
  }
  async function token() { return BaselineAuth.token(); }
  async function loadProfile() {
    profile = null;
    try {
      var r = await fetch(BASE + "/profile", { headers: { Authorization: "Bearer " + await token() } });
      if (r.ok) profile = await r.json();
    } catch (e) { /* offline */ }
    paint();
  }
  async function sendOne(r) {
    var p = CFG.payload(r), c = canon(p), prev = receipts[r.id];
    var rev = prev ? prev.revision + 1 : 1;
    var env = { protocol: CFG.protocol, reportId: r.id, revision: rev, predecessor: prev ? { revision: prev.revision, request_sha256: prev.sha } : null, payload: p };
    var headers = { Authorization: "Bearer " + await token(), "Content-Type": "application/json" };
    if (CFG.needsOrg) {
      if (!profile || profile.access !== "reporter") throw new Error(T("send.noGrant", "This account has no reporting access for an organisation yet. Ask the coordination team."));
      if (p.org !== profile.org) throw new Error(T("send.otherOrg", "This record belongs to another organisation than your account:") + " " + p.org);
      headers["X-Selected-Org"] = profile.org;
    }
    var res = await fetch(BASE + CFG.route, { method: "POST", headers: headers, body: JSON.stringify(env) });
    var body = {}; try { body = await res.json(); } catch (e) { /* empty */ }
    if (!res.ok || body.stored !== true || body.reportId !== r.id || body.revision !== rev) throw new Error((body && body.error) || ("HTTP " + res.status));
    receipts[r.id] = { revision: rev, sha: body.request_sha256, canon: c, at: new Date().toISOString() }; putJ(RKEY, receipts);
  }
  async function sendAll() {
    if (busy) return; busy = true;
    var list = pending(), ok = 0, fail = "";
    try {
      if (!list.length) { msg(T("send.none", "Nothing waiting: every saved record has been sent."), true); return; }
      msg(T("send.sending", "Sending…"));
      for (var i = 0; i < list.length; i++) {
        try { await sendOne(list[i]); ok++; } catch (e) { fail = e.message || String(e); break; }
      }
      if (fail) msg(T("send.failed", "Not sent — the record stays on this phone. Reason:") + " " + fail, false);
      else msg(T("send.done", "Sent and confirmed by the server:") + " " + ok, true);
    } finally { busy = false; paint(); }
  }
  window.FORM_SEND_AFTER_SAVE = function () {
    var u = window.BaselineAuth && BaselineAuth.currentUser && BaselineAuth.currentUser();
    if (u && navigator.onLine !== false) sendAll(); else paint();
  };
  $("#sendIn").addEventListener("click", async function () {
    msg(T("send.signingIn", "Signing in…"));
    try { await BaselineAuth.signIn($("#sendEmail").value.trim(), $("#sendPass").value); $("#sendPass").value = ""; msg(""); await loadProfile(); }
    catch (e) { msg(T("send.signinFailed", "Sign-in failed. Check the email and password."), false); }
  });
  $("#sendOutBtn").addEventListener("click", async function () { try { await BaselineAuth.signOut(); } catch (e) { /* ignore */ } profile = null; paint(); });
  $("#sendNow").addEventListener("click", sendAll);
  window.addEventListener("online", function () { window.FORM_SEND_AFTER_SAVE(); });
  document.addEventListener("i18n:changed", paint);
  if (window.BaselineAuth) BaselineAuth.onChange(function (u) { if (u) loadProfile(); else paint(); });
  paint();
})();

/* =====================================================================
   MHPSS Nepal — sending the grief and referral directory forms, and the
   worker's own records with their review status
   ---------------------------------------------------------------------
   Every record is saved on the phone first (the page does that). This card
   signs the worker in (an emailed link, or a password), sends each saved record
   to the server and counts it as sent ONLY when the server returns its receipt.
   "My records" lists what the server holds for this worker, with the
   coordinator's decision: waiting for review, accepted, or returned with a note.
   A returned record opens back into the form for correction and is sent as the
   next revision. What the server shows depends on the person's access card
   (owner decisions 19 Nov 2026): field staff see their own records.
     grief      POST /grief/intake                 (X-Selected-Org = card organisation)
     directory  POST /directory/servicepoints2/intake
   Needs current-auth.js and ../hub/assets/access-api.js before this file.
   ===================================================================== */
(function () {
  "use strict";
  /* Put a stored record back into the page's form, cascading selects first. */
  window.FORM_SEND_FILL = function (flat, first) {
    var f = document.querySelector("#f");
    function setVal(k, v) {
      var els = Array.prototype.slice.call(f.querySelectorAll('[name="' + k + '"]'));
      if (!els.length) { var e = document.getElementById(k); if (e) els = [e]; }
      els.forEach(function (e) {
        if (e.type === "checkbox" || e.type === "radio") e.checked = Array.isArray(v) ? v.map(String).indexOf(e.value) >= 0 : (v === true ? e.value === "on" || e.value === "yes" : String(v) === e.value);
        else { e.disabled = false; e.value = Array.isArray(v) ? v.join(", ") : (v == null ? "" : v); }
        e.dispatchEvent(new Event("change", { bubbles: true }));
      });
    }
    (first || []).forEach(function (k) { if (k in flat) setVal(k, flat[k]); });
    Object.keys(flat).forEach(function (k) { if ((first || []).indexOf(k) < 0) setVal(k, flat[k]); });
  };
  /* QC 20 Nov 2026: after a release the first visit could show the previous wording. When the
     new service worker takes over and nothing has been typed yet, reload once. */
  (function () {
    if (!("serviceWorker" in navigator)) return;
    var had = !!navigator.serviceWorker.controller, typed = false, done = false;
    document.addEventListener("input", function () { typed = true; }, true);
    navigator.serviceWorker.addEventListener("controllerchange", function () {
      if (!had || done || typed) return;
      done = true; location.reload();
    });
  })();
  var CFG = window.FORM_SEND || null, A = window.AccessAPI;
  if (!CFG || !A) return;
  /* 24 Nov 2026 (lesson from the review workshop): phones add a space after an autocompleted word
     and long boxes accept Enter. The server takes only trimmed single-line text and refused such
     entries ("bounded trimmed text required"). Every text value is cleaned here before it is sent:
     line breaks and control characters become a space, repeated spaces collapse, ends are trimmed.
     Records already saved on a phone are cleaned the same way when they are sent. */
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
  CFG.payload = function (r) { return fixFields(clean(rawPayload(r))); };
  var BASE = A.BASE, T = A.T, esc = A.esc;
  var RKEY = "mhpss-np-send-receipts-" + CFG.form;
  function getJ(k, d) { try { return JSON.parse(localStorage.getItem(k) || "null") || d; } catch (e) { return d; } }
  function putJ(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function canon(v) {
    if (v === null || typeof v !== "object") return JSON.stringify(v);
    if (Array.isArray(v)) return "[" + v.map(canon).join(",") + "]";
    return "{" + Object.keys(v).sort().map(function (k) { return JSON.stringify(k) + ":" + canon(v[k]); }).join(",") + "}";
  }
  var receipts = getJ(RKEY, {});
  var me = null, busy = false, mine = [];

  var card = document.createElement("div");
  card.className = "card"; card.id = "sendCard";
  card.innerHTML =
    '<h2 style="font-size:17px;margin:0 0 6px" data-i18n="send.title">Send to the server</h2>' +
    '<p class="lead" data-i18n="send.lead">Records are saved on this phone first. Sign in with your field account to send them; a record counts as sent only when the server confirms it.</p>' +
    '<div id="sendOut"></div>' +
    '<div id="sendInBox" class="hidden"><p id="sendWho" style="margin:0 0 8px"></p>' +
    '<div class="actions"><button type="button" class="btn" id="sendNow" data-i18n="send.now">Send saved records</button><button type="button" class="btn ghost" id="sendOutBtn" data-i18n="send.signout">Sign out</button></div>' +
    '<p id="sendTeam" class="hidden" style="margin:10px 0 0"><a href="../../hub/team.html" data-i18n="send.team">Check your team’s records →</a></p>' +
    '<details id="mineBox" style="margin-top:12px"><summary data-i18n="send.mine">My records on the server</summary><div id="mineList" style="margin-top:8px"></div></details></div>' +
    '<p id="sendMsg" class="lead" style="margin:10px 0 0"></p>';
  var actions = document.querySelector("#f .actions");
  var host = actions ? actions.closest(".card") : null;
  if (host && host.parentNode) host.parentNode.insertBefore(card, host); else document.body.appendChild(card);
  try { window.I18N && I18N.apply(card); } catch (e) { /* engine optional */ }
  var $ = function (s) { return card.querySelector(s); };

  /* "Filled in by" (decision 2A, 19 Nov 2026): staff without signal borrow a colleague's phone. The record
     names the person who filled it in; the phone's signed-in account only sends it, and both are kept. */
  var RECKEY = "mhpss-np-recorders";
  var rec = document.createElement("div");
  rec.id = "recBox"; rec.style.margin = "0 0 12px";
  rec.innerHTML = '<label class="f" for="recBy" data-i18n="send.recBy">Filled in by (your email)</label>' +
    '<input type="email" id="recBy" list="recList" autocomplete="email" inputmode="email"><datalist id="recList"></datalist>' +
    '<p class="lead" style="margin:4px 0 0;font-size:13px" data-i18n="send.recHelp">Your own email, also on a colleague’s phone. The record stays yours; the account on this phone only sends it.</p>';
  if (actions && actions.parentNode) actions.parentNode.insertBefore(rec, actions); else card.appendChild(rec);
  try { window.I18N && I18N.apply(rec); } catch (e) { /* engine optional */ }
  function recorders() { return getJ(RECKEY, []); }
  function fillRecorders() {
    var list = recorders(), u = A.user();
    if (u && u.email && list.indexOf(u.email.toLowerCase()) < 0) list = [u.email.toLowerCase()].concat(list);
    document.getElementById("recList").innerHTML = list.map(function (e) { return '<option value="' + esc(e) + '">'; }).join("");
    var box = document.getElementById("recBy");
    if (!box.value) box.value = list[0] || "";
  }
  window.FORM_SEND_RECORDER = function () {
    var box = document.getElementById("recBy"), v = (box.value || "").trim().toLowerCase();
    if (!v) return "";
    if (!/^[a-z0-9_+.-]+@[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(v)) { msg(T("send.recBad", "Type a valid email in “Filled in by”, or leave it empty."), false); box.focus(); return false; }
    var list = recorders().filter(function (e) { return e !== v; }); list.unshift(v); putJ(RECKEY, list.slice(0, 8));
    return v;
  };
  window.FORM_SEND_SET_RECORDER = function (v) { var box = document.getElementById("recBy"); box.value = v || ""; if (!v) fillRecorders(); };
  fillRecorders();
  function msg(text, ok) { var m = $("#sendMsg"); m.textContent = text; m.style.color = ok === true ? "#1a7f37" : ok === false ? "#a3221c" : "#52647a"; }
  A.signInPanel($("#sendOut"), function () { loadMe(); });

  function pending() {
    return CFG.read().filter(function (r) { var x = receipts[r.id]; return !x || x.canon !== canon(CFG.payload(r)); });
  }
  var ROLE = { field: "field staff", coordinator: "coordinator", focal: "focal point", admin: "coordination" };
  function paint() {
    var u = A.user();
    $("#sendOut").classList.toggle("hidden", !!u); $("#sendInBox").classList.toggle("hidden", !u);
    var n = pending().length;
    if (u) {
      var who = T("send.signedAs", "Signed in as") + " " + (u.email || "");
      if (me && me.role) who += " · " + (me.org || T("send.allOrgs", "all organisations")) + " · " + T("send.role." + me.role, ROLE[me.role]);
      else if (isPartner()) who += " · " + T("send.role.partner", "partner");
      $("#sendWho").textContent = who + " · " + T("send.waiting", "records not sent yet:") + " " + n;
      $("#sendTeam").classList.toggle("hidden", !(me && me.canReview));
    } else if (navigator.onLine === false) msg(T("send.offline", "No signal: you can still fill in and save. Saved records are sent when the phone has signal again.") + (n ? " " + T("send.waiting", "records not sent yet:") + " " + n : ""));
    else msg(n ? T("send.waiting", "records not sent yet:") + " " + n : "");
  }
  /* QC 20 Nov 2026: the organisation comes from the person's access card (set by the coordinator
     who added the email), not from the email domain; Gmail or any address works. Coordination
     accounts (all organisations) keep the choice. */
  /* Partner route (owner decision, 23 Nov 2026): a verified email without an access card may send
     its own Referral Directory entries; the server says so in me.partner. Nothing else opens. */
  function isPartner() { return !!(me && !me.role && me.partner && me.partner.forms && me.partner.forms.indexOf(CFG.form) >= 0); }
  function canSend() { return !!(me && (me.role || isPartner())); }
  window.FORM_SEND_ORG = function () { return me && me.role && me.role !== "admin" && me.org ? me.org : ""; };
  function presetOrg() {
    var o = window.FORM_SEND_ORG(), sel = document.getElementById("org");
    if (!CFG.needsOrg || !o || !sel || window.__edit) return;
    if (!Array.prototype.some.call(sel.options, function (x) { return x.value === o; })) return;
    if (sel.value !== o) { sel.value = o; sel.dispatchEvent(new Event("change", { bubbles: true })); }
  }
  async function loadMe() {
    me = null; fillRecorders();
    try { me = await A.me(); } catch (e) { /* offline */ }
    presetOrg();
    if (isPartner()) msg(T("send.partner", "Signed in as a partner: you can send entries for this directory. The coordination team checks each entry before it is published."), true);
    else if (me && me.role === null) msg(T("send.noAccess", "This email has no access yet. Ask your coordinator to add it, then sign in again."), false);
    else if (me && me.forms && me.forms.indexOf(CFG.form) < 0) msg(T("send.noForm", "Your access card does not include this form. Ask your coordinator."), false);
    paint();
    if (canSend()) loadMine();
  }
  var STATUS = { pending: ["send.st.pending", "Received", "#1f6fb2", "#e4effa"], accepted: ["send.st.accepted", "Accepted", "#1a7f37", "#e6f5ec"], returned: ["send.st.returned", "Returned — please correct", "#a3221c", "#fdecea"] };
  async function loadMine() {
    var box = $("#mineList");
    try {
      var rows = CFG.form === "grief" ? (await A.griefEntries(me.role === "admin" ? "" : me.org)).rows.filter(function (r) { return r.mine; }) : (await A.dirMine());
      mine = rows;
      rows.forEach(function (r) {
        var x = receipts[r.reportId];
        if (!x || x.revision <= r.revision) receipts[r.reportId] = { revision: r.revision, sha: r.request_sha256, canon: canon(r.payload), at: x && x.at || "" };
      });
      putJ(RKEY, receipts);
      if (!rows.length) { box.innerHTML = '<p class="lead">' + esc(T("send.mineNone", "Nothing from you on the server yet.")) + "</p>"; return; }
      var ret = rows.filter(function (r) { return r.review === "returned"; }).length;
      if (ret) $("#mineBox").open = true;
      box.innerHTML = rows.sort(function (a, b) { return (b.updatedAt || "").localeCompare(a.updatedAt || ""); }).map(function (r, i) {
        var s = STATUS[r.review] || STATUS.pending;
        return '<div style="border:1px solid #d6e0ea;border-radius:10px;padding:10px 12px;margin:0 0 8px">' +
          '<div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap"><b>' + esc(CFG.title(r.payload)) + '</b>' +
          '<span style="font-size:12px;font-weight:700;padding:2px 8px;border-radius:999px;color:' + s[2] + ';background:' + s[3] + '">' + esc(T(s[0], s[1])) + "</span></div>" +
          '<div style="font-size:12.5px;color:#52647a;margin-top:4px">' + esc((r.updatedAt || "").slice(0, 10)) + " · " + esc(T("send.revision", "version")) + " " + r.revision + "</div>" +
          (r.review === "returned" ? '<p style="margin:6px 0 0;color:#a3221c">' + esc(r.reviewNote) + '</p><button type="button" class="btn ghost" data-fix="' + i + '" style="margin-top:6px" data-i18n="send.fix">Open in the form to correct</button>' : "") +
          "</div>";
      }).join("");
      try { window.I18N && I18N.apply(box); } catch (e) { /* optional */ }
      box.querySelectorAll("[data-fix]").forEach(function (b) {
        b.addEventListener("click", function () {
          var r = rows[+b.getAttribute("data-fix")];
          CFG.load(r.payload);
          msg(T("send.fixHint", "The record is open in the form. Correct it and save; it is sent as the next version."), true);
          window.scrollTo(0, 0);
        });
      });
    } catch (e) { box.innerHTML = '<p class="lead">' + esc(T("send.mineFail", "Could not load your records now. Try again with signal.")) + "</p>"; }
  }
  async function sendOne(r) {
    var p = CFG.payload(r), c = canon(p), prev = receipts[r.id];
    var rev = prev ? prev.revision + 1 : 1;
    var env = { protocol: CFG.protocol, reportId: r.id, revision: rev, predecessor: prev ? { revision: prev.revision, request_sha256: prev.sha } : null, payload: p };
    var headers = { Authorization: "Bearer " + await BaselineAuth.token(), "Content-Type": "application/json" };
    if (!canSend()) throw new Error(T("send.noAccess", "This email has no access yet. Ask your coordinator to add it, then sign in again."));
    if (CFG.needsOrg) {
      if (me.role && me.role !== "admin" && p.org !== me.org) { var oe = new Error(T("send.otherOrg", "This record belongs to another organisation than your account:") + " " + p.org); oe.permanent = true; throw oe; }
      headers["X-Selected-Org"] = p.org;
    }
    var res = await fetch(BASE + CFG.route, { method: "POST", headers: headers, body: JSON.stringify(env) });
    var body = {}; try { body = await res.json(); } catch (e) { /* empty */ }
    if (!res.ok || body.stored !== true || body.reportId !== r.id || body.revision !== rev) {
      var se = new Error((body && body.error) || ("HTTP " + res.status));
      /* a refusal about this record (not about the connection or the sign-in) must not hold back the others */
      se.permanent = [400, 403, 404, 409, 413, 422].indexOf(res.status) >= 0;
      throw se;
    }
    receipts[r.id] = { revision: rev, sha: body.request_sha256, canon: c, at: new Date().toISOString() }; putJ(RKEY, receipts);
    if (CFG.sent) { try { CFG.sent(r); } catch (e) { /* the record stays as it was */ } }
  }
  async function sendAll() {
    if (busy) return; busy = true;
    var list = pending(), ok = 0, fail = "", skipped = 0;
    try {
      if (!list.length) { msg(T("send.none", "Nothing waiting: every saved record has been sent."), true); return; }
      msg(T("send.sending", "Sending…"));
      for (var i = 0; i < list.length; i++) {
        try { await sendOne(list[i]); ok++; }
        catch (e) { fail = e.message || String(e); if (e.permanent) { skipped++; continue; } break; }
      }
      if (fail) msg((ok ? T("send.done", "Sent and confirmed by the server:") + " " + ok + ". " : "") +
        T("send.failed", "Not sent — the record stays on this phone. Reason:") + " " + fail, false);
      else msg(T("send.done", "Sent and confirmed by the server:") + " " + ok, true);
      if (ok) loadMine();
    } finally { busy = false; paint(); }
  }
  window.FORM_SEND_AFTER_SAVE = function () {
    if (A.user() && canSend() && navigator.onLine !== false) sendAll(); else paint();
  };
  $("#sendOutBtn").addEventListener("click", async function () { try { await A.signOut(); } catch (e) { /* ignore */ } me = null; paint(); });
  $("#sendNow").addEventListener("click", sendAll);
  var authFailed = false;
  if (window.BaselineAuth) BaselineAuth.onChange(function (u, st) { authFailed = !!(st && st.restoration === "failed"); });
  function offlineNote() {
    if (navigator.onLine === false) msg(T("send.offline", "No signal: you can still fill in and save. Saved records are sent when the phone has signal again."));
  }
  window.addEventListener("offline", offlineNote);
  window.addEventListener("online", function () {
    if (authFailed && !A.user()) {
      var m = $("#sendMsg");
      m.innerHTML = esc(T("send.back", "Signal is back.")) + ' <button type="button" class="btn" id="sendReload">' + esc(T("send.reload", "Tap to connect and send")) + "</button>";
      m.querySelector("#sendReload").onclick = function () { location.reload(); };
      return;
    }
    window.FORM_SEND_AFTER_SAVE();
  });
  offlineNote();
  document.addEventListener("i18n:changed", paint);
  if (window.BaselineAuth) BaselineAuth.onChange(function (u) { if (!u) { me = null; paint(); } });
  paint();
})();

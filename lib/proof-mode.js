/* =====================================================================
   MHPSS Nepal — Nepali proofreading mode for the field forms
   ---------------------------------------------------------------------
   Open a form with ?proof=1 (for example
   preview/grief-early-assessment.html?proof=1). A "Proofreading" button
   opens a list of every sentence of the form: English, the Nepali draft,
   and three actions —
     Correct          the draft is right as it is
     Suggest a change the reviewer types the corrected Nepali
     Write the Nepali for sentences kept in English on purpose (consent,
                      safety and clinical wording), which have no draft
   Each check is sent at once to the proofreading collection `formproof`
   in Firebase project mhpss-nepal-iec-review (the same project as the IEC
   proofreading). The rules there allow adding a check only: nobody can
   read, change or delete checks from the page. The reviewer's own progress
   is remembered in this browser only.
   Nothing here changes the form or its saved records.
   ===================================================================== */
(function () {
  "use strict";
  var q = new URLSearchParams(location.search);
  if (!q.has("proof")) return;
  var FB = { pid: "mhpss-nepal-iec-review", key: "AIzaSyBN-sh64hOZeQClPi8Z8k-fXcVfBs2pxFQ" };
  var ROUND = "R1";
  var FORM = /grief/.test(location.pathname) ? "grief" : "directory";
  var PFX = FORM === "grief" ? ["grief.", "consent.grief", "safeguard.grief", "clinical.grief"] : ["dirf.", "consent.dirf", "safeguard.dirf", "clinical.dirf"];
  var PROT = ["consent.", "safeguard.", "clinical."];
  var S = window.I18N_STRINGS || { en: {}, ne: {} };
  var ME = "mhpss-np-proof-me", DONE = "mhpss-np-proof-done-" + FORM + "-" + ROUND;
  function get(k, d) { try { return JSON.parse(localStorage.getItem(k) || "null") || d; } catch (e) { return d; } }
  function put(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function plain(v) { var d = document.createElement("div"); d.innerHTML = v == null ? "" : String(v); return d.textContent; }
  var isProt = function (k) { return PROT.some(function (p) { return k.indexOf(p) === 0; }); };

  /* every key of this form: page order first, then the ones not on screen yet (messages, notes) */
  function keys() {
    var seen = {}, out = [];
    document.querySelectorAll("[data-i18n],[data-i18n-ph]").forEach(function (el) {
      var k = el.getAttribute("data-i18n") || el.getAttribute("data-i18n-ph");
      if (k && !seen[k] && PFX.some(function (p) { return k.indexOf(p) === 0; })) { seen[k] = 1; out.push(k); }
    });
    Object.keys(S.en || {}).forEach(function (k) {
      if (!seen[k] && PFX.some(function (p) { return k.indexOf(p) === 0; })) { seen[k] = 1; out.push(k); }
    });
    return out;
  }

  var css = document.createElement("style");
  css.textContent =
    "#pfBtn{position:fixed;z-index:9990;right:14px;bottom:14px;border:0;border-radius:999px;background:#5b2a86;color:#fff;font:700 14px system-ui,sans-serif;padding:12px 18px;box-shadow:0 6px 18px rgba(0,0,0,.25);cursor:pointer}" +
    "#pfPane{position:fixed;z-index:9991;inset:0;background:rgba(20,30,40,.45);display:none}" +
    "#pfPane.on{display:block}" +
    "#pfBox{position:absolute;right:0;top:0;bottom:0;width:min(760px,100%);background:#fff;display:flex;flex-direction:column;box-shadow:-8px 0 24px rgba(0,0,0,.2)}" +
    "#pfHead{padding:14px 16px;border-bottom:1px solid #e3e8ee;background:#f7f4fb}" +
    "#pfHead h2{margin:0 0 4px;font:700 18px system-ui,sans-serif;color:#3b1d5a}" +
    "#pfHead p{margin:0;font-size:13px;color:#4a5563;text-align:justify;hyphens:none}" +
    "#pfList{overflow:auto;padding:10px 16px 90px;flex:1}" +
    ".pfRow{border:1px solid #e3e8ee;border-radius:10px;padding:10px 12px;margin:10px 0}" +
    ".pfRow.done{border-color:#9bd3ae;background:#f3fbf6}.pfRow.prot{border-left:4px solid #b4541f}" +
    ".pfK{font:600 11px ui-monospace,Menlo,monospace;color:#7a8696;display:flex;justify-content:space-between;gap:8px}" +
    ".pfEn{margin:6px 0 4px;color:#1d3557}.pfNe{font-family:'Mukta','Noto Sans Devanagari',system-ui,sans-serif;font-size:16px;color:#20313b;background:#faf7ff;border-radius:6px;padding:6px 8px}" +
    ".pfNe.none{font-family:system-ui;font-size:13px;color:#b4541f;background:#fff4ec}" +
    ".pfAct{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.pfAct button{border:1px solid #c8d3df;background:#fff;border-radius:999px;padding:6px 12px;font:600 13px system-ui,sans-serif;cursor:pointer}" +
    ".pfAct button.ok{border-color:#1a7f37;color:#1a7f37}.pfAct button.pri{background:#5b2a86;border-color:#5b2a86;color:#fff}" +
    ".pfEd{display:none;margin-top:8px}.pfEd.on{display:block}.pfEd textarea,.pfEd input{width:100%;box-sizing:border-box;border:1px solid #c8d3df;border-radius:8px;padding:8px;font:16px 'Mukta','Noto Sans Devanagari',system-ui,sans-serif}" +
    ".pfEd input{font:14px system-ui;margin-top:6px}.pfMsg{font-size:12.5px;margin-top:6px}" +
    "#pfId{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;margin-top:10px}#pfId input,#pfId select{border:1px solid #c8d3df;border-radius:8px;padding:8px;font:14px system-ui}" +
    "#pfTools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px;font-size:13px}#pfTools button{border:1px solid #c8d3df;background:#fff;border-radius:999px;padding:6px 12px;cursor:pointer}" +
    "#pfClose{float:right;border:0;background:none;font-size:24px;line-height:1;cursor:pointer;color:#3b1d5a}" +
    "@media (max-width:600px){#pfBox{overflow:auto}#pfList{overflow:visible;flex:none}#pfHead p{font-size:12.5px}}" +
    ".pfFlash{outline:3px solid #e0a100!important;outline-offset:3px;transition:outline-color 1.5s}";
  document.head.appendChild(css);

  var me = get(ME, { name: "", org: "", email: "", credit: "name" });
  var done = get(DONE, {});
  var btn = document.createElement("button");
  btn.id = "pfBtn"; btn.type = "button";
  var pane = document.createElement("div"); pane.id = "pfPane";
  pane.innerHTML = '<div id="pfBox" role="dialog" aria-label="Nepali proofreading"><div id="pfHead"><button id="pfClose" type="button" aria-label="Close">×</button>' +
    '<h2>Nepali proofreading · Round 1</h2><p>Check each sentence: is the Nepali right for field staff? Tap <b>Correct</b>, or <b>Suggest a change</b> and type the better Nepali. Sentences marked <b>kept in English</b> (consent, safety and clinical wording) have no draft on purpose: please write the Nepali yourself. Each check is sent as soon as you tap Send. Your corrections are also kept as a reference for future Nepali translations of MHPSS Nepal materials.</p>' +
    '<div id="pfId"><input id="pfName" placeholder="Your name" autocomplete="name"><input id="pfOrg" placeholder="Organisation" autocomplete="organization"><input id="pfEmail" type="email" placeholder="Email" autocomplete="email">' +
    '<select id="pfCredit" aria-label="How you wish to be acknowledged"><option value="name">Acknowledge me by name</option><option value="org">Acknowledge my organisation only</option><option value="none">Do not list me</option></select></div>' +
    '<div id="pfTools"><label><input type="checkbox" id="pfTodo"> Show only sentences not yet checked</label><span id="pfCount"></span></div></div><div id="pfList"></div></div>';
  document.body.appendChild(btn); document.body.appendChild(pane);
  var $ = function (s) { return pane.querySelector(s); };
  $("#pfName").value = me.name; $("#pfOrg").value = me.org; $("#pfEmail").value = me.email; $("#pfCredit").value = me.credit || "name";
  ["#pfName", "#pfOrg", "#pfEmail", "#pfCredit"].forEach(function (s) {
    $(s).addEventListener("change", function () { me = { name: $("#pfName").value.trim(), org: $("#pfOrg").value.trim(), email: $("#pfEmail").value.trim(), credit: $("#pfCredit").value }; put(ME, me); });
  });

  var K = [];
  function count() {
    var n = K.filter(function (k) { return done[k]; }).length;
    btn.textContent = "Proofreading · " + n + " / " + K.length;
    $("#pfCount").textContent = n + " of " + K.length + " checked";
  }
  function render() {
    K = keys();
    var only = $("#pfTodo").checked;
    $("#pfList").innerHTML = K.filter(function (k) { return !only || !done[k]; }).map(function (k) {
      var en = (S.en || {})[k], ne = (S.ne || {})[k], p = isProt(k);
      var has = ne != null && String(ne).trim() !== "" && !p;
      return '<div class="pfRow' + (done[k] ? " done" : "") + (p ? " prot" : "") + '" data-k="' + esc(k) + '">' +
        '<div class="pfK"><span>' + esc(k) + (done[k] ? " · ✓ " + esc(done[k]) : "") + '</span><a href="#" class="pfShow">Show in form</a></div>' +
        '<div class="pfEn">' + esc(plain(en)) + '</div>' +
        (has ? '<div class="pfNe" lang="ne">' + esc(plain(ne)) + '</div>' : '<div class="pfNe none">' + (p ? "Kept in English on purpose (consent, safety or clinical wording) — please write the Nepali." : "No draft yet — please write the Nepali.") + '</div>') +
        '<div class="pfAct">' + (has ? '<button type="button" class="ok" data-a="ok">✓ Correct</button><button type="button" data-a="edit">✎ Suggest a change</button>' : '<button type="button" class="pri" data-a="edit">✎ Write the Nepali</button>') + '</div>' +
        '<div class="pfEd"><textarea rows="3" lang="ne" placeholder="Nepali"></textarea><input class="pfNote" placeholder="Note (optional), e.g. why this word"><div class="pfAct"><button type="button" class="pri" data-a="send">Send</button><button type="button" data-a="cancel">Cancel</button></div></div>' +
        '<div class="pfMsg"></div></div>';
    }).join("");
    count();
  }
  function send(row, verdict, text, note) {
    var k = row.getAttribute("data-k"), msg = row.querySelector(".pfMsg");
    me = { name: $("#pfName").value.trim(), org: $("#pfOrg").value.trim(), email: $("#pfEmail").value.trim(), credit: $("#pfCredit").value }; put(ME, me);
    if (!me.name || !me.org || !/.+@.+\..+/.test(me.email)) { msg.textContent = "Please fill in your name, organisation and email at the top first."; msg.style.color = "#a3221c"; $("#pfName").focus(); return; }
    var f = { form: FORM, key: k, verdict: verdict, name: me.name, org: me.org, email: me.email, credit: me.credit, round: ROUND,
      clientTime: new Date().toISOString(), page: location.pathname.slice(-200), en: plain((S.en || {})[k]).slice(0, 3000) };
    var dr = (S.ne || {})[k]; if (dr && !isProt(k)) f.draft = plain(dr).slice(0, 3000);
    if (text) f.text = text.slice(0, 3000);
    if (note) f.note = note.slice(0, 1000);
    var fields = {}; Object.keys(f).forEach(function (x) { fields[x] = { stringValue: String(f[x]) }; });
    msg.textContent = "Sending…"; msg.style.color = "#52647a";
    fetch("https://firestore.googleapis.com/v1/projects/" + FB.pid + "/databases/(default)/documents/formproof?key=" + FB.key,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ fields: fields }) })
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        done[k] = verdict === "ok" ? "correct" : verdict === "change" ? "change sent" : "Nepali sent"; put(DONE, done);
        row.classList.add("done"); msg.textContent = "Sent. Thank you."; msg.style.color = "#1a7f37";
        row.querySelector(".pfEd").classList.remove("on"); row.querySelector(".pfK span").textContent = k + " · ✓ " + done[k]; count();
      })
      .catch(function () { msg.textContent = "Not sent — check the connection and tap again."; msg.style.color = "#a3221c"; });
  }
  $("#pfList").addEventListener("click", function (e) {
    var row = e.target.closest(".pfRow"); if (!row) return;
    if (e.target.closest(".pfShow")) {
      e.preventDefault(); var k = row.getAttribute("data-k");
      var el = document.querySelector('[data-i18n="' + k.replace(/"/g, '\\"') + '"],[data-i18n-ph="' + k.replace(/"/g, '\\"') + '"]');
      pane.classList.remove("on");
      if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.classList.add("pfFlash"); setTimeout(function () { el.classList.remove("pfFlash"); }, 2500);}
      return;
    }
    var b = e.target.closest("button[data-a]"); if (!b) return;
    var a = b.getAttribute("data-a"), ed = row.querySelector(".pfEd");
    if (a === "ok") send(row, "ok");
    if (a === "edit") { ed.classList.add("on"); var ta = ed.querySelector("textarea"); var d = (S.ne || {})[row.getAttribute("data-k")]; if (!ta.value && d && !isProt(row.getAttribute("data-k"))) ta.value = plain(d); ta.focus(); }
    if (a === "cancel") ed.classList.remove("on");
    if (a === "send") { var t = ed.querySelector("textarea").value.trim(); if (!t) { ed.querySelector("textarea").focus(); return; }
      var k = row.getAttribute("data-k"); send(row, (S.ne || {})[k] && !isProt(k) ? "change" : "write", t, ed.querySelector(".pfNote").value.trim()); }
  });
  $("#pfTodo").addEventListener("change", render);
  btn.addEventListener("click", function () { render(); pane.classList.add("on"); });
  $("#pfClose").addEventListener("click", function () { pane.classList.remove("on"); });
  pane.addEventListener("click", function (e) { if (e.target === pane) pane.classList.remove("on"); });
  setTimeout(function () { K = keys(); count(); }, 600);
})();

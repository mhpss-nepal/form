# Keying evidence — `referral.html`, `phq9.html`, `contact.html`

MHPSS Nepal · task `t_2cfc3bab` · reconciliation run · 2026-09-20

Revised scope for this run: reconcile the two worktrees, get the three keyed
pages clean through `tools/i18n-check.py`, and report the verified
`professionalOnly` count **after** keying. Translation to a reviewed standard is
the next ticket and is **not attempted here** (see the follow-on note at the
end).

Every command below was run from `/root/mhpss-nepal-work/form-translation` and
its output is reproduced verbatim, including the dictionary's sha256 — because
the previous evidence recorded a gate run whose result depended on a file the
command never named, and that file later went stale.

### Gate: the dictionary names itself

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n-check.py

MHPSS Nepal — bilingual gate
  dictionary: ../hub/assets/i18n-strings.js
  dictionary sha256: 6ef1aa0095c0ad705d5d2eec012356fe89e554daf664de43f7fa05a47ad340fa
  WARNING: this file is not under version control. It is a
           staging copy, so it can be older than the tracked
           dictionary; the counts below describe this copy.
  English strings: 971   Nepali strings: 294

  KEPT IN ENGLISH ON PURPOSE
    32 strings held back from translation: clinical.phq9ValidatedTextWarning, consent.label, consent.phq9, phq9.cutoff.interpretation, phq9.cutoff.useWarning, phq9.item1, phq9.item2, phq9.item3, phq9.item4, phq9.item5, phq9.item6, phq9.item7, phq9.item8, phq9.item9, phq9.item9Instruction, phq9.itemDifficulty, phq9.itemInstruction, phq9.scale0, phq9.scale1, phq9.scale2, phq9.scale3, phq9.scaleDifficulty0, phq9.scaleDifficulty1, phq9.scaleDifficulty2, phq9.scaleDifficulty3, safeguard.checkLabel, safeguard.confirmation, safeguard.consequence, safeguard.referralExclusion, sr.clinicalNote, sr.p001, sr.p007

  ENFORCED — keyed and fully translated
    (none yet)

  KEYED — no loose English allowed; Nepali still awaited
    contact.html                       OK    93 keys  (37 awaiting Nepali)
    index.html                         OK    88 keys  (82 awaiting Nepali)
    phq9.html                          OK    51 keys  (23 awaiting Nepali)
    referral.html                      OK    88 keys  (40 awaiting Nepali)
    selfreport.html                    OK    54 keys  (49 awaiting Nepali)

  NOT YET MIGRATED
    5ws-report.html                      872 words
    cards.html                           500 words
    TOTAL                               1372 words to key up

  Gate open: every enforced page is fully keyed and fully translated.

(exit 0)
```

---

### Reconciliation: gate dictionary vs canonical, by sha256

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n-dictionary-sync-check.py

gate dictionary      6ef1aa0095c0ad70  /root/mhpss-nepal-work/form-translation/../hub/assets/i18n-strings.js
canonical dictionary 6ef1aa0095c0ad70  /root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js
IN SYNC

(exit 0)
```

---

### professionalOnly prefix health + per-page protection count

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n-protection-report.py

dictionary: /root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js
live EN keys: 971   professionalOnly prefixes: 9

PREFIX HEALTH
  sr.p007        matches  1 live key(s)
  sr.p001        matches  1 live key(s)
  sr.clinicalNote matches  1 live key(s)
  phq9.item      matches 12 live key(s)
  phq9.scale     matches  8 live key(s)
  phq9.cutoff    matches  2 live key(s)
  consent.       matches  2 live key(s)
  safeguard.     matches  4 live key(s)
  clinical.      matches  1 live key(s)
  9 of 9 prefixes match a live key; 0 dead
  32 keys held in English in total

PER PAGE (keys the page really uses)
  page                 keys  protected  prefixes in force
  referral.html          88          4  safeguard.=4
        - safeguard.checkLabel
        - safeguard.confirmation
        - safeguard.consequence
        - safeguard.referralExclusion
  phq9.html              52         12  phq9.item=3, phq9.scale=4, phq9.cutoff=2, consent.=2, clinical.=1
        - clinical.phq9ValidatedTextWarning
        - consent.label
        - consent.phq9
        - phq9.cutoff.interpretation
        - phq9.cutoff.useWarning
        - phq9.item9Instruction
        - phq9.itemDifficulty
        - phq9.itemInstruction
        - phq9.scaleDifficulty0
        - phq9.scaleDifficulty1
        - phq9.scaleDifficulty2
        - phq9.scaleDifficulty3
  contact.html           93          0  -
  index.html             88          0  -
  selfreport.html        54          3  sr.p007=1, sr.p001=1, sr.clinicalNote=1
        - sr.clinicalNote
        - sr.p001
        - sr.p007
  5ws-report.html       104          0  -

phq9.html shows one more key than tools/i18n-check.py's HTML scanner,
because phq9.item9Instruction is minted inside a <script> (the item-9
safety instruction, rendered only after a positive answer). The scanner
cannot see script text; this report reads the attribute wherever it is.

OK: every professionalOnly prefix matches a live key.

(exit 0)
```

---

### Keying contract tests (10)

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 -m unittest test_i18n_keying

..........
----------------------------------------------------------------------
Ran 10 tests in 5.506s

OK

(exit 0)
```

---

### Keying failing-first: pinned pre-keying fixtures

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n_failing_first.py

AT BASE: exit=1
AssertionError: 'safeguard.' not found in '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>Referral record — MHPSS Nepal</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<!-- Lora + Manrope. design.css declares Georgia / system fallbacks, so a\n     failed font request costs typography and never legibility -- which\n     matters on the field forms, where there may be no signal at all. -->\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Manrope:wght@400;600;700;800&display=swap">\n<link rel="stylesheet" href="../hub/assets/app.css">\n<link rel="stylesheet" href="../hub/assets/design.css">\n<link rel="stylesheet" href="../hub/assets/form.css">\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="theme-color" content="#1d1d1b">\n<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n<meta name="apple-mobile-web-app-title" content="MHPSS Field">\n</head>\n<body class="fx">\n<div class="ribbon">Revised draft for field piloting <span>· saved on this phone, sent to the coordination register when there is signal</span></div>\n\n<div class="top">\n  <div>\n    <div class="brand">Referral record</div>\n    <div class="sub">Layer 1 · Rasuwa / Bhote Koshi</div>\n  </div>\n  <div class="spacer"></div>\n  <a href="index.html">← Forms</a>\n  <a href="../hub/">Hub</a>\n</div>\n\n<div class="wrap">\n\n  <h1>Where a person was sent, and whether they arrived</h1>\n  <p class="lede">On 14 September the briefing recorded that around 5,000 psychosocial counselling cases\n    had been logged, but that once a person reaches a health facility their case goes into HMIS and is no\n    longer visible here. This form is the join. Without it, “continuum of care” is a claim rather than\n    something anyone can show.</p>\n\n  <div class="banner stop">\n    <b>Three kinds of case do not belong on this form. Stop and use the proper pathway.</b>\n    <ul>\n      <li><b>Gender-based violence.</b> GBV cases follow the specialised, survivor-centred pathway of the\n        protection cluster, with its own consent and its own confidential system. Never record a GBV\n        referral in a shared coordination form, not even coded.</li>\n      <li><b>An unaccompanied or separated child.</b> These go to child-protection case management.\n        Around 200 were reported in one area alone on 14 September; each one is a case file, not a row.</li>\n      <li><b>Immediate risk to life.</b> Act first. Record afterwards, if at all.</li>\n    </ul>\n    Recording these here would put people at risk and would break the consent under which they spoke to\n    you. The count of such referrals can be reported to coordination as a number, by the pathway that\n    holds them — never as records here.\n  </div>\n\n  <form id="f" autocomplete="off" novalidate>\n\n    <div class="card">\n      <div class="step"><span class="n">1</span><h2>Who is referring</h2><span class="hint">remembered</span></div>\n      <div class="row three">\n        <div class="f"><label for="org">Referring organisation</label><select id="org"></select></div>\n        <div class="f"><label for="cadre">Referred by</label><select id="cadre"></select></div>\n        <div class="f"><label for="dateAD">Date of referral (AD)</label><input type="date" id="dateAD"></div>\n      </div>\n      <div class="row three">\n        <div class="f"><label for="district">District</label><select id="district"></select></div>\n        <div class="f">\n          <label for="site">Site referred from</label><select id="site"></select>\n        </div>\n        <div class="f">\n          <label for="focalPhone">Referrer phone <span class="opt">— optional</span></label>\n          <input type="tel" id="focalPhone" placeholder="98XXXXXXXX">\n          <div class="help">So the receiving service can close the loop with you.</div>\n        </div>\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">2</span><h2>Who is being referred</h2></div>\n      <div class="banner"><b>No name, no phone number, no date of birth.</b> A referral needs those to work,\n        and they are handed over <b>person to person or on paper</b> between the referring worker and the\n        receiving service. What is recorded here is only what coordination needs in order to see whether\n        referrals are being made and completed.</div>\n      <div class="row four">\n        <div class="f">\n          <label for="ccode">Contact code</label>\n          <input type="text" id="ccode" placeholder="NP-XXXXX-XXXXX" style="font-family:ui-monospace,Menlo,monospace">\n          <div class="help">From the <a href="contact.html">contact record</a>.</div>\n        </div>\n        <div class="f">\n          <label for="sex">Sex</label>\n          <select id="sex"><option value="">— choose —</option><option value="F">Female</option><option value="M">Male</option><option value="O">Other</option><option value="NS">Not stated</option></select>\n        </div>\n        <div class="f">\n          <label for="ageband">Age band</label>\n          <select id="ageband"><option value="">— choose —</option><option value="0-4">0–4</option><option value="5-11">5–11</option><option value="12-17">12–17</option><option value="18-24">18–24</option><option value="25-59">25–59</option><option value="60+">60 and over</option><option value="NS">Not stated</option></select>\n        </div>\n        <div class="f">\n          <label for="tgroup">Target group</label><select id="tgroup"></select>\n        </div>\n      </div>\n      <div class="f">\n        <label>Safeguarding check</label>\n        <div class="radios">\n          <label><input type="checkbox" id="notgbv"> This is not a GBV case, not an unaccompanied or separated child, and not an immediate risk to life</label>\n        </div>\n        <div class="help">If you cannot tick this, close the form and use the specialised pathway.</div>\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">3</span><h2>The referral</h2></div>\n      <div class="row three">\n        <div class="f">\n          <label for="reason">Referred for</label>\n          <select id="reason"></select>\n        </div>\n        <div class="f">\n          <label for="direction">Direction</label>\n          <select id="direction">\n            <option value="">— choose —</option>\n            <option value="OUT">Out — we sent them elsewhere</option>\n            <option value="IN">In — they were sent to us</option>\n          </select>\n        </div>\n        <div class="f">\n          <label for="urgency">Urgency</label>\n          <select id="urgency">\n            <option value="">— choose —</option>\n            <option value="SAME">Same day</option>\n            <option value="WEEK">Within a week</option>\n            <option value="ROUT">Routine</option>\n          </select>\n        </div>\n      </div>\n      <div class="row">\n        <div class="f">\n          <label for="toType">Type of service referred to</label>\n          <select id="toType">\n            <option value="">— choose —</option>\n            <option value="PSC">Psychosocial counselling</option>\n            <option value="PHC">Health post / primary care</option>\n            <option value="HOSP">Hospital — general</option>\n            <option value="PSYT">Psychiatric service</option>\n            <option value="PROT">Protection services</option>\n            <option value="LEG">Legal or documentation support</option>\n            <option value="LIVE">Livelihood or cash support</option>\n            <option value="OTH">Other</option>\n          </select>\n        </div>\n        <div class="f">\n          <label for="toName">Name of receiving service <span class="opt">— optional</span></label>\n          <input type="text" id="toName" maxlength="120" placeholder="Facility or organisation">\n          <div class="help">Free text for now. The agreed directory of services does not exist yet — it is\n            still the single Excel sheet noted on 14 September, which is why this is not a dropdown.</div>\n        </div>\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">4</span><h2>Did they arrive?</h2></div>\n      <div class="banner warn"><b>This is the field that will be empty, and that is the finding.</b>\n        A referral is only complete when the receiving service confirms the person arrived. Nobody can\n        fill this in from the referring side alone. Leave it as “not yet known” and come back — the\n        proportion that stays unknown is the honest measure of whether the pathway works.</div>\n      <div class="row three">\n        <div class="f">\n          <label for="arrived">Arrival</label>\n          <select id="arrived">\n            <option value="UNK">Not yet known</option>\n            <option value="Y">Confirmed arrived</option>\n            <option value="N">Did not arrive</option>\n            <option value="DECL">Person declined the referral</option>\n          </select>\n        </div>\n        <div class="f">\n          <label for="arrDate">Date confirmed <span class="opt">— if known</span></label>\n          <input type="date" id="arrDate">\n        </div>\n        <div class="f">\n          <label for="confBy">Confirmed how <span class="opt">— optional</span></label>\n          <select id="confBy">\n            <option value="">— choose —</option>\n            <option value="RECV">Receiving service told us</option>\n            <option value="PERS">The person told us</option>\n            <option value="FAM">A family member told us</option>\n            <option value="OTH">Other</option>\n          </select>\n        </div>\n      </div>\n      <div class="f">\n        <label for="barrier">If they did not arrive, what got in the way? <span class="opt">— optional</span></label>\n        <select id="barrier">\n          <option value="">— choose —</option>\n          <option value="DIST">Distance or no transport</option>\n          <option value="COST">Cost</option>\n          <option value="CLOSED">Service was closed or full</option>\n          <option value="STIG">Stigma or family objection</option>\n          <option value="LOST">Lost contact with the person</option>\n          <option value="OTH">Other</option>\n        </select>\n        <div class="help">The barrier list is what turns a broken pathway into something fixable.</div>\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">5</span><h2>Save</h2></div>\n      <div id="errs"></div>\n      <div style="display:flex;gap:9px;flex-wrap:wrap;align-items:center">\n        <button type="submit" class="btn">Save this referral</button>\n        <button type="button" class="btn ghost" id="csvBtn">Export CSV</button>\n        <button type="button" class="btn grey" id="clearBtn">Clear everything on this device</button>\n        <span class="xs" id="count"></span>\n      </div>\n      <div class="f" style="margin-top:16px">\n        <label>What would be sent, if there were anywhere to send it</label>\n        <pre id="payload" class="pay">—</pre>\n      </div>\n    </div>\n  </form>\n</div>\n\n<script src="../hub/assets/codes.js"></script>\n<script src="../hub/assets/l1.js"></script>\n<script src="../hub/assets/fb-config.js"></script>\n<script src="../hub/assets/fb.js"></script>\n<script>\n(function () {\n  "use strict";\n  var C = window.CODES, L = window.L1, KIND = "referral";\n  var $ = function (id) { return document.getElementById(id); };\n\n  var REASONS = [\n    { code: "DISTRESS", name: "Severe distress not settling with support" },\n    { code: "SUSPMNS",  name: "Possible mental disorder needing clinical assessment" },\n    { code: "MEDS",     name: "Medication review or continuation" },\n    { code: "PREEX",    name: "Pre-existing condition interrupted by the disaster" },\n    { code: "SUBST",    name: "Alcohol or substance use" },\n    { code: "EPIL",     name: "Seizures / epilepsy" },\n    { code: "SOCIAL",   name: "Social, documentation or livelihood need" },\n    { code: "OTH",      name: "Other" }\n  ];\n\n  L.fillSelect($("org"), C.ORGS.concat([{ code: "OTHER", name: "Other — not listed", np: "अन्य — सूचीमा नभएको", np_src: "draft" }]));\n  L.fillSelect($("cadre"), C.CADRES);\n  L.fillSelect($("district"), C.DISTRICTS);\n  L.fillSelect($("tgroup"), C.TARGET_GROUPS);\n  L.fillSelect($("reason"), REASONS);\n  $("dateAD").value = L.today();\n  ["org", "cadre", "focalPhone", "district"].forEach(function (id) {\n    var v = L.recall(id); if (v) $(id).value = v;\n    $(id).addEventListener("change", function () { L.remember(id, $(id).value); });\n  });\n\n  function refreshSites() {\n    var d = $("district").value;\n    var list = C.FORM_SITES.filter(function (s) { return s.source !== "escape" && (!d || s.district === d); });\n    L.fillSelect($("site"), list.concat([{ code: "OTHER", name: "Other — not on the roster" }]));\n  }\n  $("district").addEventListener("change", function () { refreshSites(); payload(); });\n  refreshSites();\n\n  function record() {\n    return {\n      schema: "mhpss-np-referral/0.1.0-draft",\n      kind: "referral",\n      org: $("org").value,\n      referred_by: $("cadre").value,\n      referrer_phone: $("focalPhone").value.trim(),\n      date_ad: $("dateAD").value,\n      district: $("district").value,\n      site_from: $("site").value,\n      contact_code: $("ccode").value.trim().toUpperCase(),\n      sex: $("sex").value,\n      age_band: $("ageband").value,\n      target_group: $("tgroup").value,\n      safeguarding_confirmed: $("notgbv").checked,\n      excludes_gbv_uasc_lifethreat: $("notgbv").checked,\n      reason: $("reason").value,\n      direction: $("direction").value,\n      urgency: $("urgency").value,\n      to_service_type: $("toType").value,\n      to_service_name: $("toName").value.trim(),\n      arrived: $("arrived").value,\n      arrival_confirmed_date: $("arrDate").value,\n      confirmed_by: $("confBy").value,\n      barrier: $("barrier").value\n    };\n  }\n  var COLS = Object.keys(record()).concat(["_saved"]);\n  function payload() { $("payload").textContent = JSON.stringify(record(), null, 2); }\n\n  function problems(r) {\n    var e = [];\n    if (!r.org) e.push("Choose the referring organisation.");\n    if (!r.referred_by) e.push("Say who made the referral.");\n    if (!r.date_ad) e.push("Give the date.");\n    if (r.date_ad && r.date_ad > L.today()) e.push("The referral date is in the future.");\n    if (!r.district) e.push("Choose the district.");\n    if (!r.site_from) e.push("Choose the site.");\n    if (!r.contact_code) e.push("Give the contact code.");\n    if (r.contact_code && !/^NP-[0-9A-Z]{5}-[0-9A-Z]{5}$/.test(r.contact_code))\n      e.push("The contact code should look like NP-ABCDE-12345.");\n    if (!r.age_band) e.push("Choose the age band.");\n    if (!r.target_group) e.push("Choose the target group.");\n    if (!r.safeguarding_confirmed)\n      e.push("The safeguarding check is not ticked. If this is a GBV case, an unaccompanied or separated child, or an immediate risk to life, it must not be recorded here at all.");\n    if (!r.reason) e.push("Say what the referral is for.");\n    if (!r.direction) e.push("Say whether the referral is out or in.");\n    if (!r.urgency) e.push("Choose the urgency.");\n    if (!r.to_service_type) e.push("Choose the type of service referred to.");\n    if (r.arrived === "Y" && !r.arrival_confirmed_date)\n      e.push("If arrival is confirmed, give the date it was confirmed.");\n    if (r.arrival_confirmed_date && r.arrival_confirmed_date < r.date_ad)\n      e.push("Arrival cannot be confirmed before the referral was made.");\n    if (r.arrived === "N" && !r.barrier)\n      e.push("If the person did not arrive, say what got in the way — that is the point of recording it.");\n    return e;\n  }\n\n  function showCount() {\n    var n = L.all(KIND).length;\n    $("count").textContent = n ? n + " referral(s) on this device" : "nothing saved on this device yet";\n  }\n  showCount();\n\n  Array.prototype.forEach.call(document.querySelectorAll("input,select"), function (el) {\n    el.addEventListener("change", payload);\n    if (el.tagName === "INPUT" && el.type === "text") el.addEventListener("input", payload);\n  });\n\n  $("f").addEventListener("submit", function (ev) {\n    ev.preventDefault();\n    var r = record(), e = problems(r);\n    if (e.length) {\n      $("errs").innerHTML = \'<div class="banner stop"><b>Not saved.</b><ul><li>\' + e.join("</li><li>") + "</li></ul></div>";\n      $("errs").scrollIntoView({ block: "center" });\n      return;\n    }\n    var res = L.save(KIND, r);\n    $("errs").innerHTML = \'<div class="banner ok"><b>Saved on this device.</b> \' +\n      (res.persisted ? "" : "Storage is blocked — export before closing. ") +\n      "The record goes to the coordination register when there is signal. Come back to update whether the person arrived.</div>";\n    showCount();\n  });\n\n  $("csvBtn").addEventListener("click", function () {\n    var list = L.all(KIND);\n    if (!list.length) { alert("Nothing saved on this device yet."); return; }\n    L.download("mhpss_np_referrals_" + L.stamp() + ".csv", L.toCSV(list, COLS), "text/csv");\n  });\n  $("clearBtn").addEventListener("click", function () {\n    if (!L.all(KIND).length) { alert("Nothing saved on this device yet."); return; }\n    if (confirm("Delete every referral held in this browser? This cannot be undone.")) {\n      L.clear(KIND); showCount(); $("errs").innerHTML = \'<div class="banner"><b>Cleared.</b></div>\';\n    }\n  });\n\n  payload();\n})();\n</script>\n<script src="pwa.js"></script>\n<!-- The bilingual engine. On a page that is not yet keyed up it still earns\n     its place: it sets data-lang, which is what makes the Nepali words in\n     the code lists appear in the dropdowns, and it mounts the ENG/NEP\n     toggle and an honest notice saying the prose is still English. -->\n<script src="../hub/assets/mark.js"></script>\n<script src="../hub/assets/icons.js"></script>\n<script src="../hub/assets/i18n-strings.js"></script>\n<script src="../hub/assets/i18n.js"></script>\n</body>\n</html>\n<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>PHQ-9 follow-up measure — MHPSS Nepal</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<!-- Lora + Manrope. design.css declares Georgia / system fallbacks, so a\n     failed font request costs typography and never legibility -- which\n     matters on the field forms, where there may be no signal at all. -->\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Manrope:wght@400;600;700;800&display=swap">\n<link rel="stylesheet" href="../hub/assets/app.css">\n<link rel="stylesheet" href="../hub/assets/design.css">\n<link rel="stylesheet" href="../hub/assets/form.css">\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="theme-color" content="#1d1d1b">\n<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n<meta name="apple-mobile-web-app-title" content="MHPSS Field">\n</head>\n<body class="fx">\n<div class="ribbon">Revised draft <span>· English items only — the validated Nepali text has not been obtained · saved on this phone, sent to the coordination register when there is signal</span></div>\n\n<div class="top">\n  <div>\n    <div class="brand">PHQ-9 · follow-up measure</div>\n    <div class="sub">Layer 1 · Rasuwa / Bhote Koshi</div>\n  </div>\n  <div class="spacer"></div>\n  <a href="index.html">← Forms</a>\n  <a href="../hub/">Hub</a>\n</div>\n\n<div class="wrap">\n\n  <h1>Following one person over time</h1>\n  <p class="lede">This measure exists to answer one question the 14 September briefing asked: does a person\n    move from acute distress towards a clinical disorder, or away from it? It is for repeating with\n    <b>someone already in care</b>, so the second score can be compared with the first.</p>\n\n  <div class="banner stop">\n    <b>Do not use this to screen a shelter.</b> In the Nepali validation the cut-off of 10 or more had a\n    positive predictive value of 0.42 — in that primary-care sample, fewer than half of the people who\n    screened positive turned out to have a depressive episode. Run it across a displaced population and\n    most positives will be wrong, while the people you flag will have been told something about themselves\n    that is not true. Use it where someone has already been identified and referred.\n  </div>\n\n  <div class="banner warn">\n    <b>The Nepali text is missing, and this form is not ready for field use without it.</b> The Nepali\n    version validated by the PRIME consortium exists, but the copy available is typeset in a legacy\n    non-Unicode Nepali font, so the characters cannot be transferred here without risking a corrupted\n    questionnaire. <b>Nothing has been translated or approximated.</b> Before any real use, obtain the\n    Unicode Nepali items from the PRIME / Kohrt source and have them checked by a Nepali-speaking\n    clinician. Administering the English items to a Nepali speaker through an untrained interpreter is\n    not the same instrument and the cut-off does not carry over.\n  </div>\n\n  <form id="f" autocomplete="off" novalidate>\n\n    <div class="card">\n      <div class="step"><span class="n">1</span><h2>Who, and which visit</h2></div>\n      <div class="row three">\n        <div class="f">\n          <label for="org">Organisation</label>\n          <select id="org"></select>\n        </div>\n        <div class="f">\n          <label for="cadre">Administered by</label>\n          <select id="cadre"></select>\n          <div class="help">A measure like this belongs with a counsellor or clinician, not a volunteer.</div>\n        </div>\n        <div class="f">\n          <label for="dateAD">Date — Gregorian (AD)</label>\n          <input type="date" id="dateAD">\n        </div>\n      </div>\n      <div class="row three">\n        <div class="f">\n          <label for="ccode">Contact code</label>\n          <input type="text" id="ccode" placeholder="NP-XXXXX-XXXXX" style="font-family:ui-monospace,Menlo,monospace">\n          <div class="help">Paste the code from the person\'s <a href="contact.html">service contact\n            record</a>, so the two scores can be lined up without a name.</div>\n        </div>\n        <div class="f">\n          <label for="visit">Which administration is this?</label>\n          <select id="visit">\n            <option value="">— choose —</option>\n            <option value="1">First — baseline</option>\n            <option value="2">Follow-up</option>\n            <option value="X">Not recorded</option>\n          </select>\n        </div>\n        <div class="f">\n          <label for="lang">Language used</label>\n          <select id="lang">\n            <option value="">— choose —</option>\n            <option value="EN">English, directly</option>\n            <option value="NE-INT">Nepali, through an interpreter</option>\n            <option value="NE-VAL">Validated Nepali form on paper</option>\n            <option value="OTH">Another language</option>\n          </select>\n          <div class="help">Recorded because it changes what the score means.</div>\n        </div>\n      </div>\n      <div class="f">\n        <label>Consent</label>\n        <div class="radios">\n          <label><input type="checkbox" id="consent"> The person was told what this is for and agreed to answer</label>\n        </div>\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">2</span><h2>The nine items</h2><span class="hint" id="answered"></span></div>\n      <p class="lede" style="margin-bottom:14px"><b>Over the last 2 weeks, how often have you been bothered\n        by any of the following problems?</b></p>\n      <div class="scale" id="items"></div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">3</span><h2>Difficulty, and the score</h2></div>\n      <div class="f">\n        <label for="fx">If you checked off any problems, how difficult have these problems made it for you\n          to do your work, take care of things at home, or get along with other people?</label>\n        <select id="fx">\n          <option value="">— choose —</option>\n          <option value="0">Not difficult at all</option>\n          <option value="1">Somewhat difficult</option>\n          <option value="2">Very difficult</option>\n          <option value="3">Extremely difficult</option>\n        </select>\n      </div>\n\n      <div class="score" id="score">\n        <span class="big" id="sNum">—</span>\n        <span class="of">out of 27</span>\n        <span class="band" id="sBand">answer all nine items</span>\n      </div>\n\n      <div id="risk"></div>\n\n      <div class="help" style="margin-top:12px">\n        Bands are the standard PHQ-9 cut-points (Kroenke, Spitzer &amp; Williams, 2001): 0–4 minimal,\n        5–9 mild, 10–14 moderate, 15–19 moderately severe, 20–27 severe. The action threshold of\n        <b>10 or more</b> is the one validated in Nepal (Kohrt et al., 2016; sensitivity 0.94,\n        specificity 0.80, in 125 primary-care patients in Chitwan). A score is not a diagnosis and\n        must not be recorded as one.\n      </div>\n    </div>\n\n    <div class="card">\n      <div class="step"><span class="n">4</span><h2>Save</h2></div>\n      <div id="errs"></div>\n      <div style="display:flex;gap:9px;flex-wrap:wrap;align-items:center">\n        <button type="submit" class="btn">Save this administration</button>\n        <button type="button" class="btn ghost" id="csvBtn">Export CSV</button>\n        <button type="button" class="btn grey" id="clearBtn">Clear everything on this device</button>\n        <span class="xs" id="count"></span>\n      </div>\n      <div class="f" style="margin-top:16px">\n        <label>What would be sent, if there were anywhere to send it</label>\n        <pre id="payload" class="pay">—</pre>\n        <div class="help">Item-by-item answers are kept because a total alone cannot be re-checked, and\n          because item 9 has to be auditable. There is no name, no phone number and no date of birth.</div>\n      </div>\n    </div>\n\n  </form>\n\n  <h2>Attribution</h2>\n  <div class="banner">\n    PHQ-9 was developed by Drs Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with\n    an educational grant from Pfizer Inc. The instrument carries the statement: <i>“No permission required\n    to reproduce, translate, display or distribute.”</i> The items above are reproduced verbatim on that\n    basis. The Nepali adaptation was made and validated through the Programme for Improving Mental Health\n    Care (PRIME) consortium, funded by UK aid — and is <b>not</b> included here, for the reason given at\n    the top of this page.\n  </div>\n</div>\n\n<script src="../hub/assets/codes.js"></script>\n<script src="../hub/assets/l1.js"></script>\n<script src="../hub/assets/fb-config.js"></script>\n<script src="../hub/assets/fb.js"></script>\n<script>\n(function () {\n  "use strict";\n  var C = window.CODES, L = window.L1, KIND = "phq9";\n  var $ = function (id) { return document.getElementById(id); };\n\n  /* Verbatim PHQ-9 items. Do not paraphrase, reorder or shorten these —\n     a reworded PHQ-9 is no longer the validated instrument. */\n  var ITEMS = [\n    "Little interest or pleasure in doing things",\n    "Feeling down, depressed, or hopeless",\n    "Trouble falling or staying asleep, or sleeping too much",\n    "Feeling tired or having little energy",\n    "Poor appetite or overeating",\n    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",\n    "Trouble concentrating on things, such as reading the newspaper or watching television",\n    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",\n    "Thoughts that you would be better off dead or of hurting yourself in some way"\n  ];\n  var OPTS = [\n    { v: 0, l: "Not at all" },\n    { v: 1, l: "Several days" },\n    { v: 2, l: "More than half the days" },\n    { v: 3, l: "Nearly every day" }\n  ];\n\n  L.fillSelect($("org"), C.ORGS.concat([{ code: "OTHER", name: "Other — not listed", np: "अन्य — सूचीमा नभएको", np_src: "draft" }]));\n  L.fillSelect($("cadre"), C.CADRES);\n  $("dateAD").value = L.today();\n  ["org", "cadre"].forEach(function (id) {\n    var v = L.recall(id); if (v) $(id).value = v;\n    $(id).addEventListener("change", function () { L.remember(id, $(id).value); });\n  });\n\n  /* render items */\n  var html = ITEMS.map(function (t, i) {\n    var opts = OPTS.map(function (o) {\n      return \'<label><input type="radio" name="q\' + i + \'" value="\' + o.v + \'"> \' + o.l +\n             \' <span style="color:var(--mute)">(\' + o.v + \')</span></label>\';\n    }).join("");\n    return \'<div class="q" id="qw\' + i + \'"><div class="qt">\' + (i + 1) + \'. \' +\n           t.replace(/&/g, "&amp;").replace(/</g, "&lt;") +\n           \'<span class="np">Nepali text not obtained — see the warning above.</span></div>\' +\n           \'<div class="opts">\' + opts + \'</div></div>\';\n  }).join("");\n  $("items").innerHTML = html;\n\n  function answers() {\n    return ITEMS.map(function (_, i) {\n      var r = document.querySelector(\'input[name="q\' + i + \'"]:checked\');\n      return r ? +r.value : null;\n    });\n  }\n  function band(t) {\n    if (t <= 4)  return { t: "Minimal", act: false };\n    if (t <= 9)  return { t: "Mild", act: false };\n    if (t <= 14) return { t: "Moderate", act: true };\n    if (t <= 19) return { t: "Moderately severe", act: true };\n    return { t: "Severe", act: true };\n  }\n\n  function refresh() {\n    var a = answers(), done = a.filter(function (x) { return x !== null; }).length;\n    $("answered").textContent = done + " of 9 answered";\n    a.forEach(function (x, i) {\n      $("qw" + i).className = x === null ? "q" : "q done";\n    });\n\n    if (done === 9) {\n      var total = a.reduce(function (s, x) { return s + x; }, 0), b = band(total);\n      $("sNum").textContent = total;\n      $("sBand").textContent = b.t + (b.act ? " — at or above the threshold validated in Nepal" : "");\n      $("sBand").style.color = b.act ? "#9b2c2c" : "#2f6b53";\n    } else {\n      $("sNum").textContent = "—";\n      $("sBand").textContent = "answer all nine items";\n      $("sBand").style.color = "";\n    }\n\n    /* item 9 — asking this question creates a duty to act on the answer */\n    if (a[8] !== null && a[8] > 0) {\n      $("risk").innerHTML = \'<div class="banner stop" style="margin:14px 0 0"><b>Item 9 is positive. \' +\n        \'Do not close this form and move on.</b> Stay with the person, ask directly about thoughts of \' +\n        \'suicide and about means and plan, and follow your organisation\\\'s referral pathway now — record \' +\n        \'it on the <a href="referral.html">referral form</a>. If your organisation has no pathway for \' +\n        \'this, that is the gap to raise at the Technical Working Group, and it should be raised before this \' +\n        \'instrument is used in the field at all. The answer to item 9 is kept in the record so that a \' +\n        \'positive answer can be audited against whether a referral followed.</div>\';\n    } else {\n      $("risk").innerHTML = "";\n    }\n    payload();\n  }\n\n  function record() {\n    var a = answers(), done = a.filter(function (x) { return x !== null; }).length;\n    var total = done === 9 ? a.reduce(function (s, x) { return s + x; }, 0) : null;\n    return {\n      schema: "mhpss-np-phq9/0.1.0-draft",\n      kind: "phq9",\n      instrument: "PHQ-9",\n      item_language: $("lang").value,\n      nepali_validated_text_used: $("lang").value === "NE-VAL",\n      org: $("org").value,\n      administered_by: $("cadre").value,\n      date_ad: $("dateAD").value,\n      contact_code: $("ccode").value.trim().toUpperCase(),\n      administration: $("visit").value,\n      consent_recorded: $("consent").checked,\n      q1: a[0], q2: a[1], q3: a[2], q4: a[3], q5: a[4],\n      q6: a[5], q7: a[6], q8: a[7], q9: a[8],\n      total: total,\n      band: total === null ? "" : band(total).t,\n      at_or_above_nepal_threshold: total === null ? "" : total >= 10,\n      functional_difficulty: $("fx").value,\n      item9_positive: a[8] === null ? "" : a[8] > 0,\n      is_diagnosis: false\n    };\n  }\n  var COLS = Object.keys(record()).concat(["_saved"]);\n  function payload() { $("payload").textContent = JSON.stringify(record(), null, 2); }\n\n  function problems(r) {\n    var e = [];\n    if (!r.org) e.push("Choose the organisation.");\n    if (!r.administered_by) e.push("Say who administered it.");\n    if (!r.date_ad) e.push("Give the date.");\n    if (r.date_ad && r.date_ad > L.today()) e.push("The date is in the future.");\n    if (!r.contact_code) e.push("Give the contact code, so this score can be matched to a person without a name.");\n    if (r.contact_code && !/^NP-[0-9A-Z]{5}-[0-9A-Z]{5}$/.test(r.contact_code))\n      e.push("The contact code should look like NP-ABCDE-12345.");\n    if (!r.administration) e.push("Say whether this is the baseline or a follow-up.");\n    if (!r.item_language) e.push("Say which language was used.");\n    if (!r.consent_recorded) e.push("Consent has not been recorded. Do not administer this without it.");\n    if (r.total === null) e.push("All nine items have to be answered — a partial PHQ-9 has no score.");\n    if (!r.functional_difficulty) e.push("Answer the difficulty question.");\n    return e;\n  }\n\n  function showCount() {\n    var n = L.all(KIND).length;\n    $("count").textContent = n ? n + " administration(s) on this device" : "nothing saved on this device yet";\n  }\n  showCount();\n\n  document.querySelectorAll(\'input[type=radio]\').forEach(function (i) {\n    i.addEventListener("change", refresh);\n  });\n  ["lang", "fx", "visit", "ccode", "consent", "org", "cadre", "dateAD"].forEach(function (id) {\n    $(id).addEventListener("change", payload);\n  });\n  $("ccode").addEventListener("input", payload);\n\n  $("f").addEventListener("submit", function (ev) {\n    ev.preventDefault();\n    var r = record(), e = problems(r);\n    if (e.length) {\n      $("errs").innerHTML = \'<div class="banner stop"><b>Not saved.</b><ul><li>\' +\n        e.map(function (x) { return x; }).join("</li><li>") + "</li></ul></div>";\n      $("errs").scrollIntoView({ block: "center" });\n      return;\n    }\n    var res = L.save(KIND, r);\n    $("errs").innerHTML = \'<div class="banner ok"><b>Saved on this device.</b> \' +\n      (res.persisted ? "" : "Storage is blocked, so it is only in memory — export before closing. ") +\n      "The record goes to the coordination register when there is signal.</div>";\n    showCount();\n  });\n\n  $("csvBtn").addEventListener("click", function () {\n    var list = L.all(KIND);\n    if (!list.length) { alert("Nothing saved on this device yet."); return; }\n    L.download("mhpss_np_phq9_" + L.stamp() + ".csv", L.toCSV(list, COLS), "text/csv");\n  });\n  $("clearBtn").addEventListener("click", function () {\n    if (!L.all(KIND).length) { alert("Nothing saved on this device yet."); return; }\n    if (confirm("Delete every record held in this browser? This cannot be undone.")) {\n      L.clear(KIND); showCount(); $("errs").innerHTML = \'<div class="banner"><b>Cleared.</b></div>\';\n    }\n  });\n\n  refresh();\n})();\n</script>\n<script src="pwa.js"></script>\n<!-- The bilingual engine. On a page that is not yet keyed up it still earns\n     its place: it sets data-lang, which is what makes the Nepali words in\n     the code lists appear in the dropdowns, and it mounts the ENG/NEP\n     toggle and an honest notice saying the prose is still English. -->\n<script src="../hub/assets/mark.js"></script>\n<script src="../hub/assets/icons.js"></script>\n<script src="../hub/assets/i18n-strings.js"></script>\n<script src="../hub/assets/i18n.js"></script>\n</body>\n</html>\n' : safeguard.

----------------------------------------------------------------------
Ran 10 tests in 5.314s

FAILED (failures=4)

base: 4 failing test(s)
AT HEAD: exit=0  OK

(exit 0)
```

---

### Rendered Stage-B proof: protected wording is English on the Nepali page

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n_safety_proof_file_url.py

==========================================================================
PHQ-9 page in Nepali (phq9.html) - clinical wording must stay English
==========================================================================
data-lang=ne  Devanagari chars in body=666  h1=Following one person over time
  OK   phq9.item1                         Little interest or pleasure in doing things
  OK   phq9.item2                         Feeling down, depressed, or hopeless
  OK   phq9.item3                         Trouble falling or staying asleep, or sleeping too much
  OK   phq9.item4                         Feeling tired or having little energy
  OK   phq9.item5                         Poor appetite or overeating
  OK   phq9.item6                         Feeling bad about yourself — or that you are a failure o
  OK   phq9.item7                         Trouble concentrating on things, such as reading the new
  OK   phq9.item8                         Moving or speaking so slowly that other people could hav
  OK   phq9.item9                         Thoughts that you would be better off dead or of hurting
  OK   phq9.scale0                        Not at all
  OK   phq9.scale1                        Several days
  OK   phq9.scale2                        More than half the days
  OK   phq9.scale3                        Nearly every day
  OK   phq9.itemInstruction               Over the last 2 weeks, how often have you been bothered 
  OK   phq9.itemDifficulty                If you checked off any problems, how difficult have thes
  OK   phq9.cutoff.interpretation         Bands are the standard PHQ-9 cut-points (Kroenke, Spitze
  OK   phq9.cutoff.useWarning             Do not use this to screen a shelter. In the Nepali valid
  OK   clinical.phq9ValidatedTextWarning  The Nepali text is missing, and this form is not ready f
  OK   consent.label                      Consent
  OK   consent.phq9                       The person was told what this is for and agreed to answe

item-9 instruction after a positive answer:
  <b>Item 9 is positive. Do not close this form and move on.</b> Stay with the person, ask directly about thoughts of suicide and about means 

==========================================================================
Referral page in Nepali - the safeguarding gate
==========================================================================
data-lang=ne  Devanagari chars in body=2301  h1=व्यक्तिलाई कहाँ पठाइयो, र उनी पुगे कि पुगेनन
  OK   safeguard.checkLabel               Safeguarding check
  OK   safeguard.confirmation             This is not a GBV case, not an unaccompanied or separate
  OK   safeguard.consequence              If you cannot tick this, close the form and use the spec
  OK   safeguard.referralExclusion        Three kinds of case do not belong on this form. Stop and
safeguarding gate visibility: {'checkbox_present': True, 'checkbox_type': 'checkbox', 'checkbox_visible': True, 'confirmation_visible': True, 'consequence_visible': True}

==========================================================================
RESULT
==========================================================================
checks: 30   failures: 0
VERDICT: all safety properties hold

(exit 0)
```

---

### Failing-first for the two new instruments

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n_dictionary_failing_first.py

==========================================================================
BASELINE (head): both new instruments must pass
==========================================================================
sync-check exit=0  IN SYNC
protection-report exit=0  OK: every professionalOnly prefix matches a live key.
unittest DictionaryIntegrity exit=0  OK

==========================================================================
A. gate's dictionary reverted to the pre-keying revision (ff2d4e2)
==========================================================================
staged dictionary sha256=fe66576d4110774c (was 6ef1aa0095c0ad70)
sync-check exit=1
   gate dictionary      fe66576d4110774c  /root/mhpss-nepal-work/form-translation/../hub/assets/i18n-strings.js
   canonical dictionary 6ef1aa0095c0ad70  /root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js
   DRIFT: the gate is reading a different dictionary than the canonical one.
          Every count the gate prints -- including the professionalOnly
          protection count -- describes the file it read, not the change.
          Copy the canonical file over the gate's path before trusting a run.
unittest->FAILED (caught)
restored canonical dictionary sha256=6ef1aa0095c0ad70

==========================================================================
B. a DEAD prefix added to _meta.professionalOnly
==========================================================================
protection-report exit=1
     dead.prefix.sentinel matches  0 live key(s)   <-- DEAD
     9 of 10 prefixes match a live key; 1 dead
   FAIL: prefix(es) matching no live key: dead.prefix.sentinel
unittest->FAILED (caught)
restored both dictionaries: canonical=6ef1aa0095c0ad70 staged=6ef1aa0095c0ad70

==========================================================================
RESTORED -- re-running the baseline
==========================================================================
sync-check=0  protection-report=0  unittest=0  OK
FAILING-FIRST PROVEN: both conditions are caught, both clear at head.

(exit 0)
```

---

### Offline completeness (keyed pages need the dictionary precached)

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/sw-precache-check.py

MHPSS Nepal -- offline completeness
  cache: mhpss-np-field-v39   precached entries: 30
  pages checked: 8

  Complete: every file the precached pages need is precached.

(exit 0)
```

---

### Text setting

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/text-setting-check.py

MHPSS Nepal -- text setting, static gate
  running-text rule declared in assets/design.css   ok
  hyphens:auto declared nowhere                      ok
  no rule bundles th with td on text-align:left     ok
  overflow-wrap uses break-word, not anywhere        ok

  True: running text is set justified with no hyphenation, and nothing
  in the cascade takes it away again.

(exit 0)
```

---

### QR payload consistency

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/qr-check.py

MHPSS Nepal -- QR integrity  [digest mode]
  declared base: https://mhpss-nepal.github.io
  matrices: 6
    master     OK   https://mhpss-nepal.github.io/form/
    5ws        OK   https://mhpss-nepal.github.io/form/5ws-report.html
    contact    OK   https://mhpss-nepal.github.io/form/contact.html
    phq9       OK   https://mhpss-nepal.github.io/form/phq9.html
    referral   OK   https://mhpss-nepal.github.io/form/referral.html
    self       OK   https://mhpss-nepal.github.io/form/selfreport.html

  Consistent: every url+matrix matches the digest written when it
  was generated (and generation decoded it), inside the base.
  card sheet: the card sheet's 6 codes all exist

(exit 0)
```

---

## What this run did NOT do — translation

Translation to a reviewed standard is **not attempted here**. The revised scope
is explicit: the previous run tried to bundle keying + safety classification +
multi-translator translation + back-translation + terminology lock + an
independent native-speaker proofread across three forms under one goal, and two
equivalent failures followed (a provider glitch, then a 150-iteration budget).
The fix is to split, not to retry the whole thing faster.

So the state at this head is: the three pages are **keyed**, the dictionary has
their English, the safety classification is **verified to bind** (9 of 9
prefixes, 32 keys held in English, proven in a real browser on the Nepali page),
and `tools/i18n-check.py` is clean. The Nepali that exists is the previous run's
**machine drafts**, honestly labelled `_meta.source.machine`, with 100 keys still
in English because two drafting lanes disagreed and a disagreement is not decided
by a vote. `_meta.source.human` remains **empty** — no human translator has seen
this text.

**Follow-on ticket (not this one): translate the keyed strings to Nepali**,
starting with `referral.html`, because its safeguarding gate is wording a field
worker actually reads before ticking a box; then `phq9.html`; then
`contact.html`. The multi-translator comparison, back-translation and
independent native-speaker proofread requirements stay fully in force there.

### Safety rules unchanged

- PHQ-9 clinical meaning is untouched: items, scale, cut-off and the item-9
  suicide instruction render in **English on the Nepali page**, asserted by key
  in a real browser (`tools/i18n_safety_proof_file_url.py`, 30 checks, 0
  failures), and at base the same script fails 5 checks including `kept=0` — the
  historic 0-of-204 condition, reproduced on demand.
- No field `id`, `name`, value, validation, storage, queue, sync or service
  worker was changed by keying.
- Production refs unchanged: public `68bf197`, form `9032bb7`, hub `ff2d4e2`.
- No push, PR, merge or deploy. Synthetic data only.

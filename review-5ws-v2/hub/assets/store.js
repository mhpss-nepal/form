/* =====================================================================
   MHPSS Nepal — local store
   ---------------------------------------------------------------------
   The device copy is the first durable copy. `save()` writes it to
   localStorage, then `syncToRegister()` hands a stripped copy to the loaded
   Firebase bridge (`fb.js`) for the `submissions` register; failed delivery
   stays queued for retry. The Hub reads that register.

   Focal-point name, phone and email deliberately never cross the network:
   `fb.js` removes them and the security rules reject them. They remain only
   in this device store and in the CSV/JSON export. Collect an export before
   clearing or replacing a handset, because the remote register cannot restore
   those contact details.
   ===================================================================== */

const KEY = "mhpss-np-4ws-v1";
const SCHEMA_VERSION = "5ws-np-0.7.0";  /* 0.2.0: four age bands · 0.3.0: donors list, partners, palika, iascSub, 16 Sep 2026 · 0.4.0: five age groups, settings, cadre list, "Other" text fields, funding source off the form — EDCD review 17 Sep 2026 · 0.5.0 (17 Sep 2026, afternoon): the instrument is the 5Ws; activity list v3 (layer.item codes, IASC terms in the backend only); one report per session with its attendance — countBasis no longer asked, always CONTACTS; sessionTime in the record id */

/* ---------------------------------------------------------------------
   Deterministic record id.
   The same report submitted twice — a double tap, a page reload, a
   re-sync after signal returns — produces the same id and therefore one
   record, not two. This is the anti-duplication guarantee at the record
   level; it is separate from the analytical de-duplication check, which
   looks for two different organisations reporting one site on one day.
   FNV-1a, 32-bit, rendered base36. Not a security hash; an identity hash.
   ------------------------------------------------------------------- */
function fnv1a(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
  }
  return h >>> 0;
}
function recordId(r) {
  /* `palika` is in the basis so that two palika-level reports (site
     "PALIKA") for two palikas on one day are two records, not one. For a
     report at a named site the palika is implied by the site and changes
     nothing. */
  /* `sessionTime` (0.5.0) is in the basis so that two sessions of one
     activity at one place on one day are two records when the reporter
     gives their start times; left blank, a second report of the same
     activity updates the first, and the form says so. */
  const parts = [r.org, r.orgOther || "", r.site, r.siteOther || "", r.palika || "", r.dateAD, r.activity, r.modality, r.sessionTime || ""].join("|");
  return "R" + fnv1a(parts).toString(36).toUpperCase().padStart(7, "0");
}

/* ---------------------------------------------------------------------
   Storage. Wrapped because localStorage throws in private windows and
   returns empty when site data is cleared. A form that breaks when
   storage is unavailable is a form that loses a day of field reporting.
   ------------------------------------------------------------------- */
function read() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.warn("store: read failed, continuing in memory", e);
    return window.__mem || [];
  }
}
function write(list) {
  window.__mem = list;
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
    return true;
  } catch (e) {
    console.warn("store: write failed, held in memory for this page only", e);
    return false;
  }
}

function all() {
  return read().sort((a, b) => (b.createdAt || "").localeCompare(a.createdAt || ""));
}

/* Today, on this device, as YYYY-MM-DD. Built from local components on
   purpose: toISOString() would give the UTC day and reject early-morning
   reports from Nepal. */
function todayLocal() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate());
}

function save(rec) {
  const list = read();
  const id = recordId(rec);
  const now = new Date().toISOString();
  const idx = list.findIndex((x) => x.id === id);
  const out = { ...rec, id, schemaVersion: SCHEMA_VERSION };

  if (idx >= 0) {
    // Same report again: keep the original creation time, record the revision.
    out.createdAt = list[idx].createdAt;
    out.revisedAt = now;
    out.revision = (list[idx].revision || 0) + 1;
    out.previous = list[idx].previous ? [...list[idx].previous, stripHistory(list[idx])] : [stripHistory(list[idx])];
    list[idx] = out;
    const persistedRev = write(list);
    syncToRegister(out);   /* a corrected report must reach the register too */
    return { record: out, duplicateOf: id, persisted: persistedRev };
  }
  out.createdAt = now;
  out.revision = 0;
  list.push(out);
  const persisted = write(list);

  /* The device copy is written FIRST and unconditionally -- that is the
     record. Only then is a push attempted, and a failed push leaves the
     record queued rather than losing it.

     This was missing until 16 Sep 2026: the activity report is the only
     form that saves through this file rather than l1.js, so wiring the
     bridge into l1.js alone left the 4Ws report -- the form that feeds
     the 5W -- saving locally and never reaching the register. Found by
     submitting the real form and checking the queue. */
  syncToRegister(out);
  return { record: out, duplicateOf: null, persisted: persisted };
}

/* Shape an activity report for the register and hand it to the bridge.
   `kind` and `schema` are what the security rules match on; the bridge
   adds the server timestamp and strips the focal point. Silent when no
   bridge is loaded, so the form still works as a local-only instrument. */
function syncToRegister(rec) {
  if (!window.FB || typeof window.FB.submit !== "function") return null;
  return window.FB.submit(registerBody(rec));
}
/* The copy of a report that goes to the register. The device copy keeps
   everything, including empty fields and the revision history; the
   register copy carries only what was filled. The security rules cap a
   document at 60 keys (size() < 60), and a report with every band and
   every "Other" box present as an empty string would sit within a few
   keys of that cap -- so empties are dropped here, deliberately, and the
   cap stays out of reach. Readers already treat a missing key and an
   empty one the same way. */
function registerBody(rec) {
  const body = { kind: "activity", schema: "mhpss-np-5ws/" + SCHEMA_VERSION };
  for (const [k, v] of Object.entries(rec || {})) {
    if (k === "previous" || k === "archived" || k === "archivedAt" || k === "archiveReason") continue;
    if (v === "" || v === null || v === undefined) continue;
    body[k] = v;
  }
  return body;
}

/* Nothing is deleted. A removed record is archived with a reason, so the
   figure a report carried on a given date can always be reconstructed. */
function archive(id, reason) {
  const list = read();
  const i = list.findIndex((x) => x.id === id);
  if (i < 0) return false;
  list[i] = { ...list[i], archived: true, archivedAt: new Date().toISOString(), archiveReason: reason || "" };
  return write(list);
}

function stripHistory(r) {
  const { previous, ...rest } = r;
  return rest;
}

function active() {
  return all().filter((r) => !r.archived);
}

/* ---------------------------------------------------------------------
   AGE BANDS — the one place they are defined.
   Five groups, agreed with EDCD (NCD and mental health) on 17 September
   2026: 18–59 was too wide and mixed very different needs. The groups are
   0–4 · 5–14 · 15–49 · 50–59 · 60+. Two of them cross the 18-year line
   the national 5W has used, so the on-screen fold is now at 15 and is
   labelled by that boundary, never as "under 18". How the 5W return is
   compiled from these groups is a ruling still to come (R-U1 / R-D1);
   nothing here pretends to know it.
   Records filed under the four bands of 16–17 Sep (0–4, 5–17, 18–59, 60+)
   still fold, at 18, through BANDS_V03. Any page that needs the fold calls
   fold(); nothing else knows the shapes.
   ------------------------------------------------------------------- */
const BANDS = [
  { key: "04",     lo: 0,  hi: 4,    label: "0\u20134",   f: "f04",     m: "m04",     o: "o04",     child: true  },
  { key: "5to9",   lo: 5,  hi: 9,    label: "5\u20139",   f: "f5to9",   m: "m5to9",   o: "o5to9",   child: true  },
  { key: "10to19", lo: 10, hi: 19,   label: "10\u201319", f: "f10to19", m: "m10to19", o: "o10to19", child: false },
  { key: "20to59", lo: 20, hi: 59,   label: "20\u201359", f: "f20to59", m: "m20to59", o: "o20to59", child: false },
  { key: "60",     lo: 60, hi: null, label: "60+",   f: "f60",     m: "m60",     o: "o60",     child: false },
];
const FOLD_BOUNDARY = 20;   /* child: true means younger than this */

const BANDS_V04 = [
  { key: "04",   lo: 0,  hi: 4,    label: "0–4",   f: "f04",   m: "m04",   o: "o04",   child: true  },
  { key: "514",  lo: 5,  hi: 14,   label: "5–14",  f: "f514",  m: "m514",  o: "o514",  child: true  },
  { key: "1549", lo: 15, hi: 49,   label: "15–49", f: "f1549", m: "m1549", o: "o1549", child: false },
  { key: "5059", lo: 50, hi: 59,   label: "50–59", f: "f5059", m: "m5059", o: "o5059", child: false },
  { key: "60",   lo: 60, hi: null, label: "60+",   f: "f60",   m: "m60",   o: "o60",   child: false },
];
const PART_IDS = BANDS.reduce((a, b) => a.concat([b.f, b.m, b.o]), []);

/* Schema 0.3.0 (16–17 Sep 2026): kept so those records still read and
   fold; never offered on the form. */
const BANDS_V03 = [
  { key: "04",   lo: 0,  hi: 4,    label: "0–4",   f: "f04",   m: "m04",   o: "o04",   child: true  },
  { key: "517",  lo: 5,  hi: 17,   label: "5–17",  f: "f517",  m: "m517",  o: "o517",  child: true  },
  { key: "1859", lo: 18, hi: 59,   label: "18–59", f: "f1859", m: "m1859", o: "o1859", child: false },
  { key: "60",   lo: 60, hi: null, label: "60+",   f: "f60",   m: "m60",   o: "o60",   child: false },
];
const PART_IDS_V03 = BANDS_V03.reduce((a, b) => a.concat([b.f, b.m, b.o]), []);

/* "Seen at the session" -- five counts a PFA provider can make by looking,
   without asking anyone anything. They follow the LOOK step of the WHO
   Psychological First Aid guide (2011): people with urgent needs or
   injuries, people in serious distress, and people who need special
   attention -- children without a caregiver, people with a visible
   disability or who need help to move, pregnant women and women with an
   infant. Chosen with the Coordinator on 17 Sep 2026 in place of a long
   vulnerable-group list: what cannot be seen is not asked here.
   NOT additive: a person already counted in a band above can appear in
   one or several of these. They never enter the sum check -- a pregnant
   woman counted once as 15-49 female and once here is one person, not
   two. All optional. */
/* ---------------------------------------------------------------------
   DISABILITY (21 Sep 2026) [CMC-Nepal]
   Asked for by Laxman Nath, CMC-Nepal, so that reporting is inclusive of
   persons with disabilities. Two distinct things, deliberately not merged:

   `disAsked` is the ONE question each agency was asked to add -- the person
   says whether they identify as a person with disability. Optional, and
   blank is kept distinct from "No": a worker who judges that asking is
   unsafe or inappropriate leaves it blank, and the data then says "not
   asked" rather than inventing a refusal or a denial.

   The four counts are what a provider OBSERVED, split by sex and by the 18
   boundary, because a disability figure that is not age-and-sex split cannot
   be reported against the rest of the attendance. They sit INSIDE the total:
   a person in an age band above and here is one person, so they are checked
   against the total and never added to it or to each other.

   The TYPE of disability is deliberately not asked. CMC-Nepal said further
   detail "seems difficult ... for now", and a guessed impairment list would
   be worse than a gap -- the Washington Group Short Set is the instrument
   for that and adopting it is its own decision.
   ------------------------------------------------------------------- */
const DISABILITY = ["disF0_17", "disM0_17", "disF18", "disM18"];
const DISABILITY_ASKED = "disAsked";
const DISABILITY_LABEL = {
  disF0_17: "Female, under 18, person with disability",
  disM0_17: "Male, under 18, person with disability",
  disF18:   "Female, 18 and over, person with disability",
  disM18:   "Male, 18 and over, person with disability",
};

/* The four counts, or null when none was entered -- null matters, because a
   blank block and a block of zeros are different claims. */
function disabilityTotal(r) {
  const vals = DISABILITY.map((k) => num(r[k])).filter((v) => v !== null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) : null;
}

const OF_WHOM = ["ofChildAlone", "ofPreg", "ofPwd", "ofInjured", "ofDistress"];
const OF_WHOM_LABEL = {
  ofChildAlone: "Children without an adult with them",
  ofPreg:       "Pregnant women or women with an infant",
  ofPwd:        "Visible disability or needing help to move",
  ofInjured:    "Visibly injured or unwell",
  ofDistress:   "In acute distress, needing one-to-one attention",
};

/* Which age shape a record carries. "v04" = the five groups (fold at 15);
   "v03" = the four bands of 16–17 Sep (fold at 18); "pair" = the earliest
   records, which carry only fU18/f18. f04 and f60 exist in both banded
   shapes, so the shape is read from the keys only one of them has, and
   from the schema version when neither is filled. */
function ageShape(r) {
  const has = (k) => num(r[k]) !== null;
  const v05only = ["f5to9", "m5to9", "o5to9", "f10to19", "m10to19", "o10to19",
                   "f20to59", "m20to59", "o20to59"];
  const v04only = ["f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059"];
  const v03only = ["f517", "m517", "o517", "f1859", "m1859", "o1859"];
  if (v05only.some(has)) return "v05";
  if (v04only.some(has)) return "v04";
  if (v03only.some(has)) return "v03";
  if (PART_IDS.some(has)) return /-0\.([4-9]|\d\d)\./.test(r.schemaVersion || "") || !(r.schemaVersion) ? "v05" : "v03";
  return "pair";
}

/* Fold a record to two groups, labelled by the boundary that applies to
   its shape: 15 for the five groups, 18 for everything filed before.
   Generic names (fLow …) are the ones to use; fU18 … are kept as aliases
   for pages written against 0.3.0 and mean "below the boundary", not
   "under 18", whenever boundary is 15. */
function fold(r) {
  const shape = ageShape(r);
  if (shape === "pair") {
    const d = {
      fLow: num(r.fU18) || 0, mLow: num(r.mU18) || 0, oLow: num(r.oU18) || 0,
      fHigh: num(r.f18) || 0, mHigh: num(r.m18) || 0, oHigh: num(r.o18) || 0,
      boundary: 18, banded: false, shape,
    };
    return withAliases(d);
  }
  const bands = shape === "v05" ? BANDS : shape === "v04" ? BANDS_V04 : BANDS_V03;
  const g = (k) => num(r[k]) || 0;
  const kids = bands.filter((b) => b.child), adults = bands.filter((b) => !b.child);
  const s = (set, sex) => set.reduce((a, b) => a + g(b[sex]), 0);
  const d = {
    fLow: s(kids, "f"),    mLow: s(kids, "m"),    oLow: s(kids, "o"),
    fHigh: s(adults, "f"), mHigh: s(adults, "m"), oHigh: s(adults, "o"),
    boundary: shape === "v05" ? FOLD_BOUNDARY : 18, banded: true, shape,
  };
  return withAliases(d);
}
function withAliases(d) {
  d.fU18 = d.fLow; d.mU18 = d.mLow; d.oU18 = d.oLow;
  d.f18 = d.fHigh; d.m18 = d.mHigh; d.o18 = d.oHigh;
  return d;
}

/* Total disaggregated people in a record, either shape. */
function disaggTotal(r) {
  const d = fold(r);
  return d.fU18 + d.mU18 + d.oU18 + d.f18 + d.m18 + d.o18;
}

/* ---------------------------------------------------------------------
   Validation. Returns a list of problems; an empty list means valid.
   The disaggregation rule matters: in the current workbook several rows
   have sex and age breakdowns typed into the provider column because the
   form has nowhere to put them. Here they have somewhere, and the parts
   are checked against the total rather than trusted.
   ------------------------------------------------------------------- */
function validate(r) {
  const p = [];
  const need = { org: "Reporting organisation", site: "Site", dateAD: "Date", activity: "Activity", modality: "Modality", focalName: "Focal point name", focalPhone: "Focal point phone" };
  for (const [k, label] of Object.entries(need)) if (!r[k]) p.push(`${label} is required`);
  if (r.org === "OTHER" && !r.orgOther) p.push("Name the organisation");
  if (r.site === "OTHER" && !r.siteOther) p.push("Name the site");
  /* "Other (free text)" on every list -- EDCD, 17 Sep 2026. Each one is a
     name or a description, never a person: digits in bulk or an @ are
     refused so a phone number or email cannot ride in on a text field. */
  const OTHER_TEXT = { cadre: ["cadreOther", "Say which cadre"], modality: ["modalityOther", "Say where the activity took place"],
                       district: ["districtOther", "Name the district"] };
  for (const [k, [tk, msg]] of Object.entries(OTHER_TEXT)) {
    if ((r[k] === "OTH" || r[k] === "OTHER") && !(r[tk] || "").trim()) p.push(msg);
  }
  /* Activity list v3 (17 Sep 2026): "Other (describe)" is x.9 within a
     layer or 9 outside every layer; each needs the description. A code the
     current list does not offer -- a retired one, or a typo -- is refused
     at entry; retired codes exist only so old records resolve. */
  if (r.activity) {
    const a = (window.CODES && window.CODES.activityByCode) ? window.CODES.activityByCode[r.activity] : null;
    if (!a || a.retired) p.push("Choose an activity from the current list");
    else if (a.other && !(r.activityOther || "").trim()) p.push("Describe the activity");
  }
  if (r.sessionTime && !/^([01]\d|2[0-3]):[0-5]\d$/.test(r.sessionTime)) p.push("Start time must be hh:mm");
  if ((r.targetGroups || []).includes("TG-OTH") && !(r.targetGroupOther || "").trim()) p.push("Say which other group");
  for (const tk of ["cadreOther", "modalityOther", "districtOther", "activityOther", "targetGroupOther", "orgOther", "siteOther"]) {
    if (r[tk] && /\d{7,}|@/.test(r[tk])) p.push("Free-text fields are names of things, not of people — no phone numbers or emails");
  }
  /* A report that covers a palika and no site is coded at palika level:
     it needs the palika, and it is never counted as a site. */
  if (r.site === "PALIKA" && !r.palika) p.push("Choose the palika the report covers");
  if (r.palika && !/^NP\d{7}$/.test(r.palika)) p.push("Palika must be a COD-AB P-code");
  if (r.partners && r.partners.some((x) => /\d{7,}|@/.test(x))) p.push("Joint-activity partners are organisation names — no phone numbers or emails");
  /* The DEVICE's date, not UTC. Nepal is UTC+05:45, so from midnight until
     05:45 local the UTC date is still yesterday -- a worker filing an early
     report with today's date was told it was in the future and could not
     submit at all. Found by test, 16 Sep 2026. */
  if (r.dateAD && r.dateAD > todayLocal()) p.push("Date is in the future");
  if (!(r.targetGroups || []).length) p.push("Select at least one target group");

  const t = num(r.reachedTotal);
  if (t === null) p.push("Attendance is required (enter 0 if nobody came)");
  /* Since 17 Sep 2026 (afternoon) the form does not ask what the figure
     counts: a report is one session, and its figure is the attendance --
     everyone who took part, once for that session. Across sessions that is
     a count of attendances, i.e. service contacts, so the record carries
     countBasis CONTACTS and the dashboard says "attendances". Distinct
     people come from the optional attendance list, not from this form.
     Records filed earlier keep the basis they were filed with. */
  if (!r.countBasis) p.push("Count basis missing (the form sets it)");
  const dp = num(r.distinctPeople);
  if (dp !== null && r.countBasis !== "CONTACTS") p.push("Distinct people applies only when the total is a contact count");
  if (dp !== null && t !== null && dp > t) p.push(`Distinct people (${dp}) cannot exceed the attendance of ${t}`);
  const sum = disaggTotal(r);
  if (t !== null && sum > t) p.push(`Disaggregated figures add to ${sum}, more than the total of ${t}`);
  if (t !== null && sum > 0 && sum < t) p.push(`Disaggregated figures add to ${sum} of ${t} — ${t - sum} unaccounted. Leave all blank, or account for all.`);
  /* The "of whom" counts sit INSIDE the total, so each one can be at most
     the total -- but they are not added to it and not added to each other,
     because one person can be in both. */
  for (const k of OF_WHOM) {
    const v = num(r[k]);
    if (v !== null && t !== null && v > t) p.push(`${OF_WHOM_LABEL[k]} (${v}) is more than the total of ${t}`);
  }
  /* The disability counts sit inside the total, like the "of whom" block:
     each at most the total, and never summed with each other or with it. */
  for (const k of DISABILITY) {
    const v = num(r[k]);
    if (v !== null && t !== null && v > t) p.push(`${DISABILITY_LABEL[k]} (${v}) is more than the total of ${t}`);
  }
  return p;
}
function num(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

/* ---------------------------------------------------------------------
   Export. CSV is one row per record, flat, with no subtotal rows.
   The largest defect in the current workbook comes from subtotals living
   in the same column as the data, so a plain sum counts a large share of
   the reach twice. Totals belong in the analysis, never in the dataset.
   ------------------------------------------------------------------- */
const CSV_COLUMNS = [
  "id", "createdAt", "revision", "dateAD", "dateBS", "district", "palika", "ward", "site", "siteOther", "siteSource",
  "org", "orgOther", "donors", "partners", "focalName", "focalPhone", "focalEmail", "cadre", "cadreOther",
  "sessionTime",
  /* the two readings of one activity code (list v3, 17 Sep 2026): the code
     and the plain label the form showed, then the backend reading -- IASC
     layer and 4Ws subcode -- computed at export from codes.js, never typed */
  "activity", "activityLabel", "activityLayer", "iascSub", "iascReading", "activityOther", "modality", "modalityOther", "status", "targetGroups", "targetGroupOther", "districtOther", "description",
  "reachedTotal", "countBasis", "distinctPeople",
  /* the five groups as collected (0.4.0) and the four bands of 0.3.0, so a
     record of either vintage exports in full */
  /* 0.6.0: the Ministry's groups. The 0.4.0 middle ids stay listed so a
     record filed under them still exports in full. */
  "f04", "m04", "o04", "f5to9", "m5to9", "o5to9", "f10to19", "m10to19", "o10to19",
  "f20to59", "m20to59", "o20to59", "f60", "m60", "o60",
  "f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059",
  "f517", "m517", "o517", "f1859", "m1859", "o1859",
  /* folded to two at export, never stored; foldBoundary says whether the
     split is at 15 (five groups) or 18 (earlier records) */
  "fLow", "mLow", "oLow", "fHigh", "mHigh", "oHigh", "foldBoundary",
  /* seen at the session -- counted inside the figures above, never added to them */
  "ofChildAlone", "ofPreg", "ofPwd", "ofInjured", "ofDistress",
  /* 0.7.0: disability, asked for by CMC-Nepal. The yes/no question comes
     first so it reads as the question it is; the four counts are the
     sex x 18-boundary split. Blank "not asked" is kept distinct from "No". */
  "disAsked", "disF0_17", "disM0_17", "disF18", "disM18",
  "schemaVersion",
];

/* The backend reading of the activity on a record, computed from codes.js
   at export and at read: the plain label the form showed, the IASC layer,
   and the 4Ws subcode -- the one on the record (set at entry for a direct
   match, or at coordination) or the candidates when it is not set yet. A
   retired code is read through its crosswalk. Nothing here is typed. */
function activityReadings(r) {
  const C = window.CODES;
  if (!C || !C.activityResolve) return {};
  const res = C.activityResolve(r.activity);
  const code = res.placed || r.activity;
  const a = C.activityByCode[code];
  const g = a && !a.retired ? C.activityGroupByCode[a.group] : null;
  return {
    activityLabel: res.legacy ? res.name + " (previous list" + (res.placed ? ", read as " + res.placed : ", not yet placed") + ")" : (a ? a.name : r.activity || ""),
    activityLayer: g ? g.code + " " + g.name : (res.legacy && !res.placed ? "not yet placed" : ""),
    iascReading: res.placed ? C.activityIasc(res.placed) : "",
  };
}

function toCSV(rows) {
  const esc = (v) => {
    const s = Array.isArray(v) ? v.join(";") : v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  const head = CSV_COLUMNS.join(",");
  /* The folded columns are computed at export, not stored on the record:
     one figure in two places is one figure that can disagree with itself. */
  const body = rows.map((r) => {
    const d = fold(r);
    const row = { ...r, ...d, foldBoundary: d.boundary, donors: donorsOf(r), ...activityReadings(r) };
    return CSV_COLUMNS.map((c) => esc(row[c])).join(",");
  }).join("\n");
  return "﻿" + head + "\n" + body + "\n"; // BOM so Excel reads UTF-8
}

function download(filename, text, mime) {
  const blob = new Blob([text], { type: (mime || "text/plain") + ";charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function stamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`;
}

function clearAll() {
  try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  window.__mem = [];
}

/* The funding tags of a record, whatever its vintage. 0.3.0 records carry
   `donors` (a list -- one report in the current workbook is funded by two
   donors at once); earlier records carry a single `donor`. Read through
   this so no consumer has to know which. */
function donorsOf(r) {
  if (!r) return [];
  if (Array.isArray(r.donors)) return r.donors.filter(Boolean);
  if (r.donor && r.donor !== "Not specified") return [r.donor];
  return [];
}

/* Global for the same reason as codes.js — see the note there. */
window.STORE = {
  SCHEMA_VERSION, CSV_COLUMNS, BANDS, BANDS_V04, BANDS_V03, PART_IDS, PART_IDS_V03, FOLD_BOUNDARY, OF_WHOM, OF_WHOM_LABEL, DISABILITY, DISABILITY_ASKED, DISABILITY_LABEL, disabilityTotal, fold, ageShape, disaggTotal, donorsOf, todayLocal, registerBody, activityReadings,
  recordId, all, active, save, archive,
  validate, toCSV, download, stamp, clearAll
};

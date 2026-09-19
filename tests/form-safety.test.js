"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const SAFETY_HUB = path.join(ROOT, "..", "hub-safety");
const HUB = path.resolve(process.env.MHPSS_HUB_ROOT ||
  (fs.existsSync(SAFETY_HUB) ? SAFETY_HUB : path.join(ROOT, "..", "hub")));
const FORM_PAGES = ["contact.html", "referral.html", "phq9.html", "selfreport.html"];

function page(name) {
  return fs.readFileSync(path.join(ROOT, name), "utf8");
}

function formScript(name) {
  const scripts = Array.from(page(name).matchAll(/<script>([\s\S]*?)<\/script>/g), (match) => match[1]);
  const source = scripts.find((script) => script.includes("L.save(KIND"));
  assert.ok(source, `${name}: real L.save call site not found`);
  return source;
}

function submitCallSite(name, saveResult) {
  const source = name === "5ws-report.html" ? page(name) : formScript(name);
  const start = source.indexOf('$("f").addEventListener("submit", function');
  assert.notEqual(start, -1, `${name}: submit call site not found`);
  const endMarker = name === "5ws-report.html"
    ? "\n\n  function softReset()"
    : '\n\n  $("csvBtn").addEventListener';
  const end = source.indexOf(endMarker, start);
  assert.notEqual(end, -1, `${name}: submit call site end not found`);

  const elements = new Map();
  const element = (id) => {
    if (!elements.has(id)) {
      const handlers = {};
      elements.set(id, {
        id, checked: true, hidden: false, innerHTML: "", textContent: "", value: "sensitive",
        addEventListener(type, handler) { handlers[type] = handler; this[`_${type}`] = handler; },
        scrollIntoView() {},
      });
    }
    return elements.get(id);
  };
  let resetCalls = 0;
  let renderCalls = 0;
  let successCalls = 0;
  const toasts = [];
  const selectedInputs = [{ checked: true, value: "sensitive" }];
  const document = {
    querySelector() { return { checked: true, value: "sensitive" }; },
    querySelectorAll() { return selectedInputs; },
  };
  ["ini", "byear", "say", "ageband"].forEach(element);
  const context = vm.createContext({
    $: element,
    KIND: name === "selfreport.html" ? "selfreport" : name.replace(".html", ""),
    L: {
      save() { return saveResult; },
      all() { return [{ marker: "recovery" }]; },
    },
    S: {
      save() { return saveResult; },
      validate() { return []; },
    },
    collect() { return { marker: "sensitive" }; },
    problems() { return []; },
    record() {
      return { marker: "sensitive", site: "SITE", coping: "OK", knows_where: "Y" };
    },
    saveReporter() {},
    showCount() { successCalls += 1; },
    refreshCode() { successCalls += 1; },
    softReset() { resetCalls += 1; },
    render() { renderCalls += 1; },
    toast(message, warning) { toasts.push({ message, warning }); },
    tx(key) { return key; },
    document,
    Array,
  });
  vm.runInContext(source.slice(start, end), context, { filename: `${name}#submit-call-site` });
  const handler = element("f")._submit;
  assert.equal(typeof handler, "function", `${name}: submit handler was not registered`);
  handler({ preventDefault() {} });
  return { elements, resetCalls, renderCalls, successCalls, toasts, selectedInputs };
}

function failedPersistenceBranch(source, name) {
  const start = source.indexOf("if (!res.sourcePersisted)");
  assert.notEqual(start, -1, `${name}: sourcePersisted:false branch not found`);
  const end = source.indexOf("\n    }", start);
  assert.notEqual(end, -1, `${name}: persisted:false branch end not found`);
  return source.slice(start, end + 6);
}

function exportColumns(name) {
  const match = formScript(name).match(/var COLS\s*=\s*Object\.keys\(record\(\)\)\.concat\(\[([^\]]+)\]\)/);
  assert.ok(match, `${name}: CSV columns not found`);
  return ["schema", "kind"].concat(Array.from(match[1].matchAll(/"([^"]+)"/g), (item) => item[1]));
}

function sharedHubContext() {
  const data = new Map();
  const localStorage = {
    getItem(key) { return data.has(key) ? data.get(key) : null; },
    setItem(key, value) { data.set(key, String(value)); },
    removeItem(key) { data.delete(key); },
  };
  const element = () => ({
    appendChild() {}, insertBefore() {}, removeChild() {}, setAttribute() {},
    addEventListener() {}, className: "", firstElementChild: null, innerHTML: "",
  });
  const document = {
    body: element(), head: element(), readyState: "complete",
    addEventListener() {}, dispatchEvent() {}, createElement: element,
    querySelectorAll() { return []; }, getElementById() { return null; },
  };
  let random = 0;
  const window = {
    FB_CONFIG: {}, document, localStorage,
    addEventListener() {}, alert() {},
    crypto: { getRandomValues(bytes) {
      for (let i = 0; i < bytes.length; i += 1) bytes[i] = (random = (random + 1) & 255);
      return bytes;
    } },
    location: { href: "https://example.test/form/contact.html", origin: "https://example.test", pathname: "/form/contact.html", search: "" },
  };
  const context = vm.createContext({
    Blob: class Blob {}, URL: { createObjectURL() { return "blob:test"; }, revokeObjectURL() {} },
    console, document, localStorage, navigator: { onLine: false, geolocation: null },
    setTimeout, clearTimeout, window,
  });
  window.window = window;
  window.navigator = context.navigator;
  window.setTimeout = setTimeout;
  for (const file of ["assets/fb.js", "assets/l1.js"]) {
    const filename = path.join(HUB, file);
    vm.runInContext(fs.readFileSync(filename, "utf8"), context, { filename });
  }
  return context.window;
}

function precacheFingerprint(source) {
  const match = source.match(/const\s+PRECACHE\s*=\s*\[([\s\S]*?)\]\s*;/);
  assert.ok(match, "service worker precache list not found");
  const entries = Array.from(match[1].matchAll(/"([^"]+)"/g), (item) => item[1]);
  const hash = crypto.createHash("sha256");
  for (const entry of entries) {
    const file = entry === "./" ? path.join(ROOT, "index.html")
      : entry.startsWith("../hub/") ? path.join(HUB, entry.slice("../hub/".length))
        : path.join(ROOT, entry);
    hash.update(entry);
    hash.update(fs.readFileSync(file));
  }
  return hash.digest("hex");
}

for (const name of FORM_PAGES) {
  test(`${name} CSV columns preserve save-generated immutable event ids`, () => {
    const source = formScript(name);
    assert.match(
      source,
      /var COLS\s*=\s*Object\.keys\(record\(\)\)\.concat\(\["_rid",\s*"_saved"\]\)/,
    );
  });

  test(`${name} shared Hub save/export round trip keeps the generated event id`, () => {
    const hub = sharedHubContext();
    const kind = name === "selfreport.html" ? "selfreport" : name.replace(".html", "");
    const recordKind = name === "contact.html" ? "service_contact"
      : name === "selfreport.html" ? "self_report" : kind;
    const record = { schema: `test/${kind}`, kind: recordKind };
    const result = hub.L1.save(kind, record);
    const csv = hub.L1.toCSV(hub.L1.all(kind), exportColumns(name));
    const [header, row] = csv.trim().split(/\r?\n/);
    const columns = header.split(",");
    const cells = row.split(",");

    assert.equal(result.persisted, true);
    assert.match(record._rid, new RegExp(`^${recordKind}_evt_[0-9a-f]{32}$`));
    assert.equal(cells[columns.indexOf("_rid")], record._rid);
  });
}

for (const name of ["contact.html", "referral.html", "phq9.html"]) {
  test(`${name} tells volatile-memory records to export and does not promise delivery`, () => {
    const branch = failedPersistenceBranch(formScript(name), name);
    assert.match(branch, /Not saved on this device/i);
    assert.match(branch, /only in this open page/i);
    assert.match(branch, /Export (?:CSV|it) now/i);
    assert.match(branch, /not queued/i);
    assert.match(branch, /will not be (?:sent|delivered) automatically/i);
    assert.match(branch, /return\s*;/);
    assert.doesNotMatch(branch, /<b>Saved on this device/i);
    assert.doesNotMatch(branch, /when there is signal/i);
  });
}

test("self-report keeps the answers visible and exportable when persistence fails", () => {
  const source = formScript("selfreport.html");
  const branch = failedPersistenceBranch(source, "selfreport.html");
  const failure = source.indexOf("if (!res.sourcePersisted)");
  const success = source.indexOf("Your answer was saved and queued on this device", failure);
  const reset = source.indexOf("input[type=radio]", failure);

  assert.match(branch, /Not saved on this device/i);
  assert.match(branch, /only in this open page/i);
  assert.match(branch, /Export CSV now/i);
  assert.match(branch, /not queued/i);
  assert.match(branch, /will not be delivered automatically/i);
  assert.match(branch, /return\s*;/);
  assert.doesNotMatch(branch, /Thank you/i);
  assert.notEqual(success, -1, "selfreport.html: successful persistence message not found");
  assert.notEqual(reset, -1, "selfreport.html: successful-save reset not found");
  assert.ok(reset > success, "reset must be after the successful persistence message");
});

test("contact clears identifying inputs only after persistence succeeds", () => {
  const source = formScript("contact.html");
  const failure = source.indexOf("if (!res.sourcePersisted)");
  const branch = failedPersistenceBranch(source, "contact.html");
  const clearInputs = source.indexOf('["ini", "byear", "mun"].forEach', failure);
  assert.notEqual(clearInputs, -1);
  assert.ok(clearInputs >= failure + branch.length,
    "identifying inputs must remain available in the persistence-failure branch");
});

for (const name of FORM_PAGES) {
  test(`${name} executed call site fails closed when source persisted but queue did not`, () => {
    const outcome = submitCallSite(name, {
      persisted: true,
      sourcePersisted: true,
      queuePersisted: false,
      acknowledged: false,
      deliveryState: "not-queued",
      recoveryRequired: true,
    });

    assert.match(outcome.elements.get("errs").innerHTML, /not queued/i);
    assert.match(outcome.elements.get("errs").innerHTML, /export/i);
    assert.doesNotMatch(outcome.elements.get("errs").innerHTML, /goes to|will be (?:sent|delivered)/i);
    assert.equal(outcome.successCalls, 0);
    if (name === "contact.html") {
      assert.equal(outcome.elements.get("ini").value, "sensitive");
      assert.equal(outcome.elements.get("byear").value, "sensitive");
    }
    if (name === "selfreport.html") {
      assert.equal(outcome.elements.get("say").value, "sensitive");
      assert.equal(outcome.selectedInputs[0].checked, true);
    }
  });
}

for (const name of FORM_PAGES) {
  test(`${name} successful call site distinguishes queueing from acknowledgement`, () => {
    const outcome = submitCallSite(name, {
      persisted: true,
      sourcePersisted: true,
      queuePersisted: true,
      acknowledged: false,
      deliveryState: "queued",
      recoveryRequired: false,
    });

    assert.match(outcome.elements.get("errs").innerHTML, /queued/i);
    assert.match(outcome.elements.get("errs").innerHTML, /acknowledg/i);
    assert.doesNotMatch(outcome.elements.get("errs").innerHTML, /goes to|will be (?:sent|delivered)|when there is signal/i);
  });
}

test("5Ws successful call site distinguishes queueing from acknowledgement", () => {
  const outcome = submitCallSite("5ws-report.html", {
    persisted: true,
    sourcePersisted: true,
    queuePersisted: true,
    acknowledged: false,
    deliveryState: "queued",
    recoveryRequired: false,
    record: { id: "R1" },
  });

  assert.equal(outcome.resetCalls, 1);
  assert.equal(outcome.renderCalls, 1);
  assert.match(outcome.toasts[0].message, /queued/i);
  assert.match(outcome.toasts[0].message, /acknowledg/i);
  assert.doesNotMatch(outcome.toasts[0].message, /goes to|will be (?:sent|delivered)|when there is signal/i);
});

test("5Ws executed call site returns before reset or durable-save render on source failure", () => {
  const outcome = submitCallSite("5ws-report.html", {
    persisted: false,
    sourcePersisted: false,
    queuePersisted: false,
    acknowledged: false,
    deliveryState: "volatile",
    recoveryRequired: true,
    record: { id: "R1" },
  });

  assert.equal(outcome.resetCalls, 0);
  assert.equal(outcome.renderCalls, 0);
  assert.equal(outcome.toasts.length, 1);
  assert.match(outcome.toasts[0].message, /export/i);
  assert.doesNotMatch(outcome.toasts[0].message, /Report saved|Report updated/i);
});

test("5Ws executed call site returns before reset or durable-save render on queue failure", () => {
  const outcome = submitCallSite("5ws-report.html", {
    persisted: true,
    sourcePersisted: true,
    queuePersisted: false,
    acknowledged: false,
    deliveryState: "not-queued",
    recoveryRequired: true,
    record: { id: "R1" },
  });

  assert.equal(outcome.resetCalls, 0);
  assert.equal(outcome.renderCalls, 0);
  assert.equal(outcome.toasts.length, 1);
  assert.match(outcome.toasts[0].message, /not queued/i);
  assert.match(outcome.toasts[0].message, /export/i);
  assert.doesNotMatch(outcome.toasts[0].message, /Report saved|Report updated/i);
});

test("an already-installed cache upgrades to the form safety release", async () => {
  const source = fs.readFileSync(path.join(ROOT, "sw.js"), "utf8");
  assert.match(source, /const CACHE = "mhpss-np-field-v40";/);
  assert.equal(
    fs.readFileSync(path.join(ROOT, "tools", "precache.sha"), "utf8").trim(),
    precacheFingerprint(source),
    "precache.sha must fingerprint this form release and its paired Hub assets",
  );

  const listeners = {};
  const stores = new Map([["mhpss-np-field-v39", new Map([["contact.html", "old cached form"]])]]);
  const deleted = [];
  const precacheModes = new Map();
  let claimed = false;
  let skipped = false;
  const cacheKey = (request) => {
    const raw = typeof request === "string" ? request : request.url;
    if (/^https?:/.test(raw)) return new URL(raw).pathname.replace(/^\/form\//, "");
    return raw.replace(/^\.\//, "");
  };
  class Request {
    constructor(url, options) { this.url = url; this.cache = options && options.cache; }
  }
  const caches = {
    async open(name) {
      if (!stores.has(name)) stores.set(name, new Map());
      return {
        async add(request) {
          const key = cacheKey(request);
          const local = key === "" ? path.join(ROOT, "index.html")
            : key.startsWith("../hub/assets/") ? path.join(HUB, key.slice("../hub/".length))
              : path.join(ROOT, key);
          precacheModes.set(key, request.cache);
          stores.get(name).set(key, fs.readFileSync(local, "utf8"));
        },
        async match(request) {
          const key = cacheKey(request);
          return stores.get(name).has(key) ? new Response(stores.get(name).get(key)) : undefined;
        },
        async put(request, response) { stores.get(name).set(cacheKey(request), await response.text()); },
      };
    },
    async keys() { return Array.from(stores.keys()); },
    async delete(name) { deleted.push(name); return stores.delete(name); },
    async match(request) {
      const key = cacheKey(request);
      for (const store of stores.values()) {
        if (store.has(key)) return new Response(store.get(key));
      }
      return undefined;
    },
  };
  const self = {
    addEventListener(type, listener) { listeners[type] = listener; },
    skipWaiting() { skipped = true; },
    clients: { async claim() { claimed = true; } },
    location: { origin: "https://example.test" },
  };
  vm.runInContext(source, vm.createContext({ caches, console, fetch: async () => {}, Request, Response, self, URL }), {
    filename: path.join(ROOT, "sw.js"),
  });

  let installWork;
  listeners.install({ waitUntil(work) { installWork = work; } });
  await installWork;
  assert.equal(skipped, true);
  assert.equal(stores.has("mhpss-np-field-v40"), true);
  const refreshed = stores.get("mhpss-np-field-v40");
  for (const name of FORM_PAGES) {
    assert.equal(refreshed.has(name), true, name);
    assert.equal(precacheModes.get(name), "reload", name);
  }
  assert.match(refreshed.get("../hub/assets/l1.js"), /ensureEventId/);
  assert.match(refreshed.get("../hub/assets/l1.js"), /persisted:\s*false/);
  assert.match(refreshed.get("../hub/assets/fb.js"), /restoreQueue/);

  let activateWork;
  listeners.activate({ waitUntil(work) { activateWork = work; } });
  await activateWork;
  assert.equal(claimed, true);
  assert.deepEqual(deleted, ["mhpss-np-field-v39"]);
  assert.equal(stores.has("mhpss-np-field-v39"), false);

  let offlineWork;
  const request = {
    method: "GET",
    mode: "navigate",
    url: "https://example.test/form/contact.html",
    headers: { get() { return "text/html"; } },
  };
  listeners.fetch({ request, respondWith(work) { offlineWork = work; } });
  const response = await offlineWork;
  const html = await response.text();
  assert.match(html, /Not saved on this device/);
  assert.match(html, /_rid/);
  assert.doesNotMatch(html, /old cached form/);
});

test("a failed v40 precache keeps installed v39 active and removes partial v40", async () => {
  const source = fs.readFileSync(path.join(ROOT, "sw.js"), "utf8");
  const listeners = {};
  const stores = new Map([["mhpss-np-field-v39", new Map([["contact.html", "working v39 form"]])]]);
  const deleted = [];
  let skipped = false;
  let claimed = false;
  const cacheKey = (request) => {
    const raw = typeof request === "string" ? request : request.url;
    return raw.replace(/^\.\//, "");
  };
  class Request {
    constructor(url, options) { this.url = url; this.cache = options && options.cache; }
  }
  const caches = {
    async open(name) {
      if (!stores.has(name)) stores.set(name, new Map());
      return {
        async add(request) {
          const key = cacheKey(request);
          if (key === "contact.html") throw new Error("required response failed");
          stores.get(name).set(key, `v40:${key}`);
        },
        async match(request) {
          const key = cacheKey(request);
          return stores.get(name).has(key) ? new Response(stores.get(name).get(key)) : undefined;
        },
        async put(request, response) { stores.get(name).set(cacheKey(request), await response.text()); },
      };
    },
    async keys() { return Array.from(stores.keys()); },
    async delete(name) { deleted.push(name); return stores.delete(name); },
    async match(request) {
      const key = cacheKey(request);
      for (const store of stores.values()) {
        if (store.has(key)) return new Response(store.get(key));
      }
      return undefined;
    },
  };
  const self = {
    addEventListener(type, listener) { listeners[type] = listener; },
    skipWaiting() { skipped = true; },
    clients: { async claim() { claimed = true; } },
    location: { origin: "https://example.test" },
  };
  vm.runInContext(source, vm.createContext({ caches, console, fetch: async () => {}, Request, Response, self, URL }), {
    filename: path.join(ROOT, "sw.js"),
  });

  let installWork;
  listeners.install({ waitUntil(work) { installWork = work; } });
  await assert.rejects(installWork, /required response failed|precache/i);

  assert.equal(skipped, false, "failed worker must not call skipWaiting");
  assert.equal(claimed, false, "failed worker must not claim installed clients");
  assert.equal(stores.has("mhpss-np-field-v39"), true, "active v39 cache must remain");
  assert.equal(stores.get("mhpss-np-field-v39").get("contact.html"), "working v39 form");
  assert.equal(stores.has("mhpss-np-field-v40"), false, "partial v40 cache must be removed");
  assert.deepEqual(deleted, ["mhpss-np-field-v40"]);
});

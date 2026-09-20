/* ============================================================================
   MHPSS Nepal — 5Ws B2 "Institutional App" preview core.
   ----------------------------------------------------------------------------
   PREVIEW ONLY. A presentation layer over the frozen 5Ws page.

   The rule that keeps the data contract safe
   ------------------------------------------
   This script never re-creates, renames, moves out of the form, or reparents a
   form control. Each existing `#s1…#s5` card BECOMES an app screen in place, so
   every field keeps its own id, name, `<label for>`, help text, `inputmode`,
   value list and event listeners, and stays a descendant of `<form id="f">`.

   The script then *adds* enhancement layers whose only job is to write into
   those same real controls through real `input`/`change` events, so the
   baseline page's own listeners, validation and save path run unchanged.

   Never touched: STORE, FB, the queue, retries, acknowledgement, localStorage,
   the service worker, the manifest, the submit handler, analytics, auth, or any
   field semantic.

   Exposes window.IUPreview for automated tests.
   ========================================================================= */
(function () {
  "use strict";

  var YEAR_MIN = 1940;

  /* ---------------------------------------------------------------- helpers */
  function $(id) { return document.getElementById(id); }
  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return [].slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function txt(s) { return String(s == null ? "" : s).replace(/\s+/g, " ").trim(); }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  function nowDate() { return new Date(); }
  function todayISO() {
    var t = nowDate();
    return t.getFullYear() + "-" + pad2(t.getMonth() + 1) + "-" + pad2(t.getDate());
  }
  /* Drive the real control the way a person would, so the page's own
     listeners observe it and do the work. */
  function fire(node, type) { node.dispatchEvent(new Event(type, { bubbles: true })); }
  function setValue(node, value, type) {
    if (!node) return false;
    node.value = value;
    fire(node, type || "input");
    fire(node, "change");
    return true;
  }
  function labelFor(control) {
    if (!control) return "Field";
    if (control.labels && control.labels[0]) return txt(control.labels[0].textContent);
    var wrap = control.closest(".f");
    var lab = wrap && wrap.querySelector("label");
    return lab ? txt(lab.textContent) : (control.id || "Field");
  }

  /* ============================== CHIPS ================================== */
  /* A short, flat <select> is presented as a chip group. The select keeps its
     id/name/value and stays the single source of truth; the chips carry the
     interaction. Arrow keys, Home and End move between chips. */
  function chipCandidate(sel) {
    if (!sel || sel.tagName !== "SELECT") return false;
    var opts = [].slice.call(sel.options);
    if (opts.length < 3 || opts.length > 8) return false;   /* 2 options read better as a real pair of choices, but keep threshold at 3 to avoid changing status/first-upper lists */
    if (sel.querySelector("optgroup")) return false;
    return true;
  }
  function enhanceSelect(sel, onSync) {
    var group = el("div", "iu-chips");
    group.setAttribute("role", "radiogroup");
    group.setAttribute("aria-label", labelFor(sel));
    var buttons = [];

    function build() {
      group.innerHTML = "";
      buttons = [];
      [].slice.call(sel.options).forEach(function (opt) {
        if (opt.value === "") return;             /* the "Select…" placeholder */
        var b = el("button", "iu-chip");
        b.type = "button";
        b.setAttribute("role", "radio");
        b.dataset.v = opt.value;
        b.textContent = txt(opt.textContent);
        b.addEventListener("click", function () { pick(b); });
        b.addEventListener("keydown", onKey);
        group.appendChild(b);
        buttons.push(b);
      });
      sync();
    }
    function pick(b) {
      setValue(sel, b.dataset.v, "change");
      sync();
      b.focus();
      if (onSync) onSync();
    }
    function onKey(e) {
      var i = buttons.indexOf(e.target);
      if (i < 0) return;
      var n = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") n = (i + 1) % buttons.length;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") n = (i - 1 + buttons.length) % buttons.length;
      else if (e.key === "Home") n = 0;
      else if (e.key === "End") n = buttons.length - 1;
      else if (e.key === " " || e.key === "Enter") { e.preventDefault(); pick(e.target); return; }
      if (n == null) return;
      e.preventDefault();
      buttons[n].focus();
    }
    function sync() {
      buttons.forEach(function (b) {
        var on = b.dataset.v === sel.value;
        b.classList.toggle("on", on);
        b.setAttribute("aria-checked", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
      });
      if (!sel.value && buttons.length) buttons[0].tabIndex = 0;
      /* Keep the real select out of the tab order and out of the a11y tree so
         a screen reader hears one control, not two. */
      sel.tabIndex = -1;
      sel.setAttribute("aria-hidden", "true");
    }

    build();
    sel.classList.add("iu-sr-select");
    sel.parentNode.insertBefore(group, sel);
    var mo = new MutationObserver(function () { build(); if (onSync) onSync(); });
    mo.observe(sel, { childList: true });
    return { root: group, sync: sync, rebuild: build };
  }

  /* ============================== PICKER ================================= */
  /* A long, flat list (organisations, cadres, districts, sites) is presented
     as a searchable picker: one tap opens a filterable list, so a 69-item site
     list never becomes a long scroll. The real <select> keeps its id, name,
     value list and placeholder option — it is the single source of truth and
     the only thing submission reads. */
  function pickerCandidate(sel) {
    if (!sel || sel.tagName !== "SELECT") return false;
    var opts = [].slice.call(sel.options);
    if (opts.length <= 8) return false;                 /* short lists become chips */
    if (sel.querySelector("optgroup")) return false;    /* grouped lists keep their headings */
    return true;
  }
  function enhancePicker(sel, onSync) {
    var wrap = el("div", "iu-picker");
    var btn = el("button", "iu-picker-btn");
    btn.type = "button";
    btn.setAttribute("aria-haspopup", "listbox");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", labelFor(sel));
    var val = el("span", "iu-picker-val");
    btn.appendChild(val);
    btn.appendChild(el("span", "iu-picker-caret", "&#9662;"));

    var panel = el("div", "iu-picker-panel");
    panel.hidden = true;
    var search = el("input", "iu-picker-q");
    search.type = "search";
    search.setAttribute("autocomplete", "off");
    search.setAttribute("placeholder", "Type to search…");
    search.setAttribute("aria-label", "Search " + labelFor(sel));
    var list = el("ul", "iu-picker-list");
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", labelFor(sel));
    panel.appendChild(search);
    panel.appendChild(list);
    wrap.appendChild(btn);
    wrap.appendChild(panel);

    var open = false, focusIdx = -1;

    function options() { return [].slice.call(sel.options); }
    function labelOf(opt) {
      /* Show the option's own words, minus the "code · name" tail the baseline
         appends, so the list reads like a name list. */
      var t = txt(opt.textContent);
      return t;
    }
    function currentLabel() {
      var o = options().filter(function (x) { return x.value === sel.value; })[0];
      return o && o.value !== "" ? labelOf(o) : (options()[0] ? txt(options()[0].textContent) : "Select…");
    }
    function render(filter) {
      var f = String(filter || "").toLowerCase();
      list.innerHTML = "";
      var shown = 0;
      options().forEach(function (opt) {
        var lab = labelOf(opt);
        if (f && lab.toLowerCase().indexOf(f) < 0) return;
        var li = el("li", "iu-picker-opt" + (opt.value === sel.value && opt.value !== "" ? " on" : ""));
        li.setAttribute("role", "option");
        li.setAttribute("aria-selected", opt.value === sel.value ? "true" : "false");
        li.dataset.v = opt.value;
        li.textContent = lab;
        if (opt.value === "") li.classList.add("iu-picker-clear");
        li.addEventListener("click", function () { choose(opt.value); });
        list.appendChild(li);
        shown++;
      });
      if (!shown) {
        var none = el("li", "iu-picker-none", "No match. Try fewer letters.");
        list.appendChild(none);
      }
      sync();
    }
    function sync() {
      val.textContent = currentLabel();
      var empty = sel.value === "";
      btn.classList.toggle("is-empty", empty);
      var opts = [].slice.call(list.querySelectorAll(".iu-picker-opt"));
      opts.forEach(function (li, i) {
        li.classList.toggle("focus", i === focusIdx);
      });
    }
    function choose(v) {
      setValue(sel, v, "change");
      close();
      if (onSync) onSync();
    }
    function openPanel() {
      open = true;
      panel.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      search.value = "";
      render("");
      focusIdx = -1;
      search.focus();
    }
    function close() {
      open = false;
      panel.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }
    btn.addEventListener("click", function () { open ? close() : openPanel(); });
    search.addEventListener("input", function () { render(search.value); });
    wrap.addEventListener("keydown", function (e) {
      if (!open) {
        if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") { e.preventDefault(); openPanel(); }
        return;
      }
      var opts = [].slice.call(list.querySelectorAll(".iu-picker-opt"));
      if (e.key === "Escape") { e.preventDefault(); close(); btn.focus(); return; }
      if (e.key === "ArrowDown") { e.preventDefault(); focusIdx = Math.min(focusIdx + 1, opts.length - 1); sync(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); focusIdx = Math.max(focusIdx - 1, 0); sync(); }
      else if (e.key === "Enter" && focusIdx >= 0 && opts[focusIdx]) { e.preventDefault(); choose(opts[focusIdx].dataset.v); }
    });
    document.addEventListener("click", function (e) {
      if (open && !wrap.contains(e.target)) close();
    });

    sel.classList.add("iu-sr-select");
    sel.parentNode.insertBefore(wrap, sel);
    var mo = new MutationObserver(function () { render(search.value); if (onSync) onSync(); });
    mo.observe(sel, { childList: true });
    render("");
    return { root: wrap, sync: sync, rebuild: function () { render(search.value); } };
  }

  /* ============================== DATE =================================== */
  /* The field team asked for typed dates; that proved impractical, so typing is
     NOT the mechanism here. The real <input type="date"> stays the primary
     control — it gives the platform's own calendar and keeps the id, name,
     `max` and baseline listeners untouched — and two things are added:
       · a year list that jumps straight to any year, so reaching 1950 is one
         tap instead of a long scroll back from the current year;
       · ±1 year / ±10 year nudges for the common corrections.
     Bikram Sambat stays a text field because it is never auto-converted, and
     it gains the same year jump (offset to the BS calendar). */
  function enhanceDate(control, opts) {
    var isBS = !!opts.bs;
    /* Bikram Sambat runs about 56–57 years ahead of the Gregorian year, so its
       year list starts from the BS present, not the AD one. */
    var top = isBS ? nowDate().getFullYear() + 58 : nowDate().getFullYear() + 1;
    var yLow = isBS ? YEAR_MIN + 57 : YEAR_MIN;
    var wrap = el("div", "iu-date");

    var row = el("div", "iu-date-row");
    var yearSel = el("select", "iu-year");
    yearSel.setAttribute("aria-label", (opts.label || "Date") + " — jump to year");
    var yPlaceholder = el("option", null, "Jump to year…");
    yPlaceholder.value = "";
    yearSel.appendChild(yPlaceholder);
    for (var y = top; y >= yLow; y--) {
      var o = el("option", null, String(y));
      o.value = String(y);
      yearSel.appendChild(o);
    }
    row.appendChild(yearSel);
    wrap.appendChild(row);

    var quick = el("div", "iu-date-quick");
    wrap.appendChild(quick);

    function current() { return control.value || ""; }
    function apply(iso) {
      if (!iso) return;
      setValue(control, iso, "input");
      mirror();
      if (opts.onChange) opts.onChange();
    }
    function shiftYears(delta) {
      var base = current() || todayISO();
      var p = base.split("-");
      var yy = parseInt(p[0], 10) + delta;
      if (!isFinite(yy)) yy = nowDate().getFullYear();
      if (yy < yLow) yy = yLow;
      if (yy > top) yy = top;
      apply(yy + "-" + (p[1] || "01") + "-" + (p[2] || "01"));
    }
    function mk(label, fn) {
      var b = el("button", "iu-btn-sm", label);
      b.type = "button";
      b.addEventListener("click", fn);
      quick.appendChild(b);
      return b;
    }
    mk("Today", function () { apply(todayISO()); });
    mk("&minus;1&nbsp;yr", function () { shiftYears(-1); });
    mk("&minus;10&nbsp;yr", function () { shiftYears(-10); });

    /* The year list sets the year and keeps the rest of the date. */
    yearSel.addEventListener("change", function () {
      if (!yearSel.value) return;                 /* the prompt row is not a choice */
      var base = current() || todayISO();
      var p = base.split("-");
      apply(yearSel.value + "-" + (p[1] || "01") + "-" + (p[2] || "01"));
    });

    function mirror() {
      var iso = current();
      var yy = parseInt(String(iso).slice(0, 4), 10);
      if (isFinite(yy) && yy >= yLow && yy <= top) yearSel.value = String(yy);
      else yearSel.value = "";
    }
    control.addEventListener("input", mirror);
    control.addEventListener("change", mirror);

    control.classList.add("iu-date-input");
    /* Put the wrapper where the control lives, then MOVE the control in — the
       wrapper must be inserted first or the control would become its own
       ancestor. */
    var host = control.parentNode;
    host.insertBefore(wrap, control);
    row.insertBefore(control, yearSel);
    mirror();
    return { root: wrap, sync: mirror, yearSelect: yearSel };
  }

  /* ============================== COUNTS ================================= */
  /* The real disaggregation table and the real attendance input remain the
     only place a value lives. The panel gives the same numbers big steppers
     and a live sum check, which is what the page's own tally already watches. */
  function enhanceCounts() {
    var host = q("#s4 .dis") || q(".dis");
    if (!host) return null;
    var rows = qa("tbody tr", host);
    if (!rows.length) rows = qa("tr", host).filter(function (r) { return r.querySelector("input"); });
    if (!rows.length) return null;

    var panel = el("div", "iu-counts");
    var map = [];
    rows.forEach(function (tr) {
      var cell = tr.querySelector("th, td:first-child");
      var inputs = qa("input", tr);
      if (!cell || !inputs.length) return;
      map.push({ label: txt(cell.textContent), input: inputs[0] });
    });
    if (!map.length) return null;

    map.forEach(function (it) {
      var line = el("div", "iu-count");
      line.appendChild(el("span", "iu-count-label", it.label));
      var ctl = el("div", "iu-count-ctl");
      var minus = el("button", "iu-step", "&minus;");
      var field = el("input", "iu-count-in");
      var plus = el("button", "iu-step", "+");
      minus.type = plus.type = "button";
      field.type = "text";
      field.setAttribute("inputmode", "numeric");
      field.setAttribute("aria-label", it.label + " — count");
      var push = function (n) {
        if (n < 0) n = 0;
        field.value = String(n);
        setValue(it.input, String(n), "input");
        sync();
      };
      minus.addEventListener("click", function () { push((parseInt(it.input.value, 10) || 0) - 1); });
      plus.addEventListener("click", function () { push((parseInt(it.input.value, 10) || 0) + 1); });
      field.addEventListener("input", function () {
        var d = field.value.replace(/[^0-9]/g, "");
        field.value = d;
        setValue(it.input, d, "input");
        sync();
      });
      it.field = field;
      ctl.appendChild(minus);
      ctl.appendChild(field);
      ctl.appendChild(plus);
      line.appendChild(ctl);
      panel.appendChild(line);
    });

    var totalNode = $("reachedTotal");
    var total = el("div", "iu-total");
    total.appendChild(el("span", "iu-total-label", labelFor(totalNode)));
    var tCtl = el("div", "iu-count-ctl");
    var tMinus = el("button", "iu-step", "&minus;");
    var tField = el("input", "iu-count-in");
    var tPlus = el("button", "iu-step", "+");
    tMinus.type = tPlus.type = "button";
    tField.type = "text";
    tField.setAttribute("inputmode", "numeric");
    tField.setAttribute("aria-label", labelFor(totalNode));
    var pushTotal = function (n) {
      if (n < 0) n = 0;
      tField.value = String(n);
      setValue(totalNode, String(n), "input");
      sync();
    };
    tMinus.addEventListener("click", function () { pushTotal((parseInt(totalNode.value, 10) || 0) - 1); });
    tPlus.addEventListener("click", function () { pushTotal((parseInt(totalNode.value, 10) || 0) + 1); });
    tField.addEventListener("input", function () {
      var d = tField.value.replace(/[^0-9]/g, "");
      tField.value = d;
      setValue(totalNode, d, "input");
      sync();
    });
    tCtl.appendChild(tMinus);
    tCtl.appendChild(tField);
    tCtl.appendChild(tPlus);
    total.appendChild(tCtl);

    var check = el("p", "iu-sum-check");
    check.setAttribute("role", "status");
    check.setAttribute("aria-live", "polite");
    total.appendChild(check);
    panel.appendChild(total);

    function sync() {
      var sum = 0, any = false;
      map.forEach(function (it) {
        if (String(it.input.value).trim() !== "") { sum += parseInt(it.input.value, 10) || 0; any = true; }
        it.field.value = it.input.value;
      });
      tField.value = totalNode ? totalNode.value : "";
      if (!any && (!totalNode || totalNode.value === "")) { check.textContent = ""; check.className = "iu-sum-check"; return; }
      var tot = (!totalNode || totalNode.value === "") ? null : parseInt(totalNode.value, 10);
      if (tot == null) { check.textContent = "Attendance not entered yet."; check.className = "iu-sum-check"; return; }
      if (sum === tot) { check.textContent = sum + " counted — matches the attendance figure."; check.className = "iu-sum-check ok"; }
      else if (sum > tot) { check.textContent = sum + " counted vs " + tot + " attendance — " + (sum - tot) + " too many."; check.className = "iu-sum-check bad"; }
      else { check.textContent = sum + " counted vs " + tot + " attendance — " + (tot - sum) + " not yet allocated."; check.className = "iu-sum-check bad"; }
    }
    map.forEach(function (it) { it.input.addEventListener("input", sync); it.input.addEventListener("change", sync); });
    if (totalNode) { totalNode.addEventListener("input", sync); totalNode.addEventListener("change", sync); }

    host.parentNode.insertBefore(panel, host);
    sync();
    return { root: panel, sync: sync };
  }

  /* ========================== SAVE SAFETY ================================ */
  /* Back-dating is legitimate (the day the activity happened, not the day it
     was written up), so this never blocks a past date. It blocks only the one
     thing the existing validation already refuses — a future date — and asks
     for an explicit confirmation when the entry is not from today. */
  function buildSafety() {
    var box = el("div", "iu-safety");
    box.appendChild(el("p", "iu-safety-title", "Check the date and place before saving"));
    var list = el("ul", "iu-safety-list");
    box.appendChild(list);
    var ackRow = el("div", "iu-ack");
    var ackBtn = el("button", "iu-btn-sm", "Date and place checked");
    ackBtn.type = "button";
    var ackNote = el("span", "iu-ack-note");
    ackRow.appendChild(ackBtn);
    ackRow.appendChild(ackNote);
    box.appendChild(ackRow);

    var state = { blocked: false, needsAck: false, acked: false, needs: false };

    function signature() {
      return ($("dateAD") ? $("dateAD").value : "") + "|" + ($("site") ? $("site").value : "");
    }
    function refresh() {
      list.innerHTML = "";
      state.blocked = false;
      state.needs = false;

      var ad = $("dateAD") ? $("dateAD").value : "";
      var bs = $("dateBS") ? $("dateBS").value.trim() : "";
      var t = todayISO();
      var add = function (kind, text) {
        list.appendChild(el("li", "iu-safety-" + kind, text));
        if (kind === "bad") state.blocked = true;
      };

      if (!ad) {
        add("warn", "No Gregorian date yet. The existing validation blocks saving until one is entered.");
      } else if (ad > t) {
        add("bad", "The date is in the future (" + ad + "). Change it before saving.");
      } else if (ad < t) {
        state.needs = true;
        add("warn", "Back-dated entry (" + ad + "). Confirm this is the day the activity took place, not the day it was written up. A past date is allowed.");
      } else {
        add("ok", "Date is today (" + ad + ").");
      }

      if (bs) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(bs);
        if (!m) {
          add("warn", "Bikram Sambat value “" + bs + "” is not in YYYY-MM-DD form. It is stored exactly as typed — nothing is converted automatically.");
        } else if (ad) {
          var diff = parseInt(m[1], 10) - parseInt(ad.slice(0, 4), 10);
          if (Math.abs(diff - 57) > 1) {
            add("warn", "Bikram Sambat year " + m[1] + " is not the usual 56–57 years ahead of Gregorian " + ad.slice(0, 4) + ". Both values are stored as entered; correct the mistyped one if this was a slip.");
          } else {
            add("ok", "Bikram Sambat year is consistent with the Gregorian year.");
          }
        }
      }

      if (state.needs && !state.acked) {
        add("warn", "Tap “Date and place checked” to confirm this back-dated entry.");
      }
      box.classList.toggle("has-problem", state.blocked);
    }

    ackBtn.addEventListener("click", function () {
      state.acked = !state.acked;
      ackBtn.classList.toggle("on", state.acked);
      ackBtn.setAttribute("aria-pressed", state.acked ? "true" : "false");
      ackNote.textContent = state.acked ? "Recorded for this entry." : "";
      refresh();
    });
    /* A changed date or site invalidates a previous confirmation. */
    var lastSig = signature();
    var watch = function () {
      var s = signature();
      if (s !== lastSig) { lastSig = s; state.acked = false; ackBtn.classList.remove("on"); ackBtn.setAttribute("aria-pressed", "false"); ackNote.textContent = ""; }
      refresh();
    };
    ["dateAD", "dateBS", "site", "palika"].forEach(function (id) {
      var n = $(id);
      if (n) { n.addEventListener("input", watch); n.addEventListener("change", watch); }
    });
    refresh();

    return {
      root: box,
      refresh: watch,
      needsAck: function () { return state.needs && !state.acked; },
      isBlocked: function () { return state.blocked; },
      isAcknowledged: function () { return state.acked; }
    };
  }

  /* ================================ MOUNT ================================ */
  function mount(opts) {
    opts = opts || {};
    var cards = qa("#f > .card");
    if (!cards.length) return null;
    var total = cards.length;
    document.documentElement.setAttribute("data-iu-direction", opts.direction || "B2");

    var managed = { chips: {}, pickers: {}, dates: {}, counts: null, safety: null, api: null };
    var screens = [];

    /* --- 1. each card BECOMES a screen, in place, still inside #f ------- */
    cards.forEach(function (card, i) {
      card.classList.add("iu-screen");
      card.setAttribute("data-iu-step", String(i + 1));

      var step = q(".step", card);
      if (step) {
        var eyebrow = el("p", "iu-eyebrow", "Step " + (i + 1) + " of " + total);
        step.insertBefore(eyebrow, step.firstChild);
        /* Re-label the section heading so it is the screen title. */
        if (!step.id) step.id = "iu-h" + (i + 1);
        card.setAttribute("aria-labelledby", step.id);
      }

      /* Move everything after the header into a body wrapper. */
      var body = el("div", "iu-screen-body");
      var nodes = [].slice.call(card.childNodes);
      var seenStep = false;
      nodes.forEach(function (n) {
        if (n === step) { seenStep = true; return; }
        if (seenStep) body.appendChild(n);          /* move, not clone */
      });
      card.appendChild(body);

      var actions = el("div", "iu-actions");
      if (i > 0) {
        var back = el("button", "iu-btn ghost", "Back");
        back.type = "button";
        back.addEventListener("click", function () { go(i - 1); });
        actions.appendChild(back);
      }
      actions.appendChild(el("span", "iu-stepnote", "Step " + (i + 1) + " of " + total));
      if (i < total - 1) {
        var next = el("button", "iu-btn", "Continue");
        next.type = "button";
        next.addEventListener("click", function () { go(i + 1); });
        actions.appendChild(next);
      }
      card.appendChild(actions);
      screens.push(card);
    });

    /* --- 2. the page's own Save row joins the last screen --------------- */
    var realActions = q("#f > .actions") || q(".actions");
    if (realActions && screens[total - 1]) {
      realActions.classList.add("iu-real-actions");
      screens[total - 1].appendChild(realActions);
    }

    /* --- 3. step rail before the form ----------------------------------- */
    /* The label must be re-derived from the section heading, because that
       heading carries its own data-i18n key and is re-rendered by i18n.js
       whenever the reader switches language. A label snapshotted once at
       mount would keep the language it was built in -- which is exactly
       what happened here: the rail stayed Nepali after switching to
       English, on a page that otherwise translated correctly. Re-deriving
       also means the rail inherits the section heading's translation, so
       no new Nepali has to be authored for it. */
    var form = $("f");
    var stepper = el("nav", "iu-steps");
    stepper.setAttribute("aria-label", "Report steps");
    var stepHeads = screens.map(function (s) { return q(".step h2", s); });

    function relabelSteps() {
      qa(".iu-steplik", stepper).forEach(function (b, i) {
        var span = b.querySelector("span");
        var head = stepHeads[i];
        var text = head ? (head.textContent || "").trim() : "";
        if (span && text) span.textContent = text;
      });
    }

    screens.forEach(function (s, i) {
      var b = el("button", "iu-steplik");
      b.type = "button";
      b.innerHTML = "<i>" + (i + 1) + "</i><span></span>";
      b.addEventListener("click", function () { go(i); });
      stepper.appendChild(b);
    });
    relabelSteps();
    /* i18n.js re-renders [data-i18n] itself and then announces the change
       on this event, so this is the correct hook -- not a second polling
       loop, and not a second translation of the same words. */
    document.addEventListener("i18n:changed", function () { relabelSteps(); });
    form.parentNode.insertBefore(stepper, form);

    /* --- 4. enhancements over the REAL controls ------------------------- */
    /* Only baseline controls: never the pickers' own year lists or search
       boxes, which live outside #f. */
    qa("#f select").forEach(function (sel) {
      if (chipCandidate(sel)) {
        var key = sel.id || ("select" + Object.keys(managed.chips).length);
        managed.chips[key] = enhanceSelect(sel, function () { syncAll(); });
      } else if (pickerCandidate(sel)) {
        var pkey = sel.id || ("picker" + Object.keys(managed.pickers).length);
        managed.pickers[pkey] = enhancePicker(sel, function () { syncAll(); });
      }
    });
    var dAD = $("dateAD"), dBS = $("dateBS");
    if (dAD) managed.dates.dateAD = enhanceDate(dAD, { label: labelFor(dAD), onChange: syncAll });
    if (dBS) managed.dates.dateBS = enhanceDate(dBS, { label: labelFor(dBS), bs: true, onChange: syncAll });
    managed.counts = enhanceCounts();
    managed.safety = buildSafety();

    var s5body = screens[total - 1].querySelector(".iu-screen-body");
    if (s5body) s5body.insertBefore(managed.safety.root, s5body.firstChild);

    /* --- 5. one screen at a time ---------------------------------------- */
    var index = 0;
    function render() {
      screens.forEach(function (s, i) { s.classList.toggle("on", i === index); });
      qa(".iu-steplik", stepper).forEach(function (b, i) {
        b.classList.toggle("on", i === index);
        b.classList.toggle("done", i < index);
        b.setAttribute("aria-current", i === index ? "step" : "false");
      });
      document.body.setAttribute("data-iu-step", String(index + 1));
      var cur = screens[index];
      if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: "start", behavior: "auto" });
    }
    function go(i) {
      if (i < 0) i = 0;
      if (i > total - 1) i = total - 1;
      index = i;
      render();
    }
    function syncAll() {
      Object.keys(managed.chips).forEach(function (k) { managed.chips[k].sync(); });
      Object.keys(managed.pickers).forEach(function (k) { managed.pickers[k].sync(); });
      Object.keys(managed.dates).forEach(function (k) { managed.dates[k].sync(); });
      if (managed.counts) managed.counts.sync();
    }
    render();

    managed.api = {
      version: "2.0",
      direction: opts.direction || "B2",
      totalSteps: total,
      titles: screens.map(function (s) { return txt((q(".step h2", s) || {}).textContent || ""); }),
      currentStep: function () { return index; },
      go: go,
      next: function () { go(index + 1); },
      back: function () { go(index - 1); },
      sync: syncAll,
      screens: screens,
      stepper: stepper,
      chips: managed.chips,
      pickers: managed.pickers,
      dates: managed.dates,
      counts: managed.counts,
      safety: managed.safety,
      jumpToYear: function (id, year) {
        var d = managed.dates[id];
        if (!d) return false;
        d.yearSelect.value = String(year);
        fire(d.yearSelect, "change");
        return true;
      },
      typeDate: function (id, digits) {
        /* Digits are no longer the entry mechanism, but the helper stays so an
           automated test can assert how a typed-looking value is handled. */
        var d = managed.dates[id];
        if (!d) return false;
        return false;
      },
      yearOptions: function (id) {
        var d = managed.dates[id];
        return d ? d.yearSelect.options.length : 0;
      },
      contractAudit: contractAudit
    };
    window.IUPreview._api = managed.api;
    return managed.api;
  }

  /* ------------------------------------------------------ contract auditing */
  function contractAudit() {
    var dupes = [], seen = {};
    qa("[id]").forEach(function (n) {
      if (seen[n.id] && dupes.indexOf(n.id) < 0) dupes.push(n.id);
      seen[n.id] = true;
    });
    var required = ["dateAD", "dateBS", "sessionTime", "org", "cadre", "district", "site",
                    "palika", "modality", "activity", "status", "description", "reachedTotal",
                    "focalName", "focalPhone", "focalEmail", "partners", "tgs"];
    var missing = required.filter(function (id) { return !$(id); });
    var outside = required.filter(function (id) {
      var n = $(id);
      return !(n && n.closest("#f"));
    });
    return {
      duplicateIds: dupes,
      missingIds: missing,
      controlsOutsideForm: outside,
      clean: dupes.length === 0 && missing.length === 0 && outside.length === 0
    };
  }

  window.IUPreview = {
    version: "2.0",
    mount: mount,
    _internals: {
      todayISO: todayISO, setValue: setValue, fire: fire,
      chipCandidate: chipCandidate, contractAudit: contractAudit, YEAR_MIN: YEAR_MIN
    }
  };
})();

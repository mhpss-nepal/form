#!/usr/bin/env python3
"""Add a Province picker above the District picker in the forms that have one.

Ministry decision, 21 Sep 2026: every province, country-wide. Additive: the
District control keeps its name, id and meaning; Province simply narrows it.

Applies to contact.html and referral.html, which carry data-i18n keys. Their
district selects are populated from CODES.DISTRICTS in their own inline scripts,
so this also rewires that population through the province filter.

Usage: python3 add_province_picker.py
"""
import re
import sys
from pathlib import Path

FORMS = ["contact.html", "referral.html"]

BLOCK = """        <div class="f">
          <label for="province" data-i18n="f4.provLab">Province</label>
          <select id="province"></select>
          <div class="help" data-i18n="f4.provHelp">All seven provinces are listed. Choosing one shortens the district list; choosing nothing keeps every district available.</div>
        </div>
"""


def add_before_district(s: str) -> tuple:
    """Insert the province block immediately before the district field."""
    m = re.search(
        r'([ \t]*<div class="f">\s*\n[ \t]*<label for="district"[^>]*>.*?</label>\s*\n[ \t]*<select id="district">)',
        s, re.S)
    if not m:
        return s, False
    return s[:m.start(1)] + BLOCK + m.group(1), True


def rewire_population(s: str) -> tuple:
    """Make the district list follow the province, if it is populated inline."""
    m = re.search(
        r'([ \t]*)(C\.DISTRICTS\.forEach\(|fill\(\$\("district"\),\s*C\.DISTRICTS[^;]*;)',
        s)
    if not m:
        return s, False

    js = """
  /* Province narrows the district list; blank keeps every district, so a worker
     who does not know the province is never blocked. Country-wide per the
     Ministry's decision of 21 Sep 2026. */
  (function () {
    var pw = document.getElementById("province"), dw = document.getElementById("district");
    if (!pw || !dw || !window.CODES) return;
    var seen = [], provs = [];
    window.CODES.DISTRICTS.forEach(function (d) {
      if (d.province && seen.indexOf(d.province) === -1) { seen.push(d.province); provs.push(d.province); }
    });
    function rebuild() {
      var p = pw.value, keep = dw.value;
      var list = window.CODES.DISTRICTS.filter(function (d) { return !p || d.province === p; });
      dw.innerHTML = "";
      var o = document.createElement("option");
      o.value = ""; o.textContent = p ? "Select\\u2026" : "All districts";
      dw.appendChild(o);
      list.forEach(function (d) {
        if (d.code === "OTH") return;
        var e = document.createElement("option");
        e.value = d.code; e.textContent = d.name;
        dw.appendChild(e);
      });
      if (keep && list.some(function (d) { return d.code === keep; })) dw.value = keep;
    }
    var first = "";
    provs.forEach(function (n) {
      var o = document.createElement("option");
      o.value = n; o.textContent = n;
      if (!first) { o.textContent = "All provinces"; first = n; }
      pw.appendChild(o);
    });
    pw.addEventListener("change", rebuild);
    rebuild();
  })();
"""
    return s[:m.start(1)] + js + s[m.start(1):], True


def main() -> int:
    for form in FORMS:
        p = Path(form)
        if not p.exists():
            print("skip (absent): %s" % form)
            continue
        s = p.read_text(encoding="utf-8")
        if 'id="province"' in s:
            print("skip (already has province): %s" % form)
            continue
        s2, did_block = add_before_district(s)
        if not did_block:
            print("skip (no district label pair): %s" % form)
            continue
        s3, did_wire = rewire_population(s2)
        p.write_text(s3, encoding="utf-8")
        print("%-16s province block=%s population rewired=%s"
              % (form, did_block, did_wire))
    return 0


if __name__ == "__main__":
    sys.exit(main())

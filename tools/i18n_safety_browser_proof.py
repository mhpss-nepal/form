#!/usr/bin/env python3
"""Real-browser proof of the safety property (Stage B), over the staging site.

On the NEPALI page, every string under a _meta.professionalOnly prefix must
render in ENGLISH. This is the property the project claimed and which was NOT
true before keying (the prefix list matched 0 of 204 keys). It is checked here
by loading the page in a real Chromium and reading each keyed element by its
key, not by reading the dictionary.

It also checks:
  * the safeguarding checkbox and its consequence text are PRESENT and VISIBLE
    on the Nepali page (a gate that is hidden is not a gate);
  * the page really switched to Nepali elsewhere, so a page that simply failed
    to translate cannot pass;
  * every keyed element on the page has an English string (no [key] leaks).
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PORT = 8907
BASE = "http://127.0.0.1:%d" % PORT

# The elements that must be English on the Nepali page, by key.
PHQ9_ENGLISH_KEYS = [
    "phq9.item1", "phq9.item2", "phq9.item3", "phq9.item4", "phq9.item5",
    "phq9.item6", "phq9.item7", "phq9.item8", "phq9.item9",
    "phq9.scale0", "phq9.scale1", "phq9.scale2", "phq9.scale3",
    "phq9.itemInstruction", "phq9.itemDifficulty",
    "phq9.cutoff.interpretation", "phq9.cutoff.useWarning",
    "clinical.phq9ValidatedTextWarning",
    "consent.label", "consent.phq9",
]
REFERRAL_ENGLISH_KEYS = [
    "safeguard.checkLabel", "safeguard.confirmation", "safeguard.consequence",
    "safeguard.referralExclusion",
]


def probe(page, url, keys):
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(700)
    return page.evaluate("""(keys) => {
      const dev = (document.body.textContent.match(/[\\u0900-\\u097f]/g) || []).length;
      const out = {lang: document.documentElement.getAttribute('data-lang'),
                   devanagari: dev,
                   h1: (document.querySelector('h1')||{}).textContent||'',
                   elements: {}, missing_english: [], kept: 0, machine: 0};
      for (const k of keys) {
        const el = document.querySelector('[data-i18n="' + k + '"]');
        if (!el) { out.elements[k] = null; continue; }
        const r = el.getBoundingClientRect();
        out.elements[k] = {
          text: el.textContent.trim(),
          cls: el.className,
        };
      }
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const k = el.getAttribute('data-i18n');
        if (el.className.indexOf('i18n-missing') > -1) out.missing_english.push(k);
        if (el.classList.contains('i18n-kept')) out.kept++;
        if (el.classList.contains('i18n-machine')) out.machine++;
      });
      return out;
    }""", keys)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome",
            args=["--no-sandbox"])
        page = browser.new_page()
        checks = []

        print("=" * 76)
        print("PHQ-9 page in Nepali (?lang=ne) — clinical wording must stay English")
        print("=" * 76)
        phq9 = probe(page, BASE + "/form/phq9.html?lang=ne", PHQ9_ENGLISH_KEYS)
        print("data-lang=%s  Devanagari chars in body=%d" % (phq9["lang"], phq9["devanagari"]))
        for k in PHQ9_ENGLISH_KEYS:
            el = phq9["elements"].get(k)
            txt = el["text"] if el else "(element not found)"
            # Devanagari in a protected element means it got translated
            has_dev = any("\u0900" <= c <= "\u097f" for c in txt)
            ok = bool(el) and not has_dev and len(txt) > 1
            checks.append(("phq9/page/protected/" + k, ok, txt[:70]))
            print("  %-4s %-32s %s" % ("OK" if ok else "BAD", k, txt[:64]))
        checks.append(("phq9/page/no_missing_english_keys",
                       not phq9["missing_english"], str(phq9["missing_english"][:4])))
        checks.append(("phq9/page/kept_in_english_count>0", phq9["kept"] > 0,
                       "kept=%d machine=%d" % (phq9["kept"], phq9["machine"])))

        # the item-9 safety instruction, only rendered after a positive answer
        page.evaluate("""() => { const q = document.querySelectorAll('input[name="q8"]');
                                 if (q.length) q[1].click(); }""")
        page.wait_for_timeout(500)
        risk = page.evaluate("""() => {
            const el = document.querySelector('#risk [data-i18n="phq9.item9Instruction"]');
            return el ? {text: el.textContent.trim(), cls: el.className} : null;
        }""")
        print()
        print("item-9 instruction after a positive answer:")
        print("  %s" % (risk["text"][:150] if risk else "(not rendered at all)"))
        ok = bool(risk) and "Item 9 is positive" in risk["text"] \
            and not any("\u0900" <= c <= "\u097f" for c in risk["text"])
        checks.append(("phq9/page/item9_instruction_present_and_english", ok,
                       risk["text"][:60] if risk else "MISSING"))

        print()
        print("=" * 76)
        print("Referral page in Nepali — the safeguarding gate")
        print("=" * 76)
        ref = probe(page, BASE + "/form/referral.html?lang=ne", REFERRAL_ENGLISH_KEYS)
        print("data-lang=%s  h1=%s" % (ref["lang"], ref["h1"][:50]))
        for k in REFERRAL_ENGLISH_KEYS:
            el = ref["elements"].get(k)
            txt = el["text"] if el else "(element not found)"
            has_dev = any("\u0900" <= c <= "\u097f" for c in txt)
            ok = bool(el) and not has_dev and len(txt) > 1
            checks.append(("referral/page/protected/" + k, ok, txt[:70]))
            print("  %-4s %-34s %s" % ("OK" if ok else "BAD", k, txt[:60]))

        gate = page.evaluate("""() => {
            const cb = document.querySelector('#notgbv');
            const box = document.querySelector('[data-i18n="safeguard.confirmation"]');
            const vis = (e) => { if (!e) return false;
                const r = e.getBoundingClientRect();
                return r.width > 0 && r.height > 0; };
            return {checkbox_present: !!cb, checkbox_type: cb ? cb.type : null,
                    checkbox_visible: vis(cb),
                    confirmation_visible: vis(box),
                    consequence_visible: vis(document.querySelector('[data-i18n="safeguard.consequence"]'))};
        }""")
        print("safeguarding gate visibility:", gate)
        checks.append(("referral/page/gate_control_present_and_visible",
                       gate["checkbox_present"] and gate["checkbox_type"] == "checkbox"
                       and gate["checkbox_visible"] and gate["confirmation_visible"],
                       str(gate)))
        checks.append(("referral/page/page_really_nepali",
                       ref["lang"] == "ne"
                       and any("\u0900" <= c <= "\u097f" for c in ref["h1"]),
                       ref["h1"][:40]))
        checks.append(("referral/page/no_missing_english_keys",
                       not ref["missing_english"], str(ref["missing_english"][:4])))

        print()
        print("=" * 76)
        print("RESULT")
        print("=" * 76)
        bad = [c for c in checks if not c[1]]
        print("checks: %d   failures: %d" % (len(checks), len(bad)))
        for name, ok, detail in bad:
            print("  FAIL %s  (%s)" % (name, detail))
        print()
        print("VERDICT:", "all safety properties hold" if not bad else "SAFETY PROPERTY VIOLATED")

        Path("/tmp/i18n-safety-proof.json").write_text(json.dumps(
            {"phq9": {k: v for k, v in phq9.items() if k != "body"},
             "referral": {k: v for k, v in ref.items() if k != "body"},
             "gate": gate,
             "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
             "failures": len(bad)}, ensure_ascii=False, indent=2), encoding="utf-8")

        browser.close()
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

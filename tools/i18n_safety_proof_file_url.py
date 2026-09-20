"""Real-browser Stage B proof, over file:// (no staging server needed).

Runs the SAME assertions as tools/i18n_safety_browser_proof.py, but loads the
pages directly from disk so it does not depend on a staging HTTP server.

The property under test: on the NEPALI page, every string under a
_meta.professionalOnly prefix must render in ENGLISH.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FORM = Path("/root/mhpss-nepal-work/form-translation")
PHQ9 = FORM / "phq9.html"
REFERRAL = FORM / "referral.html"

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

PROBE = """(keys) => {
  const dev = (document.body.textContent.match(/[\\u0900-\\u097f]/g) || []).length;
  const out = {lang: document.documentElement.getAttribute('data-lang'),
               devanagari: dev,
               h1: (document.querySelector('h1')||{}).textContent||'',
               elements: {}, missing_english: [], kept: 0, machine: 0};
  for (const k of keys) {
    const el = document.querySelector('[data-i18n="' + k + '"]');
    if (!el) { out.elements[k] = null; continue; }
    out.elements[k] = {text: el.textContent.trim(), cls: el.className};
  }
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.getAttribute('data-i18n');
    if (el.className.indexOf('i18n-missing') > -1) out.missing_english.push(k);
    if (el.classList.contains('i18n-kept')) out.kept++;
    if (el.classList.contains('i18n-machine')) out.machine++;
  });
  return out;
}"""


def has_devanagari(text):
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def main():
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome",
            args=["--no-sandbox", "--allow-file-access-from-files"])
        page = browser.new_page()

        print("=" * 74)
        print("PHQ-9 page in Nepali (%s) - clinical wording must stay English" % PHQ9.name)
        print("=" * 74)
        page.goto(PHQ9.as_uri() + "?lang=ne", wait_until="load")
        page.wait_for_timeout(1200)
        phq9 = page.evaluate(PROBE, PHQ9_ENGLISH_KEYS)
        print("data-lang=%s  Devanagari chars in body=%d  h1=%s"
              % (phq9["lang"], phq9["devanagari"], (phq9["h1"] or "")[:44]))
        for k in PHQ9_ENGLISH_KEYS:
            el = phq9["elements"].get(k)
            txt = el["text"] if el else "(element not found)"
            ok = bool(el) and not has_devanagari(txt) and len(txt) > 1
            checks.append(("phq9/protected/" + k, ok, txt[:70]))
            print("  %-4s %-34s %s" % ("OK" if ok else "BAD", k, txt[:56]))
        checks.append(("phq9/no_missing_english_keys", not phq9["missing_english"],
                       str(phq9["missing_english"][:4])))
        checks.append(("phq9/kept_in_english_count>0", phq9["kept"] > 0,
                       "kept=%d machine=%d" % (phq9["kept"], phq9["machine"])))

        # item-9 instruction, only rendered after a positive answer
        page.evaluate("""() => { const q = document.querySelectorAll('input[name="q8"]');
                                 if (q.length) q[1].click(); }""")
        page.wait_for_timeout(700)
        risk = page.evaluate("""() => {
            const el = document.querySelector('#risk [data-i18n="phq9.item9Instruction"]');
            return el ? {text: el.textContent.trim(), cls: el.className} : null;
        }""")
        print()
        print("item-9 instruction after a positive answer:")
        print("  %s" % (risk["text"][:140] if risk else "(not rendered at all)"))
        ok = bool(risk) and "Item 9 is positive" in risk["text"] \
             and not has_devanagari(risk["text"])
        checks.append(("phq9/item9_instruction_present_and_english", ok,
                       risk["text"][:60] if risk else "MISSING"))

        print()
        print("=" * 74)
        print("Referral page in Nepali - the safeguarding gate")
        print("=" * 74)
        page.goto(REFERRAL.as_uri() + "?lang=ne", wait_until="load")
        page.wait_for_timeout(1200)
        ref = page.evaluate(PROBE, REFERRAL_ENGLISH_KEYS)
        print("data-lang=%s  Devanagari chars in body=%d  h1=%s"
              % (ref["lang"], ref["devanagari"], (ref["h1"] or "")[:44]))
        for k in REFERRAL_ENGLISH_KEYS:
            el = ref["elements"].get(k)
            txt = el["text"] if el else "(element not found)"
            ok = bool(el) and not has_devanagari(txt) and len(txt) > 1
            checks.append(("referral/protected/" + k, ok, txt[:70]))
            print("  %-4s %-34s %s" % ("OK" if ok else "BAD", k, txt[:56]))

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
        checks.append(("referral/gate_control_present_and_visible",
                       gate["checkbox_present"] and gate["checkbox_type"] == "checkbox"
                       and gate["checkbox_visible"] and gate["confirmation_visible"],
                       str(gate)))
        checks.append(("referral/page_really_nepali",
                       ref["lang"] == "ne" and has_devanagari(ref["h1"] or ""),
                       (ref["h1"] or "")[:40]))
        checks.append(("referral/no_missing_english_keys",
                       not ref["missing_english"], str(ref["missing_english"][:4])))

        print()
        print("=" * 74)
        print("RESULT")
        print("=" * 74)
        bad = [c for c in checks if not c[1]]
        print("checks: %d   failures: %d" % (len(checks), len(bad)))
        for name, ok, detail in bad:
            print("  FAIL %s  (%s)" % (name, detail))
        print("VERDICT:", "all safety properties hold" if not bad
              else "SAFETY PROPERTY VIOLATED")

        Path("/tmp/i18n-safety-proof-file.json").write_text(json.dumps(
            {"phq9": phq9, "referral": ref, "gate": gate,
             "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
             "failures": len(bad)}, ensure_ascii=False, indent=2), encoding="utf-8")
        browser.close()
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

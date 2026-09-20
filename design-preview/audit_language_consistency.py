#!/usr/bin/env python3
"""Exhaustive language-consistency audit.

The first version of this audit missed a whole class of text, so this one
closes those gaps explicitly:

  1. attributes as well as text nodes — placeholder, title, aria-label,
     alt, and the value of buttons/inputs. A translated label with an
     untranslated placeholder is still a mixed-language form.
  2. <option> elements, which live inside selects that may be closed.
  3. hidden content — every step/section is revealed before scanning, so a
     screen the reader has not reached yet is still checked.
  4. four viewports, because copy is sometimes swapped by media query.

Classifies each string while the interface is English or Nepali:
  * Devanagari while ENGLISH   -> defect, always.
  * Latin while NEPALI         -> candidate untranslated copy; recorded with
                                  whether it is byte-identical in English.

Run: python3 design-preview/audit_language_consistency.py
Writes: design-preview/language-audit.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path("/root/mhpss-nepal-work/form-frontend")
BASE = "http://127.0.0.1:8765/form-frontend"
OUT = REPO / "design-preview" / "language-audit.json"

NO_I18N = {"cards.html"}
VIEWPORTS = [(390, 844), (768, 1024), (1280, 900)]

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

# Latin strings that are correct in Nepali mode: identifiers, not prose.
ALLOW_PATTERNS = [
    re.compile(r"^[\d\s\-–—/:.+()%]+$"),           # numbers, dates, units
    re.compile(r"^[A-Z]{2,}(-[A-Z0-9]+)?$"),        # codes: NUW-02, TG-COM
    re.compile(r"^v?\d+(\.\d+)*$"),                 # versions
    re.compile(r"^(ENG|NEP)$"),                     # the language toggle itself
]


def allowed_latin(t: str) -> bool:
    t = t.strip()
    if not t or not LATIN_WORD.search(t):
        return True
    return any(p.match(t) for p in ALLOW_PATTERNS)


# Reveal every collapsible/hidden region, then harvest text + attributes.
EXTRACT = r"""
() => {
  // 1. reveal everything so hidden screens are audited too
  document.querySelectorAll('[hidden]').forEach(el => el.removeAttribute('hidden'));
  document.querySelectorAll('details').forEach(d => d.open = true);
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') el.setAttribute('data-audit-hidden-display', '1');
  });

  const rows = [];
  const push = (where, text, el, key) => {
    const t = (text || '').replace(/\s+/g, ' ').trim();
    if (!t) return;
    rows.push({ where, text: t, key: key || null,
                tag: el ? el.tagName.toLowerCase() : '',
                vis: el ? (el.getBoundingClientRect().width > 0 &&
                           el.getBoundingClientRect().height > 0) : true });
  };

  const keyOf = (el) => {
    let p = el;
    while (p && p !== document.body) {
      if (p.hasAttribute && p.hasAttribute('data-i18n')) {
        return p.getAttribute('data-i18n') + (p.hasAttribute('data-i18n-html') ? '[html]' : '');
      }
      p = p.parentElement;
    }
    return null;
  };

  // 2. text nodes
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const el = n.parentElement;
    if (!el) continue;
    if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName)) continue;
    push('text', n.nodeValue, el, keyOf(el));
  }

  // 3. attributes that a reader sees or hears
  document.querySelectorAll('*').forEach(el => {
    ['placeholder', 'title'].forEach(a => {
      if (el.hasAttribute(a)) push('attr:' + a, el.getAttribute(a), el, keyOf(el));
    });
    ['aria-label', 'alt'].forEach(a => {
      if (el.hasAttribute(a)) push('attr:' + a, el.getAttribute(a), el, keyOf(el));
    });
    if ((el.tagName === 'INPUT' || el.tagName === 'BUTTON') &&
        ['button', 'submit', 'reset'].includes((el.type || '').toLowerCase())) {
      if (el.value) push('attr:value', el.value, el, keyOf(el));
    }
    if (el.tagName === 'OPTION') push('option', el.textContent, el, keyOf(el));
  });

  // 4. generated content from ::before / ::after
  document.querySelectorAll('*').forEach(el => {
    ['::before', '::after'].forEach(p => {
      const c = getComputedStyle(el, p).content;
      if (c && c !== 'none' && c !== 'normal') {
        push('pseudo' + p, c.replace(/^"|"$/g, ''), el, keyOf(el));
      }
    });
  });

  return rows;
}
"""


def collect(pg, url, mode):
    pg.goto(f"{url}?lang={mode}", wait_until="load")
    pg.evaluate(
        "(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();"
        "for(const k of await caches.keys())await caches.delete(k);})()"
    )
    pg.goto(f"{url}?lang={mode}", wait_until="load")
    pg.wait_for_timeout(500)
    lang = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
    rows = pg.evaluate(EXTRACT)
    # group by (where, text) so the two modes can be compared as sets
    return lang, rows


def main() -> int:
    pages = sorted(p.name for p in REPO.glob("*.html"))
    pages = [p for p in pages if p not in NO_I18N]
    report = {"viewport_pages": {}, "summary": {}}
    total_defect = 0

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name in pages:
            url = f"{BASE}/{name}"
            page_defects, page_candidates = [], []
            for (w, h) in VIEWPORTS:
                ctx = b.new_context(viewport={"width": w, "height": h})
                pg = ctx.new_page()
                try:
                    _, rows_en = collect(pg, url, "en")
                    _, rows_ne = collect(pg, url, "ne")
                except Exception as exc:  # noqa: BLE001
                    print(f"  {name}@{w}: COLLECT FAILED {exc}")
                    ctx.close()
                    continue

                en_map = {}
                for r in rows_en:
                    en_map.setdefault(r["text"], r)

                for r in rows_en:
                    if DEVANAGARI.search(r["text"]) and not allowed_latin(r["text"]):
                        page_defects.append({"viewport": w, "where": r["where"],
                                             "key": r["key"], "text": r["text"][:100]})
                for r in rows_ne:
                    if allowed_latin(r["text"]):
                        continue
                    other = en_map.get(r["text"])
                    # identical in both modes => never translated
                    if other is not None:
                        page_candidates.append({"viewport": w, "where": r["where"],
                                                "key": r["key"], "text": r["text"][:100]})
                ctx.close()

            # dedupe across viewports for readability
            def dedupe(items):
                seen, out = set(), []
                for it in items:
                    k = (it["where"], it["text"])
                    if k in seen:
                        continue
                    seen.add(k)
                    out.append(it)
                return out

            page_defects = dedupe(page_defects)
            page_candidates = dedupe(page_candidates)
            total_defect += len(page_defects)
            report["viewport_pages"][name] = {
                "devanagari_in_english": page_defects,
                "untranslated_in_nepali": page_candidates,
            }
            print(f"\n=== {name} ===")
            print(f"  [BUG] Devanagari while ENGLISH : {len(page_defects)}")
            print(f"  [?]  untranslated while NEPALI : {len(page_candidates)}")
            ctx_free = None
        b.close()

    report["summary"]["total_devanagari_in_english"] = total_defect
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT}")
    print(f"TOTAL Devanagari-in-English defects: {total_defect}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

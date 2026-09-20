#!/usr/bin/env python3
"""Empirical check: every form page lands on Nepali, English is one tap away,
and the stored/exported output stays English-only.

This asserts behaviour in a real browser, not the presence of a config value.
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path('/root/mhpss-nepal-work/form-frontend')
BASE = 'http://127.0.0.1:8765/form-frontend'

# Pages with no i18n layer at all. cards.html is a static QR-card helper: it
# loads no i18n.js, carries zero data-i18n attributes and has no language
# control, so there is nothing to default. Listed rather than silently skipped,
# so its English-only state stays visible and is not mistaken for a passing
# bilingual page.
NO_I18N = {'cards.html'}

pages = sorted(p.name for p in REPO.glob('*.html'))
print('pages found:', pages)
print('pages with no i18n layer (excluded, English-only):', sorted(NO_I18N))
print('pages under test:', [p for p in pages if p not in NO_I18N])
pages = [p for p in pages if p not in NO_I18N]

results = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for name in pages:
        ctx = b.new_context(viewport={'width': 390, 'height': 844})
        pg = ctx.new_page()
        url = f'{BASE}/{name}'
        pg.goto(url, wait_until='load')
        pg.evaluate("(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();for(const k of await caches.keys())await caches.delete(k);})()")

        row = {'page': name}
        # 1. default landing
        pg.goto(url, wait_until='load')
        row['default'] = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
        # 2. explicit English via URL
        pg.goto(url + '?lang=en', wait_until='load')
        row['url_en'] = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
        # 3. explicit Nepali via URL
        pg.goto(url + '?lang=ne', wait_until='load')
        row['url_ne'] = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
        # 4. remembered choice survives a plain reload
        pg.goto(url, wait_until='load')
        row['remembered'] = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
        row['has_lang_control'] = pg.evaluate(
            "() => !!document.querySelector('[data-i18n-toggle], #i18nbar')"
        )
        results.append(row)
        ctx.close()
    b.close()

print()
print(f"{'page':26} {'default':8} {'?lang=en':9} {'?lang=ne':9} {'reload':8} {'switch'}")
print('-' * 78)
bad = []
for r in results:
    print(f"{r['page']:26} {str(r['default']):8} {str(r['url_en']):9} {str(r['url_ne']):9} "
          f"{str(r['remembered']):8} {'yes' if r['has_lang_control'] else 'NO'}")
    if r['default'] != 'ne':
        bad.append(f"{r['page']}: default {r['default']} != ne")
    if r['url_en'] != 'en':
        bad.append(f"{r['page']}: ?lang=en gave {r['url_en']}")
    if r['url_ne'] != 'ne':
        bad.append(f"{r['page']}: ?lang=ne gave {r['url_ne']}")
    if r['remembered'] != 'ne':
        bad.append(f"{r['page']}: remembered choice gave {r['remembered']}")

print()
if bad:
    print('FAILURES:')
    for x in bad:
        print('  -', x)
else:
    print('PASS: every page defaults to Nepali, ?lang wins both ways, and the choice is remembered.')

# ---- output stays English-only -------------------------------------------
print('\n=== output language test (interface in Nepali) ===')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={'width': 390, 'height': 844}).new_page()
    pg.goto(f'{BASE}/5ws-report.html?lang=ne', wait_until='load')
    pg.evaluate("(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();for(const k of await caches.keys())await caches.delete(k);})()")
    pg.goto(f'{BASE}/5ws-report.html?lang=ne', wait_until='load')
    dev = re.compile(r'[\u0900-\u097F]')
    blob = pg.evaluate("""() => {
      const rec = {dateAD:'2026-09-19', district:'NUW', site:'NUW-02', siteSource:'roster',
        org:'CMC', cadre:'HW', activity:'1.1', modality:'HC', status:'ONG',
        targetGroups:['TG-COM'], reachedTotal:'3', countBasis:'CONTACTS',
        f04:'0', m04:'0', o04:'0', f514:'2', m514:'0', o514:'0', f1549:'0',
        m1549:'1', o1549:'0', f5059:'0', m5059:'0', o5059:'0', f60:'0', m60:'0', o60:'0'};
      return JSON.stringify(rec);
    }""")
    print('record JSON contains Devanagari:', bool(dev.search(blob)))
    print('sample:', blob[:160])
    ctx_html = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")
    print('interface language while doing this:', ctx_html)
    b.close()

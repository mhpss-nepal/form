#!/usr/bin/env python3
"""Exact inventory of untranslated English on the 5Ws pages while Nepali is selected."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import re, json

REPO = Path('/root/mhpss-nepal-work/form-frontend')
BASE = 'http://127.0.0.1:8765/form-frontend'
DEV = re.compile(r'[\u0900-\u097F]')
LAT = re.compile(r'[A-Za-z]{2,}')

PAGES = ['5ws-report.html', '5ws-report-b2.html']

with sync_playwright() as p:
    b = p.chromium.launch()
    for name in PAGES:
        ctx = b.new_context(viewport={'width': 390, 'height': 844})
        pg = ctx.new_page()
        url = f'{BASE}/{name}?lang=ne'
        pg.goto(url, wait_until='load')
        pg.evaluate("(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();for(const k of await caches.keys())await caches.delete(k);})()")
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(800)
        rows = pg.evaluate("""() => {
          const out = [];
          const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let n;
          while ((n = w.nextNode())) {
            const el = n.parentElement;
            if (!el) continue;
            if (['SCRIPT','STYLE','NOSCRIPT'].includes(el.tagName)) continue;
            const cs = getComputedStyle(el);
            if (cs.display === 'none' || cs.visibility === 'hidden') continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) continue;
            const t = (n.nodeValue||'').replace(/\\s+/g,' ').trim();
            if (!t || t.length < 3) continue;
            if (!/[A-Za-z]{2,}/.test(t)) continue;
            // nearest ancestry info
            let id = '', cls = '', key = null, p = el;
            for (let i = 0; i < 6 && p && p !== document.body; i++) {
              if (!id && p.id) id = p.id;
              if (!cls && p.className) cls = String(p.className);
              if (!key && p.hasAttribute && p.hasAttribute('data-i18n')) key = p.getAttribute('data-i18n');
              p = p.parentElement;
            }
            out.push({y: Math.round(r.top), tag: el.tagName.toLowerCase(),
                      id, cls: cls.slice(0,40), key, text: t.slice(0,110)});
          }
          return out;
        }""")
        print(f"\n{'='*100}\n{name}  (interface = Nepali)  untranslated-looking English nodes: {len(rows)}\n{'='*100}")
        for r in rows:
            print(f"y={r['y']:>5} {r['tag']:<6} id={r['id']:<16} cls={r['cls']:<38} key={str(r['key']):<18} {r['text']}")
        ctx.close()
    b.close()

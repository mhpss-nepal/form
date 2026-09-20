#!/usr/bin/env python3
"""Reproduce the real user path: land on Nepali, then tap ENG.

A cold ?lang=en load never mounts the machine-translation notice, so it
cannot see the defect a reader actually hits. This drives the toggle.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import re, json

REPO = Path('/root/mhpss-nepal-work/form-frontend')
BASE = 'http://127.0.0.1:8765/form-frontend'
DEV = re.compile(r'[\u0900-\u097F]')

PAGES = ['5ws-report.html', '5ws-report-b2.html', 'index.html', 'phq9.html',
         'referral.html', 'contact.html', 'selfreport.html', '4ws-report.html']

with sync_playwright() as p:
    b = p.chromium.launch()
    print("Scenario: fresh visitor (Nepali) -> taps ENG -> what Devanagari remains?\n")
    for name in PAGES:
        ctx = b.new_context(viewport={'width': 390, 'height': 844})
        pg = ctx.new_page()
        url = f'{BASE}/{name}'
        pg.goto(url, wait_until='load')
        pg.evaluate("(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();for(const k of await caches.keys())await caches.delete(k);})()")
        pg.goto(url, wait_until='load')          # default = Nepali
        pg.wait_for_timeout(500)
        before = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")

        # tap the ENG control the way a user does
        clicked = pg.evaluate("""() => {
          const btns = [...document.querySelectorAll('button,a')];
          const eng = btns.find(b => (b.textContent||'').trim().toUpperCase() === 'ENG')
                   || btns.find(b => (b.getAttribute('aria-label')||'').toUpperCase().includes('ENGLISH'));
          if (!eng) return false;
          eng.click();
          return true;
        }""")
        pg.wait_for_timeout(700)
        after = pg.evaluate("() => document.documentElement.getAttribute('data-lang')")

        devanagari = pg.evaluate("""() => {
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
            if (!t) continue;
            if (/[\\u0900-\\u097F]/.test(t)) out.push({
              tag: el.tagName.toLowerCase(),
              cls: String(el.className||'').slice(0,24),
              y: Math.round(r.top), text: t.slice(0,80)});
          }
          return out;
        }""")
        print(f"{name:24} ne->{before}  clickedENG={clicked}  ->{after}   Devanagari nodes: {len(devanagari)}")
        for d in devanagari[:8]:
            print(f"      y={d['y']:>5} {d['tag']:<7} {d['cls']:<24} {d['text']}")
        ctx.close()
    b.close()

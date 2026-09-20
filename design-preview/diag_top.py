#!/usr/bin/env python3
"""What is actually at the TOP of each page, in both language modes?"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import re, json

REPO = Path('/root/mhpss-nepal-work/form-frontend')
BASE = 'http://127.0.0.1:8765/form-frontend'
DEV = re.compile(r'[\u0900-\u097F]')

PAGES = ['5ws-report.html', '5ws-report-b2.html', 'index.html', 'phq9.html', 'referral.html',
         'contact.html', 'selfreport.html', '4ws-report.html']

with sync_playwright() as p:
    b = p.chromium.launch()
    for name in PAGES:
        url = f'{BASE}/{name}'
        ctx = b.new_context(viewport={'width': 390, 'height': 844})
        pg = ctx.new_page()
        for mode in ('en', 'ne'):
            pg.goto(f'{url}?lang={mode}', wait_until='load')
            pg.evaluate("(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();for(const k of await caches.keys())await caches.delete(k);})()")
            pg.goto(f'{url}?lang={mode}', wait_until='load')
            pg.wait_for_timeout(700)
            info = pg.evaluate("""() => {
              const mt = document.getElementById('mtnote');
              const top = [];
              document.querySelectorAll('body *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.top < 620 && r.height > 0 && r.width > 0) {
                  // only leaf-ish text elements
                  const own = [...el.childNodes].filter(n=>n.nodeType===3)
                     .map(n=>n.nodeValue.replace(/\\s+/g,' ').trim()).filter(Boolean).join(' ');
                  if (own) top.push({
                    tag: el.tagName.toLowerCase(), cls: String(el.className||'').slice(0,26),
                    top: Math.round(r.top), text: own.slice(0,70)
                  });
                }
              });
              top.sort((a,b)=>a.top-b.top);
              return {
                lang: document.documentElement.getAttribute('data-lang'),
                mtnote: mt ? {present:true, text: mt.innerText.replace(/\\s+/g,' ').trim().slice(0,220),
                              display: getComputedStyle(mt).display} : {present:false},
                top: top.slice(0, 18)
              };
            }""")
            print(f"\n{'#'*72}\n# {name}   mode={mode}   data-lang={info['lang']}\n{'#'*72}")
            m = info['mtnote']
            print(f"  mtnote present: {m['present']}" + (f" display={m.get('display')}" if m['present'] else ''))
            if m['present'] and m.get('text'):
                dev = bool(DEV.search(m['text']))
                print(f"    Devanagari in notice: {dev}")
                print(f"    text: {m['text'][:200]}")
            for t in info['top']:
                flag = ' <== DEVANAGARI' if DEV.search(t['text']) and mode == 'en' else ''
                print(f"    y={t['top']:>4} {t['tag']:<7} {t['cls']:<26} {t['text']}{flag}")
        ctx.close()
    b.close()

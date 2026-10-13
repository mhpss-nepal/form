#!/usr/bin/env python3
"""Actual browser directory, URL parity and inert-source review regression."""
import http.server
import json
import os
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
HUB = Path(os.environ.get('MHPSS_HUB', str(ROOT.parent / 'all-homes')))
OUT = Path(os.environ.get('MHPSS_EVIDENCE', str(ROOT / 'directory-evidence')))
OUT.mkdir(parents=True, exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?')[0]
        root, rel = (HUB, path[5:]) if path.startswith('/hub/') else (ROOT, path[6:] if path.startswith('/form/') else path.lstrip('/'))
        return str(root / (rel or 'index.html'))
    def log_message(self, format, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%s/form/' % server.server_port
PROBE = '''(() => {
window.sideEffects=[];
for (const method of ['getItem','setItem','removeItem','clear']) { Storage.prototype[method]=function(){sideEffects.push('Storage.'+method);throw Error('Storage forbidden');}; }
for (const method of ['open','deleteDatabase']) indexedDB[method]=function(){sideEffects.push('IDB.'+method);throw Error('IDB forbidden');};
window.fetch=function(){sideEffects.push('fetch');throw Error('fetch forbidden');};
XMLHttpRequest.prototype.open=function(){sideEffects.push('XHR');throw Error('XHR forbidden');};
navigator.sendBeacon=function(){sideEffects.push('beacon');return false;};
window.WebSocket=function(){sideEffects.push('WebSocket');throw Error('WebSocket forbidden');};
window.__copied=[]; Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>__copied.push(t)}});
})();'''
results = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for width in [320,390,1280]:
        for lang in ['en','ne']:
            context = browser.new_context(viewport={'width':width,'height':900}, service_workers='block')
            context.route('https://fonts.googleapis.com/**', lambda r:r.fulfill(status=200,body=''))
            context.route('https://fonts.gstatic.com/**',lambda r:r.abort())
            # External Firebase SDKs on untouched root forms are not exercised here.
            page = context.new_page(); errors=[]; bad=[]
            page.on('pageerror', lambda e:errors.append(str(e)))
            page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
            page.add_init_script("window.__copied=[]; Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>__copied.push(t)}});")
            page.goto(BASE+'?lang='+lang); page.wait_for_timeout(250)
            cards = page.locator('.ml-card'); assert cards.count()==8
            # Switch through the live UI, not cold-load language only.
            page.evaluate("window.I18N && I18N.setLang && I18N.setLang('en')")
            page.evaluate("window.I18N && I18N.setLang && I18N.setLang('"+lang+"')")
            destinations=[]
            for i in range(8):
                card=cards.nth(i); dest=card.locator('.ml-actions a').get_attribute('href'); assert dest is not None; destinations.append(dest)
                card.locator('[data-url]').click()
                assert page.evaluate('__copied.at(-1)')==BASE+dest
                card.locator('[data-qr]').click()
                assert card.locator('.qrbox svg').count()==1
                assert card.locator('.qrbox .u').inner_text()=='https://mhpss-nepal.github.io/form/'+dest
                card.locator('[data-qr]').click()
            assert len(set(destinations))==8
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), ('directory overflow',width,lang)
            page.wait_for_timeout(1700)
            page.screenshot(path=str(OUT/f'directory-{width}-{lang}.png'),full_page=True)
            results.append({'width':width,'language':lang,'directory':8,'copy_qr':8,'destinations':destinations})
            for dest in destinations:
                # Follow the actual catalogue action before inspecting questions.
                page.goto(BASE+'?lang='+lang)
                page.locator('.ml-actions a').nth(destinations.index(dest)).click()
                assert page.url==BASE+dest
                if not dest.startswith('review/'):
                    # Actual original forms and controls, without entering or sending data.
                    page.goto(BASE+dest+'?lang='+lang);page.wait_for_timeout(300)
                    assert page.locator('input,select,textarea').count()>0, dest
                    assert page.locator('label').count()>0,dest
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('form overflow',dest,width,lang)
                    results.append({'destination':dest,'width':width,'language':lang,'controls':page.locator('input,select,textarea').count()})
                else:
                    review = context.new_page(); review.add_init_script(PROBE); review_errors=[]; requests=[]
                    review.on('pageerror',lambda e:review_errors.append(str(e)))
                    review.on('request',lambda r:requests.append({'url':r.url,'method':r.method}))
                    review.goto(BASE+dest);review.wait_for_timeout(100)
                    if lang=='ne':review.locator('[data-review-lang=ne]').click()
                    assert review.locator('label').count()>5,dest
                    assert review.locator('input:not(:disabled),select:not(:disabled),textarea:not(:disabled)').count()==0
                    assert review.locator('#org option').count()>1,dest
                    assert review.locator('select option').count()>10,dest
                    assert review.evaluate('document.documentElement.scrollWidth<=innerWidth'),('review overflow',dest,width,lang)
                    assert review.locator('body').inner_text().find('not collecting')>=0
                    assert review.locator('select').count()==review.locator('.review-options').count()
                    review.locator('.review-options summary').first.click()
                    assert review.locator('.review-options[open] li').count()>0
                    review.locator('.review-options summary').first.click()
                    # Re-enable adversarially; native and scripted submit are both fenced.
                    review.evaluate("document.querySelectorAll('input').forEach(i=>{i.disabled=false;i.value='SYNTHETIC-NOT-SAVED'}); document.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})); document.querySelector('form').submit();")
                    review.locator('input').first.press('Enter');review.wait_for_timeout(50)
                    assert review.evaluate('sideEffects')==[],(dest,review.evaluate('sideEffects'))
                    assert all(r['method']=='GET' for r in requests),requests
                    assert not any(any(x in r['url'] for x in ['fb.js','l1.js','pwa.js','firestore','firebase','preview-mode']) for r in requests),requests
                    assert review_errors==[],review_errors
                    review.reload()
                    if lang=='ne': review.locator('[data-review-lang=ne]').click()
                    assert review.evaluate('sideEffects')==[]
                    review.evaluate('window.scrollTo(0,0)')
                    review.screenshot(path=str(OUT/f'{Path(dest).stem}-{width}-{lang}.png'),full_page=True)
                    results.append({'destination':dest,'width':width,'language':lang,'labels':review.locator('label').count(),'side_effects':review.evaluate('sideEffects'),'requests':requests})
                    review.close()
            # The read-only path must be error-free; report unchanged root dependencies separately.
            results.append({'width':width,'language':lang,'root_page_errors':errors,'http_errors':bad})
            context.close()
    browser.close()
server.shutdown()
(OUT/'browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'checks':len(results),'directory_variants':6,'destinations':8,'evidence':str(OUT),'root_issues':[r for r in results if r.get('root_page_errors') or r.get('http_errors')]},indent=2))

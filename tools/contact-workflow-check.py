#!/usr/bin/env python3
"""Contact preview usability regression: genuine DOM, never real records."""
import http.server, threading, os, json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
HUB=Path(os.environ.get('MHPSS_HUB',str(ROOT.parent.parent/'directory-hotfix/hub')))
OUT=ROOT.parent
class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=path.split('?')[0]
        return str((HUB/path[5:]) if path.startswith('/hub/') else ROOT/(path[6:] or 'index.html'))
    def log_message(self,format,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
BASE=os.environ.get('MHPSS_BASE',f'http://127.0.0.1:{server.server_port}/form/')
results=[]
with sync_playwright() as pw:
    for engine in os.environ.get('ENGINES','chromium,webkit').split(','):
        browser=getattr(pw,engine).launch()
        for width in [390,1280]:
            for lang in ['en','ne']:
                context=browser.new_context(viewport={'width':width,'height':900},service_workers='block')
                context.route('https://fonts.googleapis.com/**',lambda r:r.fulfill(body=''))
                context.route('https://fonts.gstatic.com/**',lambda r:r.abort())
                page=context.new_page(); errors=[]; requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:requests.append((r.method,r.url)))
                page.goto(BASE+'review/contact.html?lang='+lang)
                form=page.frame_locator('#contact-frame') if page.locator('#contact-frame').count() else page
                assert form.locator('#org').is_enabled(),'ROOT CAUSE: all source fields disabled'
                form.locator('#org').select_option('OTHER')
                form.locator('#orgOther').fill('SYNTHETIC PREVIEW')
                form.locator('#outcome').select_option('REFER')
                assert form.locator('#refCard').is_visible(),'Referral conditional must open'
                form.locator('#reason').select_option('OTH')
                assert form.locator('a[href="../index.html"]').count()>0,'Forms navigation stripped'
                assert page.locator('#followup-tab').count()==1,'One workflow needs a follow-up action'
                page.locator('#followup-tab').click()
                follow=page.frame_locator('#followup-frame')
                follow.locator('#arrived').select_option('Y')
                page.locator('#contact-tab').click()
                assert form.locator('#orgOther').input_value()=='SYNTHETIC PREVIEW'
                form.locator('[data-review-reset]').click()
                assert form.locator('#orgOther').input_value()==''
                assert form.locator('#refCard').is_hidden()
                assert form.locator('button[type=submit]').is_disabled()
                assert form.locator('#geoBtn').is_disabled()
                form.locator('.top a[href="../index.html"]').click()
                assert page.url.split('?')[0]==BASE+'index.html'
                assert page.locator('.ml-card').count()==7
                page.locator('[data-directory-kind=contacts] .ml-actions a').click()
                assert page.locator('#contact-frame').count()==1
                page.locator('.workflow-nav a[href="../../hub/"]').click()
                assert '/hub/' in page.url
                assert all(m=='GET' for m,u in requests)
                assert not any('/review/' in u and any(x in u for x in ['l1.js','fb.js']) for m,u in requests)
                assert errors==[], errors
                results.append({'engine':engine,'version':browser.version,'width':width,'language':lang,'pass':True,'errors':errors})
                context.close()
        browser.close()
server.shutdown()
(OUT/'browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))

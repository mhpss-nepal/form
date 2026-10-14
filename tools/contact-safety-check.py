#!/usr/bin/env python3
"""Privacy, QR parity, eight-instrument walk and installed-v48 upgrade."""
import runpy,os,threading,http.server,json,subprocess,re,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent; HUB=ROOT.parent/'hub'; old=False
class Handler(http.server.SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=path.split('?')[0]; return str((HUB/path[5:]) if path.startswith('/hub/') else ROOT/(path[6:] or 'index.html'))
 def do_GET(self):
  if old and self.path.split('?')[0] in ['/form/sw.js','/form/index.html','/form/template-review.js','/form/lib/directory-status-20261013.js']:
   data=subprocess.check_output(['git','show','36e104c:'+self.path.split('?')[0][6:]],cwd=ROOT)
   self.send_response(200);self.send_header('Content-Type','application/javascript' if '.js' in self.path else 'text/html');self.end_headers();self.wfile.write(data)
  else:super().do_GET()
 def log_message(self,format,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/form/'
probe="""window.effects=[];for(const m of ['setItem','removeItem','clear'])Storage.prototype[m]=function(){effects.push(m);throw Error(m)};for(const m of ['open','deleteDatabase'])indexedDB[m]=function(){effects.push(m);throw Error(m)};window.fetch=function(){effects.push('fetch');throw Error('fetch')};XMLHttpRequest.prototype.open=function(){effects.push('xhr');throw Error('xhr')};navigator.sendBeacon=function(){effects.push('beacon');return false};navigator.geolocation.getCurrentPosition=function(){effects.push('geo')};"""
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch();ctx=b.new_context(service_workers='block');ctx.route('https://**',lambda r:r.abort());p=ctx.new_page()
 for lang in ['en','ne']:
  p.goto(BASE+'?lang='+lang); cards=p.locator('.ml-card');assert cards.count()==7
  routes=[]
  for i in range(7):
   c=cards.nth(i);dest=c.locator('.ml-actions a').get_attribute('href');routes.append(dest);c.locator('[data-qr]').click();assert c.locator('.directory-qr-url').inner_text()=='https://mhpss-nepal.github.io/form/'+dest;c.locator('[data-qr]').click()
  assert len(set(routes))==7
  for dest in routes:
   p.goto(BASE+dest); assert p.locator('input,select,iframe').count()>0,dest
  results.append({'language':lang,'workflows':7,'instruments':8,'routes':routes,'QR_text':True})
 for dest in ['review/contact-instrument.html','review/referral-outcome.html','drafts/contact.html','drafts/referral-outcome.html','contact.html','referral-outcome.html']:
  q=ctx.new_page();q.add_init_script(probe);errors=[];req=[];q.on('pageerror',lambda e:errors.append(str(e)));q.on('request',lambda r:req.append((r.method,r.url)));q.goto(BASE+dest)
  frame=q.frame_locator('#contact-frame') if q.locator('#contact-frame').count() else q
  frame.locator('#org').select_option('OTHER');frame.locator('input[type=text]').first.fill('SYNTHETIC')
  frame.locator('form').evaluate("f=>{f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));f.submit();f.requestSubmit()}")
  for f in q.frames: assert f.evaluate('effects')==[]
  assert errors==[],errors;assert all(m=='GET' for m,u in req);assert not any(re.search(r'/(l1|fb|store|pwa)\.js|firebase|firestore',u) for m,u in req)
  results.append({'safe_route':dest,'effects':[],'writer_requests':0});q.close()
 ctx.close()
 ctx=b.new_context(service_workers='allow');ctx.route('https://**',lambda r:r.abort());p=ctx.new_page();old=True;p.goto(BASE)
 p.evaluate("localStorage.setItem('legacy-pending','UNCHANGED');new Promise((resolve,reject)=>{let r=indexedDB.open('legacy-sentinel',1);r.onupgradeneeded=()=>r.result.createObjectStore('pending');r.onsuccess=()=>{let t=r.result.transaction('pending','readwrite');t.objectStore('pending').put('UNCHANGED','report');t.oncomplete=resolve}})")
 p.evaluate("navigator.serviceWorker.register('sw.js').then(()=>navigator.serviceWorker.ready)");p.reload();p.wait_for_function('navigator.serviceWorker.controller')
 assert 'v48' in p.evaluate('caches.keys()')[0];old=False
 p.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())');p.wait_for_function("caches.keys().then(k=>k.includes('mhpss-np-field-v49'))")
 p.goto(BASE+'review/contact.html');p.frame_locator('#contact-frame').locator('#outcome').select_option('REFER');assert p.frame_locator('#contact-frame').locator('#refCard').is_visible()
 assert p.evaluate("localStorage.getItem('legacy-pending')")=='UNCHANGED'
 assert p.evaluate("new Promise(resolve=>{let r=indexedDB.open('legacy-sentinel');r.onsuccess=()=>{let g=r.result.transaction('pending').objectStore('pending').get('report');g.onsuccess=()=>resolve(g.result)}})")=='UNCHANGED'
 p.goto(BASE+'index.html');p.go_back();assert p.frame_locator('#contact-frame').locator('#org').is_enabled()
 results.append({'installed_upgrade':'v48 -> v49','localStorage':'unchanged','IDB':'unchanged','back_forward':'editable'});b.close()
server.shutdown();(ROOT.parent/'safety-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))

#!/usr/bin/env python3
"""Finite current-producer loopback PWA replay. Synthetic Auth, NOT SDK/delivery proof.
Run with a compatible Playwright Python: --output DIR [--red]. No remote requests.
Old Form is read from git objects; candidate is this checkout, never another writer.
"""
import argparse, hashlib, json, mimetypes, re, subprocess, threading, time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
BASE = '39cc79098af566b88e15366d141cad09bf25be20'
HUB_PIN = '0429103dc93707101702ce019508a6303ccd7348'
HUB_REPO = ROOT.parents[1] / 'continuation-20261013/hub'
HUB = ROOT.parent / 'hub'
OLD = 'mhpss-np-field-v49'
NEW = 'mhpss-np-field-v50'
UID = 'SYNTHETIC_PWA_ONLY'
AUTH = """/* SYNTHETIC Auth facade: no SDK, credentials or backend proof. */
window.__syntheticUser={uid:'SYNTHETIC_PWA_ONLY',emailVerified:true};
window.BaselineAuth={currentUser:()=>window.__syntheticUser,onChange:f=>{window.__authListener=f;f(window.__syntheticUser,{ready:true,error:''});},token:async()=>{throw Error('SYNTHETIC credential-independent refusal');}};
"""
CONTROL = """()=>({controls:[...document.querySelectorAll('#f input[id],#f select[id],#f textarea[id]')].map(e=>({id:e.id,value:e.value,checked:e.checked})),open:[...document.querySelectorAll('#actGrid details')].filter(e=>e.open).map(e=>e.id)})"""
def digest(b): return hashlib.sha256(b).hexdigest()
def git(path, *args): return subprocess.check_output(['git','-C',str(path),*args])
def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    state={'version':'old','fault':'','requests':[]}
    old_sw=git(ROOT,'show',BASE+':sw.js')
    # RED uses the exact baseline implementation with only a test cache-name bump
    # to make the otherwise byte-identical worker eligible for an upgrade.
    candidate_sw=(ROOT/'sw.js').read_bytes()
    if args.red: candidate_sw=candidate_sw.replace(OLD.encode(),NEW.encode())
    sw_assets=re.findall(r'"([^"]+)"',re.search(r'const PRECACHE = \[(.*?)\];',candidate_sw.decode(),re.S).group(1))
    pair={}
    for entry in sw_assets:
        if entry.startswith('../hub/'):
            rel=entry[len('../hub/'):]; expected=git(HUB_REPO,'show',HUB_PIN+':'+rel)
            assert (HUB/rel).read_bytes()==expected, 'paired Hub archive differs: '+rel
            pair[rel]=digest(expected)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def do_GET(self):
            path=self.path.split('?')[0]; rel=path.lstrip('/'); rel += 'index.html' if path.endswith('/') else ''
            version,fault=state['version'],state['fault']; status=200
            try:
                if rel=='form/sw.js': body=old_sw if version=='old' else candidate_sw
                elif rel.startswith('form/'):
                    name=rel[5:]; body=git(ROOT,'show',BASE+':'+name) if version=='old' else (ROOT/name).read_bytes()
                elif rel.startswith('hub/'): body=(HUB/rel[4:]).read_bytes()
                else: raise FileNotFoundError()
                if rel=='hub/review-current-v51/current-auth.js': body=(AUTH.replace("{uid:'SYNTHETIC_PWA_ONLY',emailVerified:true}", 'null') if state.get('signedout') else AUTH).encode()
                if version=='candidate' and ((fault=='helper' and rel=='form/lib/activity-form.js') or (fault=='worker' and rel=='form/sw.js')): status=503; body=b'SYNTHETIC 503'
                if version=='candidate' and rel=='form/lib/activity-form.js' and fault in ('partial','throwing'):
                    body=("window.ActivityForm={submit:()=>{window.__partialCalled=true}};" if fault=='partial' else "throw Error('SYNTHETIC module initialization failure');").encode()
            except (FileNotFoundError,subprocess.CalledProcessError): status=404; body=b'not found'
            state['requests'].append({'path':path,'version':version,'fault':fault,'status':status})
            self.send_response(status); self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream'); self.send_header('Cache-Control','no-store'); self.end_headers()
            try: self.wfile.write(body)
            except (BrokenPipeError,ConnectionResetError): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    url=f'http://127.0.0.1:{server.server_port}'
    results=[]
    def storage(p): return p.evaluate('()=>Object.fromEntries(Object.entries(localStorage))')
    def fill(p):
        p.evaluate("""()=>{for(const id of ['org','district','site','modality']){const e=document.getElementById(id); const o=[...e.options].find(o=>o.value&&!['OTHER','OTH','PALIKA'].includes(o.value));if(o){e.value=o.value;e.dispatchEvent(new Event('change',{bubbles:true}));}}document.querySelector('#actGrid details').open=true;const n=document.querySelector('#actGrid details input[type=number]');n.value='3';n.dispatchEvent(new Event('input',{bubbles:true}));const t=document.querySelector('#actGrid details input[type=text],#actGrid details textarea');if(t){t.value='SYNTHETIC activity detail';t.dispatchEvent(new Event('input',{bubbles:true}));}document.querySelector('#tgs input').checked=true;document.querySelector('#description').value='SYNTHETIC unsent editor';document.querySelector('#description').dispatchEvent(new Event('input',{bubbles:true}));ActivityForm.saveDraft();}""")
    def seed(p):
        p.evaluate("""async()=>{const payload={kind:'activity',schema:'mhpss-np-5ws/5ws-np-0.10.0',description:'SYNTHETIC pending'};await ActivityForm.api.enqueue(payload);ActivityForm.saveDraft();localStorage.setItem('pwa-foreign-synthetic','retain');for(const name of ['mhpss-hub-synthetic','foreign-synthetic']){const c=await caches.open(name);await c.put('/sentinel',new Response('SYNTHETIC retained'));}await new Promise((resolve,reject)=>{const r=indexedDB.open('pwa-synthetic',1);r.onupgradeneeded=()=>r.result.createObjectStore('sentinel');r.onsuccess=()=>{const db=r.result,t=db.transaction('sentinel','readwrite');t.objectStore('sentinel').put('SYNTHETIC retained','key');t.oncomplete=()=>{db.close();resolve();};t.onerror=reject;};});}""")
    def intact(p, before):
        assert storage(p)==before,'persistent device/draft/outbox/event bytes changed'
        assert p.evaluate("""async()=>{return await new Promise((resolve,reject)=>{const r=indexedDB.open('pwa-synthetic',1);r.onsuccess=()=>{const db=r.result,t=db.transaction('sentinel');const q=t.objectStore('sentinel').get('key');q.onsuccess=()=>{resolve(q.result==='SYNTHETIC retained');db.close();};q.onerror=reject;};});}"""), 'IDB changed'
    def restore(p, controls, before):
        p.reload(wait_until='load');p.wait_for_timeout(400)
        # v49 cache-first JS may serve the previous helper once while its real
        # network revalidation completes. No cache/storage clearing workaround.
        if not p.evaluate('!!window.ActivityForm?.saveDraft && (!window.ActivityDelivery || window.ActivityDelivery.ready())'):
            p.reload(wait_until='load');p.wait_for_timeout(400)
        p.wait_for_function('!!window.ActivityForm?.saveDraft && (!window.ActivityDelivery || window.ActivityDelivery.ready())');p.locator('#activityRestore').press('Enter');p.wait_for_timeout(100)
        actual=p.evaluate(CONTROL)
        assert actual==controls,'manual draft restore mismatch: '+json.dumps({'changed':[(x,y) for x,y in zip(controls['controls'],actual['controls']) if x!=y],'open':[controls['open'],actual['open']]})
        assert 'Draft restored' in p.locator('#activityStatus').inner_text();intact(p,before)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for mode in ('helper','worker','normal','partial','throwing'):
                row={'mode':mode};results.append(row);ctx=None
                try:
                    state.update(version='old',fault='');ctx=browser.new_context(service_workers='allow')
                    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(url+'/') else r.abort())
                    a=ctx.new_page(); errors=[];a.on('pageerror',lambda e:errors.append(str(e)))
                    a.goto(url+'/form/5ws-report.html');a.wait_for_function('!!navigator.serviceWorker.controller');a.wait_for_function('!!window.ActivityForm?.saveDraft')
                    b=ctx.new_page();b.goto(url+'/form/5ws-report.html');b.wait_for_function('!!navigator.serviceWorker.controller')
                    fill(a);seed(a);controls=a.evaluate(CONTROL);before=storage(a)
                    b.locator('#description').fill('SYNTHETIC second tab');a.evaluate('ActivityForm.saveDraft()');before=storage(a)
                    for p in (a,b): p.evaluate('window.__changes=0;navigator.serviceWorker.addEventListener("controllerchange",()=>window.__changes++)')
                    state.update(version='candidate',fault=mode if mode!='normal' else '')
                    a.evaluate('fetch(location.href,{headers:{Accept:"text/html"}}).then(r=>r.text())')
                    a.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration();window.__states=[];r.addEventListener('updatefound',()=>{const w=r.installing;w.addEventListener('statechange',()=>window.__states.push(w.state));});}""")
                    row['update']=a.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update()).then(()=>"updated").catch(()=>"rejected")')
                    if mode!='worker': a.wait_for_function('window.__states.includes("activated")||window.__states.includes("redundant")',timeout=20000)
                    a.wait_for_timeout(250);row['states']=a.evaluate('window.__states');keys=a.evaluate('caches.keys()');row['caches']=keys
                    assert a.locator('#description').input_value()=='SYNTHETIC unsent editor' and b.locator('#description').input_value()=='SYNTHETIC second tab','open editor changed'
                    intact(a,before)
                    if args.red_readiness:
                        pass  # Separate baseline readiness assertion, not atomic acceptance.
                    elif mode in ('helper','worker'):
                        assert OLD in keys and NEW not in keys and a.evaluate('__changes')==0 and b.evaluate('__changes')==0,'required install failure activated/claimed/deleted predecessor'
                    else:
                        assert NEW in keys and OLD not in keys,'candidate not active'
                        assert all(n in keys for n in ['mhpss-hub-synthetic','foreign-synthetic']),'foreign caches deleted'
                    row['atomic_and_owned_cache_check']=True
                    if mode in ('helper','partial','throwing'):
                        # Evict only helper to reproduce new HTML cached by an old controller
                        # without required new JS. Browser cache cleared, remote blocked.
                        a.evaluate("""async()=>{for(const n of await caches.keys()){const c=await caches.open(n);await c.delete('/form/lib/activity-form.js');}}""")
                        ctx.new_cdp_session(a).send('Network.clearBrowserCache')
                        if mode=='helper': ctx.set_offline(True)
                        a.reload(wait_until='load');a.wait_for_timeout(200)
                        a.locator('#description').fill('SYNTHETIC refusal editor');saved=storage(a);editor=a.evaluate(CONTROL)
                        assert a.locator('button[type=submit][form=f]').is_disabled() and a.locator('#activityRetry').is_disabled(),'missing/partial module leaves actions enabled'
                        a.locator('#focalName').press('Enter')
                        refused=a.evaluate("""()=>{let saves=0;const old=STORE.save;STORE.save=(...a)=>{saves++;return old(...a)};const allowed=document.querySelector('#f').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));document.querySelector('#activityRetry').dispatchEvent(new MouseEvent('click',{bubbles:true}));document.querySelector('#reset').click();document.querySelector('#f').submit();STORE.save=old;return {saves,allowed,partial:!!window.__partialCalled};}""")
                        assert refused=={'saves':0,'allowed':False,'partial':False},'forced handler bypass'
                        assert 'unavailable' in a.locator('#activityStatus').inner_text().lower();assert a.evaluate(CONTROL)==editor;intact(a,saved);row['controlled_refusal']=True
                        ctx.set_offline(False)
                    state.update(version='candidate',fault='')
                    a.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())')
                    a.wait_for_function('async()=> (await caches.keys()).includes("mhpss-np-field-v50")',timeout=20000)
                    restore(a,controls,before);row['reconnect_manual_restore_exact']=True
                    # Keyboard activation of the actual Retry handler; synthetic token refusal,
                    # never an ACK or genuine authenticated delivery claim.
                    a.locator('#activityRetry').press('Enter');a.wait_for_function('document.querySelector("#activityStatus").textContent.includes("SYNTHETIC credential-independent refusal")');intact(a,before);assert a.evaluate(CONTROL)==controls
                    row['keyboard_retry_original_queue_retained']=True
                    ctx.new_cdp_session(a).send('Network.clearBrowserCache');ctx.set_offline(True);restore(a,controls,before);row['offline_restore']=True;ctx.set_offline(False)
                    state.update(version='old',fault='')
                    a.evaluate('navigator.serviceWorker.getRegistration().then(r=>r.update())');a.wait_for_function('async()=> (await caches.keys()).includes("mhpss-np-field-v49")&&!(await caches.keys()).includes("mhpss-np-field-v50")',timeout=20000)
                    restore(a,controls,before);ctx.new_cdp_session(a).send('Network.clearBrowserCache');ctx.set_offline(True);restore(a,controls,before);intact(b,before)
                    row.update(exact_v49_rollback=True,persistent_sha256=digest(json.dumps(before,sort_keys=True).encode()),control_count=len(controls['controls']),open_details=len(controls['open']),passed=True,page_errors=errors)
                except Exception as e: row.update(passed=False,error=str(e),error_type=type(e).__name__)
                finally:
                    if ctx:ctx.close()
            state.update(version='candidate',fault='',signedout=True)
            ctx=browser.new_context(service_workers='allow');ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(url+'/') else r.abort())
            row={'mode':'signed-out-device-save'};results.append(row)
            try:
                p=ctx.new_page();p.goto(url+'/form/5ws-report.html');p.wait_for_function('!!window.ActivityForm?.saveDraft');fill(p)
                p.evaluate("""()=>{window.__syntheticUser=null;window.__authListener(null,{ready:true,error:''});for(const [id,value]of Object.entries({focalName:'SYNTHETIC TEST',focalPhone:'0000000000',site:'OTHER',siteOther:'SYNTHETIC test site',dateAD:'2026-10-01',reachedTotal:'3',newToday:'3',reportingRole:'LEAD'})){const e=document.getElementById(id);e.value=value;e.dispatchEvent(new Event('change',{bubbles:true}));}}""")
                problems=p.evaluate('STORE.validate(ActivityCollector.collect())');assert not problems,problems
                before_controls=p.evaluate(CONTROL);assert not p.locator('button[type=submit][form=f]').is_disabled()
                p.evaluate("document.querySelector('#f').requestSubmit()")
                p.wait_for_function('document.querySelector("#activityStatus").textContent.includes("Device saved only")')
                assert len(json.loads(p.evaluate('localStorage.getItem("mhpss-np-4ws-v1")')))==1
                assert p.evaluate(CONTROL)==before_controls
                assert p.evaluate('Object.keys(localStorage).every(k=>!k.startsWith("mhpss-activity-outbox-v1:"))')
                row.update(passed=True,actual_submit_device_only=True,no_account_outbox=True)
            except Exception as e:row.update(passed=False,error=str(e),error_type=type(e).__name__)
            finally:ctx.close()
            browser_version=browser.version;browser.close()
    finally: server.shutdown();server.server_close();thread.join(3)
    for mode,path in [('helper','/form/lib/activity-form.js'),('worker','/form/sw.js')]:
        hits=[r for r in state['requests'] if r['fault']==mode and r['path']==path and r['status']==503]
        assert hits, 'real HTTP fault was not reached: '+mode
    result={'baseline':BASE,'hub':HUB_PIN,'browser':browser_version,'synthetic_auth_only':True,'genuine_sdk_or_delivery_proof':False,'red_test_only_cache_bump':args.red,'pair_sha256':pair,'results':results,'requests':state['requests'],'passed':all(r.get('passed') for r in results)}
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('requests','pair_sha256')},indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--red',action='store_true');p.add_argument('--red-readiness',action='store_true');raise SystemExit(run(p.parse_args()))

"""Exercise exact candidate UI/native submit via genuine demo SDK/Auth/Firestore."""
from pathlib import Path
from urllib.parse import urlparse
import sys,json,hashlib,csv,io,time,urllib.request,urllib.error,os
from playwright.sync_api import sync_playwright
R=Path('/root/mhpss-nepal-final-forms/2026-10-06/43-backend-completion/cache/emulator');origin=sys.argv[1];E=Path(sys.argv[2]);checks=[]
BUILD=R.parent/'form/review-5ws-admin-test-v35/releases/native-test-20261009'
def check(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
 (E/'progress.json').write_text(json.dumps(checks,indent=2)+'\n')
def queued(p,n):
 end=time.monotonic()+50
 while time.monotonic()<end:
  q=p.evaluate('()=>SESSION_QUEUE.all()')
  if len(q)==n and q[-1]['state']=='remotely_acknowledged':return
  p.wait_for_timeout(100)
 raise AssertionError('Queue acknowledgement timed out: '+p.locator('#status').inner_text())
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/root/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless=True,args=['--no-sandbox','--disable-background-networking','--proxy-server=http://127.0.0.1:1','--proxy-bypass-list=127.0.0.1','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'])
 c=b.new_context(accept_downloads=True,service_workers="allow");blocked=[];errors=[];requests=[];held=[];holdRead=False;holdIntake=False;heldIntake=[];holdCurrent=False;heldCurrent=[]
 def route(r):
  u=urlparse(r.request.url)
  if holdRead and u.path=='/admin/test/report':held.append(r);return
  if holdIntake and u.path=='/admin/test/intake':heldIntake.append(r);return

  if r.request.url.startswith('https://mhpss5ws-tdp3xtfnsq-as.a.run.app/admin/test/'):
   if not p.evaluate('()=>navigator.onLine'):r.abort('internetdisconnected');return
   requests.append(u.path)
   headers={k:v for k,v in r.request.headers.items() if k.lower() not in ['host','origin','referer','content-length']};headers['Origin']=origin
   if r.request.method=='OPTIONS':
    r.fulfill(status=204,headers={'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'GET,POST','Access-Control-Allow-Headers':'authorization,content-type,x-test-basis,x-session-id,x-retry-token,x-listing-cursor'});return
   req=urllib.request.Request(origin+u.path,data=r.request.post_data_buffer,headers=headers,method=r.request.method)
   try:res=urllib.request.urlopen(req,timeout=40)
   except urllib.error.HTTPError as e:res=e
   with res:
    status=res.status;body=res.read();headers={'Content-Type':'application/json','Access-Control-Allow-Origin':origin}
   if holdCurrent and u.path=='/admin/test/current' and json.loads(body).get('nextCursor') is None:heldCurrent.append((r,status,body,headers));return
   r.fulfill(status=status,body=body,headers=headers)
  elif u.scheme+'://'+u.netloc!=origin:blocked.append(r.request.url);r.abort()
  elif u.path=='/fb-config.js':r.continue_()
  else:r.continue_()
 c.add_init_script("Object.defineProperty(window,'FB_CONFIG',{get:()=>({apiKey:'emulator-only',authDomain:location.host,projectId:'demo-mhpss-admin-test',appId:'demo-mhpss'}),set:()=>{},configurable:true});");c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  def waitready(page):page.wait_for_function('()=>FB?.status().ready===true&&document.getElementById("form").contentWindow.INTEGRATION_REVIEW')
  def signin(page):
   page.evaluate("async()=>{const m=await import('./sdk/firebase-auth.js');try{m.connectAuthEmulator(FB.webAuth(),location.origin,{disableWarnings:true});}catch(e){}const secret=(await(await fetch('/signin',{method:'POST'})).json()).fixturePassword;await m.signInWithEmailAndPassword(FB.webAuth(),'adib.asrori@who.int',secret);}")
   page.wait_for_function('()=>FB.webAuth().currentUser?.emailVerified===true')
  def controls(page):return page.frames[1].evaluate("()=>Array.from(document.querySelectorAll('input,select,textarea')).map(e=>({id:e.id,value:e.value,checked:e.checked}))")
  def snap():return p.evaluate('()=>SESSION_QUEUE.snapshot()')
  def submit(page):
   page.frames[1].locator('#f').evaluate('(el)=>el.requestSubmit()')
  def settled(page):page.wait_for_function("()=>/TEST exact receipt revision|TEST pending;/.test(document.getElementById('status').textContent)")
  url=origin+'/form/review-5ws-admin-test-v35/releases/native-test-20261009/review.html'
  c.unroute('**/*',route)
  p.goto(origin+'/form/controller-fixture.html')
  (E/'stage.json').write_text(json.dumps({'stage':'register old controller','url':p.url}))
  p.evaluate("async()=>Promise.race([(async()=>{await navigator.serviceWorker.register('/form/sw.js');await navigator.serviceWorker.ready;})(),new Promise((_,reject)=>setTimeout(()=>reject(Error('Old controller registration timed out')),60000))])")
  (E/'stage.json').write_text(json.dumps({'stage':'registered old controller','url':p.url}))
  p.wait_for_function('()=>navigator.serviceWorker.controller!==null')
  c.route('**/*',route)
  p.goto(url);waitready(p)
  check('unchanged served v43 controller owns old entry',p.evaluate('()=>navigator.serviceWorker.controller?.scriptURL.endsWith("/form/sw.js")'))
  signin(p);p.frames[1].locator('#syntheticExample').click();submit(p);queued(p,1);first=snap()['envelopes'][0]
  tab2=c.new_page();tab2.on('pageerror',lambda e:errors.append(str(e)));tab2.goto(url);waitready(tab2);signin(tab2);tab2.frames[1].locator('#syntheticExample').click();submit(tab2);queued(tab2,2);second=snap()['envelopes'][1]
  check('two genuine initial receipts distinct identities',first['session']!=second['session'] and first['ack']['revision']==second['ack']['revision']==1)
  # Deliberately reopen after the other tab advanced shared durable generation.
  p.evaluate('id=>ADMIN_TEST_UI.open(id)',first['session']);c.set_offline(True);p.frames[1].locator('#sessionTime').fill('18:11');submit(p);settled(p)
  check('first correction durably queued offline',snap()['envelopes'][-1]['state']=='durably_queued')
  c.set_offline(False);tab2.evaluate('id=>ADMIN_TEST_UI.open(id)',second['session']);c.set_offline(True);tab2.frames[1].locator('#sessionTime').fill('18:12');submit(tab2);settled(tab2)
  before=snap();pending=before['envelopes'][-2:]
  check('two corrections exact genuine predecessors',all(json.loads(i['body'])['predecessor']=={k:initial['ack'][k] for k in ['event_id','revision','request_sha256']} for i,initial in zip(pending,[first,second])))
  check('two tabs same durable queue before reload',tab2.evaluate('()=>SESSION_QUEUE.snapshot()')==before)
  # Exercise actual old-editor defect once, then additive new-release transition.
  old_diag=p.frames[1].evaluate("r=>{const a=document.getElementById('backdateAck');a.checked=false;return INTEGRATION_REVIEW.check(r);}",json.loads(pending[0]['body'])['payload'])
  check('old main native validator reproduces RC01 by identity','Confirm date and place for back-dated report' in old_diag)
  c.set_offline(False)
  newurl=url.replace('native-test-20261009','native-test-rc01-20261011')
  p.goto(newurl);tab2.goto(newurl);waitready(p);waitready(tab2)
  check('additive new release keeps exact old-entry pending bytes in both tabs',snap()==before and tab2.evaluate('()=>SESSION_QUEUE.snapshot()')==before)
  check('new release does not replace old v43 controller',p.evaluate('()=>navigator.serviceWorker.controller?.scriptURL.endsWith("/form/sw.js")'))
  # Allow unchanged old controller's cache puts to settle; no cache deletion or worker upgrade.
  p.wait_for_timeout(1500)
  c.set_offline(True)
  cd=c.new_cdp_session(p);cd.send('Network.clearBrowserCache');cd.send('ServiceWorker.enable');cd.send('ServiceWorker.stopAllWorkers');p.reload(wait_until='domcontentloaded');tab2.reload(wait_until='domcontentloaded');waitready(p);waitready(tab2)
  check('offline worker stop wake two tab queue exact',snap()==before and tab2.evaluate('()=>SESSION_QUEUE.snapshot()')==before)
  check('offline reload no auth entitlement',p.evaluate('()=>FB.webAuth().currentUser===null') and tab2.evaluate('()=>FB.webAuth().currentUser===null'))
  payload=json.loads(pending[0]['body'])['payload']
  diagnostic=p.frames[1].evaluate("r=>{const a=document.getElementById('backdateAck');const before=a.checked;const off=INTEGRATION_REVIEW.check(r);a.checked=true;const on=INTEGRATION_REVIEW.check(r);a.checked=before;return {checkbox:before,persisted:r.backdateAcknowledged,off,on};}",payload)
  (E/'validation-seam.json').write_text(json.dumps({'diagnostic':diagnostic,'before':before,'after':snap(),'checks':checks},indent=2)+'\n')
  check('RC01 valid persisted correction independent of empty reload editor',diagnostic['persisted'] is True and diagnostic['checkbox'] is False and diagnostic['off']==diagnostic['on']==[])
  for v in [False,None,'true',1]:
   result=p.frames[1].evaluate('r=>INTEGRATION_REVIEW.check(r)',{**payload,'backdateAcknowledged':v})
   check('typed persisted backdate refusal '+repr(v),bool(result))
  omitted={k:v for k,v in payload.items() if k!='backdateAcknowledged'}
  check('missing persisted backdate refusal',bool(p.frames[1].evaluate('r=>INTEGRATION_REVIEW.check(r)',omitted)))
  signedout=p.evaluate("async()=>{try{await ADMIN_TEST_UI.flush();return false}catch(e){return true}}")
  check('signed out flush denied with exact queue',signedout and snap()==before)
  c.set_offline(False);signin(p);signin(tab2)
  # Plant unsaved raw fields in both fresh editors without prefilling the queued report.
  p.frames[1].locator('#description').fill('UNSENT synthetic tab one');tab2.frames[1].locator('#description').fill('UNSENT synthetic tab two')
  raw1=controls(p);raw2=controls(tab2);n=len(requests)
  p.locator('#flush').click();p.wait_for_function('()=>document.getElementById("status").textContent.includes("TEST device authority: no_pending_requests; pending 0")',timeout=50000)
  after=snap();items=after['envelopes']
  (E/'retry-result.json').write_text(json.dumps({'requests_before':n,'requests':requests,'before':before,'after':after,'status':p.locator('#status').inner_text()},indent=2)+'\n')
  check('actual Retry button dispatches both exact queued corrections',len(requests)-n==2 and all(i['state']=='remotely_acknowledged' for i in items))
  check('initial receipts unchanged',items[:2]==[first,second])
  for old,new in zip(pending,items[-2:]):
   check('exact durable identity body predecessor retained '+old['session'],{k:v for k,v in old.items() if k not in ['state','ack']}=={k:v for k,v in new.items() if k not in ['state','ack']} and new['ack']['revision']==2 and new['ack']['request_sha256']==hashlib.sha256(old['body'].encode()).hexdigest() and new['ack']['event_id']!=json.loads(old['body'])['predecessor']['event_id'])
  check('retry preserves both unsaved editor controls',controls(p)==raw1 and controls(tab2)==raw2)
  check('two tabs converge same acknowledged queue',tab2.evaluate('()=>SESSION_QUEUE.snapshot()')==after)
  exact=tab2.evaluate('token=>ADMIN_TEST_UI.retry(token)',pending[0]['token'])
  check('second tab exact correction retry identical committed receipt',exact==items[-2]['ack'] and controls(p)==raw1 and controls(tab2)==raw2)
  for i in items[-2:]:
   row=p.evaluate('id=>ADMIN_TEST_TRANSPORT.create(FB.webAuth()).read(id)',i['session'])
   check('actual backend readback revision2 body '+i['session'],row['revision']==2 and row['payload']==json.loads(i['body'])['payload'] and row['request_sha256']==i['sha256'])
  negative=p.evaluate("async item=>{try{await ADMIN_TEST_UI.submit({...JSON.parse(item.body).payload,siteOther:'not approved'});return false}catch(e){return true}}",pending[0])
  check('synthetic guard still refuses changed venue',negative and controls(p)==raw1)
  # Same validator remains on the actual native Submit path: no acknowledgment, no dispatch.
  p.frames[1].locator('#syntheticExample').click();p.frames[1].locator('#backdateAck').uncheck();negativeBefore=snap();negativeRequests=len(requests);submit(p)
  check('native unchecked backdate Submit refused without enqueue or transport','Confirm date and place' in p.frames[1].locator('#problems').inner_text() and snap()==negativeBefore and len(requests)==negativeRequests)
  check('no browser errors',not errors);check('no external request',not blocked)
  # Independent adversarial probes: validly digested queued false versus checked editor.
  p.frames[1].locator('#backdateAck').check()
  adversarial=[]
  for value in [False,None,'true',1,{},[]]:
   got=p.frames[1].evaluate('r=>INTEGRATION_REVIEW.check(r)',{**payload,'backdateAcknowledged':value})
   check('independent livechecked typed refusal '+repr(value),'Confirm date and place for back-dated report' in got)
   adversarial.append({'persisted':value,'live':True,'errors':got})
  invalid_payload={**payload,'backdateAcknowledged':False}
  invalid_item=p.evaluate("async payload=>SESSION_QUEUE.enqueue('report-review-ackfalse-r1-a123456789abc',payload)",invalid_payload)
  bad_before=snap();bad_controls1=controls(p);bad_controls2=controls(tab2);bad_n=len(requests)
  refusal=p.evaluate("async token=>{try{await ADMIN_TEST_UI.retry(token);return {rejected:false}}catch(e){return {rejected:true,error:String(e)}}}",invalid_item['token'])
  check('independent persistedfalse livechecked actual retry refused before transport',refusal['rejected'] and 'approved synthetic TPO fixture required' in refusal['error'] and len(requests)==bad_n)
  check('independent invalid retry exact queue and both editors preserved',snap()==bad_before and controls(p)==bad_controls1 and controls(tab2)==bad_controls2)
  tab2.frames[1].locator('#backdateAck').uncheck()
  good_before=snap();good_raw1=controls(p);good_raw2=controls(tab2);good_n=len(requests)
  good_receipt=tab2.evaluate('token=>ADMIN_TEST_UI.retry(token)',pending[1]['token'])
  good_after=snap();expected=json.loads(json.dumps(good_before));expected['generation']+=1
  check('independent persistedtrue liveunchecked actual retry exact receipt',good_receipt==items[-1]['ack'] and len(requests)==good_n+1)
  check('independent valid retry no body rewrite both unsent editors exact',good_after==expected and controls(p)==good_raw1 and controls(tab2)==good_raw2)
  (E/'independent-boolean-probes.json').write_text(json.dumps({'typed_livechecked':adversarial,'invalid_envelope':invalid_item,'refusal':refusal,'bad_before':bad_before,'bad_after':good_before,'good_receipt':good_receipt,'good_before':good_before,'good_after':good_after,'request_delta_invalid':0,'request_delta_valid':len(requests)-good_n,'editors_preserved':True},indent=2)+'\n')
  # Read-only rollback to retained old URL while both new editors remain unsent.
  rollback_before=snap();rollback_raw1=controls(p);rollback_raw2=controls(tab2);rollback_n=len(requests)
  rollback=c.new_page();rollback.goto(url);waitready(rollback)
  check('old URL rollback retains identical queue including invalid pending body',rollback.evaluate('()=>SESSION_QUEUE.snapshot()')==rollback_before)
  check('rollback old entry neither authenticates nor automatically dispatches',rollback.evaluate('()=>FB.webAuth().currentUser===null') and len(requests)==rollback_n)
  check('rollback leaves both candidate unsent editors exact',controls(p)==rollback_raw1 and controls(tab2)==rollback_raw2)
  rollback.goto(newurl);waitready(rollback)
  check('return from rollback retains exact queue and same oldcontroller',rollback.evaluate('()=>SESSION_QUEUE.snapshot()')==rollback_before and rollback.evaluate('()=>navigator.serviceWorker.controller?.scriptURL.endsWith("/form/sw.js")'))
  rollback.close()
  report={'count':len(checks),'checks':checks,'reports':items[-2:],'before':before,'after':snap(),'production_write':False,'scope':'actual native DOM + Firebase SDK local Auth + unchanged local backend Firestore'}
  (E/'browser.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'count':len(checks)}))
 except Exception as exc:
  (E/'browser-failure.json').write_text(json.dumps({'error':repr(exc),'url':p.url,'count':len(checks),'checks':checks,'errors':errors,'blocked':blocked,'dom':p.evaluate('()=>document.body.innerText'),'registrations':p.evaluate('async()=>Promise.all((await navigator.serviceWorker.getRegistrations()).map(r=>({scope:r.scope,installing:r.installing?.state,waiting:r.waiting?.state,active:r.active?.state})))')},indent=2)+'\n');raise
 finally:c.close();b.close()

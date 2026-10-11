"""Bounded demo-only native/Auth/Firestore proof; existing source34 runner pattern."""
import os,sys,json,socket,subprocess,signal,time,secrets,copy,threading,hashlib
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
R=Path('/root/mhpss-nepal-final-forms/2026-10-06/43-backend-completion/cache/emulator');D=Path(__file__).resolve().parent;S=Path('/root/mhpss-nepal-final-forms/2026-10-06')
PY=S/'34-primary-backup-admin/.venv/bin/python';BP=S/'15-ministry-form-conformance/frontend-review/.venv/bin/python'
PROJECT='demo-mhpss-admin-test'
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def ready(proc,p):
 end=time.monotonic()+45
 while time.monotonic()<end:
  if proc.poll() is not None:raise RuntimeError('local startup failed')
  try:
   with socket.create_connection(('127.0.0.1',p),.2):return
  except OSError:time.sleep(.1)
 raise RuntimeError('startup timeout')
def main():
 E=Path(sys.argv[1]).resolve();E.relative_to(Path('/root/mhpss-nepal-final-forms/2026-10-06/51-operational-closure/form-lane'));E.mkdir(exist_ok=False);W=E/'runtime';W.mkdir();(W/'home').mkdir()
 ports=[]
 while len(ports)<5:
  p=port()
  if p not in ports:ports.append(p)
 a,f,h,l,ff=ports
 env={k:v for k,v in os.environ.items() if not any(x in k for x in ['GOOGLE','GCLOUD','FIREBASE','CREDENTIAL','TOKEN','PROXY','MHPS5WS'])}
 env.update(FIREBASE_AUTH_EMULATOR_HOST=f'127.0.0.1:{a}',FIRESTORE_EMULATOR_HOST=f'127.0.0.1:{f}',GCLOUD_PROJECT=PROJECT,NO_PROXY='127.0.0.1',HOME=str(W/'home'),XDG_CONFIG_HOME=str(W/'home/.config'),CI='true',PYTHONDONTWRITEBYTECODE='1')
 os.environ.clear();os.environ.update(env)
 cfg=W/'firebase.json';cfg.write_text(json.dumps({'emulators':{'auth':{'host':'127.0.0.1','port':a},'hub':{'host':'127.0.0.1','port':h},'logging':{'host':'127.0.0.1','port':l},'ui':{'enabled':False},'singleProjectMode':True}}))
 processes=[];server=None;app=None;db=None;checks=[];success=False;logs=[]
 def check(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 try:
  commands=[['firebase','emulators:start','--only','auth','--project',PROJECT,'--config',str(cfg)],['/usr/lib/jvm/java-21-openjdk-amd64/bin/java','-jar','/root/.cache/firebase/emulators/cloud-firestore-emulator-v1.22.0.jar','--host','127.0.0.1','--port',str(f),'--project_id',PROJECT,'--single_project_mode','--single_project_mode_error','--rules',str(R/'tests/active-v3.rules')]]
  for i,(cmd,p) in enumerate(zip(commands,[a,f])):
   log=open(W/('startup-'+str(i)+'.log'),'w');logs.append(log)
   proc=subprocess.Popen(cmd,cwd=W,env=env,stdout=log,stderr=log,start_new_session=True);processes.append(proc);ready(proc,p)
  sys.path.insert(0,str(R/'functions'));import requests,firebase_admin,admin_test,admin,intake,identity
  from firebase_admin import auth
  from google.auth.credentials import AnonymousCredentials
  from google.cloud import firestore
  app=firebase_admin.initialize_app(options={'projectId':PROJECT,'httpTimeout':5},name='local-proof')
  db=firestore.Client(project=PROJECT,credentials=AnonymousCredentials())
  session=requests.Session();session.trust_env=False
  def account(uid,email):
   password=secrets.token_urlsafe(32);auth.create_user(uid=uid,email=email,password=password,email_verified=True,app=app)
   res=session.post(f'http://127.0.0.1:{a}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=emulator-only',json={'email':email,'password':password,'returnSecureToken':True},timeout=10)
   check('genuine demo Auth sign-in '+uid,res.status_code==200)
   return res.json()['idToken'],password
  pt,pp=account(admin_test.PRIMARY_UID,admin_test.PRIMARY_EMAIL)
  bt,_=account('zXHvdu0kEPRQUNDgZlmAoKpA5Ho1','asroriadib@gmail.com');ut,_=account('fixture-unrelated','unrelated@who.int')
  control={'version':1,'revision':1,'primary':{'uid':admin_test.PRIMARY_UID,'email':admin_test.PRIMARY_EMAIL,'role':'admin','mode':'primary','enabled':True},'backup':{'uid':'zXHvdu0kEPRQUNDgZlmAoKpA5Ho1','email':'asroriadib@gmail.com','role':'admin','mode':'backup','enabled':True}}
  cref=db.document(admin.CONTROL_PATH);cref.create(control)
  check('synthetic control create readback',cref.get().to_dict()==control)
  # Dedicated narrow static fixture, no filesystem serving outside exact allowlist.
  form=R.parent/'form'
  routes={}
  for name in ['native-test-20261009','native-test-rc01-20261011']:
   root=form/'review-5ws-admin-test-v35/releases'/name
   for p in root.rglob('*'):
    if p.is_file():routes['/form/'+str(p.relative_to(form))]=p.read_bytes()
  # Serve real old-controller precache dependencies; no placeholder responses.
  import re
  sw=(form/'sw.js').read_bytes()
  match=re.search(r'const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;',sw.decode(),re.S)
  assert match is not None,'unchanged old controller PRECACHE missing'
  block=match.group(1)
  for entry in re.findall(r'"([^"]+)"',block):
   if entry=='./':routes['/form/']=(form/'index.html').read_bytes()
   elif entry.startswith('../hub/'):
    routes['/hub/'+entry.removeprefix('../hub/')]=subprocess.check_output(['git','show','490f793f6cb81ca4ab07cc9b79eab688a6df080f:cache-releases/706eb304578e7030a941b300/assets/hub/'+entry.removeprefix('../hub/')],cwd=form)
   else:routes['/form/'+entry]=(form/entry).read_bytes()
  routes['/form/sw.js']=sw
  routes['/form/controller-fixture.html']=b'<!doctype html><title>Unchanged served v43 controller fixture</title>'
  nonce=secrets.token_hex(24)
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def reply(self,status,data,typ='application/json'):
    if not isinstance(data,bytes):data=json.dumps(data).encode()
    self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
   def proxy(self):
    headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','connection']};headers['Origin']=origin
    raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
    res=session.request(self.command,f'http://127.0.0.1:{ff}'+self.path,headers=headers,data=raw,timeout=40)
    self.reply(res.status_code,res.content)
   def do_GET(self):
    with open(E/'request-paths.log','a') as log:log.write(self.path.split('?')[0]+'\n')
    if self.path=='/nonce':self.reply(200,{'nonce':nonce});return
    if self.path.startswith('/admin/test/'):self.proxy();return
    data=routes.get(self.path.split('?')[0])
    if data is None:self.reply(404,{});return
    self.reply(200,data,{'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json'}.get(Path(self.path.split('?')[0]).suffix,'text/plain'))
   def do_POST(self):
    if self.path.startswith(('/identitytoolkit.googleapis.com/','/securetoken.googleapis.com/')):
     raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
     res=session.post(f'http://127.0.0.1:{a}'+self.path,data=raw,headers={'Content-Type':self.headers.get('Content-Type','application/json')},timeout=10)
     self.reply(res.status_code,res.content);return
    if self.path=='/signin':
     self.rfile.read(int(self.headers.get('Content-Length','0')))
     res=session.post(f'http://127.0.0.1:{a}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=emulator-only',json={'email':admin_test.PRIMARY_EMAIL,'password':pp,'returnSecureToken':True},timeout=10)
     self.reply(res.status_code,{'fixturePassword':pp});return
    if self.path=='/admin/test/intake':self.proxy();return
    self.reply(404,{})
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True;ports.append(server.server_port)
  origin=f'http://127.0.0.1:{server.server_port}';env['TEST_ORIGIN']=origin
  log=open(W/'framework.log','w');logs.append(log)
  proc=subprocess.Popen([str(PY.parent/'functions-framework'),'--target','admin_emulator','--source',str(R/'tests/emulator_entry.py'),'--host','127.0.0.1','--port',str(ff)],cwd=W,env=env,stdout=log,stderr=log,start_new_session=True);processes.append(proc);ready(proc,ff)
  threading.Thread(target=server.serve_forever,daemon=True).start()
  check('intended fixture nonce',session.get(origin+'/nonce',timeout=5).json()['nonce']==nonce)
  result=subprocess.run([str(BP),str(D/'browser_rc01.py'),origin,str(E)],cwd=R,env=env,capture_output=True,text=True,timeout=300)
  (E/'browser-process.json').write_text(json.dumps({'exit_code':result.returncode,'stderr':result.stderr},indent=2)+'\n')
  if result.returncode:raise RuntimeError('native browser failed: '+result.stderr)
  browser=json.loads(result.stdout)
  evidence=json.loads((E/'browser.json').read_text())
  for report in evidence['reports']:
   ref=db.collection(admin_test.TEST_ROOT).document(report['session']);cur=ref.get().to_dict()
   check('projection exact correction '+report['session'],cur['revision']==2 and cur['request_sha256']==report['sha256'])
   check('one initial and correction event '+report['session'],len(list(ref.collection('events').stream()))==2 and len(list(ref.collection('retryTokens').stream()))==2)
  for name in ['roles','submissions','mhpss5wsReportsV2','mhpss5wsGrantsV2','public_stats']:
   check('operational and grants untouched '+name,len(list(db.collection(name).stream()))==0)
  result={'state':'LOCAL_NATIVE_EMULATOR_PASS_NOT_REVIEWED_NOT_DEPLOYED','checks':checks,'count':len(checks),'browser_count':browser['count'],'production_crypto_proven':False,'production_write':False,'source_classification':admin_test.CLASSIFICATION}
  (E/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));success=True
 finally:
  if server is not None:server.shutdown();server.server_close()
  if db is not None:db.close()
  if app is not None:firebase_admin.delete_app(app)
  for proc in reversed(processes):
   if proc.poll() is None:
    os.killpg(proc.pid,signal.SIGTERM)
    try:proc.wait(timeout=8)
    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
  for log in logs:log.close()
  closed=[]
  for p in ports:
   try:
    with socket.create_connection(('127.0.0.1',p),.2):closed.append(False)
   except OSError:closed.append(True)
  (E/'cleanup.json').write_text(json.dumps({'success':success,'ports':ports,'listeners_closed':closed,'processes_stopped':all(p.poll() is not None for p in processes),'all_closed':all(closed)},indent=2)+'\n')
  if success:
   pass # Retain startup/framework logs; generated credentials never logged intentionally
  if not all(closed):raise RuntimeError('listener cleanup failed')
if __name__=='__main__':main()

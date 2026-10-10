const CONFIG={"owner":"mhpss-field-w43","root":true,"release":null,"manifest":null,"allowed":["/form/","/hub/assets/"],"entries":["/form/","/form/index.html","/form/5ws-report.html","/form/4ws-report.html","/form/cards.html"]};
'use strict';
/* Ordinary trusted browser/HTTPS deployment boundary. No self-fetch claim about
 * already-executed bytes. Install verifies immutable manifest + every asset.
 * A complete staging cache is published with one strict IDB transaction; no
 * partially copied target cache can become visible. Prior caches are retained.
 */
const BASE=new URL('./',self.location.href),Q=new URL(self.location.href).searchParams;
const RELEASE=CONFIG.release||Q.get('release'),MH=CONFIG.manifest||Q.get('manifest'),WH=Q.get('worker');
const DB='mhpss-cache-release-authority-v1',AUTHORITY=BASE.href+'|'+RELEASE;
const hex=x=>typeof x==='string'&&/^[0-9a-f]{64}$/.test(x);
const exact=(x,k)=>x&&typeof x==='object'&&!Array.isArray(x)&&Object.keys(x).sort().join(',')===k.slice().sort().join(',');
const digest=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('');
async function db(){return new Promise((ok,no)=>{const r=indexedDB.open(DB,1);r.onupgradeneeded=()=>r.result.createObjectStore('releases');r.onsuccess=()=>ok(r.result);r.onerror=()=>no(r.error);r.onblocked=()=>no(Error('authority blocked'));});}
async function authority(write){const d=await db();try{return await new Promise((ok,no)=>{const tx=d.transaction('releases',write?'readwrite':'readonly',write?{durability:'strict'}:undefined),s=tx.objectStore('releases');let value;const r=s.get(AUTHORITY);r.onsuccess=()=>{value=r.result;if(write){try{value=write(value);s.put(value,AUTHORITY);if(value.accepted)s.put(value,BASE.href+'|selected');}catch(e){tx.abort();}}};tx.oncomplete=()=>ok(value);tx.onerror=tx.onabort=()=>no(tx.error||Error('authority refused'));});}finally{d.close();}}
function validState(s){if(!exact(s,['scope','release','manifest','cache','accepted'])||s.scope!==BASE.href||s.release!==RELEASE||s.manifest!==MH||typeof s.accepted!=='boolean'||typeof s.cache!=='string'||!s.cache.startsWith(CONFIG.owner+'-stage-'))throw Error('authority shape');return s;}
async function state(){return validState(await authority());}
async function servingState(){const current=await state();if(current.accepted)return current;const d=await db();try{return await new Promise((ok,no)=>{const tx=d.transaction('releases'),r=tx.objectStore('releases').get(BASE.href+'|selected');r.onsuccess=()=>{const s=r.result;if(!s){ok(null);return;}if(!exact(s,['scope','release','manifest','cache','accepted'])||s.scope!==BASE.href||!hex(s.release)||!hex(s.manifest)||s.accepted!==true||typeof s.cache!=='string'||!s.cache.startsWith(CONFIG.owner+'-stage-')){no(Error('selected authority'));return;}ok(s);};r.onerror=()=>no(r.error);});}finally{d.close();}}
async function verify(r,pin){if(!r||r.status!==200||r.redirected||r.type==='opaque'||r.headers.has('Set-Cookie')||(r.headers.get('Content-Type')||'').split(';')[0].trim()!==pin.type)throw Error('media/status');if(!r.headers.has('Content-Encoding')&&r.headers.has('Content-Length')&&Number(r.headers.get('Content-Length'))!==pin.bytes)throw Error('declared length');const b=await r.arrayBuffer();if(b.byteLength!==pin.bytes||await digest(b)!==pin.sha256)throw Error('asset integrity');}
function validate(m){
 if(!exact(m,['version','assets'])||m.version!==2||!Array.isArray(m.assets)||m.assets.length<1||m.assets.length>100)throw Error('manifest shape');let total=0;const requests=new Set(),files=new Set();
 for(const a of m.assets){if(!exact(a,['request','file','sha256','bytes','type'])||!hex(a.sha256)||!Number.isSafeInteger(a.bytes)||a.bytes<1||a.bytes>3000000||!['text/html','application/javascript','text/css','application/json','application/manifest+json','image/png'].includes(a.type))throw Error('asset shape');
  if(!/^\/[a-z0-9/_-]*(\.[a-z0-9-]+)?$/.test(a.request)||a.request.includes('//')||a.request.includes('..')||/\/(api|auth|admin|signin)(\/|\.)/i.test(a.request)||requests.has(a.request))throw Error('request path');
  if(!/^[a-z0-9][a-z0-9/_-]*\.[a-z0-9-]+$/.test(a.file)||a.file.includes('//')||a.file.includes('..')||files.has(a.file))throw Error('file path');
  if(!CONFIG.allowed.some(p=>a.request.startsWith(p)))throw Error('request outside scope');
  requests.add(a.request);files.add(a.file);total+=a.bytes;if(total>15000000)throw Error('release bound');
 }return m;
}
async function manifest(r,hash=MH){if(!hex(hash)||!hex(RELEASE)||!r||r.status!==200||r.redirected||(r.headers.get('Content-Type')||'').split(';')[0].trim()!=='application/json')throw Error('manifest response');const raw=await r.arrayBuffer();if(raw.byteLength>60000||await digest(raw)!==hash)throw Error('manifest integrity');return validate(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw)));}
const manifestURL=()=>new URL('cache-manifests/'+MH+'.json',BASE);
async function complete(s){validState(s);const c=await caches.open(s.cache),m=await manifest(await c.match(manifestURL()));if((await c.keys()).length!==m.assets.length+1)throw Error('incomplete inventory');for(const a of m.assets)await verify(await c.match(new URL(a.request,BASE)),a);return m;}
self.addEventListener('install',e=>e.waitUntil((async()=>{
 if([...Q.keys()].sort().join(',')!=='manifest,release,worker'||![RELEASE,MH,WH].every(hex)||await digest(new TextEncoder().encode(JSON.stringify({manifest_sha256:MH,worker_sha256:WH})))!==RELEASE)throw Error('expected release identity');
 /* A second HTTP response detects accidental deployment mismatch only. It is
    NOT proof of already-executed bytes against a differential/malicious origin. */
 const wr=await fetch(self.location.href,{cache:'no-store',credentials:'omit',redirect:'error'});if(wr.status!==200||wr.redirected||(wr.headers.get('Content-Type')||'').split(';')[0].trim()!=='application/javascript'||await digest(await wr.arrayBuffer())!==WH)throw Error('served worker package mismatch');
 const mr=await fetch(manifestURL(),{cache:'no-store',credentials:'omit',redirect:'error'}),m=await manifest(mr.clone());
 const prior=await authority();if(prior){await complete(prior);return;}
 const name=CONFIG.owner+'-stage-'+crypto.randomUUID();let published=false;
 try{const c=await caches.open(name);for(const a of m.assets){const r=await fetch(new URL(a.file,BASE),{cache:'no-store',credentials:'omit',redirect:'error'});await verify(r.clone(),a);/* Reset response URL to the stable request key so relative ES-module imports stay inside the verified inventory, not the immutable download directory. */const body=await r.arrayBuffer(),headers=new Headers(r.headers);headers.delete('Content-Encoding');headers.set('Content-Length',String(body.byteLength));await c.put(new URL(a.request,BASE),new Response(body,{status:200,headers}));}await c.put(manifestURL(),mr);const s={scope:BASE.href,release:RELEASE,manifest:MH,cache:name,accepted:false};await complete(s);
  const chosen=await authority(old=>{if(old){validState(old);return old;}return s;});published=chosen.cache===name;
 }finally{if(!published)await caches.delete(name);}
})()));
self.addEventListener('message',e=>e.waitUntil((async()=>{let accepted=false,reason='refused';try{const d=e.data,c=await self.clients.get(e.source?.id);if(!exact(d,['type','release'])||d.type!=='ACCEPT_RELEASE'||d.release!==RELEASE||e.origin!==BASE.origin||!c||new URL(c.url).origin!==BASE.origin||!CONFIG.entries.includes(new URL(c.url).pathname))throw Error('expected release/client mismatch');
 const s=await state();await complete(s);await authority(old=>{validState(old);if(old.cache!==s.cache)throw Error('concurrent pointer');return {...old,accepted:true};});await self.skipWaiting();if(self.registration.active?.scriptURL===self.location.href)await self.clients.claim();accepted=true;reason='durable acceptance';
 }catch(err){reason=String(err.message);}e.ports[0]?.postMessage({accepted,release:RELEASE,reason});})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{const s=await state();await complete(s);if(s.accepted)await self.clients.claim();/* No prefix/global deletion. No legacy/child/unrelated cache is owned by this install. */})()));
self.addEventListener('fetch',e=>{
 const r=e.request,u=new URL(r.url);
 if(r.method!=='GET'||u.origin!==BASE.origin||u.search||u.username||u.password||r.headers.has('Authorization')||/\/(api|auth|admin|signin)(\/|\.)/i.test(u.pathname)||!CONFIG.allowed.some(p=>u.pathname.startsWith(p)))return;
 e.respondWith((async()=>{const s=await servingState();if(!s)return fetch(r,{cache:'no-store'});const c=await caches.open(s.cache),m=await manifest(await c.match(new URL('cache-manifests/'+s.manifest+'.json',BASE)),s.manifest),a=m.assets.find(x=>x.request===u.pathname);if(!a)return fetch(r,{cache:'no-store'});const hit=await c.match(new URL(a.request,BASE));await verify(hit?.clone(),a);return hit;})());
});

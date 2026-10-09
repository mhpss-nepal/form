'use strict';
// Scoped native TEST cache. Whole identity binds the manifest AND these bytes.
const BASE=new URL('./',self.location.href), Q=new URL(self.location.href).searchParams;
const RELEASE=Q.get('release'), MH=Q.get('manifest'), WH=Q.get('worker');
const PREFIX='mhpss-native-test-w38-', CACHE=PREFIX+RELEASE, DB=PREFIX+'acceptance';
const hex=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
const digest=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(n=>n.toString(16).padStart(2,'0')).join('');
let loading;
function exact(o,keys){return o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).sort().join(',')===keys.slice().sort().join(',');}
async function bytes(r,type,size,hash){
 if(!r||r.status!==200||r.redirected||r.type==='opaque'||(r.headers.get('Content-Type')||'').split(';')[0].trim()!==type)throw Error('media/status');
 if(r.headers.has('Content-Length')&&Number(r.headers.get('Content-Length'))!==size)throw Error('declared length');
 const b=await r.arrayBuffer();if(b.byteLength!==size||await digest(b)!==hash)throw Error('integrity');return b;
}
async function contract(){
 if(!loading)loading=(async()=>{
  if([...Q.keys()].sort().join(',')!=='manifest,release,worker'||![RELEASE,MH,WH].every(hex))throw Error('identity format');
  if(await digest(new TextEncoder().encode(JSON.stringify({manifest_sha256:MH,worker_sha256:WH})))!==RELEASE)throw Error('identity binding');
  const r=await fetch(new URL('cache-manifest.json',BASE),{cache:'no-store',credentials:'omit',redirect:'error'});
  if(r.status!==200||r.redirected||(r.headers.get('Content-Type')||'').split(';')[0]!=='application/json')throw Error('manifest response');
  if(Number(r.headers.get('Content-Length'))>20000)throw Error('manifest bound');
  const raw=await r.arrayBuffer();if(raw.byteLength>20000||await digest(raw)!==MH)throw Error('manifest digest');
  const m=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
  if(!exact(m,['version','assets'])||m.version!==1||!m.assets||Array.isArray(m.assets)||typeof m.assets!=='object')throw Error('manifest shape');
  const entries=Object.entries(m.assets);if(entries.length<18||entries.length>40)throw Error('inventory bound');
  let total=0;for(const [path,pin]of entries){
   if(!/^[a-z0-9][a-z0-9/-]*\.(html|js|css|json)$/.test(path)||path.includes('//')||path.split('/').some(p=>p==='..'||p==='.')||['coherent-sw.js','cache-manifest.json'].includes(path))throw Error('path');
   if(!exact(pin,['sha256','bytes','type'])||!hex(pin.sha256)||!Number.isSafeInteger(pin.bytes)||pin.bytes<1||pin.bytes>2000000||!['text/html','text/javascript','text/css','application/json'].includes(pin.type))throw Error('pin');
   total+=pin.bytes;if(total>6000000)throw Error('total bound');
  }
  for(const p of ['review.html','form/5ws-report.html','offline/session-queue.js','editor-authority.js','admin-test-ui.js','sdk/firebase-app.js','sdk/firebase-auth.js','sdk/firebase-firestore.js','cache-boot.js'])if(!m.assets[p])throw Error('mandatory asset');
  return entries;
 })();return loading;
}
// Cached verified manifest allows genuine worker wake while offline.
async function entries(){
 const c=await caches.open(CACHE),r=await c.match(new URL('cache-manifest.json',BASE));
 if(r){const raw=await r.arrayBuffer();if(raw.byteLength>20000||await digest(raw)!==MH)throw Error('stored manifest');const m=JSON.parse(new TextDecoder().decode(raw));return Object.entries(m.assets);}
 return contract();
}
async function complete(c,list){
 const keys=await c.keys();if(keys.length!==list.length+1)throw Error('inventory mismatch');
 for(const [p,pin]of list)await bytes(await c.match(new URL(p,BASE)),pin.type,pin.bytes,pin.sha256);
 const m=await c.match(new URL('cache-manifest.json',BASE));if(!m||await digest(await m.arrayBuffer())!==MH)throw Error('manifest missing');
}
async function consent(write=false){
 const db=await new Promise((resolve,reject)=>{const r=indexedDB.open(DB,1);r.onupgradeneeded=()=>r.result.createObjectStore('accepted');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
 try{return await new Promise((resolve,reject)=>{const tx=db.transaction('accepted',write?'readwrite':'readonly',write?{durability:'strict'}:undefined);const s=tx.objectStore('accepted');let value;const r=write?s.put({release:RELEASE,manifest:MH,worker:WH,scope:BASE.href},RELEASE):s.get(RELEASE);r.onsuccess=()=>value=r.result;tx.oncomplete=()=>resolve(write||!!(value&&exact(value,['release','manifest','worker','scope'])&&value.release===RELEASE&&value.manifest===MH&&value.worker===WH&&value.scope===BASE.href));tx.onerror=tx.onabort=()=>reject(tx.error||Error('acceptance storage'));});}finally{db.close();}
}
self.addEventListener('install',e=>e.waitUntil((async()=>{
 const list=await contract();const own=await fetch(self.location.href,{cache:'no-store',credentials:'omit',redirect:'error'});if(own.status!==200||own.redirected||await digest(await own.arrayBuffer())!==WH)throw Error('worker identity');
 if((await caches.keys()).includes(CACHE)){await complete(await caches.open(CACHE),list);return;}
 const stageName=PREFIX+'stage-'+crypto.randomUUID();let created=false;
 try{const stage=await caches.open(stageName);for(const [p,pin]of list){const r=await fetch(new URL(p,BASE),{cache:'no-store',credentials:'omit',redirect:'error'});await bytes(r.clone(),pin.type,pin.bytes,pin.sha256);await stage.put(new URL(p,BASE),r);}
 const mr=await fetch(new URL('cache-manifest.json',BASE),{cache:'no-store',credentials:'omit',redirect:'error'});if(await digest(await mr.clone().arrayBuffer())!==MH)throw Error('manifest changed');await stage.put(new URL('cache-manifest.json',BASE),mr);await complete(stage,list);
 const target=await caches.open(CACHE);created=true;for(const req of await stage.keys())await target.put(req,await stage.match(req));await complete(target,list);
 }catch(err){if(created)await caches.delete(CACHE);throw err;}finally{await caches.delete(stageName);}
})()));
self.addEventListener('message',e=>e.waitUntil((async()=>{
 let accepted=false;try{const d=e.data,client=await self.clients.get(e.source?.id);if(!exact(d,['type','release'])||d.type!=='ACCEPT_RELEASE'||d.release!==RELEASE||e.origin!==BASE.origin||!client||new URL(client.url).origin!==BASE.origin||new URL(client.url).pathname!==new URL('review.html',BASE).pathname)throw Error('acceptance refused');await complete(await caches.open(CACHE),await entries());await consent(true);await self.skipWaiting();await self.clients.claim();accepted=true;}catch(_){}e.ports[0]?.postMessage({accepted,release:RELEASE});
})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{await complete(await caches.open(CACHE),await entries());if(await consent())await self.clients.claim();})()));
self.addEventListener('fetch',e=>{
 const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==BASE.origin||u.search||u.username||u.password||e.request.headers.has('Authorization')||!u.pathname.startsWith(BASE.pathname))return;
 e.respondWith((async()=>{const list=await entries(),entry=list.find(([p])=>new URL(p,BASE).pathname===u.pathname);if(!entry||!await consent())return fetch(e.request,{cache:'no-store'});const r=await(await caches.open(CACHE)).match(new URL(entry[0],BASE));await bytes(r.clone(),entry[1].type,entry[1].bytes,entry[1].sha256);return r;})());
});

/* REVIEW ONLY. Synthetic paired root scope; no production registration. */
'use strict';
const CONTRACT={"entries":[{"bytes":180,"path":"SDK-PROVENANCE.json","sha256":"b2676630fcddb85292ea36a9751581bf7a78df1f7985ba90cccb3fa7e53e99b2","type":"application/json"},{"bytes":6859,"path":"companion.js","sha256":"06df99e7ed55b0ea3cc4133d4c9778d5a31fe8e340d9be9e97fb8064e9f5d8e0","type":"text/javascript"},{"bytes":120,"path":"endpoint-config.js","sha256":"035c08eeb72a5388b53f83290c45a2198e48a5ee5d871bb4464450cf81f54508","type":"text/javascript"},{"bytes":16113,"path":"fb-auth-paired.js","sha256":"b3139678b339ea660c908668e857e72d5b4749c636221b2724e784606e721f93","type":"text/javascript"},{"bytes":1366,"path":"fb-config.js","sha256":"7756103cabd291ee4322a4c9fe63f6bfb4239cebabeba1eb702a5b0321051034","type":"text/javascript"},{"bytes":719784,"path":"form/5ws-report.html","sha256":"fb172c3c61d40a7089eaae27f5011280875a0ddb3a9df0ba6ab34abd605c938f","type":"text/html"},{"bytes":23824,"path":"form/integration-review.js","sha256":"ba5b7de2930b7854d00d5f006f05920ea8e49d34b774356f45d961ee95fe5c57","type":"text/javascript"},{"bytes":2277,"path":"form-bridge.js","sha256":"4e5f950b27b98af7d587b338f165a871f39210410b37ba6bc5dcd3fde665c918","type":"text/javascript"},{"bytes":16865,"path":"hub/assets/app.css","sha256":"474e45bce8fb969093f4ae46bcb9c2f7044032f1e78923cc30090a3c2deebae5","type":"text/css"},{"bytes":217194,"path":"hub/assets/codes.js","sha256":"846aec4e5f980d9a97e8a9ddddc3cd348700ecd10f03887d07f5adf24760d90c","type":"text/javascript"},{"bytes":46395,"path":"hub/assets/design.css","sha256":"6b317fc300c8c395fc429ac9ecebe3c4e3624997d4a14a487767350e652b2a7e","type":"text/css"},{"bytes":15519,"path":"hub/assets/form.css","sha256":"d15c5a17e97b1228adb5870238c8a177676db1d7f19a7941750378099663c4ab","type":"text/css"},{"bytes":314731,"path":"hub/assets/i18n-strings.js","sha256":"feb9241604dafc18a5ad5d9fdd3b089188b9840579e3e9cd5bcceac3cb7d0cc1","type":"text/javascript"},{"bytes":43019,"path":"hub/assets/i18n.js","sha256":"7fde722dded90401f0d7f74c5568811d367c00077fa507e9609070953ddff93b","type":"text/javascript"},{"bytes":4855,"path":"hub/assets/icons.js","sha256":"d53f0ff421da3fcd003253674970d9288ee51c806df17ea5ef3e1d34148585b7","type":"text/javascript"},{"bytes":6886,"path":"hub/assets/mark.js","sha256":"841956be39c55f95099a3b1e2727ac067541beaf2eab9717a654048dad1b52da","type":"text/javascript"},{"bytes":27469,"path":"hub/assets/store.js","sha256":"ffeee988efc0d961777aaee6df3a2ee2153a457dad78e3d7890c94dc3e9f3e7f","type":"text/javascript"},{"bytes":384994,"path":"hub/index.html","sha256":"da5baf5c6617e38c50019eb975af586c94401d32e0c4d201d401187110810e06","type":"text/html"},{"bytes":12561,"path":"legacy-recovery.js","sha256":"30c2a86af2401dd1711020b111149a2658a468efc4b1f79d8679c8bdd68c8b43","type":"text/javascript"},{"bytes":10653,"path":"offline/session-queue.js","sha256":"a8347bd6a6cc57bbe8d20bf2ce98f9b3c49d6367853db72afa2a8a4ae42afc56","type":"text/javascript"},{"bytes":4242,"path":"production-transport.js","sha256":"13d35e4163c7fadee6d13be80d3ccc452bb5002d5e1e7244db0a735a2a94abae","type":"text/javascript"},{"bytes":1447,"path":"pwa-review.js","sha256":"0b59b03dc99220a2b2ab195cb5c08790e2504ee282227721bd14d30af176f596","type":"text/javascript"},{"bytes":366,"path":"reader.cjs","sha256":"ce677fb64e4197442980e8d4e4f942ccb12ce47943c80076d4cc270bddc33038","type":"text/javascript"},{"bytes":5324,"path":"review.html","sha256":"d5560ef1982bda81270bff84fe46621c364200630fdf604f67f5b2a7e4ed9004","type":"text/html"},{"bytes":102882,"path":"sdk/firebase-app.js","sha256":"f7ec36066094ccc2cc288a5c76453daf5f8d6dcdb5063d3a3ae4392add8344a7","type":"text/javascript"},{"bytes":150531,"path":"sdk/firebase-auth.js","sha256":"f7b4b6c2a048a971dc0468db2c234f032ccc25218f9f0a5df5df73507b279641","type":"text/javascript"},{"bytes":440170,"path":"sdk/firebase-firestore.js","sha256":"978aee9ea886a9b66570efe20ba6f7f7a3422a0b22578a2830300d7ae446c3d7","type":"text/javascript"},{"bytes":4160,"path":"runtime-contract.json","sha256":"1d9d600f54abe87aab28d40976321dd758cc090f320387b8a395b93ac1861e67","type":"application/json"}],"pair":"7d613491cbe9db1485fad9a55999773c6a365af48177b6e98d76a63f911eaca8"};
const CACHE='mhpss-paired-review-'+CONTRACT.pair;
const BASE=new URL('./',self.location.href);
if(BASE.origin!=='https://mhpss-nepal.github.io' || !BASE.pathname.startsWith('/form/')) throw Error('Review worker requires exact secure loopback');
function url(entry){return new URL(entry.path,BASE).href;}
async function verify(response,entry){
 if(!response || response.status!==200 || response.type==='opaque' || (response.headers.get('content-type')||'').split(';')[0].trim()!==entry.type) throw Error('Status/type mismatch: '+entry.path);
 const body=await response.clone().arrayBuffer();
 if(body.byteLength!==entry.bytes) throw Error('Size mismatch: '+entry.path);
 const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',body))).map(x=>x.toString(16).padStart(2,'0')).join('');
 if(sha!==entry.sha256) throw Error('Digest mismatch: '+entry.path);
}
function canonical(v){return JSON.stringify(Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))));}
async function digest(data){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(x=>x.toString(16).padStart(2,'0')).join('');}
async function metadata(action,value){
 const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('mhpss-review-release-acceptance-v2',1);r.onupgradeneeded=()=>r.result.createObjectStore('pairs');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
 try{return await new Promise((resolve,reject)=>{const tx=db.transaction('pairs',action==='get'?'readonly':'readwrite'),store=tx.objectStore('pairs');const r=action==='get'?store.get(CONTRACT.pair):store.put(value,CONTRACT.pair);let result;r.onsuccess=()=>{result=r.result;};tx.oncomplete=()=>resolve(result);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error);});}finally{db.close();}
}
async function accepted(){const m=await metadata('get');return m?.accepted===true && m.release===m.expectedRelease;}
async function complete(cache){
 const keys=await cache.keys();
 if(keys.length!==CONTRACT.entries.length) throw Error('Cache entry set mismatch');
 for(const entry of CONTRACT.entries) await verify(await cache.match(url(entry)),entry);
}
self.addEventListener('install',event=>event.waitUntil((async()=>{
 // Separate whole-release identity: observed worker bytes plus runtime pair.
 // Trust comes from the reviewer's frozen external bootstrap, not this observation.
 const worker=await fetch(self.location.href,{cache:'no-store',credentials:'omit',redirect:'error'});
 if(worker.status!==200)throw Error('Worker identity fetch failed');
 const workerSha=await digest(await worker.arrayBuffer());
 const expectedRelease=await digest(new TextEncoder().encode(canonical({pair_sha256:CONTRACT.pair,worker_sha256:workerSha,runtime_contract_sha256:CONTRACT.entries.find(e=>e.path==='runtime-contract.json').sha256})));
 await metadata('put',{expectedRelease,accepted:false});
 // A rollback can reuse an already complete immutable cache; never overwrite it.
 if((await caches.keys()).includes(CACHE)){
  await complete(await caches.open(CACHE));return;
 }
 const staging=CACHE+'-stage-'+crypto.randomUUID();
 let created=false;
 try{
  const staged=await caches.open(staging);
  for(const entry of CONTRACT.entries){
   const response=await fetch(url(entry),{cache:'no-store',credentials:'omit',redirect:'error'});
   await verify(response,entry);await staged.put(url(entry),response);
  }
  await complete(staged);
  const target=await caches.open(CACHE);created=true;
  for(const entry of CONTRACT.entries) await target.put(url(entry),await staged.match(url(entry)));
  await complete(target);
 }catch(error){if(created)await caches.delete(CACHE);throw error;}
 finally{await caches.delete(staging);}
 // Deliberately remain waiting until a reviewer explicitly accepts this pair.
})()));
self.addEventListener('message',event=>{
 if(event.data?.type!=='ACTIVATE_REVIEW')return;
 event.waitUntil((async()=>{
  try{
   const d=event.data;
   if(!d || Object.keys(d).sort().join(',')!=='pair,release,type' || d.pair!==CONTRACT.pair || typeof d.release!=='string' || !/^[0-9a-f]{64}$/.test(d.release))throw Error('Exact acceptance fields/pair required');
   if(event.origin!==BASE.origin || !event.source?.id)throw Error('Same-origin client required');
   const client=await self.clients.get(event.source.id);
   if(!client || client.type!=='window' || new URL(client.url).origin!==BASE.origin || new URL(client.url).pathname!==new URL('review.html',BASE).pathname)throw Error('Review window client required');
   const m=await metadata('get');
   if(!m || m.expectedRelease!==d.release)throw Error('Whole-release mismatch');
   await complete(await caches.open(CACHE));
   await metadata('put',{expectedRelease:d.release,release:d.release,accepted:true});
   if(self.registration.active?.scriptURL===self.location.href && !self.registration.waiting)await self.clients.claim();
   await self.skipWaiting();event.source.postMessage({type:'REVIEW_ACTIVATION',ok:true,pair:CONTRACT.pair,release:d.release});
  }
  catch(error){event.source?.postMessage({type:'REVIEW_ACTIVATION',ok:false,error:String(error)});}
 })());
});
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 await complete(await caches.open(CACHE));
 // First workers may auto-activate; acceptance gates claiming and serving.
 if(await accepted())await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const request=event.request,u=new URL(request.url);
 if(request.method!=='GET'||u.origin!==BASE.origin)return;
 if(u.search || u.username || u.password || request.headers.has('Authorization'))return;
 const entry=CONTRACT.entries.find(e=>url(e)===u.origin+u.pathname);
 if(!entry)return;
 event.respondWith((async()=>{
  try{
   if(!await accepted()){
    if(['review.html','pwa-review.js'].includes(entry.path))return fetch(request,{cache:'no-store'});
    throw Error('Exact release not accepted');
   }
   const response=await (await caches.open(CACHE)).match(url(entry));
   await verify(response,entry);return response;
  }
  catch(error){return new Response('Review shell incomplete; reopen a complete reviewed pair online.',{status:503,headers:{'Content-Type':'text/plain'}});}
 })());
});

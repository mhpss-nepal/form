'use strict';
// A user action, never installation or page load, accepts a pinned cache release.
(async()=>{
 const status=document.getElementById('cacheStatus'),button=document.getElementById('acceptCache');
 if(!status||!button||!('serviceWorker'in navigator))return;
 const base=new URL('./',location.href);
 const hash=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(n=>n.toString(16).padStart(2,'0')).join('');
 try{
  const r=await fetch(new URL('../../cache-control-v38.json',base),{cache:'no-store',credentials:'omit',redirect:'error'});
  if(!r.ok||r.redirected)throw Error('release pin unavailable');const pin=await r.json();
  if(Object.keys(pin).sort().join(',')!=='manifest_sha256,release,worker_sha256'||!Object.values(pin).every(v=>typeof v==='string'&&/^[0-9a-f]{64}$/.test(v)))throw Error('release pin shape');
  const identity=await hash(new TextEncoder().encode(JSON.stringify({manifest_sha256:pin.manifest_sha256,worker_sha256:pin.worker_sha256})));
  if(identity!==pin.release)throw Error('release identity');
  const u=new URL('coherent-sw.js',base);u.search=new URLSearchParams({release:pin.release,manifest:pin.manifest_sha256,worker:pin.worker_sha256});
  const registration=await navigator.serviceWorker.register(u,{scope:base.pathname,updateViaCache:'none'});
  button.disabled=false;status.textContent='TEST cache candidate available. Review identity '+pin.release+'. Acceptance is separate from sign-in; no record is sent.';
  button.addEventListener('click',async()=>{
   button.disabled=true;
   try{
    const w=registration.waiting||registration.active||registration.installing;if(!w||w.state==='installing')throw Error('installation not complete; try again');
    if(w.scriptURL!==u.href)throw Error('expected release URL differs');
    const c=new MessageChannel();const result=new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('acceptance timeout; no success claimed')),12000);c.port1.onmessage=e=>{clearTimeout(timer);resolve(e.data);c.port1.close();};});
    w.postMessage({type:'ACCEPT_RELEASE',release:pin.release},[c.port2]);const reply=await result;
    if(!reply||reply.accepted!==true||reply.release!==pin.release)throw Error('acceptance refused');
    status.textContent='Exact TEST release accepted on this browser. Reload to use its verified static package. Sign-in remains online and memory-only; pending requests are not automatically sent.';
   }catch(e){status.textContent='TEST cache not confirmed: '+e.message;}
   finally{button.disabled=false;}
  });
 }catch(e){status.textContent='TEST cache is not confirmed: '+e.message+'. Existing pending data is unchanged.';}
})();

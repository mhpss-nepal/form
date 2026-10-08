/* Review-only read-only legacy snapshots. No network, dispatch, mapping or old-key writes. */
(()=>{'use strict';
const DB='mhpss-review28-legacy-recovery', STORE='packs', FLAT='mhpss-np-4ws-v1', SHARED='mhpss-np-queue-v1', LIMIT=1048576;
const $=id=>document.getElementById(id), text=s=>{$('legacyStatus').textContent=s;}, enc=s=>new TextEncoder().encode(s);
let memory=null,busy=false,opened=false,captureGeneration=0,exportGeneration=0,activeCapture=null;
const captureFields=['legacyConsent','legacyFlat','legacyShared','legacyWhole'];
const controls=fields=>fields.map(id=>$(id).checked);
const advance=n=>Number.isSafeInteger(n)&&n<Number.MAX_SAFE_INTEGER?n+1:null;
function begin(fields,generation,error){
 if(!Number.isSafeInteger(generation))throw Error('consent_generation_exhausted_hold');
 const state=controls(fields);
 return ()=>{if(generation!==(fields===captureFields?captureGeneration:exportGeneration)||JSON.stringify(state)!==JSON.stringify(controls(fields)))throw Error(error);};
}
function cancelCapture(){captureGeneration=advance(captureGeneration);memory=null;if(activeCapture&&activeCapture.abort)activeCapture.abort();}
// Failed-write memory keeps its original capture validator, not a fresh export token.
function validMemory(){if(memory)try{memory.guard();}catch(_){memory=null;}return memory;}
for(const id of captureFields)for(const event of ['input','change'])$(id).addEventListener(event,cancelCapture);
for(const event of ['input','change'])$('legacyExportConsent').addEventListener(event,()=>{exportGeneration=advance(exportGeneration);});
const sha=async(s,guard=()=>{})=>{guard();const bytes=await crypto.subtle.digest('SHA-256',enc(s));guard();return [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');};
function exact(o,keys){if(!o||typeof o!=='object'||Array.isArray(o)||Object.keys(o).sort().join('|')!==keys.slice().sort().join('|'))throw Error('metadata');}
const digest=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
// Parse top-level array lexemes; keep selected entry text exactly, never re-stringify records.
function lexemes(raw){
 const t=raw.replace(/^\uFEFF/,'');const values=JSON.parse(t);if(!Array.isArray(values)||values.length>2000)throw Error('opaque');
 const parts=[];let start=-1,depth=0,string=false,escape=false;
 for(let i=t.indexOf('[')+1;i<t.length;i++){
  const c=t[i];if(start<0){if(/\s/.test(c))continue;if(c===']')break;start=i;}
  if(string){if(escape)escape=false;else if(c==='\\')escape=true;else if(c==='"')string=false;continue;}
  if(c==='"'){string=true;continue;}if(c==='{'||c==='[')depth++;
  if((c===','&&depth===0)||(c===']'&&depth===0)){parts.push(t.slice(start,i).trimEnd());start=-1;if(c===']')break;continue;}
  if(c==='}'||c===']')depth--;
 }
 if(parts.length!==values.length)throw Error('opaque');return parts.map((raw,index)=>({raw,index,value:values[index]}));
}
function activity(v){return !!v&&typeof v==='object'&&!Array.isArray(v)&&v.kind==='activity'&&typeof v.schema==='string'&&/^mhpss-np-5ws\/5ws-np-[0-9]+\.[0-9]+\.[0-9]+$/.test(v.schema);}
async function source(key,raw,mode,guard){
 guard();
 const bytes=raw===null?0:enc(raw).length;if(bytes>LIMIT)throw Error('source_too_large_hold');
 let data=[],shape='missing';if(raw!==null){
  shape='raw_hold';
  if(mode==='activity_entries'){
   let entries;try{entries=lexemes(raw);}catch(_){throw Error('opaque_shared_hold_requires_whole_queue_consent');}
   data=await Promise.all(entries.filter(x=>activity(x.value)).map(async x=>({index:x.index,raw:x.raw,sha256:await sha(x.raw,guard)})));guard();shape='selected_activity_entries';
  }else{data=raw;try{if(Array.isArray(JSON.parse(raw.replace(/^\uFEFF/,''))))shape='flat_array_hold';}catch(_){} }
 }
 return {key,mode,source_sha256:raw===null?null:await sha(raw,guard),source_bytes:bytes,shape,data};
}
const identity=sources=>JSON.stringify(sources);
async function validate(p,guard=()=>{}){
 guard();
 exact(p,['schema','id','generation','capturedAt','state','sources']);
 if(p.schema!=='mhpss-legacy-restricted-recovery/1'||p.state!=='retained_hold'||!digest(p.id)||!Number.isSafeInteger(p.generation)||p.generation<1||typeof p.capturedAt!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(p.capturedAt)||new Date(p.capturedAt).toISOString()!==p.capturedAt||!Array.isArray(p.sources)||p.sources.length<1||p.sources.length>2)throw Error('metadata');
 let keys=new Set();for(const s of p.sources){
  exact(s,['key','mode','source_sha256','source_bytes','shape','data']);
  if(keys.has(s.key)||![FLAT,SHARED].includes(s.key)||!Number.isSafeInteger(s.source_bytes)||s.source_bytes<0||s.source_bytes>LIMIT)throw Error('metadata');keys.add(s.key);
  if(s.key===FLAT?s.mode!=='whole_key':!['whole_queue','activity_entries'].includes(s.mode))throw Error('scope');
  if(s.source_sha256===null){if(s.source_bytes!==0||s.shape!=='missing'||!Array.isArray(s.data)||s.data.length)throw Error('missing');continue;}
  if(!digest(s.source_sha256))throw Error('digest');
  if(s.mode==='activity_entries'){
   if(s.shape!=='selected_activity_entries'||!Array.isArray(s.data)||s.data.length>2000)throw Error('entries');let last=-1;
   for(const e of s.data){exact(e,['index','raw','sha256']);if(!Number.isSafeInteger(e.index)||e.index<=last||e.index>=2000||typeof e.raw!=='string'||enc(e.raw).length>LIMIT||!digest(e.sha256)||await sha(e.raw,guard)!==e.sha256||!activity(JSON.parse(e.raw)))throw Error('entry');last=e.index;}
  }else{if(typeof s.data!=='string'||!['raw_hold','flat_array_hold'].includes(s.shape)||enc(s.data).length!==s.source_bytes||await sha(s.data,guard)!==s.source_sha256)throw Error('raw');}
 }
 if(await sha(identity(p.sources),guard)!==p.id)throw Error('pack digest');return p;
}
function open(){return new Promise((resolve,reject)=>{const r=indexedDB.open(DB,1);r.onupgradeneeded=()=>r.result.createObjectStore(STORE,{keyPath:'id'});r.onerror=()=>reject(Error('storage_unavailable'));r.onblocked=()=>reject(Error('storage_blocked'));r.onsuccess=()=>resolve(r.result);});}
async function read(guard=()=>{}){guard();const db=await open();try{guard();const rows=await new Promise((res,rej)=>{const t=db.transaction(STORE,'readonly'),r=t.objectStore(STORE).getAll();r.onsuccess=()=>res(r.result);r.onerror=()=>rej(Error('storage_unavailable'));});guard();return rows;}finally{db.close();}}
async function checked(rows,guard=()=>{}){guard();if(rows.length>64)throw Error('recovery_capacity_hold');const out=[];for(const r of rows){exact(r,['id','raw']);if(!digest(r.id)||typeof r.raw!=='string'||enc(r.raw).length>3*LIMIT)throw Error('corrupt_recovery_hold');const p=await validate(JSON.parse(r.raw),guard);if(p.id!==r.id)throw Error('corrupt_recovery_hold');out.push(p);}const gens=out.map(x=>x.generation);if(new Set(gens).size!==gens.length||gens.some(x=>x>rows.length))throw Error('generation');return out;}
async function capture(){
 if(!opened||!$('legacyConsent').checked)throw Error('consent_required_no_read');
 const keys=[];if($('legacyFlat').checked)keys.push([FLAT,'whole_key']);if($('legacyShared').checked||$('legacyWhole').checked)keys.push([SHARED,$('legacyWhole').checked?'whole_queue':'activity_entries']);if(!keys.length)throw Error('select_scope_no_read');
 const guard=begin(captureFields,captureGeneration,'capture_consent_or_scope_revoked_hold'),operation={abort:null};activeCapture=operation;
 let originals=null,sources=[],pack=null;
 try{
  // Exact allowlisted keys, under the same uninterrupted consent/scope generation.
  guard();originals=keys.map(([key])=>{guard();return localStorage.getItem(key);});
  for(let i=0;i<keys.length;i++){guard();sources.push(await source(keys[i][0],originals[i],keys[i][1],guard));guard();}
  const id=await sha(identity(sources),guard);guard();pack={schema:'mhpss-legacy-restricted-recovery/1',id,generation:1,capturedAt:new Date().toISOString(),state:'retained_hold',sources};memory={pack,guard};
  let rows;try{guard();rows=await read();guard();}catch(_){guard();throw Error('memory_only_recovery_not_saved');}let prior;try{prior=await checked(rows,guard);guard();}catch(_){guard();throw Error('corrupt_recovery_hold_exact_raw_preserved');}
  const same=prior.find(x=>x.id===id);pack.generation=same?same.generation:rows.length+1;if(!same&&rows.length>=64)throw Error('recovery_capacity_hold');await validate(pack,guard);guard();
  const db=await open();try{guard();await new Promise((resolve,reject)=>{
   const t=db.transaction(STORE,'readwrite'),s=t.objectStore(STORE),r=s.getAll();let failure='memory_only_recovery_not_saved';
   operation.abort=()=>{failure='capture_consent_or_scope_revoked_hold';try{t.abort();}catch(_){};};
   t.oncomplete=()=>{operation.abort=null;resolve();};t.onabort=()=>{operation.abort=null;reject(Error(failure));};t.onerror=()=>{};
   r.onsuccess=()=>{
    // No await between guarded old-key recheck and atomic single-record put.
    try{guard();
     if(JSON.stringify(r.result)!==JSON.stringify(rows)){failure='recovery_changed_rescan_hold';t.abort();return;}
     if(keys.some(([key],i)=>{guard();return localStorage.getItem(key)!==originals[i];})){failure='legacy_changed_rescan_hold_not_complete';t.abort();return;}
     const raw=JSON.stringify(pack);if(enc(raw).length>3*LIMIT){failure='packet_too_large_hold';t.abort();return;}guard();if(!same)s.put({id,raw});
    }catch(e){failure=e.message==='capture_consent_or_scope_revoked_hold'?e.message:'memory_only_recovery_not_saved';t.abort();}
   };
  });}finally{db.close();}
  // IDB completion is the point-in-time durable boundary; later withdrawal is not deletion.
  memory=null;return same?'retained_hold — identical bytes already retained; no duplicate.':'retained_hold — exact consented snapshot committed. Not a complete device backup, migration or delivery; old writers can change later.';
 }catch(e){try{guard();}catch(revoked){memory=null;throw revoked;}throw e;}
 finally{originals=null;sources=null;pack=null;operation.abort=null;if(activeCapture===operation)activeCapture=null;}
}
async function status(){const rows=await read();try{await checked(rows);return 'retained_hold — '+rows.length+' historical snapshot(s), no dispatch or delivery status.';}catch(_){return 'corrupt_recovery_hold — raw preserved unchanged; structured use refused.';}}
async function exportPacket(guard){
 if(!opened||!$('legacyExportConsent').checked)throw Error('restricted_export_consent_required');
 let rows=[];try{guard();rows=await read(guard);guard();}catch(_){guard();if(!memory)throw Error('storage_unavailable');}
 let packs;try{packs=await checked(rows,guard);guard();}catch(_){guard();return {schema:'mhpss-legacy-restricted-raw-hold/1',state:'corrupt_recovery_hold',rawRecords:rows,memoryOnly:null};}
 return {schema:'mhpss-legacy-restricted-export/1',state:'retained_hold',packs,memoryOnly:null};
}
$('inspectLegacy').onclick=()=>{opened=true;$('legacyPanel').hidden=false;};
async function action(fn){if(busy){text('Recovery operation already running.');return;}busy=true;try{text(await fn());}catch(e){text(e.message==='memory_only_recovery_not_saved'?e.message+' — export before closing.':e.message+' — HOLD; no old data changed.');}finally{busy=false;}}
$('captureLegacy').onclick=()=>action(capture);
$('reloadLegacy').onclick=()=>action(status);
$('exportLegacy').onclick=()=>action(async()=>{
 const exportGuard=begin(['legacyExportConsent'],exportGeneration,'restricted_export_consent_revoked_hold');
 // Observe and permanently discard invalid uncommitted memory at every async guard.
 const guard=()=>{exportGuard();validMemory();};let packet=null,attempt=null,url=null;
 try{
  packet=await exportPacket(guard);guard();attempt=validMemory();
  const finalGuard=()=>{exportGuard();if(validMemory()!==attempt)throw Error('capture_consent_or_scope_revoked_hold');};
  // No packet reference escapes the original capture validator before inclusion.
  finalGuard();packet.memoryOnly=attempt?attempt.pack:null;
  if(attempt&&packet.schema==='mhpss-legacy-restricted-export/1')packet.state='memory_only_recovery_not_saved';
  const raw=JSON.stringify(packet);finalGuard();const blob=new Blob([raw],{type:'application/json'});finalGuard();
  url=URL.createObjectURL(blob);finalGuard();const a=document.createElement('a');a.href=url;a.download='restricted-legacy-recovery.json';finalGuard();a.click();
  const downloaded=url;url=null;setTimeout(()=>URL.revokeObjectURL(downloaded),1000);return packet.state+' — restricted file downloaded; no data sent or removed.';
 }finally{if(url)URL.revokeObjectURL(url);packet=null;attempt=null;}
});
})();

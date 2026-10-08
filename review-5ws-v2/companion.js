(()=>{'use strict';
let session=null,last=null,selected=false,sourceGeneration=null;
const $=id=>document.getElementById(id),notice=text=>{$('status').textContent=text;};
function authenticated(){try{return FB.webAuth().currentUser?.emailVerified===true;}catch(_){return false;}}
function transport(){if(ENDPOINT_CONFIG.activationEnabled!==true)throw Error('Activation held: login inspection only; no cloud data request');return MHPS5WS_TRANSPORT.create({projectId:FB_CONFIG.projectId,functionURL:ENDPOINT_CONFIG.functionURL},FB.webAuth());}
const listing={current:(org)=>transport().current(org)};
async function signin(){await new Promise((res,rej)=>{if(FB.status().ready)return res();let n=0;const timer=setInterval(()=>{if(FB.status().ready){clearInterval(timer);res();}else if(++n>100){clearInterval(timer);rej(Error('Auth SDK unavailable'));}},100);});
try{await FB.signIn($('em').value.trim(),$('pw').value);}finally{$('pw').value='';}notice(authenticated()?'Verified account signed in. UID: '+FB.webAuth().currentUser.uid+' · Email: '+FB.webAuth().currentUser.email+' · Organisation access remains server-controlled. No grant was created.':'Signed in but verified email is required; no delivery acknowledged.');return authenticated();}
async function flush(){
 if(!authenticated()){notice('Signed out — immutable requests remain pending.');return SESSION_QUEUE.status();}
 const result=await SESSION_QUEUE.flush(async(token,request,digest)=>{
  const item=(await SESSION_QUEUE.pending()).find(x=>x.token===token);if(!item||item.sha256!==digest)throw Error('Queue envelope changed');
  const sid=token.replace(/-r[1-9][0-9]*(?:-a[a-f0-9]{12})?$/,'');
  return transport().send({...item,session_id:sid});
 });
 notice(result.state==='conflict_recovery_hold'?'Conflict recovery HOLD — attempted bytes retained; deliberately refresh/reopen to rebase; export recovery.':result.state==='memory_only_recovery'?'NOT SAVED — memory-only unsaved recovery; export before closing.':result.state==='recovery_hold'?'Corrupt authority HOLD — no delivery or deletion.':result.pending?'Durably queued — delivery not acknowledged. If stale, refresh My reports and deliberately reopen to rebase; no automatic merge; existing report retained.':'No pending requests; exact backend receipts matched.');return result;
}
async function submit(payload){
 if(last&&!authenticated())throw Error('Sign in again before staging a correction');
 const pre=last?{event_id:last.event_id,request_sha256:last.request_sha256,revision:last.revision}:null;
 if(!session)session='report-'+crypto.randomUUID();
 const retry=session+'-r'+(pre?pre.revision+1:1)+'-a'+crypto.randomUUID().replaceAll('-','').slice(0,12);
 const options=sourceGeneration===null?{}:{expectedGeneration:sourceGeneration};
 const item=await SESSION_QUEUE.enqueue(retry,payload,pre,options);sourceGeneration=(await SESSION_QUEUE.snapshot()).generation;notice('Durably queued on device; not yet remotely acknowledged.');await flush();
 const stored=(await SESSION_QUEUE.all()).find(x=>x.token===retry);
 if(stored.state==='remotely_acknowledged'){last=stored.ack;const status=await SESSION_QUEUE.status();notice((status.recoveries?'Conflict recovery HOLD remains; ':'')+'Remotely acknowledged exact revision '+last.revision+' — Hub current read still requires refresh.');}
 sourceGeneration=(await SESSION_QUEUE.snapshot()).generation;return {state:stored.state,sha256:item.sha256,receipt:stored.ack||null,session,recoveryState:(await SESSION_QUEUE.status()).state};
}
async function open(row){const authority=await SESSION_QUEUE.snapshot();sourceGeneration=authority.generation;if(!authenticated())throw Error('Sign in required');if(row.schema!=='mhpss-5ws-session/0.4.0-approved-joint-review'){notice('Historical report is read-only. Explicit new joint counts required; no inferred age rebinning or migration.');return;}$('form').contentWindow.INTEGRATION_REVIEW.prefill(row.payload);session=row.id;last={event_id:row.event_id,request_sha256:row.request_sha256,revision:row.revision};selected=true;notice('Opened own current report revision '+row.revision+'. Changes queue only on explicit Submit. Refresh and reopen deliberately to rebase.');}
async function refresh(){
 if(!authenticated())throw Error('Sign in required');
 const d=await listing.current($('selectedOrg').value);
 if(d.scope!=='reporter-own-org-current'||d.snapshotComplete!==true||!Array.isArray(d.rows))throw Error('Exact snapshot required');
 for(const row of d.rows)if(row.kind!=='activity'||row.document_path!=='mhpss5wsReportsV2/'+row.id||!/^report-[a-zA-Z0-9_-]{1,80}$/.test(row.id)||!Number.isSafeInteger(row.revision)||row.revision<1||!/^[0-9a-f]{64}$/.test(row.request_sha256))throw Error('Exact own activity snapshot mismatch');
 const state=$('hub').contentWindow.HUB_CANDIDATE.load(d.rows);if(!state.complete||state.rejected.length)throw Error('Full receiving validation required');$('myReports').replaceChildren();
 for(const row of d.rows){const li=document.createElement('li'),button=document.createElement('button');button.type='button';button.textContent='Open '+row.payload.dateAD+' · '+row.id+' · revision '+row.revision;button.onclick=()=>open(row).catch(()=>notice('Cannot open report. Sign in and refresh online.'));li.append(button);$('myReports').append(li);}
 notice('Authenticated own-org current snapshot loaded: '+d.rows.length+' report(s). Not coordinator entitlement approval.');return d.rows.length;
}
$('recovery').onclick=async()=>{try{const data=await SESSION_QUEUE.recoveryExport(),blob=new Blob([JSON.stringify(data)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='restricted-device-recovery.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(_){notice('Recovery unavailable; no queue removed.');}};
SESSION_QUEUE.historical().then(q=>{$('historyStatus').textContent=q.length+' historical envelope(s) held read-only; export exact recovery. No automatic migration, dispatch or production-queue claim.';}).catch(()=>notice('Historical storage held; no migration or deletion.'));
window.addEventListener('authority26change',async()=>{const s=await SESSION_QUEUE.status();$('historyStatus').textContent='Device authority: '+s.state+'; '+(s.pending??'unknown')+' pending. Recovery warnings are not delivery receipts; export before clearing. Legacy storage remains HOLD.';});
window.REVIEW_BRIDGE=Object.freeze({submit,flush,signin,refresh});
$('signin').onclick=()=>signin().catch(()=>notice('Sign-in unavailable — offline login is not supported. Nothing acknowledged; queue retained.'));
$('flush').onclick=()=>flush().catch(()=>notice('Unavailable — requests retained.'));
$('refresh').onclick=()=>refresh().catch(()=>notice('Authenticated current read unavailable — no cached report read or refresh.'));
})();

/* Native UI bridge: serialized editor authority, unchanged durable TEST contracts. */
(()=>{'use strict';const $=id=>document.getElementById(id),notice=t=>{$('status').textContent=t;};let rows=[],snapshot=null,listingAuthority={};
const transport=()=>ADMIN_TEST_TRANSPORT.create(FB.webAuth());
function synthetic(p){const f=$('form').contentWindow;if(f.INTEGRATION_REVIEW.check(p).length||p.org!=='TPO'||p.siteOther!=='SYNTHETIC community venue'||p.description!==''||p.coordinationNotes!==''||p.site!==null||p.ward!==null||p.healthFacility!==null)throw Error('TEST ONLY: approved synthetic TPO fixture required; no real details');}
function validRows(input){for(const r of input)transport().row(r);const f=$('form').contentWindow,state=f.JOINT_HUB.load(input);if(!state.complete||state.rejected.length||state.records.length!==input.length)throw Error('Pinned joint receiving validation refused');return state;}
// Preflight exact native restoration in an isolated, hidden native instance. A valid
// receiving row is not necessarily representable by every native control/vocabulary.
async function validateOpenRow(row){
 validRows([row]);
 const probe=document.createElement('iframe');probe.hidden=true;probe.setAttribute('aria-hidden','true');
 try{
  await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(Error('TEST native Open validation timed out; current fields retained.')),10000);
   probe.onload=()=>{clearTimeout(timer);resolve();};probe.onerror=()=>{clearTimeout(timer);reject(Error('TEST native Open validation unavailable.'));};
   probe.src=$('form').src;document.body.append(probe);
  });
  probe.contentWindow.INTEGRATION_REVIEW.prefill(row.payload);
 }finally{probe.remove();}
}
function nativeBytes(){const f=$('form').contentWindow;return EDITOR_AUTHORITY.canonical({wire:f.REVIEW.wire(),controls:Array.from(f.document.querySelectorAll('input,select,textarea')).map(x=>({id:x.id,value:x.value,checked:x.checked,selected:x.tagName==='SELECT'?Array.from(x.options).map(o=>o.selected):null}))});}
const authority=EDITOR_AUTHORITY.create({
 queue:SESSION_QUEUE,
 owner:()=>{try{return FB.webAuth().currentUser;}catch(_){return null;}},
 authorize:()=>transport().user(),
 send:item=>{synthetic(JSON.parse(item.body).payload);return transport().send(item);},
 read:id=>transport().read(id),
 validateRow:validateOpenRow,
 nativeBytes,
 apply:payload=>$('form').contentWindow.INTEGRATION_REVIEW.prefill(payload),
 notice
});
const {flush,open,retry}=authority;
function submit(payload){try{transport().user();synthetic(payload);return authority.submit(payload);}catch(e){return Promise.reject(e);}}
async function refresh(){
 const ticket={};listingAuthority=ticket;snapshot=null;rows=[];$('myReports').replaceChildren();
 const owner=transport().user();let d;
 try{d=await transport().current();}catch(e){if(listingAuthority!==ticket)return {superseded:true};throw e;}
 if(listingAuthority!==ticket)return {superseded:true};
 validRows(d.rows);
 if(transport().user()!==owner)throw Error('Auth changed before snapshot installation');
 rows=d.rows;snapshot={owner,readTime:d.readTime,reportCount:rows.length};
 for(const r of rows){const li=document.createElement('li'),b=document.createElement('button'),access=ADMIN_TEST_TRANSPORT.rowAccess(r.id);b.type='button';b.disabled=access==='historical_read_only';b.textContent=(b.disabled?'Historical TEST — read/export only ':'Open TEST ')+r.payload.dateAD+' · '+r.id+' · revision '+r.revision;if(!b.disabled)b.onclick=()=>open(r.id).catch(e=>notice(String(e)));li.append(b);$('myReports').append(li);}
 notice('Verified complete TEST snapshot: '+rows.length+' reports, including '+rows.filter(r=>ADMIN_TEST_TRANSPORT.rowAccess(r.id)==='historical_read_only').length+' historical read-only sources. Not operational counts.');return d;
}
function csv(){
 if(!snapshot||transport().user()!==snapshot.owner)throw Error('Refresh and verify a complete TEST snapshot before export');
 const state=validRows(rows);if(rows.length!==snapshot.reportCount)throw Error('Snapshot source-count mismatch');
 const matrix=$('form').contentWindow.JOINT_HUB.exportCSV(state),access=new Map(rows.map(r=>[r.id,ADMIN_TEST_TRANSPORT.rowAccess(r.id)]));
 return matrix.split(/\r?\n/).filter(Boolean).map((line,i)=>{if(!i)return 'source_classification,test_basis,record_access,source_report_count,snapshot_read_time,'+line;const id=line.split(',')[0];if(!access.has(id))throw Error('CSV source identity mismatch');return 'synthetic_admin_test,SYNTHETIC_NON_OPERATIONAL_NO_UNIQUE_PEOPLE,'+access.get(id)+','+snapshot.reportCount+','+snapshot.readTime+','+line;}).join('\r\n')+'\r\n';
}
function download(data,name,type){const u=URL.createObjectURL(new Blob([data],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
$('flush').onclick=()=>flush().catch(e=>notice(String(e)));$('refresh').onclick=()=>refresh().catch(e=>notice('TEST read unavailable; no cached success. '+e));$('newReport').onclick=()=>{authority.cancel();$('form').contentWindow.document.getElementById('syntheticExample').click();notice('New synthetic fixture loaded; nothing submitted.');};$('exportCSV').onclick=()=>{try{download(csv(),'TEST-ONLY-joint.csv','text/csv');}catch(e){notice(String(e));}};$('recovery').onclick=async()=>download(JSON.stringify(await SESSION_QUEUE.recoveryExport()),'TEST-device-recovery.json','application/json');$('retryOriginal').onclick=async()=>{try{const first=(await SESSION_QUEUE.all())[0];if(!first)throw Error('No TEST envelope');await retry(first.token);}catch(e){notice(String(e));}};
FB.onUser(()=>{authority.cancel();listingAuthority={};snapshot=null;rows=[];$('myReports').replaceChildren();});
window.REVIEW_BRIDGE=Object.freeze({submit,flush,refresh});window.ADMIN_TEST_UI=Object.freeze({submit,flush,refresh,open,retry,csv,operationalActivation:false});
})();

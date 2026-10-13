/* Anonymous respondent only: no account, storage, history, telemetry or person join. */
(function(root){'use strict';
const BASE='https://mhpss5ws-tdp3xtfnsq-as.a.run.app',form=document.getElementById('f'),status=document.getElementById('selfreportStatus'),retry=document.getElementById('selfreportRetry'),reset=document.getElementById('clearBtn');
let pending=null,busy=false;const pick=n=>form.querySelector('input[name="'+n+'"]:checked')?.value||'';
function collect(){return {schema:'mhpss-np-selfreport/0.1.0-draft',kind:'self_report',anonymous:true,contact_code:null,site:form.site.value,age_band:document.getElementById('ageband').value,coping:pick('cope'),need:pick('need'),knows_where:pick('know'),could_reach:pick('reach'),free_text:document.getElementById('say').value.trim(),free_text_reviewed_by_human:false};}
function canonical(v){if(v===null||typeof v!=='object')return JSON.stringify(v);return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';}
async function hash(p){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(p))))).map(b=>b.toString(16).padStart(2,'0')).join('');}
function controls(){retry.disabled=!pending||busy;form.querySelector('button[type=submit]').disabled=!!pending||busy;reset.disabled=busy;}
function lock(value){form.querySelectorAll('input,select').forEach(n=>n.disabled=value);}
async function send(){if(!pending||busy)return;busy=true;controls();status.textContent='Sending anonymous submission; not yet received…';const entry=pending;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),30000);try{
 const r=await fetch(BASE+'/selfreport/intake',{method:'POST',headers:{'Content-Type':'application/json'},body:entry.bytes,credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer',signal:controller.signal});
 if(!r.ok)throw Error(r.status===503?'Operational gate closed or server result unavailable; storage may be uncertain.':'Submission refused ('+r.status+').');const ack=await r.json();
 if(Object.keys(ack).sort().join(',')!==['protocol','request_sha256','stored','submissionId'].sort().join(',')||ack.protocol!=='selfreport-receipt/1'||ack.submissionId!==entry.id||ack.request_sha256!==entry.sha||ack.stored!==true)throw Error('Receipt mismatch.');
 pending=null;lock(false);form.reset();status.textContent='Verified receipt: '+ack.submissionId+' · '+ack.request_sha256+'. Private human review pending; not a care/referral request. Nobody can contact you from this submission. Ready for a new person.';
 }catch(e){status.textContent='Retained in this open page only. '+e.message+' Retry sends exactly the same submission; reload loses it. Do not submit a new copy when receipt is uncertain.';}
 finally{clearTimeout(timer);busy=false;controls();}}
form.addEventListener('submit',async ev=>{ev.preventDefault();if(pending||busy)return;const p=collect();if(!p.site||!p.coping||!p.knows_where){status.textContent='Not sent. Choose a site and answer questions 1 and 3.';return;}busy=true;controls();try{const id=crypto.randomUUID(),sha=await hash(p);pending={id,sha,bytes:JSON.stringify({protocol:'selfreport-submit/1',submissionId:id,payload:p})};lock(true);}catch(e){status.textContent='Not sent: secure submission identity unavailable.';}finally{busy=false;controls();}if(pending)send();});
retry.onclick=send;reset.onclick=()=>{if(pending&&!confirm('Discard the pending submission from this page? It may already have reached the server. Do not send another copy of the same answer.'))return;pending=null;lock(false);form.reset();status.textContent='New person: blank form. No previous answer is shown. Legacy browser history has not been changed.';controls();};
window.addEventListener('beforeunload',ev=>{if(pending){ev.preventDefault();ev.returnValue='';}});controls();
})(window);

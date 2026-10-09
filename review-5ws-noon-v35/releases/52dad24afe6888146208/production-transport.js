/* Endpoint-only integration seam; no UI, queue migration, login or token storage. */
(function(root){'use strict';
const SCOPE='mhpss-5ws-operational/2-candidate';
function create(config,auth){
 if(!config||Object.keys(config).sort().join(',')!=='functionURL,projectId'||config.projectId!=='mhpss-nepal-hub'||typeof config.functionURL!=='string'||config.functionURL!=='https://mhpss5ws-tdp3xtfnsq-as.a.run.app')throw Error('Explicit exact production endpoint required');
 if(!auth||typeof auth.currentUser==='undefined'||auth.app?.options?.projectId!==config.projectId)throw Error('Configured Firebase Web Auth required');
 async function request(path,org,options={}){
  const user=auth.currentUser;
  if(!user||user.emailVerified!==true||typeof user.getIdToken!=='function')throw Error('Verified online sign-in required; retain immutable queue');
  const token=await user.getIdToken();
  if(auth.currentUser!==user)throw Error('Auth changed; retain immutable queue');
  const response=await fetch(config.functionURL+path,{...options,headers:{...options.headers,'X-Selected-Org':org,Authorization:'Bearer '+token},cache:'no-store',credentials:'omit',redirect:'error',signal:AbortSignal.timeout(34000)});
  if(auth.currentUser!==user)throw Error('Auth changed; retain immutable queue');
  if(!response.ok)throw Error('HTTP '+response.status+' — retain immutable queue');
  return response.json();
 }
 async function send(item){
  if(!item||typeof item.body!=='string'||typeof item.token!=='string'||typeof item.session_id!=='string')throw Error('Exact queued envelope required');
  const parsed=JSON.parse(item.body);
  // Request is never reconstructed: reviewed queue owns immutable UTF8 bytes, digest and ACK validation.
  return request('/intake',parsed.payload.org,{method:'POST',headers:{'Content-Type':'application/json','X-Session-Id':item.session_id,'X-Retry-Token':item.token},body:item.body});
 }
 async function page(org,cursor=null){
  if(cursor!==null&&(typeof cursor!=='string'||!/^[A-Za-z0-9_-]{1,2048}$/.test(cursor)))throw Error('Typed cursor required');
  const result=await request('/current',org,{headers:cursor===null?{}:{'X-Listing-Cursor':cursor}});
  if(result.protocol!=='own-current-pages/1'||result.scope!=='reporter-own-org-current'||result.pageComplete!==true||typeof result.snapshotComplete!=='boolean'||!Array.isArray(result.rows)||result.rows.length>10||result.pageCount!==result.rows.length||typeof result.readTime!=='string'||!/^\d{4}-\d{2}-\d{2}T.*Z$/.test(result.readTime)||(result.nextCursor!==null&&(typeof result.nextCursor!=='string'||!/^[A-Za-z0-9_-]{1,2048}$/.test(result.nextCursor)))||(result.nextCursor!==null)!==(result.rows.length===10)||result.snapshotComplete!==(cursor===null&&result.nextCursor===null))throw Error('Bounded own page required');
  let previous='';
  for(const row of result.rows){
   if(row.kind!=='activity'||row.operational_schema!==SCOPE||row.document_path!=='mhpss5wsReportsV2/'+row.id||typeof row.id!=='string'||!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$/.test(row.id)||row.schema!=='mhpss-5ws-session/0.4.0-approved-joint-review'||row.id<=previous)throw Error('Exact operational candidate snapshot required');
   previous=row.id;
  }
  return result;
 }
 async function current(org){
  const user=auth.currentUser,deadline=Date.now()+300000;let cursor=null,readTime=null,previous='',rows=[];const seen=new Set();
  do {
   if(Date.now()>=deadline)throw Error('Snapshot assembly deadline; browse pages or restart');
   const result=await page(org,cursor);
   if(auth.currentUser!==user||(readTime!==null&&result.readTime!==readTime))throw Error('Mixed snapshot refused');
   readTime=result.readTime;
   for(const row of result.rows){if(row.id<=previous)throw Error('Dropped/order/replay boundary refused');previous=row.id;rows.push(row);}
   cursor=result.nextCursor;
   if(cursor!==null){if(seen.has(cursor))throw Error('Cursor replay refused');seen.add(cursor);}
  } while(cursor!==null);
  return {protocol:'own-current-pages/1',scope:'reporter-own-org-current',snapshotComplete:true,readTime,rows,totalCount:rows.length};
 }
 return Object.freeze({send,current,page});
}
root.MHPS5WS_TRANSPORT=Object.freeze({create});
})(typeof window==='undefined'?globalThis:window);

/* Owner bootstrap UX only; entitlement remains server-controlled. */
import {isSignInWithEmailLink,sendSignInLinkToEmail,signInWithEmailLink} from './sdk/firebase-auth.js';
// release-pins.js is separately pinned in the external manifest, never part of a circular cache contract.
import {PINS} from './release-pins.js';
const $=id=>document.getElementById(id),PRIMARY='adib.asrori@who.int',BACKUP='asroriadib@gmail.com';
let pendingLink=window.EMAIL_LINK_BOOT?.take();delete window.EMAIL_LINK_BOOT;
const hadLanding=!!pendingLink;
if(hadLanding)$('em').value='';
let ready=false,busy=false,nextSend=0,sendCount=0;
const notice=text=>{$('loginStatus').textContent=text;};
function controls(){ $('sendLink').disabled=!ready||busy||Date.now()<nextSend||sendCount>=3; $('finishLink').disabled=!ready||busy||!pendingLink; $('signout').disabled=!ready||busy||!FB.status().user; }
function ownerEmail(){const mail=$('em').value.trim();if(mail!==PRIMARY&&mail!==BACKUP){notice('This bootstrap accepts only the exact owner WHO primary or Gmail backup email. No email sent or link consumed.');return null;}return mail;}
// Never honour a continueUrl, query pin, or foreign project API key.
function validLanding(auth,value){try{const u=new URL(value);return u.origin===location.origin&&u.pathname===location.pathname&&u.searchParams.get('apiKey')===FB_CONFIG.apiKey&&isSignInWithEmailLink(auth,value);}catch(_){return false;}}
function safeFailure(error){const code=typeof error?.code==='string'?error.code:'';if(['auth/invalid-action-code','auth/expired-action-code','auth/invalid-email','auth/invalid-credential','auth/user-disabled'].includes(code))return 'Cannot finish this link. It may be invalid, expired, already used or for another email. Request a fresh link explicitly.';if(code==='auth/too-many-requests')return 'Request held by provider. Wait before explicitly requesting a fresh link.';if(code==='auth/operation-not-allowed')return 'Email-link sign-in is unavailable in this project. No setting was changed.';return 'Sign-in unavailable. Check connectivity and request a fresh link explicitly if needed.';}
FB.onStatus(s=>{if(s.ready&&!ready){ready=true;if(pendingLink&&!validLanding(FB.webAuth(),pendingLink)){pendingLink=null;notice('Invalid or foreign-project link. Request a fresh link explicitly.');}else if(pendingLink){notice('Link opened. Type the exact email that received this link, then choose Finish this sign-in link. Do not reload.');}controls();}});
FB.onUser(user=>{ $('status').textContent=user?'Account signed in. UID: '+user.uid+' · Email: '+user.email+' · Email verified: '+(user.emailVerified===true)+' · Organisation access remains server-controlled. No grant was created. Activation held; no delivery acknowledged.':'Signed out. Activation held; nothing acknowledged.';controls();});
if(hadLanding)history.replaceState(null,'',location.pathname+'#pair='+PINS.pair_sha256+'&release='+PINS.release_sha256);
$('sendLink').onclick=async()=>{
 if(!ready||busy||Date.now()<nextSend||sendCount>=3)return;
 const mail=ownerEmail();if(!mail)return;
 busy=true;sendCount++;nextSend=Date.now()+60000;controls();
 try{await sendSignInLinkToEmail(FB.webAuth(),mail,{url:'https://mhpss-nepal.github.io/form/review-5ws-noon-v35/releases/52dad24afe6888146208/review.html',handleCodeInApp:true});$('em').value='';notice('Check your email for the sign-in link. Delivery is not proven by this page. Open it, type the email again and choose Finish.');}
 catch(error){notice(safeFailure(error));}
 finally{busy=false;controls();setTimeout(controls,60000);}
};
$('finishLink').onclick=async()=>{
 if(!ready||busy||!pendingLink)return;
 const mail=ownerEmail();if(!mail)return;
 const link=pendingLink;pendingLink=null;busy=true;controls();
 try{await signInWithEmailLink(FB.webAuth(),mail,link);$('em').value='';notice('Link completed. Verified identity is shown below; no organisation access or grant was created.');}
 catch(error){notice(safeFailure(error));}
 finally{busy=false;controls();}
};
$('signout').onclick=async()=>{if(busy)return;busy=true;controls();try{await FB.signOut();notice('Signed out. Request a fresh link explicitly to sign in again.');}catch(_){notice('Sign-out unavailable. Reload to clear this memory-only sign-in.');}finally{busy=false;controls();}};
controls();

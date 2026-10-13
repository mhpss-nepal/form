/* Directory-only operational English fallback; no clinical translation changes. */
(function(){'use strict';const S=window.I18N_STRINGS;if(!S)return;
const labels={
'dir.banner':'FORM DIRECTORY',
'dir.bannerSub':' · Delivery and access differ by form. New operational labels are in English pending translation review.',
'dir.intro':'Eight instruments in one directory. Open the available forms below; the four source-held forms open their actual authored input in synthetic-only preview, not an empty dashboard.',
'dir.delivery':'<strong>Saving on a device is not server delivery.</strong> The 5Ws form saves a device copy; trusted delivery requires verified reporting access and a matching server receipt. Training requires verified sign-in and a matching server receipt. Other instruments are not connected for automatic delivery. Do not clear browser storage while delivery is uncertain.',
'ml.p028':'Intended for the coordination dashboard and national 5W. Delivery is confirmed only by a matching trusted server receipt; a device save alone does not feed the dashboard.',
'dir.copyHelp':'<strong>Copy link:</strong> share the selected form address. Sign-in and reporting approval depend on the instrument; sharing a link does not grant access.'};
const rows=[['training','Training & orientation','Separate approved training access is required to send reports.','Open form'],['contacts','Service contacts & referrals','Actual contact/referral input is inspectable with synthetic data only. Real collection awaits the approved locked organisation house and written basis.','Inspect form draft (synthetic only)'],['referrals','Referral outcomes','Actual follow-up input is inspectable with synthetic data only. Real collection remains held.','Inspect form draft (synthetic only)'],['providers','Provider registration','Actual registration input is inspectable with synthetic data only. Consent and publication review remain held.','Inspect form draft (synthetic only)'],['servicepoints','Service-point registration','Actual registration input is inspectable with synthetic data only. Consent and publication review remain held.','Inspect form draft (synthetic only)']];
for(const [key,title,status,action]of rows){labels['dir.'+key+'.tag']=key==='training'?'TRAINING':'AWAITING ACTIVATION';labels['dir.'+key+'.title']=title;labels['dir.'+key+'.status']=status;labels['dir.'+key+'.action']=action;}
for(const lang of ['en','ne']){S[lang]=S[lang]||{};Object.assign(S[lang],labels);}
})();

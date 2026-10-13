/* Directory-only operational English fallback; no clinical translation changes. */
(function(){'use strict';const S=window.I18N_STRINGS;if(!S)return;
const labels={
'dir.banner':'FORM DIRECTORY',
'dir.bannerSub':' · Delivery and access differ by form. New operational labels are in English pending translation review.',
'dir.intro':'Eight instruments in one directory. Open the available forms below; instruments awaiting activation link to their dashboard home.',
'dir.delivery':'<strong>Saving on a device is not server delivery.</strong> The new 5Ws form is device-only with export. Training requires verified sign-in and a matching server receipt. Other instruments are not connected for automatic delivery. Do not clear browser storage while delivery is uncertain.',
'dir.copyHelp':'<strong>Copy link:</strong> share the selected form address. Sign-in and reporting approval depend on the instrument; sharing a link does not grant access.'};
const rows=[['training','Training & orientation','Separate approved training access is required to send reports.','Open form'],['contacts','Service contacts & referrals','Individual collection is not activated.','Open dashboard home'],['referrals','Referral outcomes','Follow-up collection is not activated.','Open dashboard home'],['providers','Provider registration','Registration and publication review are not activated.','Open dashboard home'],['servicepoints','Service-point registration','Registration and publication review are not activated.','Open dashboard home']];
for(const [key,title,status,action]of rows){labels['dir.'+key+'.tag']=key==='training'?'TRAINING':'AWAITING ACTIVATION';labels['dir.'+key+'.title']=title;labels['dir.'+key+'.status']=status;labels['dir.'+key+'.action']=action;}
for(const lang of ['en','ne']){S[lang]=S[lang]||{};Object.assign(S[lang],labels);}
})();

/* Versioned directory-only English fallback; clinical translations are unchanged. */
(function(){'use strict';const S=window.I18N_STRINGS=window.I18N_STRINGS||{};
const labels={
'dir.open':'Open form',
'dir.copy':'Copy link',
'dir.qr':'QR',
'dir.banner':'FORM DIRECTORY',
'dir.bannerSub':' · Choose a form. Delivery status is shown separately.',
'dir.intro':'Seven workflows, eight instruments. Open a form, copy its link or show its QR code. Contacts and later referral outcomes share one interactive preview; nothing entered there is saved or sent.',
'dir.delivery':'<strong>Device saving is not server delivery.</strong> The 5Ws form saves a device copy and sends when signed in with approved reporting access; delivery is confirmed only by a matching server receipt. Retained pending reports require Retry after connectivity returns. Training requires verified sign-in and a matching server receipt. PHQ-9 and Self-report are not connected for automatic delivery. Provider and service-point registrations are private submissions, pending review; receipt does not publish or verify credentials. The contact/referral interactive preview cannot save or send information. Do not enter real personal information.',
'dir.offlineHelp':'<strong>Offline use:</strong> availability depends on the form and previously loaded assets. Review templates cannot retain entries. Offline delivery and installed-device updates have not been certified.',
'dir.provenance':'This directory has seven workflows covering eight instruments. Contact with referral initiation and later referral outcome share one workflow. Individual collection remains held; interactive preview is not approval to collect personal information.',
'dir.copyHelp':'<strong>Copy link:</strong> share the form or protected preview address. A shared link does not grant access to records.'};
const rows=[['training','Training & orientation','Verified training access is required to send a report.'],['contacts','Service contacts & referrals','Interactive preview: contact + referral, then later outcome. Not saved or sent. Do not enter real personal information.'],['referrals','Referral outcomes','Review only. Follow-up collection is not activated.'],['providers','Provider registration','Private registration. Verified sign-in required; credentials unverified and publication held.'],['servicepoints','Service-point registration','Private registration. Verified sign-in required; credentials unverified and publication held.']];
for(const [key,title,status]of rows){labels['dir.'+key+'.tag']=key==='training'?'TRAINING':['providers','servicepoints'].includes(key)?'PRIVATE REGISTRATION':'INTERACTIVE PREVIEW';labels['dir.'+key+'.title']=title;labels['dir.'+key+'.status']=status;}
for(const lang of ['en','ne']){S[lang]=S[lang]||{};Object.assign(S[lang],labels);}
window.DIRECTORY_STATUS_READY=true;
})();

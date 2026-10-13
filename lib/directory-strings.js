/* Directory-only English fallback; clinical translations are unchanged. */
(function(){'use strict';const S=window.I18N_STRINGS;if(!S)return;
const labels={
'dir.open':'Open form',
'dir.copy':'Copy link',
'dir.qr':'QR',
'dir.banner':'FORM DIRECTORY',
'dir.bannerSub':' · Choose a form. Delivery status is shown separately.',
'dir.intro':'Eight instruments. Open a form, copy its link or show its QR code. Templates marked review only do not collect information.',
'dir.delivery':'<strong>Device saving is not server delivery.</strong> The 5Ws form currently saves on this device with export. Training requires verified sign-in and a matching server receipt. PHQ-9 and Self-report are not connected for automatic delivery. The four review templates cannot save or send information.',
'dir.offlineHelp':'<strong>Offline use:</strong> availability depends on the form and previously loaded assets. Review templates cannot retain entries. Offline delivery and installed-device updates have not been certified.',
'dir.provenance':'This directory includes eight instruments. Four open read-only source templates; their collection is not activated. Template availability is not approval for collecting individual information.',
'dir.copyHelp':'<strong>Copy link:</strong> share the form or read-only template address. A shared link does not grant access to records.'};
const rows=[['training','Training & orientation','Verified training access is required to send a report.'],['contacts','Service contacts & referrals','Review only. Individual collection is not activated.'],['referrals','Referral outcomes','Review only. Follow-up collection is not activated.'],['providers','Provider registration','Review only. Registration and publication are not activated.'],['servicepoints','Service-point registration','Review only. Registration and publication are not activated.']];
for(const [key,title,status]of rows){labels['dir.'+key+'.tag']=key==='training'?'TRAINING':'TEMPLATE REVIEW';labels['dir.'+key+'.title']=title;labels['dir.'+key+'.status']=status;}
for(const lang of ['en','ne']){S[lang]=S[lang]||{};Object.assign(S[lang],labels);}
})();

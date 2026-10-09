/* Runs synchronously before any iframe/config/SDK fetch. No URL is persisted. */
(()=>{'use strict';
let landing=null;
const u=new URL(location.href),hasAuth=['oobCode','mode','apiKey','continueUrl','email'].some(k=>u.searchParams.has(k));
if(hasAuth){
 landing=u.href;
 // Drop every query field and untrusted fragment: no stale release pin survives a link.
 history.replaceState(null,'',u.pathname);
}
Object.defineProperty(window,'EMAIL_LINK_BOOT',{value:Object.freeze({take(){const value=landing;landing=null;return value;}}),configurable:true});
})();

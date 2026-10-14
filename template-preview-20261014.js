/* Memory-only question preview. No writer runtime, storage, auth, Firebase or export. */
(function () {
  'use strict';
  function stop(e) { e.preventDefault(); e.stopImmediatePropagation(); }
  document.addEventListener('submit', stop, true);
  // Native submit() bypasses events; fence it as well as requestSubmit().
  HTMLFormElement.prototype.submit = function () {};
  HTMLFormElement.prototype.requestSubmit = function () {};
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) stop(e);
  }, true);
  window.mountTemplateReview = function (kind) {
    var interactive = kind === 'contact' || kind === 'referral-outcome';
    var C = window.CODES, lists = window.REVIEW_LISTS;
    var lang = new URLSearchParams(location.search).get('lang') === 'ne' ? 'ne' : 'en';
    var $ = function (id) { return document.getElementById(id); };
    // Keep original English fallback text, not a translation of a translation.
    var originals = new Map();
    document.querySelectorAll('[data-i18n]').forEach(function (el) { originals.set(el, el.innerHTML); });
    function label(it) { return lang === 'ne' && it.np ? it.np : it.name; }
    function fill(id, items, value) {
      var el = $(id); if (!el || !items) return;
      el.replaceChildren();
      var ph = document.createElement('option'); ph.textContent = '—'; ph.value = ''; el.append(ph);
      items.forEach(function (it) {
        var op = document.createElement('option'); op.value = it[value || 'code']; op.textContent = label(it); el.append(op);
      });
    }
    function checks(id, items) {
      var el = $(id); if (!el) return;
      el.replaceChildren();
      items.forEach(function (it) {
        var l = document.createElement('label'); l.className = 'chk';
        var i = document.createElement('input'); i.type = 'checkbox'; i.value = it.code; i.disabled = true;
        var s = document.createElement('span'); s.textContent = label(it); l.append(i, s); el.append(l);
      });
    }
    function paint() {
      document.documentElement.lang = lang;
      originals.forEach(function (html, el) {
        var key = el.getAttribute('data-i18n');
        var text = (window.I18N_STRINGS[lang] || {})[key];
        if (text) { if (el.hasAttribute('data-i18n-html')) el.innerHTML = text; else el.textContent = text; }
        else el.innerHTML = html;
      });
      fill('org', (kind==='contact' || kind==='referral-outcome') ? C.ORGS.concat([{code:'OTHER',name:'Other — not listed',np:'अन्य — सूचीमा नभएको'}]) : C.ORGS);
      fill('cadre', C.CADRES.filter(function(i){return !i.retired;}));
      fill('district', C.DISTRICTS); fill('palika', C.PALIKAS, 'pcode');
      fill('site', C.FORM_SITES.concat([{code:'OTHER',name:'Other — not on the roster'}]));
      fill('tgroup', C.TARGET_GROUPS); fill('modality', C.MODALITIES.filter(function(i){return !i.retired;}));
      fill('province', Array.from(new Set(C.DISTRICTS.map(function(i){return i.province;}).filter(Boolean))).map(function(p){return {code:p,name:p};}));
      fill('service', lists.SERVICES); fill('reason', lists.REASONS);
      fill('orgType', lists.ORG_TYPES); fill('access', lists.ACCESS); fill('cost', lists.COST);
      if (kind === 'provider-register' || kind === 'service-point') {
        // Exactly the source filter, grouping and ordering for service choices.
        var box = $('svcs'); box.replaceChildren();
        C.ACTIVITY_GROUPS.forEach(function (g) {
          var items = C.ACTIVITIES.filter(function(a){return a.group === g.code && !a.retired && (!a.other || a.code === '9');});
          if (!items.length) return;
          var h = document.createElement('div'); h.className = 'hint'; h.style.flex = '0 0 100%'; h.textContent = label(g); box.append(h);
          items.sort(function(a,b){return label(a).localeCompare(label(b));});
          items.forEach(function(a){var l=document.createElement('label'); l.className='chk'; var i=document.createElement('input'); i.type='checkbox'; i.value=a.code; i.disabled=true; var s=document.createElement('span'); s.textContent=label(a); l.append(i,s); box.append(l);});
        });
        checks('cadres', C.CADRES.filter(function(i){return !i.retired;})); checks('tgs', C.TARGET_GROUPS); checks('a11y', lists.A11Y || []);
      }
      document.querySelectorAll('.review-options').forEach(function(el){el.remove();});
      if (!interactive) document.querySelectorAll('select').forEach(function(el){
        var details=document.createElement('details'); details.className='review-options';
        var summary=document.createElement('summary'); summary.textContent='Options';
        var list=document.createElement('ul');
        Array.from(el.options).filter(function(op){return op.value;}).forEach(function(op){var li=document.createElement('li');li.textContent=op.textContent;list.append(li);});
        details.append(summary,list);el.after(details);
      });
      // Exact local navigation allowlist, including translated HTML links.
      // No global click interceptor: ordinary anchors work in WebKit too.
      var safe = {'index.html':'../index.html','../index.html':'../index.html','../../hub/':'../../hub/','../hub/':'../../hub/','4ws-report.html':'../5ws-report.html','5ws-report.html':'../5ws-report.html','../5ws-report.html':'../5ws-report.html','contact.html':'contact.html','referral-outcome.html':'referral-outcome.html','../drafts/contact.html':'contact.html','../drafts/referral-outcome.html':'referral-outcome.html'};
      document.querySelectorAll('a').forEach(function(a){
        var href=a.getAttribute('href'); if (!href || href.startsWith('#')) return;
        if (Object.prototype.hasOwnProperty.call(safe,href)) { a.setAttribute('href',safe[href]); a.target='_top'; }
        else a.removeAttribute('href');
      });
      document.querySelectorAll('input,select,textarea').forEach(function(el){el.disabled=!interactive;el.autocomplete='off';});
      // Writer, export, geolocation and pseudonym actions remain disabled.
      document.querySelectorAll('button:not([data-review-lang]):not([data-review-reset])').forEach(function(el){el.disabled=true;});
      document.querySelectorAll('[data-review-lang]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.reviewLang===lang));});
      if (interactive) {
        var notice = lang==='ne' ? 'अन्तरक्रियात्मक पूर्वावलोकन — सुरक्षित वा पठाइँदैन। वास्तविक व्यक्तिगत जानकारी नलेख्नुहोस्। बचत, पठाउने, निर्यात, स्थान र सम्पर्क कोड उत्पादन बन्द छन्।' : 'Interactive preview — not saved or sent. Do not enter real personal information. Saving, sending, export, location and contact-code generation remain disabled.';
        document.querySelector('[data-preview-notice]').textContent=notice;
        // Source delivery descriptions must not masquerade as preview behavior.
        ['svc.p009','svc.p040','svc.p055'].forEach(function(key){var el=document.querySelector('[data-i18n="'+key+'"]');if(el)el.textContent=notice;});
        if ($('codeOut')) $('codeOut').textContent=lang==='ne'?'पूर्वावलोकनमा सम्पर्क कोड बनाइँदैन।':'Contact-code generation is not activated in preview.';
        if ($('clearBtn')) { $('clearBtn').textContent=lang==='ne'?'उपकरणको भण्डारण मेटाउने सुविधा बन्द छ':'Device storage deletion is disabled'; }
        document.querySelector('[data-review-reset]').textContent=lang==='ne'?'हालको पूर्वावलोकन खाली गर्नुहोस्':'Clear current preview';
        conditions();
      }
    }
    function conditions() {
      [['orgOtherWrap','org','OTHER'],['siteOtherWrap','site','OTHER']].forEach(function(x){if($(x[0]) && $(x[1])) $(x[0]).hidden=$(x[1]).value!==x[2];});
      if ($('refCard')) $('refCard').hidden=!($('outcome').value==='REFER' || $('service').value==='REFO');
    }
    document.addEventListener('change',function(){if(interactive)conditions();});
    document.querySelectorAll('[data-review-reset]').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('form').forEach(function(f){f.reset();});conditions();});});
    document.querySelectorAll('[data-review-lang]').forEach(function(b){b.addEventListener('click',function(){
      var values=Array.from(document.querySelectorAll('input,select,textarea')).map(function(el){return [el,el.value,el.checked];});
      lang=b.dataset.reviewLang;paint();values.forEach(function(v){v[0].value=v[1];v[0].checked=v[2];});conditions();
    });});
    // Leaving or returning from the back/forward cache clears ephemeral examples.
    if(interactive) window.addEventListener('pagehide',function(){document.querySelectorAll('form').forEach(function(f){f.reset();});});
    paint();
  };
})();

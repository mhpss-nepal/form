/* Only the two age keys needed by selfreport. Preserve shared/clinical keys.
   Source: 3f89f6ed118398efeb71fe3219d8f0988088fac1:lib/strings.js.
   Nepali numerals copied from source; no new clinical translation. */
(function () {
  "use strict";
  var S = window.I18N_STRINGS;
  if (!S) return;
  var age = {en: {"sr.age.10to17":"10–17", "sr.age.18to59":"18–59"},
             ne: {"sr.age.10to17":"१०–१७", "sr.age.18to59":"१८–५९"}};
  ["en","ne"].forEach(function(lang) {
    if (!S[lang]) return;
    Object.keys(age[lang]).forEach(function(k) {
      if (S[lang][k] == null || S[lang][k] === "") S[lang][k] = age[lang][k];
    });
  });
})();

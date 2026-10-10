/* =====================================================================
   Attribution band — MHPSS Nepal
   ---------------------------------------------------------------------
   TO TURN THE EMBLEMS ON: put the official files in assets/ and set the
   two paths below. Nothing else needs changing — every page that loads
   this file picks them up.

       who:  "assets/logo-who-nepal.png"
       mohp: "assets/logo-mohp-edcd.png"

   Leave them null and the band shows a written credit instead, which is
   what it does now.

   USE ONLY FILES SUPPLIED BY THE ORGANISATIONS THEMSELVES.
   WHO Nepal's public notice on unauthorised use of the WHO logo states
   that it "may only be used with the express written permission of the
   WHO", that its use "implies endorsement by the WHO", and that use is
   restricted to bodies with official collaborating status, in
   conjunction with work undertaken with WHO. A logo taken from a web
   search is the wrong file at the wrong resolution without that
   permission, and it lands on the person who published the page.

   The paths are a flag rather than an <img> that fails quietly on
   purpose: a missing file would 404 on every page load and fill the
   console with errors that hide real ones.
   ===================================================================== */
window.BRAND = {
  who:  null,
  mohp: null,

  /* Set by the page: "" at the repo root, "../" one level down. */
  prefix: (window.BRAND_PREFIX || "")
};

/* The ministry's name, verified 16 September 2026 from the government's own
   sites: mohp.gov.np prints "Ministry of Health and Food Safety Nepal" and
   edcd.gov.np gives its parent ministry as "Ministry of Health and Food
   Safety". The abbreviation the ministry still uses for itself is MoHP, and
   its domain is still mohp.gov.np -- so "MoHP" is right and "MoHFS" is not
   what they call themselves. "Ministry of Health and Population" is the old
   name; do not put it back. */
(function () {
  "use strict";
  var B = window.BRAND, P = B.prefix;

  function mark(src, alt) {
    return '<img class="mark" src="' + P + src + '" alt="' + alt + '">';
  }
  function credit(name, role) {
    return '<div class="slot">' + role + '<span>' + name + '</span></div>';
  }

  function html() {
    return '' +
      '<div class="who">' +
        '<b>Developed for the MHPSS Technical Working Group</b>, Rasuwa / Bhote Koshi flood ' +
        'response, with support from WHO Nepal and in coordination with the Ministry of Health ' +
        'and Food Safety — Epidemiology and Disease Control Division.' +
      '</div>' +
      '<div class="marks">' +
        (B.who  ? mark(B.who,  "WHO Nepal")
                : credit("WHO Nepal", "with the support of")) +
        (B.mohp ? mark(B.mohp, "Ministry of Health and Food Safety — EDCD")
                : credit("MoHP &middot; EDCD", "in coordination with")) +
      '</div>';
  }

  function mount() {
    var el = document.querySelector(".attrib");
    if (!el) return;
    el.innerHTML = html();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else { mount(); }
})();

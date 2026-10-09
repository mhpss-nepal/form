/* =====================================================================
   MHPSS Nepal — line icons
   ---------------------------------------------------------------------
   Inline SVG, stroke-based, 24x24, drawn here. No icon font and no CDN:
   the field forms have to render with no signal, and an icon font that
   fails to load leaves boxes or nothing at all.

   These replace the emoji the pages were using. Emoji were a large part
   of why the site looked like a draft rather than a Ministry product:
   they render differently on every platform, they carry a tone nobody
   chose, and at small sizes several of them are unreadable.

   ICON(name, size) returns the SVG string; any element with
   data-icon="name" is filled automatically. currentColor throughout, so
   an icon takes the colour of whatever it sits in.
   ===================================================================== */
(function () {
  "use strict";

  var P = {
    /* coordination: three nodes meeting at a table */
    coord:   '<circle cx="6" cy="7" r="2.4"/><circle cx="18" cy="7" r="2.4"/>' +
             '<circle cx="12" cy="18" r="2.4"/><path d="M7.7 8.6 10.6 16M16.3 8.6 13.4 16M8.4 7h7.2"/>',
    /* technical resources: a book */
    book:    '<path d="M4 5.2A1.6 1.6 0 0 1 5.6 3.6H11v15.8H5.6A1.6 1.6 0 0 0 4 21V5.2Z"/>' +
             '<path d="M20 5.2a1.6 1.6 0 0 0-1.6-1.6H13v15.8h5.4A1.6 1.6 0 0 1 20 21V5.2Z"/>',
    /* information management: bars rising */
    chart:   '<path d="M4 20h16"/><rect x="5.5" y="12" width="3.4" height="5.6" rx=".8"/>' +
             '<rect x="10.3" y="8" width="3.4" height="9.6" rx=".8"/>' +
             '<rect x="15.1" y="4.6" width="3.4" height="13" rx=".8"/>',
    /* field forms: a clipboard */
    form:    '<rect x="5" y="4.4" width="14" height="16.2" rx="2"/>' +
             '<path d="M9 4.4V3.2h6v1.2"/><path d="M8.6 10h6.8M8.6 13.4h6.8M8.6 16.8h4"/>',
    /* dashboard / coverage: a grid with one cell marked */
    grid:    '<rect x="3.6" y="3.6" width="7.2" height="7.2" rx="1.4"/>' +
             '<rect x="13.2" y="3.6" width="7.2" height="7.2" rx="1.4"/>' +
             '<rect x="3.6" y="13.2" width="7.2" height="7.2" rx="1.4"/>' +
             '<path d="M14.4 16.8l2 2 3.6-4"/>',
    /* governance / who can see what: a shield */
    shield:  '<path d="M12 3.2 19.2 6v5.4c0 4.3-2.9 7.6-7.2 9.4-4.3-1.8-7.2-5.1-7.2-9.4V6L12 3.2Z"/>' +
             '<path d="M9.4 12.2l1.9 1.9 3.5-3.7"/>',
    /* method: a compass / direction */
    method:  '<circle cx="12" cy="12" r="8.4"/><path d="M15.2 8.8l-2 4.6-4.6 2 2-4.6 4.6-2Z"/>',
    /* a site / holding centre: a pin */
    pin:     '<path d="M12 21.2s6.4-5.4 6.4-10A6.4 6.4 0 0 0 5.6 11.2c0 4.6 6.4 10 6.4 10Z"/>' +
             '<circle cx="12" cy="10.8" r="2.3"/>',
    /* people reached */
    people:  '<circle cx="9" cy="8.2" r="3"/><path d="M3.8 20c0-3.1 2.3-5.4 5.2-5.4s5.2 2.3 5.2 5.4"/>' +
             '<path d="M16 5.6a3 3 0 0 1 0 5.6M17.4 14.9c1.7.7 2.8 2.3 2.8 4.3"/>',
    /* offline / no signal */
    offline: '<path d="M2.6 8.6a14 14 0 0 1 18.8 0"/><path d="M6.2 12.4a9 9 0 0 1 11.6 0"/>' +
             '<path d="M9.4 16a4.4 4.4 0 0 1 5.2 0"/><circle cx="12" cy="19.6" r="1.1" fill="currentColor" stroke="none"/>' +
             '<path d="M3.4 3.4 20.6 20.6" stroke-width="2.1"/>',
    /* a calendar / reporting cycle */
    cycle:   '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20.4 3.6v4.2h-4.2"/>',
    /* language */
    lang:    '<circle cx="12" cy="12" r="8.4"/><path d="M3.6 12h16.8"/>' +
             '<path d="M12 3.6c2.4 2.3 3.6 5.1 3.6 8.4S14.4 18.1 12 20.4c-2.4-2.3-3.6-5.1-3.6-8.4S9.6 5.9 12 3.6Z"/>',
    /* mail / contact */
    mail:    '<rect x="3.2" y="5.4" width="17.6" height="13.2" rx="2"/><path d="M3.8 6.8 12 13l8.2-6.2"/>'
  };

  function ICON(name, size) {
    var d = P[name];
    if (!d) return "";
    size = size || 20;
    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" ' +
      'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" ' +
      'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">' + d + '</svg>';
  }

  function paint() {
    var els = document.querySelectorAll("[data-icon]");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.getAttribute("data-icon-done")) continue;
      var out = ICON(el.getAttribute("data-icon"),
                     parseInt(el.getAttribute("data-icon-size"), 10) || 20);
      if (out) { el.innerHTML = out; el.setAttribute("data-icon-done", "1"); }
      else { try { console.warn("[icons] no such icon:", el.getAttribute("data-icon")); } catch (e) {} }
    }
  }

  window.ICON = ICON;
  window.ICON_NAMES = Object.keys(P);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", paint);
  else paint();
})();

/* =====================================================================
   MHPSS Nepal — the mark
   ---------------------------------------------------------------------
   WHY THIS EXISTS AT ALL
   The site had no visual identity, which for a country-level coordination
   product reads as a draft. It also cannot borrow one: the WHO emblem
   needs express written permission, and the Nepal national emblem belongs
   to the Ministry. Using either without that would be worse than plain.

   So this is an ORIGINAL mark, drawn here, owned by nobody else. It says
   the two things the product is actually about:

     · three stacked bands  = the three layers (field, coordination,
                              public) -- the architecture, and the reason
                              anything on this site can be trusted to
                              come from somewhere
     · two peaks rising out of them
                            = Rasuwa / Bhote Koshi. Also, read the other
                              way, two shapes meeting at one line: the
                              health and protection tracks at one table,
                              which is the whole point of the Technical Working Group

   Drawn as inline SVG, not an image file: it renders with no signal, it
   stays sharp at any size, it costs one HTTP request of nothing, and it
   cannot 404. Legible down to 20px -- the bands are 2px apart at 40px,
   which is why they are bands and not hairlines.

   MARK(size, opts) returns the SVG string.
     opts.mono   true  -> single colour, for a dark background
     opts.flat   true  -> no gradient (print, and any context where a
                          gradient bands badly)
   ===================================================================== */
(function () {
  "use strict";

  function MARK(size, opts) {
    size = size || 40;
    opts = opts || {};
    var id = "mkg" + Math.random().toString(36).slice(2, 8);

    /* MONO is not "the same drawing in white" -- a white glyph on a white
       tile is nothing, which is exactly what the first version rendered.
       On a dark background the tile is dropped entirely and the glyph
       itself carries the shape. */
    var mono = !!opts.mono;
    var tileFill = opts.flat ? "#009fe3" : "url(#" + id + ")";
    var glyph = mono ? "#fff" : "#fff";
    /* the notch has to contrast with whatever the glyph sits on */
    var notch = mono ? "rgba(255,255,255,.30)" : "#004969";

    return '' +
    '<svg class="mk" width="' + size + '" height="' + size + '" viewBox="0 0 48 48" ' +
         'role="img" aria-label="MHPSS Nepal" xmlns="http://www.w3.org/2000/svg">' +
      (mono || opts.flat ? '' :
        '<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#00a4eb"/><stop offset=".55" stop-color="#009fe3"/>' +
        '<stop offset="1" stop-color="#006996"/></linearGradient></defs>') +
      (mono ? '' : '<rect x="0" y="0" width="48" height="48" rx="11" fill="' + tileFill + '"/>') +
      /* two peaks, one taller, meeting on a shared line */
      '<path d="M8 28.5 L18.5 12.5 L25.2 22.5 L30 16 L40 28.5 Z" ' +
            'fill="' + glyph + '" fill-opacity=".97"/>' +
      /* the notch that keeps them reading as TWO peaks, not one ridge */
      '<path d="M25.2 22.5 L30 16 L27.6 12.8 L22.8 19.3 Z" fill="' + notch + '"/>' +
      /* three bands = three layers, widest at the base, 2px apart so they
         stay separate at 20px rather than blurring into one block */
      '<rect x="8"    y="31.6" width="32" height="3.2" rx="1.6" fill="' + glyph + '" fill-opacity=".95"/>' +
      '<rect x="11.5" y="36.4" width="25" height="3.2" rx="1.6" fill="' + glyph + '" fill-opacity=".70"/>' +
      '<rect x="15.5" y="41.2" width="17" height="3.2" rx="1.6" fill="' + glyph + '" fill-opacity=".46"/>' +
    '</svg>';
  }

  /* Fill every [data-mark] element on the page. The attribute value is the
     pixel size; data-mark-mono / data-mark-flat switch the variants. */
  function paint() {
    var els = document.querySelectorAll("[data-mark]");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.getAttribute("data-mark-done")) continue;
      el.innerHTML = MARK(parseInt(el.getAttribute("data-mark"), 10) || 40, {
        mono: el.hasAttribute("data-mark-mono"),
        flat: el.hasAttribute("data-mark-flat")
      });
      el.setAttribute("data-mark-done", "1");
    }
  }

  /* The field and hub pages share one dark chrome bar, .top, built before
     there was a mark. Rather than editing ten files, the mark is slipped
     in here.

     The first version of this assumed .brand was a direct child of .top
     and called top.insertBefore(mark, brand). On every real page .brand
     sits inside a wrapper div, so that threw NotFoundError and the mark
     appeared on none of them -- caught by rendering the pages, not by
     reading the code. It now inserts relative to whatever the brand's
     actual parent is, and does nothing at all if it cannot find a place,
     because a missing logo is a blemish and a thrown error stops the rest
     of the script. */
  function adoptTop() {
    var tops = document.querySelectorAll(".top");
    for (var i = 0; i < tops.length; i++) {
      var t = tops[i];
      if (t.querySelector("svg.mk")) continue;
      var brand = t.querySelector(".brand");
      if (!brand) continue;
      /* the block that holds brand + sub -- usually a wrapper div, but the
         brand itself if there is no wrapper */
      var block = (brand.parentNode && brand.parentNode !== t) ? brand.parentNode : brand;
      if (!block.parentNode) continue;
      var holder = document.createElement("span");
      holder.className = "mkslot";
      holder.innerHTML = MARK(34);
      try {
        block.parentNode.insertBefore(holder, block);
        if (block !== brand) block.classList.add("brandbox");
      } catch (e) {
        try { console.warn("[mark] could not place the mark:", e.message); } catch (e2) {}
      }
    }
  }

  /* The coordination view has its own masthead with a .mark tile whose
     content is the placeholder text "MH". Replace it with the real mark. */
  function adoptMast() {
    var els = document.querySelectorAll(".mast .mark, .mark");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.querySelector("svg.mk")) continue;
      var txt = (el.textContent || "").trim();
      /* only take over a placeholder -- never something with real content */
      if (txt.length > 4) continue;
      el.textContent = "";
      el.innerHTML = MARK(38);
      el.classList.add("mkslot");
    }
  }

  window.MARK = MARK;
  function boot() { paint(); adoptTop(); adoptMast(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }
})();

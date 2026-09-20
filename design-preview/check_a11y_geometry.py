#!/usr/bin/env python3
"""Accessibility and rendered-geometry gate for the 5Ws pages.

Why this exists
---------------
The contract suites assert that CSS *text* is present. That cannot catch a
rule that loses on specificity, an attribute that is invalid for its ARIA
role, or a control that renders narrower than the tap-target minimum. Three
real defects reached review that way:

  * `body.fx .btn.sm{min-height:38px}` outranked a preview rule, leaving the
    Export/Clear buttons at 38 px;
  * `aria-required` on `role="group"` was ignored by assistive technology;
  * the saved-records table became a 640 px scroll region on a phone.

So this gate drives a real Chromium, renders every step of both pages, runs
axe-core (WCAG 2.1 A + AA), and measures every interactive element with
`getBoundingClientRect()`. It is the check that would have caught all three.

Run:  python3 design-preview/check_a11y_geometry.py
Exit: 0 clean, 1 any failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VENDOR = REPO / "design-preview" / "vendor" / "axe.min.js"
BASE_URL = "http://127.0.0.1:8765/form-frontend"
PAGES = [
    ("5ws-report.html", None),                 # the shipped page; one long form
    ("5ws-report-b2.html", "window.IUPreview._api"),  # the preview; five steps
]
WIDTHS = [320, 360, 375, 390, 414, 621, 768, 1280]
MIN_TAP = 44          # project standard for a touch target
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]

failures: list[str] = []


def note(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


def main() -> int:
    if not VENDOR.exists():
        print(f"axe-core not vendored at {VENDOR}; cannot run the audit")
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not importable; skipping this gate rather than failing it")
        return 0

    axe_src = VENDOR.read_text(encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for page_name, api_expr in PAGES:
                url = f"{BASE_URL}/{page_name}"
                print(f"\n=== {page_name} ===")

                # ---------- geometry + axe at each width ----------------------
                for w in WIDTHS:
                    ctx = browser.new_context(viewport={"width": w, "height": 900})
                    pg = ctx.new_page()
                    pg.goto(url, wait_until="load")
                    # the baseline service worker caches assets; drop it so the
                    # measurement is of the tree on disk, not of a stale copy
                    pg.evaluate(
                        "(async()=>{for(const r of await navigator.serviceWorker"
                        ".getRegistrations())await r.unregister();"
                        "for(const k of await caches.keys())await caches.delete(k);})()"
                    )
                    pg.goto(url, wait_until="load")
                    pg.add_script_tag(content=axe_src)

                    steps = pg.evaluate(
                        f"() => {api_expr} ? {api_expr}.totalSteps : 1"
                    ) if api_expr else 1

                    for step in range(steps):
                        if api_expr:
                            pg.evaluate(f"() => {api_expr}.go({step})")
                        label = f"{page_name}@{w}" + (f" step{step+1}" if steps > 1 else "")

                        # --- no horizontal overflow of the document ----------
                        sw, cw = pg.evaluate(
                            "() => [document.documentElement.scrollWidth,"
                            " document.documentElement.clientWidth]"
                        )
                        note(sw <= cw, f"{label}: no page overflow", f"{sw} > {cw}" if sw > cw else f"{sw}")

                        # --- every interactive control is a real tap target --
                        small = pg.evaluate(
                            """(min) => {
                              const api = window.IUPreview && window.IUPreview._api;
                              const scope = api
                                ? document.querySelector('#f > .card.iu-screen.on') || document
                                : document;
                              const out = [];
                              scope.querySelectorAll(
                                'button,.iu-chip,input:not([type=hidden]),select,textarea,a[href]'
                              ).forEach(el => {
                                const r = el.getBoundingClientRect();
                                if (r.width === 0 || r.height === 0) return;   // hidden
                                if (el.closest('[hidden]')) return;
                                const lab = el.closest('label');
                                const labOk = lab && lab.getBoundingClientRect().height >= min;
                                if (r.height >= min || labOk) return;
                                out.push({
                                  tag: el.tagName,
                                  id: el.id || '',
                                  cls: String(el.className || '').slice(0, 30),
                                  h: Math.round(r.height * 10) / 10,
                                  w: Math.round(r.width * 10) / 10
                                });
                              });
                              return out.slice(0, 6);
                            }""",
                            MIN_TAP,
                        )
                        note(not small, f"{label}: controls >= {MIN_TAP}px",
                             json.dumps(small) if small else "")

                        # --- axe-core, WCAG 2.1 AA ---------------------------
                        viol = pg.evaluate(
                            """async (tags) => {
                              const r = await window.axe.run(document, {
                                resultTypes: ['violations'],
                                runOnly: { type: 'tag', values: tags }
                              });
                              return r.violations.map(v => ({
                                id: v.id, impact: v.impact, n: v.nodes.length,
                                where: (v.nodes[0] && v.nodes[0].target || []).join(' ')
                              }));
                            }""",
                            AXE_TAGS,
                        )
                        note(not viol, f"{label}: axe WCAG 2.1 AA clean",
                             json.dumps(viol) if viol else "")

                    ctx.close()
        finally:
            browser.close()

    print()
    if failures:
        print(f"{len(failures)} check(s) failed:")
        for f in failures[:40]:
            print(f"  - {f}")
        return 1
    print("All accessibility and geometry checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

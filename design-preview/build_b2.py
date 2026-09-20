#!/usr/bin/env python3
"""Build the B2 "Institutional App" preview page from the committed 5Ws page.

Why a builder instead of hand-editing HTML:
  The B2 preview must never drift from the real form. Deriving the page from a
  specific commit makes that guarantee mechanical — the <form> block and every
  runtime <script> are copied byte-for-byte, so no field id, name, value list,
  listener or submit contract can be altered by accident.

What it changes:
  · the surrounding chrome (header, step rail, status strip) — presentation only
  · the stylesheet link and one extra script tag for the preview layer
  · content-hashed asset URLs, so a browser can never serve a stale preview asset

What it must never change:
  · the <form> block
  · the page's own <script> tags (store.js, fb.js, codes.js, i18n.js, pwa.js …)
  · the Save/Clear action row (it is moved into the last screen by the preview
    script at runtime, not rewritten here)

Usage:  python3 design-preview/build_b2.py [git-ref]
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DP = REPO / "design-preview"
OUT = REPO / "5ws-report-b2.html"
SOURCE = "5ws-report.html"


def git_show(path: str, ref: str) -> str:
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=REPO,
        capture_output=True, text=True, check=True,
    ).stdout


def stamp(name: str) -> str:
    """Content-hashed URL: changes whenever the file changes, so no stale asset."""
    h = hashlib.sha256((DP / name).read_bytes()).hexdigest()[:10]
    return f"design-preview/{name}?h={h}"


BODY = """<body class="fx iu" data-iu-preview="B2">

<div class="iu-previewbar" role="note">
  <b>B2 Institutional App &mdash; design preview.</b>
  Demonstration / non-identifiable data only. New interface copy is English pending human-reviewed Nepali wording.
</div>

<header class="iu-top">
  <button type="button" class="iu-back" data-iu-back>&#8249; All forms</button>
  <div class="iu-brandwrap">
    <div class="iu-brand">MHPSS Activity Report</div>
    <div class="iu-brandsub">Rasuwa &ndash; Bhote Koshi flood response</div>
  </div>
  <!-- The bilingual engine mounts its ENG / NEP switch into this slot. It must
       stay a [data-i18n-toggle] slot and must NOT be given id="i18nbar": the
       engine skips mounting when an element with that id already exists. -->
  <div class="iu-lang" data-i18n-toggle></div>
</header>

<main class="iu-main">
  <div class="iu-sync" id="iuSyncStatus" role="status" aria-live="polite" aria-atomic="true" data-state="waiting">
    <b>Checking device and connection state&hellip;</b>
    <span>Checking device and connection state&hellip;</span>
  </div>

__FORM__

__ACTIONS__

  <section class="iu-saved">
__SAVED__
  </section>
</main>

<script src="__STATUS__"></script>
__SCRIPTS__
</body>
</html>
"""


def build(ref: str | None = None) -> Path:
    ref = ref or subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO,
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    src = git_show(SOURCE, ref)

    head = src[: src.index("<body")]
    m = re.search(r'<form id="f"[\s\S]*?</form>', src)
    if not m:
        raise SystemExit("could not locate the <form id=\"f\"> block")
    form = m.group(0)
    tail = src[m.end(): src.index("</body>")]

    # Direction B's preview layer is replaced, not inherited.
    head = re.sub(r'\n<style id="institutional-utility-preview">[\s\S]*?</style>\n', "\n", head)
    tail = re.sub(r'<script id="institutional-utility-status">[\s\S]*?</script>\n?', "", tail)

    # The source page declares its own language default (data-i18n-default="ne")
    # because it is the trial form and is fully translated. This derived preview
    # is NOT: its own chrome (the B2 banner, the status strip) is English-only
    # until the new copy has human-reviewed Nepali. A page that is not fully
    # translated must not default to Nepali, so the declaration is stripped from
    # the copied <head>. Without this the rebuild would silently inherit it.
    head = re.sub(r'\s+data-i18n-default="[^"]*"', "", head, count=1)

    # Keep the page's own runtime scripts untouched.
    cut = tail.index("<script")
    tail_markup, tail_scripts = tail[:cut], tail[cut:]

    act_m = re.search(r'<div class="actions">[\s\S]*?</div>\s*', tail_markup)
    actions = act_m.group(0) if act_m else ""
    saved = tail_markup[act_m.end():] if act_m else tail_markup

    head = head.replace(
        '<link rel="stylesheet" href="../hub/assets/form.css">',
        '<link rel="stylesheet" href="../hub/assets/form.css">\n'
        f'<link rel="stylesheet" href="{stamp("5ws-preview.css")}">',
    ).replace(
        "</head>",
        f'<script src="{stamp("5ws-preview-core.js")}"></script>\n</head>',
    )

    html = (
        head
        + BODY.replace("__FORM__", form)
              .replace("__ACTIONS__", actions)
              .replace("__SAVED__", saved)
              .replace("__SCRIPTS__", tail_scripts)
              .replace("__STATUS__", stamp("5ws-preview-status.js"))
    )
    OUT.write_text(html, encoding="utf-8")

    # --- self-checks: refuse to write a page that violated the contract -------
    new = OUT.read_text(encoding="utf-8")
    m2 = re.search(r'<form id="f"[\s\S]*?</form>', new)
    if not m2 or hashlib.sha256(form.encode()).hexdigest() != hashlib.sha256(m2.group(0).encode()).hexdigest():
        raise SystemExit("BUILD FAILED: the <form> block is not byte-identical")
    ids = re.findall(r'\bid="([^"]+)"', new)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"BUILD FAILED: duplicate ids {dupes}")
    # The language slot must be a [data-i18n-toggle] slot, never id="i18nbar":
    # the engine skips mounting when that id already exists. Inspect elements
    # only, so an explanatory comment cannot satisfy or trip this check.
    if re.search(r'<[a-zA-Z][^>]*\bid="i18nbar"', new):
        raise SystemExit("BUILD FAILED: the language slot must not own id=i18nbar")
    if not re.search(r'<[a-zA-Z][^>]*\bdata-i18n-toggle\b', new):
        raise SystemExit("BUILD FAILED: no [data-i18n-toggle] slot for the language switch")
    for asset in ("codes.js", "store.js", "fb.js", "i18n.js", "pwa.js"):
        if asset not in new:
            raise SystemExit(f"BUILD FAILED: runtime asset {asset} missing")

    return OUT


if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    p = build(ref)
    print(f"built {p.relative_to(REPO)} from {ref or 'HEAD'}")

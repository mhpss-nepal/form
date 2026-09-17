#!/usr/bin/env python3
"""
MHPSS Nepal -- the offline-completeness check
=============================================
The field form is meant to work with no signal. That only holds if every
file the form NEEDS is in the service worker's precache list. The fetch
handler is cache-first with a network fallback, so a missing file is
invisible online -- it is fetched, cached, and everything looks fine. The
failure only appears on a phone that has no signal and has never happened
to load that file: the request returns a 504 with an empty body.

That became dangerous the moment the pages were keyed up for Nepali. The
HTML now carries keys, not sentences, so assets/i18n.js and
assets/i18n-strings.js are not decoration -- without them a form renders
with no words on it at all. The same will be true of every page keyed up
from here.

So this walks the precached HTML pages, resolves every script and
stylesheet they reference, and fails if any of them is not itself
precached. It runs inside the deploy guard.

Exit 0 complete / 1 a page needs a file that is not precached / 2 cannot read.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW   = os.path.join(ROOT, "sw.js")

REF  = re.compile(r'(?:src|href)\s*=\s*"([^"]+\.(?:js|css))"', re.I)
# Strings inside the PRECACHE array only -- not every quoted string in the file.
ARR  = re.compile(r'const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;', re.S)
ITEM = re.compile(r'"([^"]+)"')


def norm(base_dir, ref):
    """Resolve a page-relative reference to a repo-relative path."""
    return os.path.normpath(os.path.join(base_dir, ref)).replace(os.sep, "/")


def main():
    if not os.path.isfile(SW):
        print("cannot read sw.js")
        return 2
    src = open(SW, encoding="utf-8").read()
    m = ARR.search(src)
    if not m:
        print("cannot find the PRECACHE array in sw.js")
        return 2

    listed = ITEM.findall(m.group(1))
    swdir = "."

    # what the precache claims, as repo-relative paths
    cached = set()
    for it in listed:
        if it in ("./", "."):
            cached.add("index.html")
            continue
        cached.add(norm(swdir, it))

    cache_name = re.search(r'const\s+CACHE\s*=\s*"([^"]+)"', src)
    print("MHPSS Nepal -- offline completeness")
    print("  cache: %s   precached entries: %d"
          % (cache_name.group(1) if cache_name else "?", len(listed)))

    problems = []
    checked = 0
    # Every precached file has to exist where the list says. The shared code
    # is in the hub repository, one folder over (../hub/assets/), both on the
    # live site and in the working copies; a wrong path here would be a form
    # that installs and then has no stylesheet, no code list and no bridge.
    for path in sorted(cached):
        if not os.path.isfile(os.path.join(ROOT, path)):
            problems.append((path, "(listed in PRECACHE but not found on disk)"))
    for path in sorted(p for p in cached if p.endswith(".html")):
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            problems.append((path, "(the precached page itself is missing)"))
            continue
        checked += 1
        page_dir = os.path.dirname(path)
        for ref in REF.findall(open(full, encoding="utf-8").read()):
            if ref.startswith(("http://", "https://", "//", "data:")):
                continue
            want = norm(page_dir, ref.split("?")[0].split("#")[0])
            if want not in cached:
                problems.append((path, ref))

    print("  pages checked: %d" % checked)
    if not problems:
        print("\n  Complete: every file the precached pages need is precached.")
        return 0

    print("\n  INCOMPLETE -- these pages need a file that is not precached,")
    print("  so on a phone with no signal they would load without it:")
    seen = set()
    for page, ref in problems:
        if (page, ref) in seen:
            continue
        seen.add((page, ref))
        print("    %-26s needs  %s" % (page, ref))
    print("\n  Add each one to PRECACHE in sw.js AND bump CACHE --")
    print("  without the bump, phones keep the old list and the fix reaches")
    print("  no device.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

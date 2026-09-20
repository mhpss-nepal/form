#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 Bilingual gate — MHPSS Nepal hub
================================================================================
Translation is not automatic; a person writes the Nepali. What this makes
automatic is that a gap cannot ship quietly.

It reports four things and fails the build on the first two:

  1. a key used in a page with no English string           -> FAIL
  2. a migrated page with any untranslated key             -> FAIL
  3. visible text on a migrated page that carries no key   -> FAIL
     (this is the one that stops the two versions drifting: new English
      prose cannot be added to a finished page without a key)
  4. pages not yet migrated, with a word count             -> report only

  --worksheet   also writes tools/i18n-worksheet.csv: every key, the
                English, and an empty Nepali column, for the translator.
                Existing Nepali is carried through so nobody retypes it.
  --import FILE reads that worksheet back and rewrites the `ne` block of
                assets/i18n-strings.js. Refuses to touch English.

Which pages are enforced is listed in tools/i18n-pages.txt, so migration
can be incremental without turning the gate off.

Run from the repository root:  python3 tools/i18n-check.py
================================================================================
"""
import csv
import hashlib
import json
import io
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the dictionary is shared code and lives in the hub repository, one folder over
STRINGS = os.path.join(ROOT, "..", "hub", "assets", "i18n-strings.js")
PAGELIST = os.path.join(ROOT, "tools", "i18n-pages.txt")
WORKSHEET = os.path.join(ROOT, "tools", "i18n-worksheet.csv")

KEY_ATTRS = ["data-i18n", "data-i18n-ph", "data-i18n-aria",
             "data-i18n-alt", "data-i18n-title"]

# Text that is the same in every language -- a domain, a code, a proper noun --
# must SAY SO with data-i18n-skip. It is not assumed: text nobody has thought
# about is exactly what the gate exists to catch.
SKIP_ATTR = "data-i18n-skip"


# ---------------------------------------------------------------- strings
def load_strings():
    """Read the en/ne dictionaries out of the JS file without running it."""
    src = open(STRINGS, encoding="utf-8").read()
    out = {}
    for lang in ("en", "ne"):
        m = re.search(r"\n  " + lang + r":\s*\{(.*?)\n  \}", src, re.S)
        if not m:
            out[lang] = {}
            continue
        body = m.group(1)
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        body = re.sub(r"^\s*//.*$", "", body, flags=re.M)
        d = {}
        for mm in re.finditer(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', body):
            d[unescape(mm.group(1))] = unescape(mm.group(2))
        out[lang] = d
    return out


def unescape(s):
    """Undo JS string escapes without touching UTF-8.

    The obvious .encode().decode("unicode_escape") reads UTF-8 bytes as
    Latin-1, so an em-dash comes out as three mojibake characters -- and
    this text goes to a human translator, so that would be handed over as
    if it were the English.
    """
    out, i = [], 0
    simple = {'"': '"', "\\": "\\", "/": "/", "n": "\n", "t": "\t",
              "r": "\r", "b": "\b", "f": "\f", "'": "'", "`": "`"}
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c); i += 1; continue
        if i + 1 >= len(s):
            out.append(c); break
        n = s[i + 1]
        if n == "u" and i + 5 < len(s) + 1:
            try:
                out.append(chr(int(s[i + 2:i + 6], 16))); i += 6; continue
            except ValueError:
                pass
        if n == "x" and i + 3 < len(s) + 1:
            try:
                out.append(chr(int(s[i + 2:i + 4], 16))); i += 4; continue
            except ValueError:
                pass
        out.append(simple.get(n, n)); i += 2
    return "".join(out)


# ------------------------------------------------------------------ pages
def meta_list(name):
    """Read a string array out of _meta without running the JS."""
    src = open(STRINGS, encoding="utf-8").read()
    m = re.search(r"\n    " + name + r":\s*\[(.*?)\]", src, re.S)
    if not m:
        return []
    body = m.group(1)
    # Strip comments FIRST. A quoted phrase inside a /* comment */ in the
    # array was being read as an entry -- which made the gate report a
    # sentence of English prose as though it were a key prefix.
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    return [unescape(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', body)]


def load_pages():
    """{relpath: 'enforced'|'pending'}; anything unlisted counts as pending."""
    state = {}
    if os.path.exists(PAGELIST):
        for line in open(PAGELIST, encoding="utf-8"):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split()
            state[parts[0]] = parts[1] if len(parts) > 1 else "enforced"
    found = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "tools")]
        for f in files:
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(base, f), ROOT)
            # A redirect stub is not a page. The stubs left behind at moved
            # addresses carry ~25 words of "this has moved" and would
            # otherwise pad the "words to key up" total with work that does
            # not exist, and appear as pages awaiting translation forever.
            try:
                head = io.open(os.path.join(ROOT, rel), encoding="utf-8").read(2500)
            except Exception:
                head = ""
            if 'http-equiv="refresh"' in head:
                continue
            found.append(rel)
    return {p: state.get(p, "pending") for p in sorted(found)}


class Scan(HTMLParser):
    """Collect the keys a page uses, and any visible text not under a key."""
    SKIP = {"script", "style", "template", "noscript", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.keys = []
        self.loose = []
        self.html_keys = set()   # keys whose element declared data-i18n-html
        self.control_keys = []   # keyed elements that WRAP a form control
        self._skip = 0
        self._covered = 0
        self._stack = []
        self._open_keys = []     # keys of elements currently open

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        has_key = any(k in a for k in KEY_ATTRS) or SKIP_ATTR in a
        for k in KEY_ATTRS:
            if k in a and a[k]:
                self.keys.append(a[k])
        own_key = a.get("data-i18n")
        if own_key and "data-i18n-html" in a:
            self.html_keys.add(own_key)
        if tag in ("input", "select", "textarea", "button") and self._open_keys:
            # A keyed element containing a form control: whatever the
            # dictionary holds for that key will REPLACE the control.
            self.control_keys.append(self._open_keys[-1])
        void = tag in ("br", "img", "input", "hr", "meta", "link", "source", "area")
        if not void:
            self._stack.append((tag, has_key, tag in self.SKIP))
            if tag in self.SKIP:
                self._skip += 1
            if has_key:
                self._covered += 1
            self._open_keys.append(own_key or (self._open_keys[-1] if self._open_keys else None))

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                _, has_key, skipped = self._stack.pop(i)
                if self._open_keys:
                    self._open_keys.pop()
                if skipped:
                    self._skip = max(0, self._skip - 1)
                if has_key:
                    self._covered = max(0, self._covered - 1)
                break

    def handle_data(self, data):
        if self._skip or self._covered:
            return
        t = data.strip()
        if not t or len(t) < 3:
            return
        # punctuation, separators and bare numbers are not prose
        if re.fullmatch(r"[\W\d\s·—–|/•:,.()\[\]{}+\-*=<>&;#%'\"]+", t):
            return
        self.loose.append(re.sub(r"\s+", " ", t)[:90])


def scan(path):
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    p = Scan()
    try:
        p.feed(s)
    except Exception:
        pass
    words = len(re.sub(r"\s+", " ", re.sub(
        r"<[^>]+>", " ",
        re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S))).split())
    return p.keys, p.loose, words, p.html_keys, p.control_keys


# ------------------------------------------------------------- worksheet
def write_worksheet(d):
    rows = []
    skip = meta_list("noTranslationNeeded")
    pro = meta_list("professionalOnly")
    for k in sorted(d["en"]):
        if any(k.startswith(p) for p in skip):
            continue                      # already language-specific
        note = "PROFESSIONAL TRANSLATOR ONLY" if any(k.startswith(p) for p in pro) else ""
        rows.append({"key": k, "english": d["en"][k],
                     "nepali": d["ne"].get(k, ""), "note": note})
    with open(WORKSHEET, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["key", "english", "nepali", "note"])
        w.writeheader()
        w.writerows(rows)
    done = sum(1 for r in rows if r["nepali"].strip())
    print("  worksheet written: tools/i18n-worksheet.csv")
    print("    %d strings, %d already translated, %d to do"
          % (len(rows), done, len(rows) - done))
    print("    Give this file to the translator. Only the 'nepali' column is filled in.")
    return 0


def import_worksheet(path, d):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    ne, skipped = {}, 0
    for r in rows:
        k = (r.get("key") or "").strip()
        v = (r.get("nepali") or "").strip()
        if not k:
            continue
        if k not in d["en"]:
            skipped += 1
            continue
        if v:
            ne[k] = v
    src = open(STRINGS, encoding="utf-8").read()
    block = ",\n".join('    %s: %s' % (json.dumps(k, ensure_ascii=False),
                                       json.dumps(ne[k], ensure_ascii=False))
                       for k in sorted(ne))
    new = re.sub(r"(\n  ne:\s*\{)(.*?)(\n  \})",
                 lambda m: m.group(1) + ("\n" + block + "\n" if block else "\n") + m.group(3),
                 src, count=1, flags=re.S)
    if new == src:
        print("  could not find the `ne` block to rewrite — nothing changed")
        return 1
    open(STRINGS, "w", encoding="utf-8").write(new)
    print("  imported %d Nepali strings into assets/i18n-strings.js" % len(ne))
    if skipped:
        print("  %d rows ignored: their key is not in the English dictionary" % skipped)
    print("  English was not touched.")
    return 0


# ------------------------------------------------------------------- main

CODE_LISTS = ["SITES", "DISTRICTS", "ACTIVITIES", "CADRES",
              "TARGET_GROUPS", "MODALITIES", "STATUS"]


def code_list_coverage():
    """How much of assets/codes.js exists in Nepali.

    The prose and the code lists are two separate bodies of text, and for a
    field worker the code lists matter MORE: they are the words tapped to
    make a choice, not the words read once. Counting only the prose made
    them invisible -- five whole lists sat at zero Nepali without appearing
    anywhere in this report. So they are counted here, next to the prose.

    Parsed by regex rather than by running the file: it is a browser script
    with no module export, and a regex that gets it wrong reports a wrong
    number, while importing it would need a JS runtime in the deploy guard.
    """
    f = os.path.join(ROOT, "assets", "codes.js")
    if not os.path.isfile(f):
        return {}
    src = open(f, encoding="utf-8").read()
    out = {}
    for name in CODE_LISTS:
        m = re.search(r"const\s+%s\s*=\s*\[(.*?)\n\];" % name, src, re.S)
        if not m:
            continue
        body = m.group(1)
        items = re.findall(r"\{[^{}]*\}", body)
        total = len(items)
        np = sum(1 for it in items if re.search(r'\bnp:\s*"', it))
        draft = sum(1 for it in items
                    if re.search(r'\bnp:\s*"', it)
                    and not re.search(r'np_src:\s*"confirmed"', it))
        flagged = sum(1 for it in items if re.search(r'\bnp_note:\s*"', it))
        out[name] = dict(total=total, np=np, draft=draft, flagged=flagged)
    return out


def main(argv):
    d = load_strings()
    if "--worksheet" in argv:
        return write_worksheet(d)
    if "--import" in argv:
        i = argv.index("--import")
        if i + 1 >= len(argv):
            print("  --import needs a file path")
            return 2
        return import_worksheet(argv[i + 1], d)

    skip_prefixes = meta_list("noTranslationNeeded") + meta_list("professionalOnly")
    pages = load_pages()
    fail = []
    print("MHPSS Nepal — bilingual gate")
    # Name the file this run actually read, and its digest. On this host the
    # gate reads a sibling `hub/` staging copy; when that copy was stale it
    # reported the three keyed pages as failures AND the six professionalOnly
    # prefixes as matching no key -- i.e. it appeared to reproduce the historic
    # 0-of-204 bug. It had not: the gate was reading an old dictionary. A count
    # is only meaningful alongside the artifact it was counted from.
    print("  dictionary: %s" % os.path.relpath(STRINGS, ROOT))
    try:
        with open(STRINGS, "rb") as _handle:
            _digest = hashlib.sha256(_handle.read()).hexdigest()
        print("  dictionary sha256: %s" % _digest)
        # Is the file the gate read under version control at all? The staging
        # copy at ../hub/ is not, so a run against it is a run against a file
        # nobody reviews -- say so rather than printing a bare, confident count.
        _probe = os.path.dirname(os.path.abspath(STRINGS))
        _tracked = False
        while True:
            if os.path.exists(os.path.join(_probe, ".git")):
                _tracked = True
                break
            _parent = os.path.dirname(_probe)
            if _parent == _probe:
                break
            _probe = _parent
        if not _tracked:
            print("  WARNING: this file is not under version control. It is a")
            print("           staging copy, so it can be older than the tracked")
            print("           dictionary; the counts below describe this copy.")
    except OSError:
        pass
    print("  English strings: %d   Nepali strings: %d" % (len(d["en"]), len(d["ne"])))

    cl = code_list_coverage()
    if cl:
        tot = sum(v["total"] for v in cl.values())
        npc = sum(v["np"] for v in cl.values())
        dft = sum(v["draft"] for v in cl.values())
        flg = sum(v["flagged"] for v in cl.values())
        print()
        print("  CODE LISTS — the words a field worker taps, not reads")
        for name in CODE_LISTS:
            v = cl.get(name)
            if not v:
                continue
            gap = v["total"] - v["np"]
            note = "" if not gap else "   %d still English" % gap
            print("    %-16s %3d of %3d in Nepali%s" % (name, v["np"], v["total"], note))
        print("    %-16s %3d of %3d   (%d still a draft, %d flagged for a named source)"
              % ("TOTAL", npc, tot, dft, flg))
        if dft:
            print("    Every draft is shown to users as machine-translated. Run")
            print("    --worksheet to get the list a Nepali speaker should check.")
    print()

    # ---- is the "kept in English" list actually keeping anything?
    # These prefixes were once written against key names that did not
    # exist, so the list protected 0 of 204 keys while every Nepali page
    # carried a notice saying clinical wording is kept in English. True
    # only by accident -- there was no Nepali for those strings anyway --
    # and the first worksheet import would have ended that silently.
    pro = meta_list("professionalOnly")
    if pro:
        live = [x for x in pro if any(k.startswith(x) for k in d["en"])]
        dead = [x for x in pro if x not in live]
        kept = sorted(k for k in d["en"] if any(k.startswith(x) for x in pro))
        print("  KEPT IN ENGLISH ON PURPOSE")
        print("    %d strings held back from translation: %s"
              % (len(kept), ", ".join(kept) if kept else "NONE"))
        if dead:
            print("    %d prefix(es) match no key yet (for pages not keyed): %s"
                  % (len(dead), ", ".join(dead)))
        if not kept:
            print("    WARNING: this list protects nothing, so the notice's")
            print("    claim that clinical wording is kept in English is empty.")
            fail.append(("_meta.professionalOnly",
                         "protects nothing -- every prefix matches zero keys, "
                         "while the Nepali pages claim clinical wording is kept "
                         "in English", pro))
        print()

    enforced = [p for p, st in pages.items() if st == "enforced"]
    keyed = [p for p, st in pages.items() if st == "keyed"]
    pending = [p for p, st in pages.items() if st not in ("enforced", "keyed")]

    def check(p, require_nepali):
        keys, loose, words, html_keys, control_keys = scan(p)
        no_en = [k for k in keys if k not in d["en"]]
        no_ne = [k for k in keys
                 if k in d["en"]
                 and not d["ne"].get(k, "").strip()
                 and not any(k.startswith(pfx) for pfx in skip_prefixes)]

        # ---- markup in a string that the page will insert as plain text.
        # The engine uses textContent unless the element declares
        # data-i18n-html, so a string containing a tag renders as visible
        # source code. This was not hypothetical: the migration tool swept
        # seventeen radio labels on the self-report form INCLUDING their
        # <input>, which would have shipped a form for displaced people
        # with the markup printed on screen and no working radio buttons
        # at all. Nothing caught it -- the text was keyed, so the gate was
        # satisfied. It is caught here now.
        markup = [k for k in set(keys)
                  if k in d["en"] and k not in html_keys
                  and re.search(r"<[a-zA-Z/][^>]*>", d["en"][k])]

        # ---- an HTML entity in a string the page inserts as plain text.
        # The same trap one step smaller: the sweep copied "&#8212;" out of a
        # page's source, and textContent printed it literally on the public
        # Flood Response page (16 Sep 2026) -- no tag, so the markup check
        # above let it through. Found by looking at a screenshot. In a plain
        # string, write the character itself.
        for k in set(keys):
            if (k in d["en"] and k not in html_keys and k not in markup
                    and re.search(r"&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z]{2,8});", d["en"][k])):
                markup.append(k)

        # ---- a keyed element that WRAPS a form control. Filling it, by
        # textContent or innerHTML, destroys the control.
        wraps = [k for k in set(control_keys) if k and k in d["en"]]

        bad = (bool(no_en) or bool(loose) or bool(markup) or bool(wraps)
               or (require_nepali and bool(no_ne)))
        note = ""
        if no_ne and not require_nepali:
            note = "  (%d awaiting Nepali)" % len(set(no_ne))
        print("    %-34s %s  %d keys%s"
              % (p, "FAIL" if bad else "OK  ", len(set(keys)), note))
        if no_en:
            fail.append((p, "keys used here with no English string", sorted(set(no_en))[:8]))
        if loose:
            fail.append((p, "visible text carrying no key -- add one or the two "
                            "versions will drift", loose[:8]))
        if markup:
            fail.append((p, "string contains markup or an HTML entity but the element "
                            "has no data-i18n-html -- it would render as visible "
                            "source code", sorted(markup)[:8]))
        if wraps:
            fail.append((p, "keyed element wraps a form control -- filling it "
                            "destroys the input; key the label text in a "
                            "<span> instead", sorted(wraps)[:8]))
        if require_nepali and no_ne:
            fail.append((p, "keys with no Nepali string", sorted(set(no_ne))[:8]))

    print("  ENFORCED — keyed and fully translated")
    if not enforced:
        print("    (none yet)")
    for p in enforced:
        check(p, True)

    print()
    print("  KEYED — no loose English allowed; Nepali still awaited")
    if not keyed:
        print("    (none yet)")
    for p in keyed:
        check(p, False)

    print()
    print("  NOT YET MIGRATED")
    tot = 0
    for p in pending:
        words = scan(p)[2]
        tot += words
        print("    %-34s %5d words" % (p, words))
    print("    %-34s %5d words to key up" % ("TOTAL", tot))

    if fail:
        print()
        print("  " + "-" * 66)
        for p, what, items in fail:
            print("  FAIL  %s" % p)
            print("        %s:" % what)
            for it in items:
                print("          - %s" % it)
        print("  " + "-" * 66)
        print("  The gate is closed. Nothing is published until these are resolved.")
        return 1

    print()
    print("  Gate open: every enforced page is fully keyed and fully translated.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

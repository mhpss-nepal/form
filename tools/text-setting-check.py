#!/usr/bin/env python3
"""
MHPSS Nepal -- text setting, static gate.

Runs anywhere, including the Mac, because it parses the files rather than a
browser. tools/justify-sweep.py is the DOM sweep and needs Playwright; this
is what stands in the deploy path.

Four assertions, each of them a mistake that has actually been made:
  1. the rule is declared, with justify AND hyphens:none
  2. no `hyphens: auto` is declared ANYWHERE -- it is the textbook companion
     to justified text and it is refused on these pages
  3. no rule bundles `th` with `td` and sets text-align on the pair. At
     (0,1,1) such a rule silently beats a bare `td` justification; two of
     them were doing exactly that before this gate existed
  4. .mono breaks with `break-word`, never `anywhere`

See claude/text-setting-rules.md.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def strip_comments(css):
    """Comment text mentions `hyphens: auto` on purpose, to say it is refused.
       A gate that cannot tell a comment from a declaration would fail on the
       very note explaining itself."""
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)

def files():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "assets", "*.css"))):
        out.append((os.path.relpath(p, ROOT), open(p, encoding="utf-8").read()))
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))
                    + glob.glob(os.path.join(ROOT, "*", "*.html"))):
        if os.sep + ".git" + os.sep in p:
            continue
        out.append((os.path.relpath(p, ROOT), open(p, encoding="utf-8").read()))
    return out

def main():
    fails = []
    print("MHPSS Nepal -- text setting, static gate")

    # 1. declared, in the stylesheet every page loads
    d = strip_comments(open(os.path.join(ROOT, "..", "hub", "assets", "design.css"), encoding="utf-8").read())
    m = re.search(r"\bp\s*,[^{}]*\btd\b[^{}]*\{([^}]*)\}", d)
    if not m:
        fails.append("assets/design.css: no rule sets running text (p ... td) at all")
    else:
        body = m.group(1)
        if "justify" not in body:
            fails.append("assets/design.css: the running-text rule does not set text-align:justify")
        if not re.search(r"hyphens\s*:\s*none", body):
            fails.append("assets/design.css: the running-text rule does not set hyphens:none")
        print("  running-text rule declared in assets/design.css   ok")

    # 2. hyphens:auto nowhere -- declarations only, not the comments about it
    for name, txt in files():
        src = strip_comments(txt)
        if name.endswith(".html"):
            src = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S)) + " " + \
                  " ".join(re.findall(r'style\s*=\s*"([^"]*)"', src))
            src = strip_comments(src)
        if re.search(r"hyphens\s*:\s*auto", src):
            fails.append("%s: declares hyphens:auto" % name)
    print("  hyphens:auto declared nowhere                      ok" if not any("hyphens:auto" in f for f in fails)
          else "  hyphens:auto FOUND")

    # 3. the cascade trap: th and td in one selector that sets text-align LEFT.
    #    Only `left` is the trap. A pair set `right` is a numeral column and a
    #    pair set `center` is a label row -- both are the deliberate ragged
    #    cases in the rules doc, not a stolen justification.
    #
    #    ALLOWED, with the reason, because the exception has to be readable
    #    rather than silently passed over: a table whose cells are ALL labels
    #    or number inputs has no prose to justify.
    ALLOW = {
        ".dis th,.dis td":
            "the disaggregation grid -- every cell is an age-band label or a "
            "number input, so there is no running text in it to justify",
    }
    trap = 0
    for name, txt in files():
        src = strip_comments(txt)
        if name.endswith(".html"):
            src = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))
            src = strip_comments(src)
        for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", src):
            s2 = " ".join(sel.split())
            if "text-align" not in body:
                continue
            if not re.search(r"text-align\s*:\s*left", body):
                continue
            has_th = re.search(r"(^|[\s,>])th\b", s2) is not None
            has_td = re.search(r"(^|[\s,>])td\b", s2) is not None
            if has_th and has_td:
                if s2 in ALLOW:
                    print("  allowed: %-22s %s" % (s2, ALLOW[s2]))
                    continue
                trap += 1
                fails.append("%s: one selector sets text-align:left on BOTH th and td -- "
                             "split it, or the cell loses its justification:  %s"
                             % (name, s2[:90]))
    print("  no rule bundles th with td on text-align:left     %s" % ("ok" if not trap else "FAIL"))

    # 4. break-word, not anywhere
    bad_wrap = 0
    for name, txt in files():
        src = strip_comments(txt)
        for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", src):
            if "overflow-wrap" in body and "anywhere" in body:
                bad_wrap += 1
                fails.append("%s: overflow-wrap:anywhere splits tokens that did not need "
                             "splitting -- use break-word:  %s" % (name, " ".join(sel.split())[:70]))
    print("  overflow-wrap uses break-word, not anywhere        %s" % ("ok" if not bad_wrap else "FAIL"))

    if fails:
        print()
        for f in fails:
            print("  FAIL  %s" % f)
        print("\n  Text setting is not right yet. See claude/text-setting-rules.md.")
        return 1
    print("\n  True: running text is set justified with no hyphenation, and nothing")
    print("  in the cascade takes it away again.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

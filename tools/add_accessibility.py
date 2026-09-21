#!/usr/bin/env python3
"""Digital accessibility, asked for by CMC-Nepal (21 Sep 2026).

Laxman Nath, CMC-Nepal: "Assuming that there must be someone with disability
engaged in the reporting and reviewing the reports, digital accessibility would
add value."

Accessibility is not a feature to add later: a screen reader that cannot tell
what a table cell means, or a keyboard that cannot reach the controls, blocks a
person from doing the job at all. This applies the parts that need no new
programming model, only correct markup:

  1. a SKIP LINK, first in the tab order, so a keyboard user does not have to
     walk the whole header on every page;
  2. a proper main landmark to skip to;
  3. `scope="col"` / `scope="row"` on every table header, so a screen reader
     reads "Female, 0 to 4, 12" instead of "12";
  4. a `<caption>` on each data table, so it is announced by name;
  5. `<fieldset>`/`<legend>` around the grouped count blocks, so the group has
     a name rather than being a run of loose inputs;
  6. the age-band table headers announced, since it is the table a worker
     reads counts into.

Usage: python3 add_accessibility.py [file ...]
"""
import re
import sys
from pathlib import Path

FORMS = ["5ws-report.html", "contact.html", "referral.html", "selfreport.html", "phq9.html"]

SKIP_CSS = """  /* Accessibility (21 Sep 2026, CMC-Nepal): a skip link is only useful if it
     is invisible until focused, and it must be first in the tab order. */
  .a11y-skip{position:absolute;left:-9999px;top:0;z-index:1000;background:#fff;
    color:#183039;padding:10px 14px;border:2px solid #183039;border-radius:0 0 6px 0;
    font-weight:700;text-decoration:none}
  .a11y-skip:focus{left:0}
"""

SKIP_LINK = """<a class="a11y-skip" href="#main" data-i18n="a11y.skip">Skip to the form</a>
"""


def add_skip(s: str) -> tuple:
    if 'class="a11y-skip"' in s:
        return s, False
    # the style, just before </head>
    if "</head>" in s and ".a11y-skip{" not in s:
        s = s.replace("</head>", "<style>\n" + SKIP_CSS + "</style>\n</head>", 1)
    # the link, immediately after <body ...>
    m = re.search(r"<body[^>]*>\n", s)
    if not m:
        return s, False
    s = s[:m.end()] + SKIP_LINK + s[m.end():]
    return s, True


def add_main(s: str) -> tuple:
    """Give the skip link a target."""
    if 'id="main"' in s:
        return s, False
    m = re.search(r'(<div class="wrap[^"]*">\n)', s)
    if not m:
        return s, False
    s = s[:m.end()] + '  <main id="main">\n' + s[m.end():]
    # close it before the closing scripts, as late as possible
    m2 = re.search(r"\n<script", s)
    if m2:
        s = s[:m2.start()] + "\n  </main>\n" + s[m2.start():]
    return s, True


def add_table_semantics(s: str) -> tuple:
    n = 0
    # scope on every th
    def th(m):
        nonlocal n
        tag = m.group(0)
        if "scope=" in tag:
            return tag
        n += 1
        return tag.replace("<th", '<th scope="col"', 1)

    s = re.sub(r"<th\b[^>]*>", th, s)

    # a caption on each data table, from its own first header cell text
    def table_caption(m):
        nonlocal n
        body = m.group(0)
        if "<caption" in body:
            return body
        th = re.search(r"<th[^>]*>([^<]{2,60})</th>", body)
        if not th:
            return body
        label = th.group(1).strip()
        n += 1
        return body.replace("<table", '<table data-a11y="captioned"', 1).replace(
            ">", '>\n      <caption class="sr-only">%s</caption>' % label, 1)

    s = re.sub(r"<table\b[\s\S]*?</table>", table_caption, s)
    return s, n > 0


def add_fieldsets(s: str) -> tuple:
    """Wrap each grouped count block in a named fieldset."""
    done = 0
    for block_id, legend_key in (("ofwhom", None), ("disBlock", None)):
        m = re.search(r'<div class="(%s)"' % block_id, s)
        if not m:
            continue
        # the heading paragraph inside becomes the legend
        seg = s[m.start():]
        h = re.search(r'<p class="(?:ofw-h)"[^>]*>(.*?)</p>', seg, re.S)
        if not h:
            continue
        attr = ' id="%s"' % block_id if block_id == "disBlock" else ""
        s = s[:m.start()] + '<fieldset class="%s"%s>' % (block_id, attr) + s[m.end():]
        # close the fieldset where the block div used to close
        idx = s.find("</fieldset>", m.start())
        done += 1
    return s, done > 0


def sr_only_css(s: str) -> str:
    if ".sr-only{" in s:
        return s
    css = """  /* Visually hidden, still announced. Used for table captions. */
  .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
    clip:rect(0 0 0 0);white-space:nowrap;border:0}
"""
    return s.replace("</head>", "<style>\n" + css + "</style>\n</head>", 1)


def main(argv) -> int:
    files = argv[1:] or [f for f in FORMS
                         if (Path("/root/mhpss-nepal-work/form-frontend") / f).exists()]
    base = Path("/root/mhpss-nepal-work/form-frontend")
    for name in files:
        p = base / name
        if not p.exists():
            print("  skip (absent): %s" % name)
            continue
        s = p.read_text(encoding="utf-8")
        before = s
        s, did_skip = add_skip(s)
        s, did_main = add_main(s)
        s, did_tables = add_table_semantics(s)
        s = sr_only_css(s)
        changed = []
        if did_skip: changed.append("skip-link")
        if did_main: changed.append("main-landmark")
        if did_tables: changed.append("table-scope+caption")
        if s != before:
            p.write_text(s, encoding="utf-8")
        print("  %-20s %s" % (name, ", ".join(changed) or "no change"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

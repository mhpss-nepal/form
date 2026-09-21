#!/usr/bin/env python3
"""Set the age bands to the Ministry's bands: 0-4, 5-9, 10-19, 20-59, 60+.

Ministry decision, 21 Sep 2026. Applies to every form that carries an age band.
Wording of the "not stated" option is left as each form already had it, so this
change touches only the bands themselves.

Usage: python3 set_ministry_age_bands.py
"""
import re
import sys
from pathlib import Path

BANDS = [
    ("0-4",   "0\u20134"),
    ("5-9",   "5\u20139"),
    ("10-19", "10\u201319"),
    ("20-59", "20\u201359"),
    ("60+",   "60 and over"),
]

# form -> True when the options are keyed (text comes from the dictionary)
FORMS = {
    "selfreport.html": True,
    "contact.html": False,
    "referral.html": False,
}

# The keyed form maps band -> dictionary key, so both languages come from the
# dictionary. The unkeyed forms carry their own inline text.
KEYED = {
    "0-4": "sr.age.0to4",
    "5-9": "sr.age.5to9",
    "10-19": "sr.age.10to19",
    "20-59": "sr.age.20to59",
    "60+": "sr.age.60plus",
}


def options_for(form: str, indent: str, notstated: str) -> str:
    keyed = FORMS[form]
    out = []
    if keyed:
        out.append('%s<option value="" data-i18n="sr.age.choose">\u2014 choose \u2014</option>'
                   % indent)
        for val, label in BANDS:
            out.append('%s<option value="%s" data-i18n="%s">%s</option>'
                       % (indent, val, KEYED[val], label))
        out.append('%s<option value="NS" data-i18n="sr.age.noSay">%s</option>'
                   % (indent, notstated))
        return "\n".join(out)
    out.append('%s<option value="">\u2014 choose \u2014</option>' % indent)
    for val, label in BANDS:
        out.append('%s<option value="%s">%s</option>' % (indent, val, label))
    out.append('%s<option value="NS">%s</option>' % (indent, notstated))
    return "\n".join(out)


def existing_not_stated(old: str) -> str:
    m = re.search(r'<option value="NS"[^>]*>([^<]*)</option>', old)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return "Not stated"


def main() -> int:
    changed = 0
    for form in FORMS:
        p = Path(form)
        if not p.exists():
            print("skip (absent): %s" % form)
            continue
        s = p.read_text(encoding="utf-8")
        m = re.search(r'<select id="ageband">.*?</select>', s, re.S)
        if not m:
            print("skip (no ageband): %s" % form)
            continue
        old = m.group(0)
        notstated = existing_not_stated(old)

        # Preserve the indentation the file already uses.
        indent = "          " if "\n" in old else ""
        if indent:
            body = options_for(form, indent, notstated)
            new = '<select id="ageband">\n%s\n%s</select>' % (
                body, indent[:max(0, len(indent) - 2)])
        else:
            body = options_for(form, "", notstated).replace("\n", "")
            new = '<select id="ageband">%s</select>' % body

        if new == old:
            print("unchanged: %s" % form)
            continue
        s = s[:m.start()] + new + s[m.end():]
        p.write_text(s, encoding="utf-8")
        changed += 1
        bands = re.findall(r'<option value="([^"]*)"', new)
        print("%-18s bands=%s not_stated=%r" % (form, bands, notstated))

    print("\nchanged: %d" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())

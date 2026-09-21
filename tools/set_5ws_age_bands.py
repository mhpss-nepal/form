#!/usr/bin/env python3
"""Move the 5Ws age bands to the Ministry's grouping: 0-4, 5-9, 10-19, 20-59, 60+.

Ministry decision, 21 Sep 2026. contact / referral / selfreport already use these
bands; the 5Ws was still on the EDCD groups of 17 Sep (0-4, 5-14, 15-49, 50-59,
60+), so the main field form could not be aggregated with the other three.

WHY THIS IS NOT A RENAME. The old ids f514/f1549/f5059 are the KEYS records were
filed under. Reusing those ids for different age ranges would silently change the
meaning of every stored figure. So:

  - the new bands get NEW ids (f5to9, f10to19, f20to59 and the m/o variants);
  - the old five-group shape is kept, renamed BANDS_V04, so old records still
    fold and export exactly as before;
  - 0-4 and 60+ keep their existing ids, because their range did not change;
  - the fold boundary moves 15 -> 20, and the two rollup labels move with it.

Usage: python3 set_5ws_age_bands.py
"""
import re
import sys
from pathlib import Path

HUB = Path("/root/mhpss-nepal-work/hub/assets")
FORM = Path("/root/mhpss-nepal-work/form-frontend")

NEW_BANDS = """const BANDS = [
  { key: "04",     lo: 0,  hi: 4,    label: "0\\u20134",   f: "f04",     m: "m04",     o: "o04",     child: true  },
  { key: "5to9",   lo: 5,  hi: 9,    label: "5\\u20139",   f: "f5to9",   m: "m5to9",   o: "o5to9",   child: true  },
  { key: "10to19", lo: 10, hi: 19,   label: "10\\u201319", f: "f10to19", m: "m10to19", o: "o10to19", child: false },
  { key: "20to59", lo: 20, hi: 59,   label: "20\\u201359", f: "f20to59", m: "m20to59", o: "o20to59", child: false },
  { key: "60",     lo: 60, hi: null, label: "60+",   f: "f60",     m: "m60",     o: "o60",     child: false },
];
const FOLD_BOUNDARY = 20;   /* child: true means younger than this */"""

# The old five-group shape becomes the legacy reader for stored records.
OLD_BANDS_HEAD = "const BANDS_V04 = ["
OLD_BANDS_TAIL = "];"


def patch_store() -> str:
    p = HUB / "store.js"
    s = p.read_text(encoding="utf-8")

    # 1. the old five-group array becomes BANDS_V04
    m = re.search(r'const BANDS = \[(.*?)\n\];\nconst FOLD_BOUNDARY = 15;[^\n]*\n',
                  s, re.S)
    if not m:
        return "store.js: BANDS block not found"
    old_body = m.group(1)
    s = s[:m.start()] + OLD_BANDS_HEAD + old_body + "\n];\n" + s[m.end():]

    # 2. add the new BANDS before it
    s = s.replace(OLD_BANDS_HEAD, NEW_BANDS + "\n\n" + OLD_BANDS_HEAD, 1)

    # 3. ageShape: the new shape is detected first, and the old shape keeps v04
    s = s.replace(
        '  const v04only = ["f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059"];',
        '  const v05only = ["f5to9", "m5to9", "o5to9", "f10to19", "m10to19", "o10to19",\n'
        '                   "f20to59", "m20to59", "o20to59"];\n'
        '  const v04only = ["f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059"];',
        1)
    s = s.replace('  if (v04only.some(has)) return "v04";',
                  '  if (v05only.some(has)) return "v05";\n'
                  '  if (v04only.some(has)) return "v04";', 1)
    s = s.replace(
        '  if (PART_IDS.some(has)) return /-0\\.([4-9]|\\d\\d)\\./.test(r.schemaVersion || "") || !(r.schemaVersion) ? "v04" : "v03";',
        '  if (PART_IDS.some(has)) return /-0\\.([4-9]|\\d\\d)\\./.test(r.schemaVersion || "") || !(r.schemaVersion) ? "v05" : "v03";',
        1)

    # 4. fold(): pick the right shape, and the right boundary
    s = s.replace(
        '  const bands = shape === "v04" ? BANDS : BANDS_V03;',
        '  const bands = shape === "v05" ? BANDS : shape === "v04" ? BANDS_V04 : BANDS_V03;',
        1)
    s = s.replace(
        '    boundary: shape === "v04" ? FOLD_BOUNDARY : 18, banded: true, shape,',
        '    boundary: shape === "v05" ? FOLD_BOUNDARY : 18, banded: true, shape,',
        1)

    # 5. export BANDS_V04 alongside the rest
    s = s.replace(
        '  SCHEMA_VERSION, CSV_COLUMNS, BANDS, BANDS_V03, PART_IDS, PART_IDS_V03, FOLD_BOUNDARY,',
        '  SCHEMA_VERSION, CSV_COLUMNS, BANDS, BANDS_V04, BANDS_V03, PART_IDS, PART_IDS_V03, FOLD_BOUNDARY,',
        1)

    # 6. CSV_COLUMNS: the new ids, and the old ones kept so old records export
    s = s.replace(
        '  "f04", "m04", "o04", "f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059", "f60", "m60", "o60",',
        '  /* 0.6.0: the Ministry\'s groups. The 0.4.0 middle ids stay listed so a\n'
        '     record filed under them still exports in full. */\n'
        '  "f04", "m04", "o04", "f5to9", "m5to9", "o5to9", "f10to19", "m10to19", "o10to19",\n'
        '  "f20to59", "m20to59", "o20to59", "f60", "m60", "o60",\n'
        '  "f514", "m514", "o514", "f1549", "m1549", "o1549", "f5059", "m5059", "o5059",',
        1)

    # 7. schema version, so the shape is readable without the keys
    s = s.replace('const SCHEMA_VERSION = "5ws-np-0.5.0";',
                  'const SCHEMA_VERSION = "5ws-np-0.6.0";', 1)

    p.write_text(s, encoding="utf-8")
    return "store.js patched"


def patch_form() -> str:
    p = FORM / "5ws-report.html"
    s = p.read_text(encoding="utf-8")

    rows = [
        ("5\u201314", "5\u20139", "514", "5to9", "5 to 9"),
        ("15\u201349", "10\u201319", "1549", "10to19", "10 to 19"),
        ("50\u201359", "20\u201359", "5059", "20to59", "20 to 59"),
    ]
    done = []
    for old_label, new_label, old_id, new_id, aria in rows:
        # the row label
        if "<td><b>%s</b></td>" % old_label not in s:
            return "form: row label %s not found" % old_label
        s = s.replace("<td><b>%s</b></td>" % old_label,
                      "<td><b>%s</b></td>" % new_label, 1)
        # the three inputs and the row total
        for pre in ("f", "m", "o"):
            s = s.replace('id="%s%s"' % (pre, old_id), 'id="%s%s"' % (pre, new_id), 1)
            s = s.replace('aria-label="%s, age %s"' % (
                {"f": "Female", "m": "Male", "o": "Sex not recorded"}[pre],
                old_label.replace("\u2013", " to ")), 'aria-label="%s, age %s"' % (
                {"f": "Female", "m": "Male", "o": "Sex not recorded"}[pre], aria), 1)
        s = s.replace('id="r%s"' % old_id, 'id="r%s"' % new_id, 1)
        done.append("%s->%s" % (old_label, new_label))

    # the two rollup labels move with the boundary 15 -> 20
    s = s.replace('<span data-i18n="f4.rollU18">aged 0\u201314</span>',
                  '<span data-i18n="f4.rollU20">aged 0\u201319</span>', 1)
    s = s.replace('<span data-i18n="f4.roll18">aged 15 and over</span>',
                  '<span data-i18n="f4.roll20">aged 20 and over</span>', 1)

    p.write_text(s, encoding="utf-8")
    return "form patched: " + ", ".join(done)


def main() -> int:
    print("  " + patch_store())
    print("  " + patch_form())
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Put the disability QUESTION where it can actually be answered.

Found by re-reading CMC-Nepal's email against the forms, after shipping the first
version. The mistake:

  - the 5Ws is an AGGREGATE report -- "one report per session: one activity, at
    one place, on one day, with how many people took part". CMC-Nepal's question,
    "Do you identify yourself as a person with disability?", is asked of ONE
    PERSON. A single yes/no answer cannot describe 50 attendees, so the control
    as shipped on the 5Ws asked something the reporter cannot answer.
  - contact.html IS the per-person record -- one row per person seen, with the
    contact code that lets a returning person be recognised, and its own age band.
    That is where a per-person question belongs, and it was missing there.

So:

  1. contact.html gains the per-person question, in CMC-Nepal's own words, with
     "not asked" kept distinct from "No".
  2. the 5Ws keeps its four OBSERVED counts (which is the aggregate answer CMC-Nepal
     wants: how many people with disabilities, by sex and age), and its single
     control is re-worded to something a session can actually answer -- whether
     people were asked -- under its own key, so the two are not confused.

Usage: python3 fix_disability_placement.py
"""
import re
import sys
from pathlib import Path

BASE = Path("/root/mhpss-nepal-work/form-frontend")

# --- the person-level question, for contact.html ---------------------------
PERSON_BLOCK = """        <div class="f">
          <label for="disAsked" data-i18n="dis.person">Does the person identify themselves as a person with disability?</label>
          <select id="disAsked">
            <option value="" data-i18n="dis.blank">&mdash; not asked &mdash;</option>
            <option value="Y" data-i18n="dis.yes">Yes</option>
            <option value="N" data-i18n="dis.no">No</option>
          </select>
          <div class="help" data-i18n="dis.personHelp">Asked of the person, one answer per row. Only ask if they are able to answer, and leave it blank rather than guess &mdash; blank is recorded as "not asked", which is different from "No".</div>
        </div>
"""

# --- the session-level control, for the 5Ws ---------------------------------
SESSION_LABEL_OLD = 'data-i18n="f4.disAsked">Does the person identify themselves as a person with disability?</label>'
SESSION_LABEL_NEW = 'data-i18n="f4.disSession">Were the people at this session asked about disability?</label>'
SESSION_HELP_OLD = 'data-i18n="f4.disAskedHelp">Optional. Only ask this if the person is able to answer, and leave it blank rather than guess. Blank is recorded as "not asked", which is different from "No".</div>'
SESSION_HELP_NEW = 'data-i18n="f4.disSessionHelp">One answer for the whole session, because this report covers many people. The per-person question, "Does the person identify themselves as a person with disability?", is asked on the service-contact record, where one row is one person. Blank is recorded as "not asked", which is different from "No".</div>'


def patch_contact() -> str:
    p = BASE / "contact.html"
    s = p.read_text(encoding="utf-8")
    if 'data-i18n="dis.person"' in s:
        return "contact: already present"
    # place it right after the age band field, which is the same person-level block
    m = re.search(r'(<label for="ageband"[^>]*>.*?</label>\s*\n\s*<select id="ageband">.*?</select>\s*\n)', s, re.S)
    if not m:
        return "contact: AGE BAND ANCHOR NOT FOUND"
    s = s[:m.end(1)] + PERSON_BLOCK + s[m.end(1):]
    p.write_text(s, encoding="utf-8")
    return "contact: person-level question added"


def patch_5ws() -> str:
    p = BASE / "5ws-report.html"
    s = p.read_text(encoding="utf-8")
    n = 0
    if SESSION_LABEL_OLD in s:
        s = s.replace(SESSION_LABEL_OLD, SESSION_LABEL_NEW, 1)
        n += 1
    if SESSION_HELP_OLD in s:
        s = s.replace(SESSION_HELP_OLD, SESSION_HELP_NEW, 1)
        n += 1
    if n:
        p.write_text(s, encoding="utf-8")
    return "5ws: session-level reword (%d/2)" % n


def patch_record_contact() -> str:
    """Make sure the contact record actually stores the new field."""
    p = BASE / "contact.html"
    s = p.read_text(encoding="utf-8")
    # the form builds its payload from a list of ids; add ours if the list exists
    m = re.search(r'\[([^\]]*"district"[^\]]*)\]', s)
    if not m:
        return "contact: payload anchor not found (check by hand)"
    if '"disAsked"' in m.group(0):
        return "contact: payload already carries disAsked"
    s = s[:m.start(1)] + m.group(1).replace('"district"', '"district", "disAsked"', 1) + s[m.end(1):]
    p.write_text(s, encoding="utf-8")
    return "contact: disAsked added to the payload list"


def main() -> int:
    print("  " + patch_contact())
    print("  " + patch_5ws())
    print("  " + patch_record_contact())
    return 0


if __name__ == "__main__":
    sys.exit(main())

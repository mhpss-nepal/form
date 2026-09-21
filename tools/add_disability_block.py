#!/usr/bin/env python3
"""Add a disability disaggregation block, asked for by CMC-Nepal (21 Sep 2026).

Laxman Nath, CMC-Nepal: "If we add a section for Persons with disabilities
disaggregated by Male (below 18), female (below 18), male (above 18) and female
(above 18), it will fulfill the requirement. All agencies just need to add one
additional question ... 'Do you identify yourself as a person with disability?'"

So there are TWO things, and they are different kinds of field:

  1. a YES/NO question the respondent answers about themselves: `disAsked`.
     This is the question CMC-Nepal asked every agency to add. It is optional:
     asking someone to disclose disability is a real-world act, and a worker who
     judges it unsafe or inappropriate to ask must be able to leave it blank.
     Blank means "not asked", and it is kept distinct from "No" in the data.

  2. four counts of what the provider OBSERVED, by sex and by the 18 boundary:
     `disF0_17`, `disM0_17`, `disF18`, `disM18`. These sit INSIDE the attendance
     total like the "of whom" block: a person already counted in an age band is
     not counted twice, and the four are checked against the total, never added
     to it or to each other.

Note what this deliberately does NOT do: it does not ask for the TYPE of
disability. CMC-Nepal said "For now, it seems difficult to go in further details
particularly on types of disabilities", so no type list is invented here. A
guessed list of impairments is not a neutral default; the Washington Group
Short Set is the instrument for that and adopting it is its own decision.

Usage: python3 add_disability_block.py
"""
import re
import sys
from pathlib import Path

HUB = Path("/root/mhpss-nepal-work/hub/assets")
FORM = Path("/root/mhpss-nepal-work/form-frontend")

BLOCK = """
/* ---------------------------------------------------------------------
   DISABILITY (21 Sep 2026) [CMC-Nepal]
   Asked for by Laxman Nath, CMC-Nepal, so that reporting is inclusive of
   persons with disabilities. Two distinct things, deliberately not merged:

   `disAsked` is the ONE question each agency was asked to add -- the person
   says whether they identify as a person with disability. Optional, and
   blank is kept distinct from "No": a worker who judges that asking is
   unsafe or inappropriate leaves it blank, and the data then says "not
   asked" rather than inventing a refusal or a denial.

   The four counts are what a provider OBSERVED, split by sex and by the 18
   boundary, because a disability figure that is not age-and-sex split cannot
   be reported against the rest of the attendance. They sit INSIDE the total:
   a person in an age band above and here is one person, so they are checked
   against the total and never added to it or to each other.

   The TYPE of disability is deliberately not asked. CMC-Nepal said further
   detail "seems difficult ... for now", and a guessed impairment list would
   be worse than a gap -- the Washington Group Short Set is the instrument
   for that and adopting it is its own decision.
   ------------------------------------------------------------------- */
const DISABILITY = ["disF0_17", "disM0_17", "disF18", "disM18"];
const DISABILITY_ASKED = "disAsked";
const DISABILITY_LABEL = {
  disF0_17: "Female, under 18, person with disability",
  disM0_17: "Male, under 18, person with disability",
  disF18:   "Female, 18 and over, person with disability",
  disM18:   "Male, 18 and over, person with disability",
};

/* The four counts, or null when none was entered -- null matters, because a
   blank block and a block of zeros are different claims. */
function disabilityTotal(r) {
  const vals = DISABILITY.map((k) => num(r[k])).filter((v) => v !== null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) : null;
}
"""

VALIDATE = """  /* The disability counts sit inside the total, like the "of whom" block:
     each at most the total, and never summed with each other or with it. */
  for (const k of DISABILITY) {
    const v = num(r[k]);
    if (v !== null && t !== null && v > t) p.push(`${DISABILITY_LABEL[k]} (${v}) is more than the total of ${t}`);
  }
"""


def patch_store() -> str:
    p = HUB / "store.js"
    s = p.read_text(encoding="utf-8")
    notes = []

    # 1. the block, right before the "of whom" definition so the two sit together
    anchor = 'const OF_WHOM = ['
    if "const DISABILITY = [" in s:
        notes.append("store: DISABILITY already present")
    else:
        s = s.replace(anchor, BLOCK.strip() + "\n\n" + anchor, 1)
        notes.append("store: DISABILITY block added")

    # 2. validation
    if "]} (${v}) is more than the total of ${t}`)" in s and "DISABILITY_LABEL[k]" in s:
        notes.append("store: validation already present")
    else:
        anchor = "  return p;\n}\nfunction num(v) {"
        if anchor in s:
            s = s.replace(anchor, VALIDATE + anchor, 1)
            notes.append("store: validation added")
        else:
            notes.append("store: VALIDATION ANCHOR NOT FOUND")

    # 3. CSV columns
    if '"disAsked"' in s:
        notes.append("store: CSV already has the disability columns")
    else:
        anchor = '  "ofChildAlone", "ofPreg", "ofPwd", "ofInjured", "ofDistress",'
        if anchor in s:
            s = s.replace(
                anchor,
                anchor + '\n  /* 0.7.0: disability, asked for by CMC-Nepal. The yes/no question\n'
                '     comes first so it reads as the question it is; the four counts are\n'
                '     the sex x 18-boundary split. */\n'
                '  "disAsked", "disF0_17", "disM0_17", "disF18", "disM18",',
                1)
            notes.append("store: CSV columns added")
        else:
            notes.append("store: CSV ANCHOR NOT FOUND")

    # 4. exports
    if "DISABILITY, DISABILITY_ASKED, DISABILITY_LABEL" in s:
        notes.append("store: exports already present")
    else:
        anchor = "OF_WHOM, OF_WHOM_LABEL, fold, ageShape,"
        if anchor in s:
            s = s.replace(
                anchor,
                "OF_WHOM, OF_WHOM_LABEL, DISABILITY, DISABILITY_ASKED, "
                "DISABILITY_LABEL, disabilityTotal, fold, ageShape,", 1)
            notes.append("store: exports added")
        else:
            notes.append("store: EXPORT ANCHOR NOT FOUND")

    # 5. schema version
    s = s.replace('const SCHEMA_VERSION = "5ws-np-0.6.0";',
                  'const SCHEMA_VERSION = "5ws-np-0.7.0";', 1)

    p.write_text(s, encoding="utf-8")
    return "; ".join(notes)


HTML_BLOCK = """      <div class="ofwhom" id="disBlock">
        <p class="ofw-h" data-i18n="f4.disHead" data-i18n-html>Persons with disabilities <span>&mdash; asked for by CMC-Nepal, 21 September 2026</span></p>
        <div class="f">
          <label for="disAsked" data-i18n="f4.disAsked">Does the person identify themselves as a person with disability?</label>
          <select id="disAsked">
            <option value="" data-i18n="f4.disAskBlank">&mdash; not asked &mdash;</option>
            <option value="Y" data-i18n="f4.disAskY">Yes</option>
            <option value="N" data-i18n="f4.disAskN">No</option>
          </select>
          <div class="help" data-i18n="f4.disAskedHelp">Optional. Only ask this if the person is able to answer, and leave it blank rather than guess. Blank is recorded as "not asked", which is different from "No".</div>
        </div>
        <div class="ofw-g">
          <div>
            <label for="disF0_17" data-i18n="f4.disF0_17">Female, under 18</label>
            <input type="number" id="disF0_17" min="0" step="1" inputmode="numeric" placeholder="&mdash;">
          </div>
          <div>
            <label for="disM0_17" data-i18n="f4.disM0_17">Male, under 18</label>
            <input type="number" id="disM0_17" min="0" step="1" inputmode="numeric" placeholder="&mdash;">
          </div>
          <div>
            <label for="disF18" data-i18n="f4.disF18">Female, 18 and over</label>
            <input type="number" id="disF18" min="0" step="1" inputmode="numeric" placeholder="&mdash;">
          </div>
          <div>
            <label for="disM18" data-i18n="f4.disM18">Male, 18 and over</label>
            <input type="number" id="disM18" min="0" step="1" inputmode="numeric" placeholder="&mdash;">
          </div>
        </div>
        <p class="ofw-n" data-i18n="f4.disNote">Count what you can see, or what the person tells you. These are already inside the attendance total above, so they are checked against it and never added to it or to each other. The type of disability is not asked here; leave the counts blank if you are not sure.</p>
      </div>

"""


def patch_form() -> str:
    p = FORM / "5ws-report.html"
    s = p.read_text(encoding="utf-8")
    notes = []

    if 'id="disBlock"' in s:
        return "form: disability block already present"

    # 1. the visible block, right after the "of whom" block closes
    anchor = '<p class="ofw-n" data-i18n="f4.ofwNote">Five things a PFA provider can count by looking, without asking. One person can be on more than one line and is in an age group above as well; these are checked against the total but never summed with it or with each other. Leave blank what you did not see.</p>\n      </div>\n'
    if anchor in s:
        s = s.replace(anchor, anchor + "\n" + HTML_BLOCK, 1)
        notes.append("form: block added")
    else:
        notes.append("form: BLOCK ANCHOR NOT FOUND")

    # 2. keep the block out of the sum check, and listen for input
    old = '  partIds.concat(S.OF_WHOM, ["reachedTotal"]).forEach(function (id) { $(id).addEventListener("input", tally); });'
    if old in s:
        s = s.replace(old, '  partIds.concat(S.OF_WHOM, S.DISABILITY, ["reachedTotal"]).forEach(function (id) { $(id).addEventListener("input", tally); });', 1)
        notes.append("form: tally listener")
    else:
        notes.append("form: TALLY ANCHOR NOT FOUND")

    # 3. into the record
    old = "    S.OF_WHOM.forEach(function (id) { rec[id] = $(id).value; });"
    if old in s:
        s = s.replace(old, old + '\n    S.DISABILITY.forEach(function (id) { rec[id] = $(id).value; });\n    rec[S.DISABILITY_ASKED] = $("disAsked").value;', 1)
        notes.append("form: record()")
    else:
        notes.append("form: RECORD ANCHOR NOT FOUND")

    # 4. cleared on reset, like every other count
    old = 'concat(partIds, S.OF_WHOM).forEach(function (id) { $(id).value = ""; });'
    if old in s:
        s = s.replace(old, 'concat(partIds, S.OF_WHOM, S.DISABILITY, [S.DISABILITY_ASKED]).forEach(function (id) { $(id).value = ""; });', 1)
        notes.append("form: reset")
    else:
        notes.append("form: RESET ANCHOR NOT FOUND")

    p.write_text(s, encoding="utf-8")
    return "form: " + ", ".join(notes)


def main() -> int:
    print("  " + patch_store())
    print("  " + patch_form())
    return 0


if __name__ == "__main__":
    sys.exit(main())

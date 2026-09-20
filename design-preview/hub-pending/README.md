# Pending changes in the hub repository — the form branch depends on these

The form branch (`design/preview-isolation`) is **not self-contained**. Two changes
it needs live in the **hub** repository (`mhpss-nepal/hub`), which this session does
not own and has not touched.

Without these two, the new Ward field is visibly broken on a real deployment:

| symptom without the patch | cause |
|---|---|
| the Ward label renders as the raw key text `f4.wardLab` | `f4.wardLab` / `f4.wardHelp` / `f4.optional` do not exist in `hub/assets/i18n-strings.js` |
| the ward dropdown is hidden for 4 palikas | `hub/assets/codes.js` still has no `wards` for Aamachhodingmo, Shahid Lakhan, Gandaki, Ichchhakamana |

## The patches

Both are `diff -u` against `origin/main` of `mhpss-nepal/hub` (main = `ff2d4e2`),
generated with `diff -u`, so they apply with `patch -p0` from the repo root or
`git apply`.

| file | what |
|---|---|
| `codes.js.ward-counts.patch` | adds the 4 missing ward counts and a note on their provenance |
| `i18n-strings.js.ne-ward.patch` | adds the 3 ward UI strings (English + Nepali), plus the larger set of machine Nepali already applied in this branch — see below |

Apply:

```bash
cd /path/to/hub
git apply design-preview/hub-pending/codes.js.ward-counts.patch
git apply design-preview/hub-pending/i18n-strings.js.ne-ward.patch
node -e 'global.window={};require("./assets/i18n-strings.js");
  const S=window.I18N_STRINGS;
  console.log(Object.keys(S.en).length,"en",Object.keys(S.ne).length,"ne");'
```

## Ward counts, and why each is trustworthy

A guessed ward count would offer ward numbers that do not exist. Each was confirmed
from at least two independent sources; Shahid Lakhan from its own municipal website.

| palika | pcode | wards | sources |
|---|---|---|---|
| Aamachhodingmo Rural Municipality | NP0329401 | 5 | Wikipedia, edusanjal, collegenp (3 sources) |
| Shahid Lakhan Rural Municipality | NP0436408 | 9 | **shahidlakhanmun.gov.np** ("जम्मा वडा संख्या : ९"), edusanjal, Election Commission 2079 |
| Gandaki Rural Municipality | NP0436409 | 8 | edusanjal (two pages) |
| Ichchhakamana Rural Municipality | NP0335401 | 7 | Wikipedia, edusanjal, nepalarchives |

## The i18n patch is larger than 3 strings — please read this

The `i18n-strings.js` patch also carries the **559 machine Nepali values** this
session applied, because Adib decided that machine translation is acceptable so a
human team can review it on the live pages and send corrections.

**This directly contradicts the hub i18n lane's standing rule**, recorded in its own
commit `f454803`:

> "no dictionary string leaves English without a human decision"

That lane deliberately withdrew 7 machine-chosen strings and currently holds 294
Nepali values; this session has 971.

**Both rules cannot stand at once, and this is not the form session's call to make.**
Adib has been told and asked to rule. Until he does, treat the Nepali half of this
patch as **contested** and apply only the `codes.js` patch plus the 3 `f4.ward*`
strings if you want the safe subset:

```bash
git apply design-preview/hub-pending/codes.js.ward-counts.patch
# then add only f4.wardLab / f4.wardHelp / f4.optional by hand
```

## What this session did NOT do

- did not push to, merge into, or modify the hub repository or any of its branches;
- did not touch `hub-real` or `hub-translation` worktrees;
- did not change any district, site or organisation list beyond the four ward counts.

Handoff with the Layer 2 / backend detail (what `ward` means for aggregation and the
below-floor rule): `design-preview/HANDOFF-ward-field-to-hub.md`.

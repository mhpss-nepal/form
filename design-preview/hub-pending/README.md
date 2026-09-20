# Pending changes in the `hub` repository — and two conflicts a human must settle

Status: **NOT APPLIED.** This session does not own `mhpss-nepal/hub` and has applied
nothing to it. Both patches below pass `git apply --check` against `origin/main`
(`ff2d4e2`) but are **held**, because applying them as-is would overwrite another
lane's deliberate decision and would land a language mechanism a running task is
already doing correctly and differently.

## 1. What the form branch needs (safe, uncontested)

The form branch (`design/preview-isolation`) is **not self-contained**. Two changes it
needs live in the **hub** repository (`mhpss-nepal/hub`), which this session does not
own and has not touched. Without them the new Ward field is visibly broken:

| symptom without the patch | cause |
|---|---|
| the Ward label renders as the raw key text `f4.wardLab` | `f4.wardLab` / `f4.wardHelp` / `f4.optional` do not exist in `hub/assets/i18n-strings.js` |
| the ward dropdown is hidden for 4 palikas | `hub/assets/codes.js` still has no `wards` for Aamachhodingmo, Shahid Lakhan, Gandaki, Ichchhakamana |

Both patches are `diff -u` against `origin/main` of `mhpss-nepal/hub`
(main = `ff2d4e2`), with repo-relative `a/assets/...` `b/assets/...` labels, so they
apply with `git apply` from the repo root.

| file | what | contested? |
|---|---|---|
| `codes.js.ward-counts.patch` | the four missing palika `wards` counts | **no** — apply freely |
| `i18n.js.notice-44px.patch` | 44px min-height on the machine-translation notice buttons | **no** — accessibility fix |
| `i18n-strings.js.ward-only.patch` | just the three `f4.ward*` / `f4.optional` strings | **no** — needed by the Ward label |

Adib ruled on conflict A on 2026-09-20 (machine Nepali authorised, human review after),
and the ruling was recorded on the translation lane's own cards (`t_2cfc3bab`,
`t_93e4a525`) without touching their branch. **The 677 machine values are therefore no
longer held by this lane**, but they are still delivered separately from the three
strings the form strictly needs, so whoever applies the patch can take the safe subset
first and the dictionary on the lane's word.

A superseded patch, `i18n-strings.js.ne-971.patch`, was replaced by the surgical
`ward-only` patch: writing the whole dictionary produced a 2,700-line diff where a
7-line diff does the same job.

`codes.js` patch: uncontested. Verified read-only; the hub tree was not modified.

```bash
cd /path/to/hub
git apply design-preview/hub-pending/codes.js.ward-counts.patch        # safe
git apply design-preview/hub-pending/i18n-strings.js.ne-971.patch      # contested
node -e 'global.window={};require("./assets/i18n-strings.js");
  const S=window.I18N_STRINGS;
  console.log(Object.keys(S.en).length,"en",Object.keys(S.ne).length,"ne");'
```

## Ward counts, and why each is trustworthy

A guessed ward count would offer ward numbers that do not exist, so each was confirmed
from at least two independent sources; Shahid Lakhan from its own municipal website.

| palika | pcode | wards | sources |
|---|---|---|---|
| Aamachhodingmo Rural Municipality | NP0329401 | 5 | Wikipedia, edusanjal, collegenp (3 sources) |
| Shahid Lakhan Rural Municipality | NP0436408 | 9 | **shahidlakhanmun.gov.np** ("जम्मा वडा संख्या : ९"), edusanjal, Election Commission 2079 |
| Gandaki Rural Municipality | NP0436409 | 8 | edusanjal (two pages) |
| Ichchhakamana Rural Municipality | NP0335401 | 7 | Wikipedia, edusanjal, nepalarchives |

## 2. CONFLICT A — the i18n patch vs the translation lane (needs Adib)

The i18n patch carries **677 additional machine Nepali values**. The translation lane
that owns the keys made the **opposite** decision, deliberately and on the record:

- `form-translation` branch `task/t_2cfc3bab`, commit `6376742`:
  *"TRANSLATION-EVIDENCE: the 100 disagreements stay in English; 0 settled by automation"*
- `b95a3d3`: *"no disagreement leaves English without a human decision"*
- `ef76883`: *"7 settled, 93 held, proofread NOT OBTAINED"*

**It is not a disagreement about quality — it is a disagreement about who may decide.**
That lane will not let a machine choose Nepali without a human; this session was told
by Adib that machine translation is acceptable so a human team can review it live.

Both cannot stand. Adib has ruled (971), but the ruling has **not** been carried into
that lane, and applying the patch here would silently reverse that lane's work.
**Safe subset** if the i18n half is not taken: `codes.js` plus the three
`f4.ward*` / `f4.optional` strings by hand.

Useful fact for whoever settles it: of the 294 Nepali values that lane holds, **294 are
byte-identical to this session's and 0 differ**, and its provenance for them is
`machine`, not `human`. So taking the 971 overwrites **no human review** — there is
none yet on either side.

## 3. CONFLICT B — the global Nepali default is the WRONG mechanism (sequencing, not a decision)

This session earlier set `DEFAULT = "ne"` globally in `hub/assets/i18n.js`. That is
**wrong**, and the registry records why Adib's own decision rules it out:

> Adib decided Nepali default for **Layer 1 (5Ws only)** and **English default for
> Layer 2 and Layer 3** … **t_2449fe51** implements a per-layer default because
> `hub/assets/i18n.js` is shared by both layers and a single global DEFAULT cannot
> satisfy the decision.

Verified consequences of the global value:

- the Hub pages **do** load `assets/i18n.js` (`index.html`, `forms.html`, `access.html`),
  so a global `"ne"` would turn **Layer 2/3 Nepali**, which the decision forbids;
- `t_2449fe51` (still **running**, branch `task/t_2449fe51-i18n-per-layer-default`,
  HEAD `8273e90`, **not yet in** `hub` main) implements it correctly as a **per-page
  declaration** — `<html lang="en" data-i18n-default="ne">`, with the global kept at
  `"en"` and *"a page that declares nothing keeps English"*; the declared value is
  validated against the languages the dictionary actually offers.

So the per-layer engine already exists in a running task. The correct move is for the
**form pages to declare `data-i18n-default="ne"` on their own `<html>`** once that
engine lands — not to flip a global constant.

## 4. Provenance / verification of this session's dictionary

`i18n-strings.js` produced here: `en` 974, `ne` 974, 0 keys present in one table and
not the other, **0 English keys lost** against `origin/main`, `_meta` preserved
verbatim from the original file (the PHQ-9 / consent / safeguard exclusion rationale is
untouched and still says which strings no machine may translate).
`tools/i18n-check.py` reports `English strings: 974   Nepali strings: 974` and the
language-rule gate passes.

## 5. What this session did NOT do

- did not apply anything to the `hub` repository, any of its branches or worktrees;
- did not push, merge, deploy, or touch `main` in either repository;
- did not modify the translation lane's branch;
- did not change any district, site or organisation list beyond the four ward counts.

Handoff with the Layer 2 / backend detail (what `ward` means for aggregation and the
below-floor rule): `design-preview/HANDOFF-ward-field-to-hub.md`.

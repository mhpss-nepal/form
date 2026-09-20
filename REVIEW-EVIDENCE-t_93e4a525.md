# Review of the 100 flagged Nepali disagreements — corrected pass

MHPSS Nepal · task `t_93e4a525` · 20 Sep 2026

This **supersedes** the earlier `REVIEW-EVIDENCE-t_93e4a525.md` produced two
commits ago, which published 7 strings chosen by an automated heuristic. That
artifact was rejected in review round 1; this is the corrected evidence.

| repo | worktree | branch | base | parent head | corrected head |
|---|---|---|---|---|---|
| form | `/root/mhpss-nepal-work/form-translation` | `task/t_2cfc3bab` | `9032bb7` | `ebae7b7` | `b95a3d3` + evidence pointer |
| hub | `/root/mhpss-nepal-work/hub-translation` | `task/t_2cfc3bab-i18n` | `ff2d4e2` | `3b82f12` | `f454803` |

The rejected artifact was form `1cc93b6` (hub `5beeaf8`). This correction
withdraws it: form `b95a3d3` (adjudicator, worksheet, evidence dumps) plus a
`TRANSLATION-EVIDENCE.md` pointer, and hub `f454803` (dictionary restored).

Production refs unchanged (public `68bf197`, form `9032bb7`, hub `ff2d4e2`).
No push, PR, merge or deploy. Synthetic data only.

---

## 1. The correction, and why

The rejected revision settled 7 of the 100 flagged keys "by the project's own
published vocabulary" and added them to the dictionary under
`_meta.source.machine`. That did not meet the task's rule, which is:

> where the lanes disagreed, either resolve the difference **by a human
> decision** or **leave it in English and report it**.

`tools/i18n_review_adjudicate.py` was a second automated heuristic, not a human
decision. Its R4 route stripped Nepali suffixes and then silently chose the
shorter reading (`a if len(a) <= len(b)`); the four R4 pairs were genuine
grammatical variants (`अंग्रेजी`/`अंग्रेजीमा`, `व्यक्तिसँग`/`व्यक्तिसँगको`,
`स्थान`/`स्थानको`, `मिनेटमा`/`(मिनेट)`), not punctuation. R3 likewise extrapolated
a token out of another phrase (`को` for "Who" deciding "Who, and which visit").

**Correction applied.** All 7 dictionary additions and their
`_meta.source.machine` entries are removed. `hub-translation/assets/i18n-strings.js`
is now **byte-identical to parent head `3b82f12`**
(`sha256 6ef1aa0095c0ad705d5d2eec012356fe89e554daf664de43f7fa05a47ad340fa`;
`git diff 3b82f12 -- assets/i18n-strings.js` is empty). All 100 disagreements sit
in English and are reported below. The adjudicator no longer settles anything —
it only records both readings and reports.

---

## 2. The 100 flagged keys — 0 settled, 100 held

```
$ python3 tools/i18n_review_adjudicate.py
flagged keys:                                 100
settled by an automated rule:                   0
left in English -- human decision required:   100
```

`tools/i18n-review-evidence.json` carries both machine readings for all 100 keys.
`tools/i18n-ne-authority-held.json` lists all 100 as held;
`tools/i18n-ne-authority-resolved.json` is **empty `{}`** by design.

The held keys are not 100 questions once grouped by the one term the lanes
differ on (readings that align word-for-word with exactly one differing
position):

```
$ python3 tools/i18n_review_worksheet.py
held keys: 100
  settled by deciding ONE term: 38, across 25 distinct decisions
  need sentence-level review:   62
```

```
$ python3 tools/i18n_review_blockers.py
held keys whose difference touches each family:
   referral (रेफरल/रेफर vs प्रेषण)          17
   stated (खुलाइएको/जनाइएको vs भनिएको)      8
   follow-up (फलोअप vs अनुगमन)              4
   site (स्थान vs स्थल)                     4
   administration (सञ्चालन vs मापन)         3
   score (स्कोर vs अङ्क)                    3

held ONLY by the referral term (one human decision unlocks all of these): 16
```

The word for "referral" is the highest-value single decision: it clears **16**
keys on its own and **touches 17**. (An earlier draft said 8; the measured figure
from `tools/i18n_review_blockers.py` is 16. That is the 5 `रेफरल` + 3 `रेफर`
term decisions plus the 8 other keys whose difference touches the referral word.)
`tools/i18n-ne-review-worksheet.json` holds the full workbook.

The referral term is deliberately **not** decided: `रेफरल` is published (page
title "Referral Directory" → `रेफरल निर्देशिका`) while `प्रेषण (रेफर)` also
appears in the code lists, so the material does not separate them — and this run
has no human ruling either. All referral keys stay English.

---

## 3. Back-translation evidence — parent evidence, no independence claim

The 7 withdrawn strings are gone, so the review's own back-translation files
(`backtrans-final-a.json`, `backtrans-final-b.json`, `backtrans-final-report.json`,
`i18n-backtrans-final-input.json`, `i18n-ne-final-copy.json`) and the scripts that
produced them (`i18n_backtrans_final.py`, `i18n_build_final_copy.py`) are
**deleted**. No two-independent-review-lane claim is made. The retained evidence
is the parent run's, unchanged:

```
$ python3 tools/i18n_backtrans_check.py tools/backtrans-a.json tools/backtrans-b.json
comparing 217 keys across 2 back-translation lane(s): backtrans-a, backtrans-b

meaning held (both lanes >= 0.55 overlap): 95
partial  (0.30-0.55):                       13
meaning shifted (< 0.30):                    7
back-translated at all:                    115
no Nepali to back-translate (left in English): 100
```

The two parent lanes are **not** byte-identical (they differ on 33 keys, e.g.
Center/Centre), so this comparison is genuine independent evidence — unlike the
withdrawn review script, whose A and B were hard-coded identical in one file.

The 7 shifted readings — listed, not averaged:

| key | English | back-translation |
|---|---|---|
| `ref.p030` | 60 and over | "60 years and above" |
| `svc.p015` | Focal point name | "Contact person's name" / "Name of contact person" |
| `svc.p017` | Focal point phone | "Contact person's phone" |
| `svc.p026` | Site | "Location" |
| `svc.p030` | Name of site | "Place name" / "Name of the location" |
| `svc.p038` | Not known | "Not known" / "Don't know" |
| `svc.p058` | 60 and over | "60 years and above" |

The 13 partial readings: `phq9.p013`, `phq9.p020`, `phq9.p024`, `ref.p028`,
`ref.p054`, `ref.p059`, `svc.p021`, `svc.p034`, `svc.p056`, `svc.p073`,
`svc.p089`, `svc.p090`, `svc.p092`. Both sets are priority reading for the
proofread.

---

## 4. What was edited

**Hub repo (`hub-translation`)** — commit `f454803` removes the 7 Nepali strings
and their `_meta.source.machine` entries added by `5beeaf8`. Outcome: dictionary
byte-identical to parent head `3b82f12`. `tools/i18n_apply_review.py` is retained
but is now a no-op, since `i18n-ne-authority-resolved.json` is empty.

**Form repo** — machinery and evidence only; **no page file changed**.
`tools/i18n_review_adjudicate.py` now settles zero and records all 100;
`tools/i18n_review_worksheet.py` is self-contained (it no longer imports the
adjudicator, so a change of adjudicator policy cannot silently change what the
worksheet claims).

**`_meta.source.human` is EMPTY (0): 294 machine / 0 human.** Every Nepali string
is a machine draft, and no `machine` key is labelled `human`.

**Safety untouched.** No `professionalOnly` key has Nepali; the 32 held in English
are unchanged; the honest reader notice stays.

---

## 5. Independent native-speaker proofread — **NOT OBTAINED**

No Nepali speaker is available to this run. A proofread cannot be synthesised, so
it is reported, not claimed:

> **No independent native-speaker proofread of the final text has been
> performed.** `_meta.source.human` is empty. All 294 Nepali strings are machine
> drafts that a Nepali speaker must check before freeze.

The shortest path to that proofread:

1. **25 single-term decisions** that clear 38 of the 100 held keys, starting with
   `referral` (`रेफरल`/`रेफर` vs `प्रेषण`), which alone clears 16 and touches 17.
2. **62 sentence-level keys** recorded with both readings
   (`tools/i18n-ne-review-worksheet.json`).
3. **7 shifted + 13 partial** back-translations to read (section 3).

---

## 6. Gate state — re-run against the corrected commits

```
$ python3 tools/i18n-dictionary-sync-check.py
gate dictionary      6ef1aa0095c0ad70  .../form-translation/../hub/assets/i18n-strings.js
canonical dictionary 6ef1aa0095c0ad70  .../hub-translation/assets/i18n-strings.js
IN SYNC                                             exit 0

$ python3 tools/i18n-check.py
  English strings: 971   Nepali strings: 294
  KEPT IN ENGLISH ON PURPOSE: 32 strings held back, 0 prefixes match no key
  KEYED — no loose English allowed; Nepali still awaited
    contact.html   OK  93 keys  (37 awaiting Nepali)
    phq9.html      OK  51 keys  (23 awaiting Nepali)
    referral.html  OK  88 keys  (40 awaiting Nepali)
  Gate open: every enforced page is fully keyed and fully translated.   exit 0

$ python3 tools/i18n-protection-report.py
  9 of 9 prefixes match a live key; 0 dead
  32 keys held in English in total
  OK: every professionalOnly prefix matches a live key.                exit 0

$ python3 tools/i18n_safety_proof_file_url.py
  checks: 30   failures: 0
  VERDICT: all safety properties hold                                  exit 0

$ python3 tools/i18n_provenance_audit.py
  _meta.source.machine: 294    _meta.source.human: 0
  machine keys that have NO Nepali: 0
  Nepali keys missing from machine (unlabelled): 0
  keys in BOTH machine and human: 0
  protected keys that WRONGLY have Nepali: 0                          exit 0

$ python3 -m unittest test_i18n_keying
  Ran 10 tests ... OK                                                 exit 0
```

The safety proof drove a real headless Chromium over the **Nepali** page: all 20
PHQ-9 clinical strings and all four safeguarding strings render in English, and
the GBV / unaccompanied-child / immediate-risk checkbox and its consequence text
are present and visible.

### Dictionary staging note

`tools/i18n-check.py` reads the sibling `../hub/assets/i18n-strings.js`, an
untracked staging copy. At review time it had drifted: it was newer and much
larger (308,973 bytes, `sha256 f1d51939…`). It was backed up to
`/root/mhpss-nepal-work/backups/i18n-strings.staging-20260920-145008.js` and
replaced with the canonical `hub-translation` dictionary so the gate reads one
file; `i18n-dictionary-sync-check.py` now reports **IN SYNC**.

---

## 7. Reproduce

```
# form repo
cd /root/mhpss-nepal-work/form-translation
python3 tools/i18n_review_adjudicate.py      # 0 settled / 100 held
python3 tools/i18n_review_worksheet.py       # 25 decisions / 62 sentence-level
python3 tools/i18n_review_blockers.py        # referral: 16 alone, 17 touched
python3 tools/i18n_backtrans_check.py tools/backtrans-a.json tools/backtrans-b.json
python3 tools/i18n_safety_proof_file_url.py
python3 tools/i18n-dictionary-sync-check.py

# hub repo
cd /root/mhpss-nepal-work/hub-translation
git diff 3b82f12 -- assets/i18n-strings.js   # empty: byte-identical to parent
```

Evidence files:

| file | what it is |
|---|---|
| `tools/i18n-review-evidence.json` | all 100 keys: both readings, held |
| `tools/i18n-ne-authority-held.json` | the 100 held keys |
| `tools/i18n-ne-authority-resolved.json` | empty `{}` (nothing settled) |
| `tools/i18n-ne-review-worksheet.json` | the 25 term decisions + 62 sentence-level keys |
| `tools/i18n-ne-human-decision-required.json` | the parent worksheet (unchanged) |
| `tools/backtrans-report.json` | parent back-translation comparison |

---

## Status

**DONE - REVIEW ARTIFACT.** The 7 automated settlements are withdrawn; the
dictionary is byte-identical to the parent head; **0 of the 100 flagged keys
settled, 100 left in English and reported**; the held keys reduced to 25 term
decisions (38 keys) plus 62 sentence-level reviews; back-translation evidence is
the parent's, with no independence claim; `_meta.source.human` empty and
**independent native-speaker proofread NOT OBTAINED**. Translation of
`referral.html`, `phq9.html` and `contact.html` to a *proofread* standard is not
finished and is not claimed to be: it needs a Nepali speaker and a Ministry
terminology owner.

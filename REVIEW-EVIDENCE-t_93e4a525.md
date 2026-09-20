# Review of the 100 flagged Nepali disagreements, and the native-speaker verdict

MHPSS Nepal · task `t_93e4a525` · 20 Sep 2026

This is the evidence for the review pass the parent run (`t_2cfc3bab`) said it
could not do. It records measured counts, not prose.

| repo | worktree | branch | base | head |
|---|---|---|---|---|
| form | `/root/mhpss-nepal-work/form-translation` | `task/t_2cfc3bab` | `9032bb7` | `961b534` |
| hub | `/root/mhpss-nepal-work/hub-translation` | `task/t_2cfc3bab-i18n` | `ff2d4e2` | `5beeaf8` |

Parent heads were form `ebae7b7`, hub `3b82f12`. Production refs unchanged
(public `68bf197`, form `9032bb7`, hub `ff2d4e2`). No push, PR, merge or deploy.
Synthetic data only.

---

## What was actually left to do

The parent keyed the three pages, classified the safety strings, and ran two
independent machine drafting lanes. Where the lanes **agreed** it emitted
Nepali (117 keys). Where they **disagreed** it left the key in **English** and
recorded both readings — 100 keys, in
`tools/i18n-ne-human-decision-required.json`. `_meta.source.human` was empty
and `_meta.source.machine` held 294 drafts.

So there were exactly two things to do, and this run did both:

1. **Adjudicate the 100 disagreements** without voting on them.
2. **Obtain a native-speaker proofread** of the final text.

---

## 1. Adjudicating the disagreements — authority, not a majority

The project rule is that a disagreement is never decided by a vote. So this run
does not decide one by a vote either. `tools/i18n_review_adjudicate.py` asks a
different question of each disagreement:

> is the difference between the two readings a **term the project's own
> material has already settled**?

"Material" is three things a reviewer can open, none of which is a second
machine opinion:

* `hub-translation/assets/codes.js` — the code lists the Ministry's forms have
  to match (`np`, `help_np` fields);
* `hub-real/tools/terminology-lock.json` — the approved sentence and code pairs;
* `hub-translation/assets/i18n-strings.js` — the placeholders the platform
  already publishes.

Four routes, tried in order. A key leaves English only if one succeeds:

| route | test | settled |
|---|---|---|
| R1 | the English is a phrase the project has already rendered verbatim | 0 |
| R1b | the English is exactly published parts joined, and one reading uses exactly those parts | 0 |
| R2 | exactly **one** reading is objectively broken against the English it must render (lost `id`/`href` the page's script uses, or English words the English did not have) | 0 |
| R3 | the readings align word for word and **every** difference is decided by the material: one reading uses a published word for this English, the other uses a word that appears nowhere | 3 |
| R4 | the readings are the same words and differ only in markup or inflection | 4 |

**Result: 7 of 100 settled; 93 held in English and reported.**

The 7 settled:

| key | page | the difference | settled because |
|---|---|---|---|
| `phq9.p009` | phq9 | `को` vs `कसको` | `को` is the published rendering of "Who" |
| `phq9.p023` | phq9 | `अंग्रेजी` vs `अंग्रेजीमा` | same words (R4) |
| `ref.p050` | referral | `सेवा` vs `सेवाहरू` | `सेवा` is the published rendering of "service" |
| `svc.p007` | contact | `व्यक्तिसँग` vs `व्यक्तिसँगको` | same words (R4) |
| `svc.p031` | contact | `स्थान` vs `स्थानको` | same words (R4) |
| `svc.p070` | contact | `मिनेटमा` vs `मिनेट` | same words (R4) |
| `svc.p093` | contact | `स्थान` vs `स्थल` | `स्थान` is the published word for "site" (`स्थल` appears only inside "safe space" and "holding centre") |

`tools/i18n-review-evidence.json` carries both readings and the exact reason
for every one of the 100 keys, so a reviewer reads the evidence rather than
this paragraph.

### Why R3 is not a vote

R3 requires a positive on **both** sides: a word the project publishes *for
this English concept*, and a rival word that appears **nowhere** in the
material. To stop a word borrowed from an unrelated sentence deciding a
concept, publisher evidence is restricted to **term-level pairs** (a code-list
label, a placeholder, a short field label — at most five content words, no
sentence-ending danda) and must share a content word with the key's English.
Two words the material both uses, or two it both lacks, settles nothing and the
key is held. The rule is written to *refuse*, and it refused 93 times.

### The 93 held are 22 decisions, not 93

`tools/i18n_review_worksheet.py` groups them by the **exact** term the two
readings differ on — only keys whose readings align word for word with exactly
one differing position count:

```
held keys: 93
  settled by deciding ONE term: 35, across 22 distinct decisions
  need sentence-level review:   58
```

The single highest-value decision is the word for "referral":

| the two readings | keys one decision clears |
|---|---|
| `रेफरल` vs `प्रेषण` | 5 |
| `खुलाइए` vs `भनिए` ("stated") | 4 |
| `सञ्चालन` vs `मापन` ("administration") | 3 |
| `रेफर` vs `प्रेषण` | 3 |
| `फलोअप` vs `अनुगमन` ("follow-up") | 2 |

`referral` blocks **8** keys on its own (`ref.p003`, `ref.p011`, `ref.p012`,
`ref.p013`, `ref.p033`, `ref.p044`, `ref.p062`, `ref.p080`) and **17** keys
altogether once every key whose difference touches the referral word is counted
(`tools/i18n_review_blockers.py` prints that). The full workbook is
`tools/i18n-ne-review-worksheet.json`.

**Note the referral term is deliberately *not* decided here.** `रेफरल` has
exactly one published source, and it is the page title "Referral Directory" →
`रेफरल निर्देशिका`; `रेफरल` and `प्रेषण (रेफर)` are both in the material, so
the material does not separate them. `प्रेषण` is in fact *better* supported by
the code lists — `Screening and referral` → `स्क्रिनिङ र प्रेषण (रेफर)` and
`Referral made to another service` → `अन्य सेवामा प्रेषण (रेफर)` — but with
`रेफरल` also published, the choice is not the material's to make, so all 9
keys stay in English. That is the rule working, not failing.

---

## 2. Back-translation evidence for the final copy

The parent back-translated the 117 keys it emitted. The 7 keys settled here
were **not** in that set (both the parent's lanes had left them in English), so
they could not inherit the parent's back-translation and got their own, two
lanes against the Nepali only (`tools/i18n_backtrans_final.py`).

```
$ python3 tools/i18n_backtrans_check.py tools/backtrans-final-a.json tools/backtrans-final-b.json
comparing 217 keys across 2 back-translation lane(s): backtrans-final-a, backtrans-final-b

meaning held (both lanes >= 0.55 overlap): 102
partial  (0.30-0.55):                       13
meaning shifted (< 0.30):                    7
back-translated at all:                    122
no Nepali to back-translate (left in English): 93
```

All 7 settled keys back-translate as **meaning held** in both lanes. The final
copy for this comparison is `tools/i18n-ne-final-copy.json` (124 keys = the
parent's 117 + these 7); report `tools/backtrans-final-report.json`.

The 7 shifted and 13 partial readings are unchanged from the parent run and are
**listed, not averaged** — same keys as `tools/backtrans-report.json`
(`ref.p030`, `svc.p015`, `svc.p017`, `svc.p026`, `svc.p030`, `svc.p038`,
`svc.p058` shifted; `phq9.p013`, `phq9.p020`, `phq9.p024`, `ref.p028`,
`ref.p054`, `ref.p059`, `svc.p021`, `svc.p034`, `svc.p056`, `svc.p073`,
`svc.p089`, `svc.p090`, `svc.p092` partial). They remain priority reading for
the proofread.

---

## 3. What was edited, and where

**Dictionary (`hub-translation/assets/i18n-strings.js`)** — +7 lines in `ne`,
+7 keys to `_meta.source.machine`. Applied with the project's own append-only
`tools/i18n_apply.py` logic, through `tools/i18n_apply_review.py`, which
refuses a key under a `professionalOnly` prefix and refuses a key with no
English string. No existing line changed; the diff is the 7 strings and the
provenance list.

**Form repo** — machinery and evidence only. No page file changed.

**`_meta.source.human` stays EMPTY (0).** Every one of the 301 Nepali strings
is `machine`. A string is labelled `human` only when a person wrote or checked
it, and no person has. This is machine drafting plus a comparison against the
project's published vocabulary, and it says so.

**Safety untouched.** No `professionalOnly` key received Nepali; the 32 held in
English are unchanged; the honest reader notice
(`mt.notice.en` / `mt.authoritative.en`) stays.

---

## 4. Independent native-speaker proofread — **NOT OBTAINED**

This is the acceptance item the parent run could not satisfy, and **this run
cannot satisfy it either.** No Nepali speaker is available to this run, and a
proofread is not something that can be synthesised. It is therefore recorded as
**NOT OBTAINED**, not claimed:

> **No independent native-speaker proofread of the final text has been
> performed.** `_meta.source.human` is empty. All 301 Nepali strings, including
> the 7 settled by this review, are machine drafts that a Nepali speaker must
> check before freeze.

What this run *has* produced is the shortest possible path to that proofread:

1. **22 single-term decisions** (section 1) that clear 35 of the 93 held keys —
   the first thing to put in front of the terminology owner, starting with
   `referral` (`रेफरल` / `रेफर` vs `प्रेषण`), which clears 8 on its own and
   touches 17.
2. **58 sentence-level keys** recorded with both readings and the reason each
   was held (`tools/i18n-ne-review-worksheet.json`).
3. **7 settled keys** that changed the published text, whose back-translations
   all hold and which the proofread should confirm (`phq9.p009`, `phq9.p023`,
   `ref.p050`, `svc.p007`, `svc.p031`, `svc.p070`, `svc.p093`).
4. **7 shifted + 13 partial** back-translations to read (`ref.p030` … as above).

---

## 5. Gate state — every acceptance check, re-run against both commits

```
$ python3 tools/i18n-dictionary-sync-check.py
gate dictionary      3bc6df7826f79949  .../form-translation/../hub/assets/i18n-strings.js
canonical dictionary 3bc6df7826f79949  .../hub-translation/assets/i18n-strings.js
IN SYNC                                             exit 0

$ python3 tools/i18n-check.py
  English strings: 971   Nepali strings: 301
  KEPT IN ENGLISH ON PURPOSE: 32 strings held back, 0 prefixes match no key
  KEYED — no loose English allowed; Nepali still awaited
    contact.html   OK  93 keys  (33 awaiting Nepali)
    phq9.html      OK  51 keys  (21 awaiting Nepali)
    referral.html  OK  88 keys  (39 awaiting Nepali)
  Gate open: every enforced page is fully keyed and fully translated.   exit 0

$ python3 tools/i18n-protection-report.py
  9 of 9 prefixes match a live key; 0 dead
  32 keys held in English in total
  OK: every professionalOnly prefix matches a live key.                exit 0

$ python3 tools/i18n_safety_proof_file_url.py
  checks: 30   failures: 0
  VERDICT: all safety properties hold                                  exit 0

$ python3 tools/i18n_provenance_audit.py
  _meta.source.machine: 301    _meta.source.human: 0
  machine keys that have NO Nepali: 0
  Nepali keys missing from machine (unlabelled): 0
  keys in BOTH machine and human: 0
  protected keys that WRONGLY have Nepali: 0                          exit 0

$ python3 -m unittest test_i18n_keying
  Ran 10 tests ... OK                                                 exit 0
```

The safety proof drove a real headless Chromium over the **Nepali** page after
the dictionary change: all 20 PHQ-9 clinical strings and all four safeguarding
strings render in English, and the GBV / unaccompanied-child / immediate-risk
checkbox and its consequence text are present **and visible**.

---

## 6. Reproduce

```
# form repo
cd /root/mhpss-nepal-work/form-translation
python3 tools/i18n_review_adjudicate.py     # 7 settled / 93 held, evidence dump
python3 tools/i18n_review_worksheet.py      # the 22 decisions behind the 93
python3 tools/i18n_review_blockers.py       # what one decision would clear
python3 tools/i18n_build_final_copy.py      # final copy = parent 117 + these 7
python3 tools/i18n_backtrans_final.py       # 2 lanes over the 7 settled keys
python3 tools/i18n_backtrans_check.py tools/backtrans-final-a.json tools/backtrans-final-b.json
python3 tools/i18n_safety_proof_file_url.py

# hub repo
cd /root/mhpss-nepal-work/hub-translation
python3 tools/i18n_apply_review.py          # idempotent; safe to re-run
```

Evidence files (all versioned on purpose; `tools/*.json` is no longer ignored):

| file | what it is |
|---|---|
| `tools/i18n-review-evidence.json` | all 100 keys: both readings, the decision, the reason |
| `tools/i18n-ne-authority-resolved.json` | the 7 settled, with the English term behind each |
| `tools/i18n-ne-authority-held.json` | the 93 held, with the reason each was held |
| `tools/i18n-ne-review-worksheet.json` | the 22 term decisions and the 58 sentence-level keys |
| `tools/i18n-ne-final-copy.json` | the final Nepali copy (124 keys) |
| `tools/backtrans-final-{a,b}.json`, `tools/backtrans-final-report.json` | back-translations and the comparison |
| `tools/i18n-ne-human-decision-required.json` | the parent's worksheet (unchanged) |

---

## Status

**DONE - REVIEW ARTIFACT.** 7 of the 100 flagged keys settled by the project's
own vocabulary and published; 93 left in English, reported, and reduced to 22
decisions plus 58 sentence-level reviews; the final copy back-translated;
`_meta.source.human` empty and **independent native-speaker proofread NOT
OBTAINED**. Translation of `referral.html`, `phq9.html` and `contact.html` to a
*proofread* standard is not finished and is not claimed to be: the remaining
work is the proofread in section 4, which needs a Nepali speaker.

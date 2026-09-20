# Translation of the remaining forms — keying, safety classification, translation

MHPSS Nepal · task `t_2cfc3bab` · 20 Sep 2026

This is the evidence for bringing `referral.html`, `phq9.html` and `contact.html`
to translation-ready state and translating the translatable part of them to
Nepali. It records measured counts, not prose.

Two repositories are involved, each with its own worktree:

| repo | worktree | branch | base | head |
|---|---|---|---|---|
| form | `/root/mhpss-nepal-work/form-translation` | `task/t_2cfc3bab` | `9032bb7` | *(this commit)* |
| hub | `/root/mhpss-nepal-work/hub-translation` | `task/t_2cfc3bab-i18n` | `ff2d4e2` | *(this commit)* |

Production refs are unchanged (public `68bf197`, form `9032bb7`, hub `ff2d4e2`).
No push, PR, merge or deploy. Synthetic data only.

---

## Stage A — keying (mechanical)

`data-i18n`, `data-i18n-ph`, `data-i18n-html`, `data-i18n-skip` attributes were
added to the three pages, following the pattern in `5ws-report.html`. Every key
was added to the shared dictionary `hub/assets/i18n-strings.js` (`en` block).

| page | keys added | translatable | protected (kept English) |
|---|---|---|---|
| `referral.html` | 88 | 84 | 4 |
| `contact.html` | 93 | 93 | 0 |
| `phq9.html` | 65 | 40 | 25 |
| **total** | **246** | **217** | **29** |

Three rules were applied that a naive sweep gets wrong:

- **A `<label>` that wraps a control is never keyed on the label.** Filling a
  keyed element replaces its contents, which would delete the radio button or
  checkbox. The text goes into its own `<span data-i18n="…">` instead. Same
  reason the engine's own gate fails a keyed element that wraps a control.
- **Invariant text is declared, not assumed.** A code, a phone mask, a numeric
  pattern (`98XXXXXXXX`, `NP-XXXXX-XXXXX`, `2083-05-29`) carries
  `data-i18n-skip`, so the deploy gate does not read it as an untranslated gap.
  7 such declarations across the three pages.
- **Named protected keys.** Wording that must stay English on the Nepali page is
  keyed under a `professionalOnly` prefix (`safeguard.`, `consent.`,
  `phq9.item`, `phq9.scale`, `phq9.cutoff`, `clinical.`), so the key name is
  deliberate, not a serial number.

### No field logic changed

`test_i18n_keying.py` asserts this three ways, and it is self-contained (the
pre-keying pages are pinned in `tools/fixtures/keying-base/`, so it does not
depend on `/tmp`):

- `test_keying_does_not_change_controls_or_runtime_scripts` — every
  `input`/`select`/`textarea`/`button` (tag, type, id, name, value) and every
  `<script>` src is unchanged.
- `test_only_i18n_markup_was_added` — undo the two permitted markup edits (the
  added attributes, and the added label-text `<span>`s) and the page is
  byte-identical to its base outside the scripts.
- `test_phq9_runtime_contract_is_semantically_unchanged` — the nine item texts,
  the four scale labels and their values, and the tokens `q1: a[0]`, `q9: a[8]`,
  `total >= 10`, `item9_positive` are unchanged.

**Failing-first.** `tools/i18n_failing_first.py` restores the pinned base pages,
runs the suite, restores the keyed pages:

```
AT BASE: exit=1
base: 3 failing test(s)
AT HEAD: exit=0  OK
```

### The bilingual gate

```
$ cd /root/mhpss-nepal-work/form-translation
$ python3 tools/i18n-check.py
```

```
  KEYED — no loose English allowed; Nepali still awaited
    contact.html                       OK    93 keys  (37 awaiting Nepali)
    index.html                         OK    88 keys  (82 awaiting Nepali)
    phq9.html                          OK    51 keys  (23 awaiting Nepali)
    referral.html                      OK    88 keys  (40 awaiting Nepali)
    selfreport.html                    OK    54 keys  (49 awaiting Nepali)

  Gate open: every enforced page is fully keyed and fully translated.
```

No page has loose (unkeyed) visible English, and no keyed element wraps a form
control. Note the gate counts keys found in markup (51 for `phq9.html`); the
extractor additionally counts the keys the page mints in JavaScript (14 more:
the nine items, four scale labels, the item-9 instruction), which the gate's
HTML scanner cannot see — see the browser proof below, which covers them.

**Correction (same day, found during the reconciliation run).** The block above
is only reproducible if the gate reads the dictionary this change was made
against, and it did not say which file that was. `tools/i18n-check.py` reads a
**sibling** `../hub/assets/i18n-strings.js` — an untracked staging copy on this
host — and that copy was later left at the **pre-keying** revision while the
three pages were keyed against the new one. Running the same command then
produced the opposite result: three pages FAIL and the six `professionalOnly`
prefixes reported as matching no key, i.e. it looked like the historic
0-of-204 bug had returned. It had not; the gate was reading a stale file.

Three things now prevent that, and every count below must be read with them:

1. `tools/i18n-dictionary-sync-check.py` compares the gate's dictionary against
   the canonical tracked one by sha256 and exits 1 on drift.
2. `tools/i18n-check.py` prints the dictionary path and its sha256, and warns
   when that file is not under version control — so no count is printed without
   the artifact it was counted from.
3. The staging copy is byte-identical to the canonical dictionary
   (`6ef1aa00…40fa`); `tools/i18n_dictionary_failing_first.py` proves both
   conditions are caught by reverting the copy and by planting a dead prefix.

The exact run for this task, with the dictionary named, is in
`RECONCILIATION-t_2cfc3bab.md` and `TRANSLATION-KEYING-EVIDENCE.md`.

---

## Stage B — safety classification

`_meta.professionalOnly` holds 9 prefixes. **All 9 now match live keys**, and
32 keys are held in English:

```
  KEPT IN ENGLISH ON PURPOSE
    32 strings held back from translation: clinical.phq9ValidatedTextWarning,
    consent.label, consent.phq9, phq9.cutoff.interpretation,
    phq9.cutoff.useWarning, phq9.item1 … phq9.item9, phq9.item9Instruction,
    phq9.itemDifficulty, phq9.itemInstruction, phq9.scale0 … phq9.scale3,
    phq9.scaleDifficulty0 … phq9.scaleDifficulty3, safeguard.checkLabel,
    safeguard.confirmation, safeguard.consequence, safeguard.referralExclusion,
    sr.clinicalNote, sr.p001, sr.p007
    0 prefix(es) match no key
```

The historic bug was that this list protected **0 of 204** keys while the Nepali
pages claimed clinical wording was kept in English. The count now:

| prefix | live keys matched |
|---|---|
| `phq9.item` | 12 |
| `phq9.scale` | 8 |
| `phq9.cutoff` | 2 |
| `consent.` | 2 |
| `safeguard.` | 4 |
| `clinical.` | 1 |
| **6 of 6 live**, 29 keys | |

`test_protected_prefixes_all_match_live_keys` asserts both halves — every prefix
matches a real key, and no protected key carries a Nepali entry.

### Proven in a real browser, not by reading the source

`tools/i18n_safety_browser_proof.py` serves the site and drives a real headless
Chromium over the **Nepali** page (`?lang=ne`), then reads each protected
element by its key.

```
checks: 30   failures: 0
VERDICT: all safety properties hold
```

- All 20 PHQ-9 clinical strings render in **English** on the Nepali page: the
  nine items, the four scale labels, the item instruction, the difficulty
  question, the cut-off interpretation, the "do not use this to screen a
  shelter" warning, the missing-Nepali-text warning, and the consent wording.
- The item-9 (suicide) instruction — minted in JavaScript after a positive
  answer — renders in **English** (`<b>Item 9 is positive. Do not close this
  form and move on.</b> …`).
- All four safeguarding strings render in **English**, and the GBV /
  unaccompanied-or-separated-child / immediate-risk gate is **present and
  visible**: `#notgbv` is a real, visible checkbox, and its confirmation text and
  its consequence text both have non-zero bounding boxes. A gate that is hidden
  is not a gate, so visibility is asserted, not just presence.
- The page really is Nepali elsewhere (referral `h1` is Devanagari; 666
  Devanagari characters in the PHQ-9 page body), so "kept in English" is not
  passing merely because nothing translated.
- No element shows the `[key]` placeholder the engine prints when a key has no
  English string.

### Two real defects this found, both fixed

1. **The nine PHQ-9 items rendered as empty strings.** The keyer changed `ITEMS`
   and `OPTS` from arrays of strings to arrays of `{key, text}` objects but left
   the render code calling `t.replace(…)` on them — `renderItems` now reads
   `t.text`/`o.l`, and puts the item text in its own keyed `<span>` so the
   engine fills the text without eating the item number.
2. **The item-9 instruction rendered as the literal `[phq9.item9Instruction]`.**
   The key was minted in JavaScript but was missing from the dictionary, because
   the extractor only read the `ITEMS`/`OPTS` arrays. `i18n_extract.py` now also
   joins the concatenated JS fragments and emits the key, and the dictionary has
   the entry under a protected prefix. On the one question where someone acts on
   the answer, the instruction had been replaced by a placeholder.

Both are pinned by tests now (`test_item9_instruction_key_exists_and_is_protected`,
and the browser proof).

---

## Stage C — translation

> **Followed up 20 Sep 2026 by task `t_93e4a525` — see
> `REVIEW-EVIDENCE-t_93e4a525.md`.** The 100 disagreements this stage left for
> a human were adjudicated against the project's own published vocabulary
> (`codes.js`, the terminology lock, the dictionary's placeholders): 7 were
> settled by that material, 93 were held in English and reduced to 22 term
> decisions plus 58 sentence-level reviews. All 7 settled keys were
> back-translated; the native-speaker proofread below is still **NOT
> OBTAINED**, so `_meta.source.human` remains empty.

### Two independent translators, then a comparison

Two machine lanes drafted all 217 translatable keys from the English **without
seeing each other**: `tools/i18n-ne-draft.json` (lane A) and
`i18n-lane-b/draft-2.json` (lane B).

`tools/i18n_finalize.py` reconciles them, and the rule is the point:
**a key where the lanes disagree is left in English and reported, never decided
by a vote.**

| outcome | keys |
|---|---|
| established wording from the terminology lock (`hub-real/tools/terminology-lock.json` + `codes.js` `np`) | 33 |
| the two lanes agreed after normalisation | 84 |
| **emitted Nepali drafts** | **117** |
| left in English — the lanes disagree | 100 |

Each of the 100 disagreements is recorded with both readings and the English
source in `tools/i18n-ne-human-decision-required.json`, for a human to decide.
Worked example (`phq9.p019`, English "Follow-up"): lane A `फलोअप`, lane B
`अनुगमन`. Neither is silently picked.

**Terminology was locked to existing project vocabulary**, not invented. The 33
keys taken from the lock include `Save` → `सुरक्षित`, `District` → `जिल्ला`,
`Female` → `महिला`, `Male` → `पुरुष`, `Psychosocial counselling` →
`मनोसामाजिक परामर्श`, `Health post / primary care` → `स्वास्थ्य चौकी /
प्राथमिक उपचार`, `Psychiatric service` → `मनोचिकित्सा सेवा`. So the forms keep
matching the national code lists — which is the whole reason those lists exist.

### Back-translation

The 117 emitted drafts were back-translated to English by two lanes that saw
**only the Nepali** (`tools/backtrans-a.json`, `tools/backtrans-b.json`), in a
clean-room directory so they could not read the source English.

```
$ python3 tools/i18n_backtrans_check.py tools/backtrans-a.json tools/backtrans-b.json

meaning held (both lanes >= 0.55 overlap): 95
partial  (0.30-0.55):                       13
meaning shifted (< 0.30):                    7
back-translated at all:                    115
no Nepali to back-translate (left in English): 100
```

The 7 "shifted" readings are all flagged for human review, and they are mostly
word-choice rather than meaning loss — e.g. `svc.p026` English "Site" back
came as "Location", `svc.p015` "Focal point name" as "Contact person's name",
`ref.p030` "60 and over" as "60 years and above". Because the meaning is
ambiguous from the Nepali alone, they are listed rather than accepted. The 13
partial matches are listed too. Nothing is averaged away; a human reads the list.

### Provenance — no machine draft is labelled human

```
ne keys with text:        294
_meta.source.machine:     294   (+117 from this task)
_meta.source.human:         0
machine keys that have NO Nepali:              0
Nepali keys missing from machine (unlabelled): 0
keys in BOTH machine and human:                0
```

Every Nepali string added by this task is under `_meta.source.machine`, with a
comment in the dictionary saying in plain words that it has **not been checked
by a Nepali speaker**. `_meta.source.human` stays empty: this task has never
seen a human translator and does not label its own output as one.

### Independent native-speaker proofread — NOT OBTAINED

**This is the one acceptance item this task cannot satisfy.** There is no
native-speaker proofread of the final text, and it is not claimed. What exists
is machine drafting plus a machine comparison plus a machine back-translation;
all 294 Nepali strings are honest about being machine drafts. A Nepali speaker
must review the final text before freeze. The 100 flagged disagreements and the
7 shifted back-translations are the priority list for that review.

### The honest reader notice stays

The engine still shows "This page was translated automatically. The English
version is the authoritative one. Clinical wording is kept in English." on the
Nepali page (keys `mt.notice.en`, `mt.authoritative.en`), and it only claims
clinical wording is kept in English when the page really has a protected key —
which these pages now do.

---

## How to reproduce

```
# form repo
cd /root/mhpss-nepal-work/form-translation
python3 -m unittest -v test_i18n_keying          # 7 tests
python3 tools/i18n_failing_first.py              # base 3 failures -> head 0
python3 tools/i18n_extract.py                    # 246 keys
python3 tools/i18n_split.py                      # 217 translatable / 29 protected
python3 tools/i18n_finalize.py                   # 117 emitted / 100 flagged
python3 tools/i18n_make_apply_input.py
python3 tools/i18n_backtrans_check.py tools/backtrans-a.json tools/backtrans-b.json
python3 tools/i18n_safety_browser_proof.py       # 30 checks, needs the site on :8907

# hub repo
cd /root/mhpss-nepal-work/hub-translation
python3 tools/i18n-check.py                      # gate open
```

The browser proof needs the two worktrees staged side by side over http:
`mkdir -p /tmp/i18n-site && cp -r hub-translation /tmp/i18n-site/hub &&
cp -r form-translation /tmp/i18n-site/form`, then serve `/tmp/i18n-site` on
port 8907.

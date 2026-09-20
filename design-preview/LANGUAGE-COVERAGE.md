# Language coverage — measured state

**Question this answers:** "the Nepali page is still mixed with English, and the English
form still has Nepali in it — please check everything and make the pages consistent."

**Measured:** 2026-09-20, from the running pages plus `tools/i18n-check.py` and a
browser audit. Numbers, not impressions.

---

## 1. Nepali leaking into the English page — was real, is fixed

A fresh visitor lands on Nepali and taps **ENG**. Measured Devanagari text nodes
remaining after that switch:

| Page | before | after |
|---|---|---|
| `5ws-report.html` | 0 | 0 |
| `5ws-report-b2.html` | **5** | **0** |
| `index.html` | 0 | 0 |
| `phq9.html` | 0 | 0 |
| `referral.html` | 0 | 0 |
| `contact.html` | 0 | 0 |
| `selfreport.html` | 0 | 0 |
| `4ws-report.html` | 0 | 0 |

The five were the B2 step rail. Two causes, both mine:

1. the rail **snapshotted** its label from `.step h2` once at mount, so it kept the
   language it was built in;
2. the saved-list column crumbs are generated content (`::before`), which `i18n.js`
   cannot re-render, and they hardcoded Nepali.

Both now follow the selected language. The rail re-derives from the heading on the
`i18n:changed` event, so it needs no Nepali of its own; the crumbs match the table's
own `<th>`, which are the reviewed strings.

**Why the first audit missed this:** it loaded `?lang=en` cold. On a cold English load
the translation notice never mounts and the rail is built in English — the bug only
appears on the path a reader actually takes. The audit now drives the toggle.

---

## 2. English still untranslated in the Nepali page — measured, and large

From `tools/i18n-check.py` (the project's own gate):

```
English strings: 725       Nepali strings: 177
```

So **548 English strings have no Nepali at all**. They are not evenly spread:

| Area | Keys | State |
|---|---|---|
| 5Ws report (the form in active use) | 91 | **complete** — 0 missing |
| `index.html` | 88 | keyed, **82 awaiting Nepali** |
| `selfreport.html` | 54 | keyed, **52 awaiting Nepali** |
| `contact.html`, `phq9.html`, `referral.html`, `4ws-report.html` | 0 | **not migrated**: prose is still hardcoded in the HTML, so it cannot be translated by key. ~2,600 words |
| hub pages (`flood.*`, `live.*`, `res.*`, `home.*` …) | ~430 | **outside this worktree** — they live in the hub repo, which is not cloned here |

`i18n-check.py` reports `NOT YET MIGRATED … TOTAL 4323 words to key up`.

### The notice is already page-accurate

Worth noting because it is the honest part and it works: each page states its own
state, measured in the browser.

| Page | notice kind | says |
|---|---|---|
| `5ws-report`, `5ws-report-b2`, `4ws-report` | `full` | "This page was translated automatically." |
| `index`, `selfreport` | `full` | same (few keys translated) |
| `phq9`, `referral`, `contact` | `partial` | "The choices in this form's lists have been translated automatically" |
| `cards` | absent | no i18n layer at all |

---

## 3. No human review exists yet — important

`_meta.source.human` is **empty**. All 177 Nepali strings in the app are marked
`machine`. There is therefore **no reviewed Nepali to check new output against**, and
any claim of "accurate translation" would be unfounded. What can be measured is
*consistency* — whether new output uses the same vocabulary as the existing Nepali —
and that is what the accuracy harness measures.

---

## 4. Machine translation: engine and guardrails

Engine: `facebook/nllb-200-distilled-600M`, local, CPU-only, offline after download
(`/root/nmt/`). It replaced nothing: the previous state was no Nepali at all.

### Measured quality — and it is not "good", it is "usable as a draft"

Scored against the app's own existing Nepali (18 real pairs, 25–140 chars each):

```
mean agreement 0.648      close (>=0.45): 14/18
                          loose (0.30-0.45): 4/18
                          divergent (<0.30): 0/18
```

The disagreements were **not random — they were vocabulary drift**, which is exactly
what makes a form feel machine-made:

| concept | model produced | app's own word | problem |
|---|---|---|---|
| report | रिपोर्ट | **प्रतिवेदन** | transliteration instead of the Ministry word |
| cadre | क्यारेक्टर | **जनशक्ति** | "character" — wrong word entirely |
| save | बचत | **सुरक्षित** | "savings", not "make safe" |
| breakdown | विघटन | **विभाजन** | "disintegration", not "breakdown" |
| Bikram Sambat | *(left in Latin)* | **विक्रम संवत्** | untranslated |

A terminology guard (`/root/nmt/glossary.py`) rewrites these toward the app's own
vocabulary. Two rules keep it honest: every target must be **attested** in
`i18n-strings.js` (nothing invented), and replacements are whole-word only, with every
change recorded per string. The guard refuses to run if a target stops being attested.
It immediately caught two of my own wrong entries while I built it.

### Speed

Beam search cost **196 s for one 350-char string**; greedy decoding (beams=1) does the
same string in **22 s**. Because every value is a draft a reviewer corrects anyway,
9× the CPU for a marginal gain is the wrong trade on a 2-core box. Batch size 8.

### Markup is protected

Tags and `{placeholders}` are removed before translation and spliced back by position, so
a tag cannot be lost or reworded. Verified: `<b>Note:</b> … {thing}` →
`<b>नोटः</b> … {thing}`. When the inline pass cannot recover the spans exactly, the
engine falls back to translating the plain segments and re-inserting the original
markup, so the markup never reaches the model.

**Never machine-translated**, by prefix, in the pipeline itself:

- `phq9.*` — the Nepali PHQ-9 is validated as specific wording (Kohrt et al., cut-off
  ≥10). Re-wording it scores people against a threshold validated for different words.
- `consent.*` — consent given in Nepali to something the English did not say is not consent.
- `safeguard.*` — the GBV / child-protection / immediate-risk gate.
- `clinical.*` — terms with an established Ministry equivalent.

The 5Ws **safety copy** (offline behaviour, "keep this page open", what a record
appearing in the Hub does and does not prove) is also left to the reviewer, not
auto-published.

---

## 5. What is ready to review

- `design-preview/i18n-ne-fill.json` — 111 machine Nepali values for keys the pages
  already reference, each tagged `provenance: machine`, `reviewed_by_human: false`.
- `design-preview/i18n-ne-review.md` — English | Nepali side by side, for a Nepali
  reviewer to correct in place.

Nothing has been written into `hub/assets/i18n-strings.js` yet. That file also cannot
be committed from here: `hub/` has no git repository on this host and the `form`
repository tracks no `hub/` paths — the same blocker recorded in
`PENDING-hub-i18n-default-ne.patch.md`.

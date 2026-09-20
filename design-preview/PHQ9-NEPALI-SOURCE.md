# The validated Nepali PHQ-9 — found, with one catch

**Requested by:** Adib (Dr. Kedar said the validated Nepali PHQ-9 is published).
**Answer: he is right, and it is findable. It is now downloaded here.**

## The source

Kohrt BA, Luitel NP, Acharya P, Jordans MJD.
*Detection of depression in low resource settings: validation of the Patient Health
Questionnaire (PHQ-9) and cultural concepts of distress in Nepal.*
BMC Psychiatry 2016;16:58. DOI `10.1186/s12888-016-0768-y` · PMID 26951403 · **PMC4782581**

Open access (BMC, CC-BY). **Additional file 1** is titled
*"Nepal PHQ-9 Primary Care Depression Screening Tool"* and is the instrument itself.

Saved here: `design-preview/references/kohrt-2016-nepal-phq9-supplement.pdf` (494 KB)

Sha-256 recorded below so a later reader can prove it is the same file.

## What is actually inside it

1. **Introduction** — how the screening is explained to the patient.
2. **Step 1 — heart-mind problem screening** (1 question: `manko samasya`).
3. **Step 2 — impairment** due to the heart-mind problem (1 question).
4. **Step 3 — the nine PHQ-9 items**, each with the Nepali wording **and** the English
   back-translation side by side, plus the response grid.
5. **Water-glasses pictorial response scale** — the four levels drawn as glasses.

So it can be used as intended: a stepwise screen, not the nine items alone.

## The catch — and it is the same catch the app's page already reports

**The Nepali text in that PDF is in a legacy non-Unicode font (Preeti-family
encoding), not Unicode Devanagari.** Proof: item 1 begins

```
tkfO{ cfGo JolQmx¿ hlt /dfpF5g\ , ...
```

which is Preeti for `तपाईं अरू व्यक्तिहरू जति …` — not Devanagari characters. Extracting
the text therefore yields gibberish for the Nepali half, while the **English
back-translation extracts cleanly**.

This is exactly why `phq9.html` says the copy available was "typeset in a legacy
non-Unicode Nepali font, so the characters cannot be transferred here without risking a
corrupted questionnaire". That statement was true, and the file has now been located.

## What this means for the plan

The instrument **can** be obtained from here — it does not need to be requested from
anyone. But getting it into the app is a two-step job, and step 2 is not optional:

1. **Convert Preeti → Unicode.** Mechanical, scriptable, and verifiable: a Preeti font
   table is a fixed mapping. It is reversible, so the result can be round-tripped back
   to the original glyphs to prove the conversion lost nothing.
2. **Have the converted text read by a Nepali speaker.** This is the step that cannot be
   automated and must not be skipped: the whole reason the instrument is trusted is that
   its wording was fixed by a four-stage transcultural process (bilingual translation,
   professional review, focus groups, blind back-translation). A conversion error is
   invisible to anyone who cannot read Nepali, and a single wrong word changes what the
   instrument measures.

## Why a machine translation of the standard PHQ-9 would NOT be this instrument

Worth stating plainly, because it is the whole point:

- the validated version **rephrases every item as a question** ("In the past 2 weeks,
  compared to other people, how much do you feel…"), where the standard English items
  are declarative ("Little interest or pleasure in doing things");
- the validated **response scale was changed** to *not at all / sometimes / usually /
  always*, because test participants could not work with "more than half the days";
- item 6 was rebuilt around **`ijjat gumaune`** (damaging the family's social standing)
  and item 8 around **`chhatpatti`** (restlessness);
- a **pictorial water-glass scale** replaced the numeric response options.

A fresh English→Nepali translation reproduces none of that. The cut-off ≥10
(sensitivity 0.94, specificity 0.80, PPV 0.42) belongs to these specific words **with
this specific response scale**. So the machine draft stored for `phq9.*` stays marked
`provisional` and is not displayed as the instrument.

## Recommendation

Convert the supplement to Unicode, hold it next to the English back-translation that
extracts cleanly from the same PDF (that gives the reviewer a line-by-line check), and
send both to a Nepali-speaking clinician. Also obtain the response scale, not just the
nine items — the cut-off is attached to the scale as much as to the words.

Note: the paper says the tool was adapted through PRIME (TPO Nepal). The supplement's
own contact for administration and psychometric questions is **Nagendra Luitel**,
Research Department, TPO Nepal — worth contacting if anything in the conversion is
ambiguous.

## Provenance

```
file : kohrt-2016-nepal-phq9-supplement.pdf
src  : https://static-content.springer.com/esm/art%3A10.1186%2Fs12888-016-0768-y/MediaObjects/12888_2016_768_MOESM1_ESM.pdf
size : 494688 bytes
sha256: 5bb92375e8e8efaed9fc863a4e66d5c44c75e7156478b7ee447319371e0aef74
```

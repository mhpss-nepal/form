# Training and orientation record — the form that replaces group 5

Drop-in page: `training-report.html`, for `form/` in the field-form repository. Built on the same
shell as the other Layer 1 pages (`../hub/assets/`), Nepali by default with the ENG/NEP toggle.
**Nothing was pushed; the repositories are untouched.**

Record: `kind: "training"`, schema `mhpss-np-training/0.1.0-draft`, `iasc_sub: "11.3"`.

## Why it exists

Capacity building left the 5Ws by the Coordinator's ruling of 27 September. The reason is a
counting one: the people in a training room are aid workers, not people reached by the response,
and counting them as attendance inflates every reach figure. They are counted here instead, as
people trained. Orientations *for other relief teams* stay on the daily report as activity 1.2 —
that is a service to another team, not capacity building of one's own staff.

## What the guidance requires, and where each requirement sits

| Requirement | Source | On the form |
|---|---|---|
| The IASC code for this record is **11.3 Training / orienting**, and the topic must be named | 4Ws manual, Table 2 (the list users are asked to apply; Annex 5 numbers code 11 differently and is not used) | `iasc_sub` fixed at 11.3; *Title, as announced* is required |
| **Orientation and training are different things**: orientation is brief and one-off, training is fuller capacity building that requires ongoing support and supervision | MSP M&E Indicator Bank, p. 10 | First question of part 2, with the definition as help text |
| Staff and volunteers oriented on basic psychosocial support, **disaggregated by type of staff or volunteer** | Indicator Bank, p. 20 | Participants are counted by cadre, from the agreed twelve-code list |
| Staff **trained *and* supervised**, by type of facility and type of staff | Indicator Bank, p. 20 | Part 4: supervision provided · planned · none, and how often. Nothing in the architecture recorded supervision until now |
| Age, gender and disability disaggregation where possible | Indicator Bank, p. 6 | Sex on every row. Age bands are deliberately **not** asked: participants are adults, so the five bands would be constant. Two optional counts stand in — under 18, and participants with a disability |
| Humanitarian actors oriented, by type of workshop; a roster of trainers; follow-up, because one-off trainings are not recommended | IASC MHPSS Coordination Handbook 2022, p. 34–35 | Package or topic; facilitating **organisation** and number of facilitators. The trainer roster is a separate thing and no trainer's name is recorded here |
| Standardised, accredited training through the national and provincial health training centres | MSP Nepal project document (WHO activities 2.2.x) | *Accreditation*: NHTC or a provincial centre · not accredited · not known |
| Process and impact indicators are different | Indicator Bank, p. 6 | Counts are the process side; *knowledge assessed before and after* marks where an impact reading exists |

The package list — PFA · basic counselling skills · basic MHPSS · mhGAP · other — is the group 5
list as it stands in the SORMAS module, read on 27 September. It was not invented here.

## The participant block, and why it is built this way

One row per **palika the participants work in**, each row carrying cadre and counts by sex. Not the
palika where the training was held.

A training in Kathmandu for staff working in Rasuwa belongs to Rasuwa. Recording the venue instead
would put the trained workers on the map in the wrong place — and the map is the point: it is what
lets the referral directory say that a place has PFA-trained staff.

**One honest limit, which must be printed wherever the map is shown.** These counts are a *flow*,
not a *stock*. The same person trained twice is counted twice; people move; people leave. A figure
built from this form can only ever be labelled *people trained, cumulative* — never *trained
workers present*. The stock figure has to come from the other side: a trained-cadre marker on the
service-point and provider registrations, with this record as the evidence behind it. Each alone
misleads; together they hold.

## Safeguards carried over

- **Co-organised events.** The same lead-or-partner rule as the 5Ws: choosing *we co-organised*
  switches off every count, demands the lead organisation be named, and marks the record
  `counts_held_by_lead: true`. One event, counted once.
- **No personal data.** No participant name, no trainer name, no attendance list. The notes field
  says so in its own help text.
- Duplicate guard: the same palika and cadre cannot appear on two rows.
- Optional counts are bounded by the total trained.

## Verified

Run in Chromium against the repository's own shared assets, with all outbound network blocked and
nothing submitted anywhere: **18 checks, 0 failures.** The empty form is refused and names
supervision among the missing answers; the palika list follows the district chosen on each row; the
live total reads people, palikas and cadres; the same palika and cadre twice is refused; an
under-18 count above the total is refused; the saved record carries `kind: training`,
`iasc_sub: 11.3`, the totals and the rows with their working palika P-codes; co-organiser mode locks
the counts, demands the lead and saves with none; and the Nepali repaint carries every new label
with no untranslated key on the page.

## Before it goes out

The Nepali is a machine draft, for a translator. The page was built on the plain Layer 1 pattern, so
it does not yet carry the preview-isolation, trial-scope and QR conventions now on `main`; whoever
folds it into the package adapts those, moves the draft-string block into
`hub/assets/i18n-strings.js`, and adds the form to the index.

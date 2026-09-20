# Trial scope evidence — 5Ws only

Status: DONE — REVIEW ARTIFACT (not deployed)

## Trial entry points

Remaining actionable form page: **1**

1. `5ws-report.html`

Remaining QR payloads in the field build: **2**

1. `master` → `/form/` (the landing page, which exposes only 5Ws)
2. `5ws` → `/form/5ws-report.html`

Printable card payloads: **1**

1. `5ws` → `/form/5ws-report.html`

## Removed entry points

From `index.html`, removed **12** controls for the four unapproved forms:

- 4 open-form links
- 4 copy-URL buttons
- 4 QR buttons

Also removed the Hub Inbox navigation link because the Hub form inbox advertises
the unapproved form pages. The landing page keeps only the general Hub and
coordination links, neither of which is a form catalogue.

Three further strings were dropped from `index.html` because they described the
old five-form build: `ml.p031` (which carried a link to `../hub/forms.html`),
`ml.p077` ("...a field worker has all the forms...") and `ml.p079` ("...every
form's QR on it..."). The dictionary entries themselves are untouched.

From `cards.html`, removed **5** printable cards:

- landing-page/master card labelled “All five forms”
- Service Contact Record
- PHQ-9
- Referral Record
- Self Report

From `manifest.webmanifest`, removed **2** unapproved shortcuts:

- Service Contact
- Referral

From `sw.js`, removed **5** unapproved/prototype pages from precache:

- `4ws-report.html`
- `contact.html`
- `phq9.html`
- `referral.html`
- `selfreport.html`

The service-worker cache was bumped from `mhpss-np-field-v39` to `mhpss-np-field-v40` so an installed client cannot keep the old precache set.

From QR generation, removed **4** unapproved payloads:

- `contact`
- `phq9`
- `referral`
- `self`

The field build now loads the repository-owned `qr-trial.js`, containing only `master` and `5ws`, rather than the broader sibling Hub QR asset.
The broader Hub asset remains outside this form repository and was not edited; neither trial page loads it.
`tools/qr-check.py` now fails unless those are the exact two asset keys with the
exact approved URLs, so an additional valid-but-unapproved matrix cannot pass.

## Remaining references to unapproved page files

Reachable from approved trial pages: **0**.

The page files remain unchanged in the repository for explicitly internal review, as required. References that remain are confined to:

- the unapproved pages' own internal cross-links (`phq9.html`, `referral.html`);
- test and diagnostic inventories that enumerate repository pages;
- `test_trial_scope.py`, where the filenames are forbidden-value assertions.

No unapproved page is linked from `index.html`, printed by `cards.html`, advertised by the manifest, included in `qr-trial.js`, or precached by `sw.js`.

One item on `index.html` names unapproved instruments but is documentation, not a
path: the "Where each form comes from" provenance table (`ml.p049`–`ml.p069`)
carries no link, no QR payload, no button and no save. It is left in place with
the form pages themselves, and is flagged here rather than silently kept.

Two shared dictionary strings are now *inaccurate* for the trial build and are
left for the separate dictionary task rather than edited here (the text lives in
`hub/assets/i18n-strings.js`, outside this repository): `ml.p036` ("One link,
every form a field worker needs"), the landing-page heading, and `ml.p011`, whose
closing sentence still says the questions "go to the field for piloting". This
does not create a path to any unapproved form; it is a wording follow-up.

## Residual path — outside this task's scope (recorded, not silently accepted)

One path remains, and it lives in the **Hub** repository, which requirement 7
forbids this task from touching:

- `hub/forms.html` (the Hub form inbox) links `../form/contact.html`,
  `../form/referral.html`, `../form/phq9.html`, `../form/selfreport.html`.
- `hub/index.html` also names Service contact, Referral, PHQ-9 and Self-report in
  its navigation, pointing at `forms.html#…`.

This is a restricted, sign-in coordination surface rather than the field QR/link
set, so it is not the default entry point a field worker scans into. It is still
reachable by typing a Hub URL, so it is a real remaining exposure and must be
closed in the Hub repository (the sibling Hub task works in `/root/mhpss-nepal-work/hub-real`).
This form task removes its own contribution to that path: the `../hub/forms.html`
"Inbox" link is gone from `index.html`, and the two surviving Hub links point at
the Hub landing page, not the form catalogue.

## Verification commands

- `python3 -m unittest -v test_trial_scope.py`
- `python3 tools/qr-check.py`
- `python3 tools/sw-precache-check.py`
- `python3 -m unittest -v design-preview/test_b2_preview.py design-preview/test_institutional_preview.py`

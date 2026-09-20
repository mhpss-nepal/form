# Trial scope evidence — 5Ws only

Status: DONE — REVIEW ARTIFACT (not deployed)

- Repository: `/root/mhpss-nepal-work/form-frontend` (branch `design/form-frontend`)
- Base: `8c84f43c4d0829266e86f4be0ba9bac96b1fdb22`
- Head: the commit that contains this file; its exact hash is recorded in the
  task handoff (the file was updated by the final commit, so an in-file hash of
  itself would immediately be a hash of the wrong commit).
- Worktree: clean (`git status --porcelain` empty)
- Production refs unchanged: public `68bf197`, form `9032bb7`, hub `ff2d4e2`. No push, PR, merge or deploy.
- `hub/` paths touched: **0**. Form-page content and `pwa.js`: byte-identical to base.

## What the tests do (and do not) pin

`test_trial_scope.py` pins, from the code itself rather than from prose:

1. `git show <base>:5ws-report.html|4ws-report.html|contact.html|phq9.html|referral.html|selfreport.html|pwa.js`
   is byte-identical to the working tree (content must not drift).
2. `index.html` exposes exactly one form link (`5ws-report.html`), one copy-URL
   target (`5ws-report.html`), one QR key (`5ws`), and zero references to any of
   the four unapproved filenames; it also contains no `forms.html` target.
3. `cards.html` renders exactly one QR (`5ws`) and one URL label (`5ws`).
4. `sw.js` contains none of the four unapproved filenames, and
   `manifest.webmanifest` has exactly one shortcut, the 5Ws form.
5. `tools/qr-build.py`'s `TARGETS` list is exactly `master` + `5ws`; `qr-trial.js`
   holds exactly those two entries with exactly those approved URLs.
6. `tools/qr-check.py` returns 1 for an asset that adds a valid extra `contact`
   matrix (imported and exercised in-process, asset file untouched on disk).

Not asserted (out of a static site's reach): that a `hub/`-hosted page reached by
typing its URL cannot open an unapproved form. That is the residual path below.

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

Exact counts, base `8c84f43` → head recorded below:

| Command | At base (failing first) | At head |
| --- | --- | --- |
| `python3 -m unittest -v test_trial_scope.py` | 7 tests, **5 failures + 1 error** (`qr-trial.js` absent) | 7 tests, **0 failures** |
| `python3 -m unittest -v design-preview/test_b2_preview.py design-preview/test_institutional_preview.py` | 48 tests, 0 failures | 48 tests, 0 failures |
| `python3 tools/qr-check.py` | 0 (6 matrices) | 0 (2 matrices, allowlist enforced) |
| `python3 tools/sw-precache-check.py` | 0 (cache v39) | 0 (cache v40, 25 entries, 3 pages) |
| `python3 tools/i18n-check.py` | 0 (gate open) | 0 (gate open) |
| `python3 tools/text-setting-check.py` | 0 | 0 |

An adversarial probe confirmed the checker is not vacuous: a `qr-trial.js` with a
valid extra `contact` matrix now exits 1 (`QR ASSET SCOPE MISMATCH`), and
`test_qr_checker_rejects_any_extra_asset_entry` reproduces that in-suite.
`design-preview/test_b2_preview.py`'s byte-lock on `sw.js`/`manifest.webmanifest`
was narrowed to `pwa.js` (the file this task does not touch), because the trial
scope change to the other two is intentional and is now covered by
`test_trial_scope.py`; that narrowing is verified by the byte-parity test above,
which pins `5ws-report.html`, the four unapproved pages and `pwa.js` to base.

## Rendered-browser evidence (a real DOM, not source text)

Source-level tests cannot see chrome a shared asset injects at runtime, or prove
a declared QR actually drew. Two tools drive real Chromium over the served site
(both repos under one root, so `../hub/assets/*` resolves):

```
cd /root/mhpss-nepal-work && python3 -m http.server 8791 --bind 127.0.0.1 &
python3 tools/trial-scope-render-check.py http://127.0.0.1:8791   # exit 0
python3 tools/5ws-still-works.py        http://127.0.0.1:8791     # exit 0
```

`trial-scope-render-check.py` at 390 px and 1280 px:

```
390 mobile     landing    cards=4 qr=['5ws'] drawn=520 sheetDrawn=0 sheetUrls=[] hrefs=['5ws-report.html', 'cards.html']
390 mobile     card sheet cards=0 qr=['5ws'] drawn=0 sheetDrawn=299 sheetUrls=['mhpss-nepal.github.io/form/5ws-report.html'] hrefs=[]
1280 desktop   landing    cards=4 qr=['5ws'] drawn=520 sheetDrawn=0 sheetUrls=[] hrefs=['5ws-report.html', 'cards.html']
1280 desktop   card sheet cards=0 qr=['5ws'] drawn=0 sheetDrawn=299 sheetUrls=['mhpss-nepal.github.io/form/5ws-report.html'] hrefs=[]
```

It clicks every QR control, then asserts: no `a[href]` anywhere in the rendered
DOM resolves to an unapproved form; no rendered `[data-qr]` is anything but `5ws`
(or `master`); the landing page has exactly one actionable form card; the printed
sheet draws its QR (299 rects) and prints only the 5Ws address; and there are no
console **errors** (informational logs such as the Hub bridge's "heartbeats
undefined" are ignored, because a check that fails on noise gets switched off).

`5ws-still-works.py` renders `5ws-report.html` and compares the live DOM to the
committed source:

```
title        : MHPSS Activity Report (5Ws) — Nepal Flood Response
lang         : ne   i18n switch: True   toggle: ['ENG', 'NEP']
name= in form: 24 (source expects 24) -> match
controls     : 54 in form / 54 in document
selects      : ['org','cadre','district','site','palika','modality','activity','status']
counts       : 10 checkboxes, 21 numeric, 1 submit
ids present  : f, expCsv, expJson, wipe, reset, problems, tgs
.html hrefs  : ['index.html']
```

So the 5Ws form still resolves to Nepali by default, still mounts the ENG/NEP
switch, keeps its full `name=` contract and all eight agreed pickers, and links
only `index.html`. Matching is on ids and on the `name=` contract extracted from
the committed page — never on button *text*, which is language-dependent.

## Direct URL entry, with the service worker active

Requirement 4 has two halves, both met: the four pages are **not precached**
(Cache Storage after install holds exactly the 25 listed entries, none of them an
unapproved page — verified by reading `caches.keys()`/`c.open().keys()` from the
browser), and they are **not reachable from any in-page navigation** (no link on
any approved page; the rendered sweep above proves it).

One honest limitation remains, and it is a property of a static build, not of
this change: a person who types the exact address, or follows an old bookmark or
forwarded link, is served the file by the origin — GitHub Pages has no server-side
rule to refuse it, and this task may not modify the pages themselves. Observed
directly: with the worker active and controlling the page, `GET
/form/contact.html|phq9.html|referral.html|selfreport.html` returned 200 for all
four. Blocking that would need either a host rule, or a deny-list inside
`sw.js` — which would also block the restricted Hub's legitimate internal
"Open the form" links and belongs to that decision, not this one. It is carried
into the Hub task (`t_46e4cb25`) rather than left implicit here.

# MHPSS Nepal — Layer 1, the field forms

Served at **https://mhpss-nepal.github.io/form/** (GitHub Pages, branch `main`).

The supervised trial exposes only the approved 5Ws activity report, its printable
QR card, and the service worker that keeps it usable with no signal. The other
prototype page files remain in the repository for explicitly internal review but
are not linked, advertised, precached, or included in the trial QR asset. The
shared code — vocabularies, record store, register bridge, design tokens,
bilingual dictionary — is loaded from the sibling repository **`hub`** at
`../hub/assets/`, which is also where it sits
on the live site; a change to a code list is deployed once, in `hub`, and every
form picks it up.

`tools/sw-precache-check.py` refuses a deploy in which a precached page needs
a file that is not precached, or a precached path that does not exist.
`tools/qr-check.py` holds the trial QR asset to an **exact** allowlist — the
`master` and `5ws` entries with their declared URLs — decodes every matrix and
refuses one that points anywhere other than its own label, so a valid extra
matrix for an unapproved form cannot slip in.

Guard rails for the trial scope:

- `test_trial_scope.py` — the landing page exposes exactly one form; no link,
  copy-URL, QR payload or rendered card reaches the four unapproved forms; the
  printed sheet emits only the 5Ws code; `index.html` carries no `forms.html`
  target; the unapproved pages and `pwa.js` stay byte-identical to base.
- `tools/trial-scope-render-check.py` — the same claims checked again in a real
  browser over the served site, at 390 px and 1280 px, after clicking every QR
  control, so a QR that was declared but never drew is caught.
- `tools/5ws-still-works.py` — the one approved form still loads with its full
  `name=` contract, its eight pickers, its count and target-group controls and
  its ENG/NEP switch.

Run them with both repositories under one served root, because the pages load
`../hub/assets/*`:

```
cd <parent of form-* and hub-*> && python3 -m http.server 8791 --bind 127.0.0.1 &
python3 tools/trial-scope-render-check.py http://127.0.0.1:8791
python3 tools/5ws-still-works.py        http://127.0.0.1:8791
```

Known limitation, recorded rather than implied fixed: a static host serves these
page files to anyone who types the exact address, and this trial build cannot
refuse that. The four unapproved pages are unreachable from every approved page
and are not precached; they are not *unavailable*. See `TRIAL-SCOPE-EVIDENCE.md`.

**No personal data, and none is to be added.** No field for a name, a phone
number, a date of birth, an identity number or a diagnosis exists on any form,
and none is to be added. Focal-point contact details are kept on the handset
and never reach the register.

Draft instruments, not agreed with EDCD or the MHPSS Technical Working Group.

# MHPSS Nepal — Layer 1, the field forms

Served at **https://mhpss-nepal.github.io/form/** (GitHub Pages, branch `main`).

The supervised trial exposes only the approved 5Ws activity report, its printable
QR card, and the service worker that keeps it usable with no signal. The other
prototype page files remain in the repository for explicitly internal review but
are not linked, advertised, precached, or included in the trial QR asset. The
shared code — vocabularies, record store,
register bridge, design tokens, bilingual dictionary — is loaded from the
sibling repository **`hub`** at `../hub/assets/`, which is also where it sits
on the live site; a change to a code list is deployed once, in `hub`, and every
form picks it up.

`tools/sw-precache-check.py` refuses a deploy in which a precached page needs
a file that is not precached, or a precached path that does not exist.
`tools/qr-check.py` decodes every trial QR matrix and refuses one that points anywhere
other than its own label.

**No personal data, and none is to be added.** No field for a name, a phone
number, a date of birth, an identity number or a diagnosis exists on any form,
and none is to be added. Focal-point contact details are kept on the handset
and never reach the register.

Draft instruments, not agreed with EDCD or the MHPSS Technical Working Group.

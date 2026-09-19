# MHPSS Nepal — Layer 1, the field forms

Served at **https://mhpss-nepal.github.io/form/** (GitHub Pages, branch `main`).

Five field forms, the printable QR card sheet and the service worker that keeps
them usable with no signal. The shared code — vocabularies, record store,
register bridge, design tokens, bilingual dictionary — is loaded from the
sibling repository **`hub`** at `../hub/assets/`, which is also where it sits
on the live site; a change to a code list is deployed once, in `hub`, and every
form picks it up.

`tools/sw-precache-check.py` refuses a deploy in which a precached page needs
a file that is not precached, or a precached path that does not exist.
`tools/qr-check.py` decodes every QR matrix and refuses one that points anywhere
other than its own label.

**No personal data, and none is to be added.** No field for a name, a phone
number, a date of birth, an identity number or a diagnosis exists on any form,
and none is to be added. Focal-point contact details are kept on the handset
and never reach the register.

Draft instruments, not agreed with EDCD or the MHPSS Technical Working Group.

## Deployment blocker — atomic Form/Hub release required

**Unresolved B6 blocker:** this Form repository and the separate Hub repository
are review artifacts only. They cannot be merged or deployed as independent
releases. Forms load moving shared assets from `../hub/assets/`, so a partially
completed rollout can pair new Form call sites with an old Hub persistence
contract, or old Form call sites with new Hub behavior. The machine-verifiable
release contract produced with this review identifies the exact Hub commit,
Form commit, precache asset fingerprint and cache version that a later monorepo
integration must consume as one atomic pair. That contract does **not** resolve
rollout: the pair **must not be merged or deployed** until it is integrated and
verified atomically in the monorepo with one rollback boundary.

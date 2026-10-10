# Integrated cache correction — unpublished candidate

Ordinary browser/HTTPS deployment trust, approved by the owner. Worker self-fetch
is an accidental package-mismatch check, **not** cryptographic proof of bytes
already executed against a malicious differential origin.

## Integration

- `sw.js` replaces actual `/form/sw.js` v43. Its root scope remains `/form/`.
- `cache-migration-v43.js` is a new, uncached delivery URL appended to the four
  existing legacy landing/activity/cards/4Ws redirect pages. This matters because
  old v43 serves old `pwa.js` cache-first. No form field or data handler is changed.
- The actual restricted TEST entry remains
  `review-5ws-admin-test-v35/releases/native-test-20261009/review.html`.
  Its inherited native form, queue, Auth, validation, transport, correction,
  listing and CSV modules are unchanged.
- Root static dependency bytes are vendored from pinned Hub main
  `47f66df13198345907ace5c314f2fbe6f9d1db58`; no sibling worktree is needed to
  reproduce the release package. Existing displayed navigation remains intact.

## Authority and atomicity

Each full release uses a manifest digest and served worker digest, with their
canonical composite identity independently expected by the page's release pin.
The worker URL contains those exact pins. Manifest and asset download paths are
immutable. Requests are served from stable keys only after digest, decoded byte
length and exact hosting MIME type verification. Cached Responses reset their
response URL to the stable key, preserving relative ES-module import resolution.
Compressed transfer lengths are not confused with decoded package lengths.

Installation writes only a unique own staging cache. A complete manifest and all
assets are checked before a strict IndexedDB transaction publishes its pointer.
There is no partial target-copy window. The only cache deleted is that exact
newly-created stage on refusal or a lost same-release publication race. No prefix
sweep, origin-wide deletion, queue/localStorage cleanup, or unregister is used.
Prior complete releases, old v43, child and unrelated caches are retained.

Durable explicit acceptance is separate from install, natural activation and
login. Acceptance writes both the release record and scope-selected prior-safe
pointer in one strict transaction. A naturally activated but unaccepted newer
worker serves the prior accepted complete package; it does not accept the new
one. Cold first install without accepted predecessor remains network-only.
Rollback registers the prior pinned worker URL and explicitly accepts that exact
release. A served pin mismatch is refused without changing pending obligations.
No automatic reload or queued dispatch occurs in cache adapters.

Queries, fragments visible to the worker, Authorization, non-GET, foreign origin,
auth/API/admin/signin routes and non-inventory paths are not cached. Browser URL
fragments are not generally transmitted to fetch, so page navigation semantics
still apply. An offline query-bearing legacy link is deliberately not satisfied
using an ignoreSearch fallback. Normal legacy 4Ws-to-5Ws navigation is preserved.

## Verification and limits

`python tools/sw-precache-check.py` invokes the manifest-based verifier. Browser
and genuine Auth/Firestore replay commands, exact freeze and acceptance counts
are in the sibling cache control directory's `HANDOFF.md` / `FREEZE.json`.

This is not published, production/device acceptance, or all-forms offline
certification. Safari is unavailable on this server. Browser/OS storage eviction,
forced full disk/power-loss, and hostile same-origin code remain outside exercised
assurance. Older naturally activated v43 can still delete caches until replaced;
new source cannot retroactively change already-running old bytes. Do not roll
back to unsafe v43 after this migration. Retained immutable asset copies cost
storage; deliberate bounded garbage collection is a future separately-reviewed
operation, not a reason to delete unknown caches now.

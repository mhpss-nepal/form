# Actual activity0.10 Form candidate

Branch feat/activity010-journey, direct child of immutable directory6068ef946c6a919fbaf2c44c14976927345b4526. Pair with Hub feat/activity010-reader and backend b16aa15e2706676e4d308bb5978b76702ec5ceea. Candidate only; parent owns review/release. No push/deploy/production writes.

Existing collector questions/layout/IDs retained. Submit now invokes explicit activity transport after device persistence, not legacy FB. UID scoped crypto identity, pending immutable envelope, hash matched exact200 receipt, explicit Retry/New/Restore/received-history correction actions. New retains current fields for review and creates distinct identity even for identical payloads. Correction fetches a complete own listing, verifies full-payload SHA256, binds predecessor and advances one revision. Network refusal/ACK loss/account changes never erase old outboxes. Form draft retained per UID. Received corrections overlay only edited collector fields onto raw predecessor to preserve untouched null/blank/absent distinctions.

Local store accepts an optional explicit event key rather than permanently collapsing identical events under FNV. Historical records and default old-device export columns remain unchanged. Wire payload excludes previous/archive history. Explicit crypto local key is omitted from optional wire `id`: backend reserves that provenance field for R[A-Z0-9]{7}; authoritative crypto ID is envelope.reportId. Other full fields/cells remain intact. Device record still retains its crypto local key.

Verified commands (run in this Form checkout):
- `node tools/activity010-store.cjs` PASS (distinct equal events, retained legacy record, local history).
- Hub `node tests/activity010.cjs` PASS (strict200/hash, immutable ACK-loss retry, UID switch/race, safe integers, canonical Unicode hash, paging/repeated cursor/refusal).
- Hub `/root/mhpss-nepal-final-forms/2026-10-06/45-automatic-baseline/.venv/bin/python tests/activity010-browser.py` PASS actual DOM/save -> labelled HTTP ACK loss -> exact retry -> correction2 -> actual Hub history/current -> downloaded parsed CSV fold2/3/0/5/0/1, boundary18, no page errors.
- Hub `/root/mhpss-nepal-final-forms/2026-10-06/30-cloud-functions-interim/.venv/bin/python tests/run-activity010-provider.py` PASS real isolated Auth+Firestore and unchanged backend adapter; actual Form/Hub source journey and source-backed CSV. Uses demo provider ID tokens via browser auth shim, not a new email/password or full browser SDK login. Existing persistent Auth adapter unchanged. Evidence joint010-bridge/frontend/provider/{RESULT.json,pytest.log,browser.json}; emulators stopped.
- Paired form+hub package `python form/tools/sw-precache-check.py` PASS34 entries/4 pages. sw cachev46, required activity assets/auth/home-nav added; engine unchanged. Installed-device upgrade/rollback unverified.
- Both `git diff --check` PASS.

Limits: full independent combined review and installed-device upgrade required. Focused suite, not a whole repository suite. No six-other-receiver completion, operational reopening or production authority claim. New English operational UI requires translation review. Parent must pair both frontend commits with backend, otherwise endpoints fail closed and original queue remains.

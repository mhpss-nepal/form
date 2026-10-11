# Isolated RC01 publication candidate

One new immutable TEST release `review-5ws-admin-test-v35/releases/native-test-rc01-20261011/`; existing release and entire main tree retained. Native document is byte-identical to independently reviewed `490f793f6cb81ca4ab07cc9b79eab688a6df080f` native document. Behavioral delta relative to main: backdated validation reads typed `r.backdateAcknowledged`, not current editor checkbox. Submit still serializes checkbox normally. New release pins/inventory exclude pins and manifest from the canonical digest to avoid circularity.

No new worker, cache boot, auth contract, queue namespace/schema, clinical text, design, access grants or operational activation. Held PR21 and reviewed worker/cache corrections remain on `w43-cache-integrated`; do not merge that branch as part of this candidate. Existing old-controller limitations remain; this release does not claim general offline readiness.

## Replay (server only, synthetic demo fixtures)

From `/root/mhpss-nepal-final-forms/2026-10-06/43-backend-completion/cache/form`:

```
python tests/rc01/check_release.py /root/mhpss-nepal-final-forms/2026-10-06/51-operational-closure/form-lane/release-check-NEW.json
/root/mhpss-nepal-final-forms/2026-10-06/34-primary-backup-admin/.venv/bin/python tests/rc01/run_rc01.py /root/mhpss-nepal-final-forms/2026-10-06/51-operational-closure/form-lane/native-replay-ABSENT
```

Evidence path must be absent. Existing Java/Firestore, Firebase CLI, backend and Playwright dependencies are reused, not deployed. Browser networking cannot reach external hosts. Auth fixture secret is randomly generated, memory-only and never printed/persisted by the runner; generated demo fixture configs/logs stay local. Only real emulator transactions generate receipts. Existing public identifiers in fixture control are not real signed-in identities.

Browser journey: exact served root v43 controller → old native entry creates two real initial receipts and offline correction envelopes → actual RC01 diagnostic RED by identity → new immutable entry in both tabs preserves exact queue → offline worker stop/wake/reload → no inherited entitlement → real demo SDK authentication → actual Retry button sends both unchanged correction bodies → revision2 and exact duplicate receipts → persisted false/livechecked validly-digested envelope refused before transport → editor/queue preservation → read-only URL rollback and return while both candidate editors stay unsent. No storage or service-worker deletion. `Network.clearBrowserCache` is confined to the disposable browser HTTP cache, not localStorage/CacheStorage.

The old controller precache dependencies use sealed immutable Hub asset copies in the retained reviewed form commit, not the concurrently owned Hub checkout. Product script bytes, old controller and new release are unmodified by the runner. External TEST backend transport URLs are redirected only to real local backend via the existing harness route; SDK Auth connector is demo-only.

Publication remains parent-controlled: exact-head independent packaging/delta review, protected CI/PR and served pins/bytes plus actual permitted browser journey required. No self-approved verified tag. Rollback points readers to retained old immutable URL without deleting pending data; old RC01 defect returns there, so it is not a repaired substitute.

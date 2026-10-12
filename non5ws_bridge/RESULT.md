# Non-5Ws selective candidate — engineering checkpoint, NOT a release

## Outcome
- Branch `feat/non5ws-bridge`, based exactly on `c71b18c4f667f5b53ff4ff98334dd2a9b48f3db3`.
- Claude source pinned to `3f89f6ed118398efeb71fe3219d8f0988088fac1` (`origin/feat/activity-age-grid-12oct2026`). No whole-branch merge.
- Seven actual existing HTML forms collected synthetic inputs, saved to isolated browser localStorage and downloaded CSVs; actual saved payloads ran through a pure typed Python receiving adapter. This is a receiving-contract boundary, NOT a network endpoint, storage service, API acknowledgement or wired backend.
- Four parked drafts initially crashed because assets still pointed one directory too high. Relative Hub references now resolve from `drafts/`; drafts remain parked, not added to public navigation. Transport remains held in those drafts.
- Source age changes applied to contact/selfreport with just two local selfreport dictionary keys. Legacy `10-19` and `20-59` records are preserved verbatim by adapter; no inferred child/adult split.
- Training source debug-payload removal integrated; additionally fixed two browser-reproduced defects: incomplete sex rows previously saved unknown counts, and CSV serialized participant objects as `[object Object]`. Explicit zeros now required in nonempty sex rows; nested participants/partners exported as JSON cells.
- PHQ-9 only receives `data-i18n-html` binding correction. Validated Hub item text, clinical wording, Home navigation and legacy referral link preserved. Source draft says English-only; actual EN/NE render uses Hub dictionary (nine exact item equality checks per language). The Hub item-9 instruction still links `referral.html`, overriding Claude's proposed no-link wording. Nepali instruction has no approved localized dictionary value and intentionally remains English (`i18n-kept`); do not claim translated safety instruction.

## Protected files and exclusions
Tests byte-compare `5ws-report.html`, `lib/store.js`, `index.html`, root `contact.html` and root `referral.html` against base. No `lib/strings.js` copied, no 5Ws strings/runtime edit. Existing Home links retained on PHQ/selfreport. Training baseline and source have no `data-home-link`; no false claim that they did. No shared root Hub/backend edits, remote pushes, PR, merge, deployment, grants, email, production records, Luna or children.

## Re-run
From this worktree:
```
/root/mhpss-nepal-final-forms/2026-10-06/45-automatic-baseline/.venv/bin/python non5ws_bridge/browser_regression.py
python -m unittest discover -s non5ws_bridge -p 'test*.py'
python non5ws_bridge/build_inventory.py
```
Browser harness reads `/root/mhpss-nepal-work/hub` assets without writing them; loopback only, nonlocal requests aborted, Firebase/PWA scripts disabled, service workers blocked. That exclusion is deliberate safety isolation, NOT transport proof. Hub checkout observed `8d01dac`; PHQ dictionary SHA256 is in browser evidence. Browser inputs are explicitly synthetic; institution codes are code-list selections, not actual reports.

`inventory.json`: seven source paths/pins/blobs/hashes, schema, unit, grain, complete actual field/type list, local save keys, proposed receiving collections, sensitive-field candidates, Layer-2 destination/role proposals and export omissions. `build_inventory.py` computes all counts and checks the exact seven-instrument set. Owner checkpoint copy: `51-operational-closure/non5ws-bridge/inventory.json`.

Evidence: `evidence/baseline-browser.json` contains four original draft crashes; `pre-validation-fix-browser.json` exposes training missing-sex save; `browser.json` contains final real saves/downloads and constraint/render checks. Final suite has seven passing unittest methods; multiple subtests per instrument. No synthetic API responses exist.

## Exact next receiving-engineering blockers
1. **Training first — backend owner:** implement a separate authenticated `training_events` receiver/storage path against this adapter contract. Current revision `00008-vux` supports 5Ws only (owner-provided context, not revalidated here). Do not route training into 5Ws/reach/attendance. Commission organisation identity from server claims, not submitted org; add request IDs, payload-bound idempotency, acknowledgements, retry/offline queue, readback and export. Adapter is not yet invoked by an HTTP handler or existing form transport.
2. **Full validation — backend owner:** adapter enforces schema/instrument routing and focused numeric/privacy/safety boundaries, not full server validation of all seven instruments. Add complete required/enumerated field schemas, size/date/range checks, unknown-field policy and malicious nested-value rejection. Frontend training optional demographics/facilitator NaN rejection is not exhaustive; direct invalid DOM values can bypass HTML bounds. Never equate this adapter with production authorization/validation.
3. **Clinical partition — engineering + governance:** implement per-organisation restricted contact/referral/PHQ paths, server authorization and salt/key custody, collision handling, audit, retention, correction and secure exports. Draft README's claimed written basis is provenance only; institutional permission NOT verified. Do not activate parked forms or delete root legacy forms/index until owner-approved navigation/compatibility and backend containment are verified.
4. **Referral join semantics:** `kind=referral` with `record_type=outcome` is NOT the legacy root referral event. Adapter rejects legacy event-as-outcome; receiving migration needs explicit source version. Contact local storage uses `mhpss-np-l1-contact-v1` although payload kind is `service_contact`. Decide organisation scope and uniqueness for contact-code+referral date; collisions and multiple same-day referrals remain unresolved.
5. **Directory receiver/publication:** registration consent is not moderation, credential verification or access grant. Implement separate registration/review/public projection. Service-point CSV omits `schema`, `kind`, `source` and focal contact fields; provider CSV omits schema/kind/selfRegistered. JSON/browser source preserves these, but CSV imports need an explicit instrument envelope, not guessed schema. Provider/service render uses unescaped HTML from user input: harden before any real records/publication.
6. **Anonymous feedback:** no person join in adapter; free text remains potentially identifying and human-review-only. Implement server minimization, metadata/telemetry policy, abuse protection and review/suppression before presentation. Reject unexpected identity fields comprehensively, not only current named guards.
7. **PHQ/clinical review:** independently accept exact validated dictionary provenance, item-9 referral destination and English fallback safety text. Source-vs-render differs intentionally because dictionary wins. Existing success messages promise later coordination delivery even when held; reconcile approved bilingual delivery-status wording with actual receiver before field use, without silently rewriting clinical items.
8. **Parent review/release:** review this exact committed candidate, then exercise actual authorised receiver readback, access isolation, listing/export, offline ACK, rollback and recovery. Local seven-form success is not seven operational instruments. Production operational coverage remains 0 verified in this task.

Execution is stopped at this committed checkpoint. Parent owns next engineering assignment, independent review and release; nothing merges automatically.

# 5Ws Institutional Utility preview — final QA report

## Scope

- Executor: ☁️ Thar Lay/server
- Branch: `design/form-frontend`
- Baseline: `9032bb7a3e198882cce8ca1bf350621aba856db7`
- Selected preview: Direction B — Institutional Utility
- Active form: `5ws-report.html`
- Data used: synthetic, non-identifiable demonstration data only

## Verified

- Contract regression suite: 18 tests passed.
- Repository text-setting static gate passed.
- Independent review blockers were fixed: no new status-layer storage writes; text wrapping follows the repo rule; Clear removes the error outline; the mobile action bar remains in normal flow so keyboard Tab focus is never covered; Nepali validation now uses existing translated field labels and explicitly flags the remaining English validation detail; an empty toast is hidden and cannot obscure operational guidance.
- Exact existing form-control tuple list remains equivalent to baseline (element/type/id/name/form owner).
- Runtime script/style call sites remain equivalent to baseline.
- `pwa.js`, `sw.js`, and `manifest.webmanifest` remain byte-identical to baseline.
- Mobile/desktop reflow checked at 320×720, 320×844, 390×844, 768×900, and 1280×900 with no document-level horizontal overflow; the Step 4 hint wraps within the 320 px viewport.
- Primary controls and target-group labels meet the 44 px touch-target requirement; compact checkbox glyphs sit inside 44+ px clickable labels.
- Empty submit exposes all nine existing validation failures, moves keyboard focus to the assertive summary, scrolls the summary into view, and adds a visible 3 px error outline.
- A complete synthetic report saved through the existing `STORE.save()` path while the remote adapter was stubbed. One device record appeared, queue count remained zero, then QA records and reporter defaults were cleared.
- Empty saved-list state returned after cleanup.
- English and existing validated Nepali strings render; new operational status copy remains English and is explicitly marked as pending human-reviewed Nepali translation.
- Display states checked: online/queue empty, queued, remote unavailable, local-storage blocked logic, validation error, device-saved record, and empty saved list.
- Reduced-motion rule remains present.
- Final 390 px screenshot received visual QA with no blocker. Slop diagnostic: 2/10.

## Truthful state wording

- Online connectivity and empty queue are not called delivery.
- Saving on the device is distinguished from remote delivery.
- Offline-entry capability is stated, while reconnect reliability remains qualified.
- The supervised-pilot confirmation remains the record appearing in the Hub.
- Guidance says to keep the page open after internet returns and not repeatedly resubmit or clear browser storage when status is unclear.

## Limitations

- New interface-only operational copy has no validated Nepali translation yet; it is flagged rather than invented.
- Firebase remote acknowledgement was not exercised with a test submission. QA deliberately stubbed the remote adapter to avoid writing demonstration data to external state.
- Browser QA used the existing page runtime over a Thar Lay/server preview HTTP origin; it was not deployed.
- No production deployment, merge, push, or PR was performed.

## Artifacts

- Final narrow-mobile screenshot: `design-preview/5ws-institutional-phone-320-final.png`
- Final standard-mobile screenshot: `design-preview/5ws-institutional-phone-390-final.png`
- Validation state: `design-preview/5ws-institutional-validation-mobile.png`
- Synthetic device-saved state: `design-preview/5ws-institutional-saved-mobile.png`
- Contract test: `design-preview/test_institutional_preview.py`
- Preservation inventory: `design-preview/5ws-preservation-inventory.md` and `.yaml`

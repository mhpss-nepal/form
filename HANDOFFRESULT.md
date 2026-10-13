# Directory functional correction — prepared for independent review

Base: `6135d80a67cb0b277d1b243a8c02f37ca1437164` (fresh `origin/main`). Branch: `fix/directory-functional-correction`. Executor: Thar Lay/server; sole Form frontend writer. No backend or Hub changes, push, PR, deployment, grants, records, emails or peer-host writes.

## Usable result

The canonical directory has eight distinct instrument destinations with identical **Open form / Copy link / QR** action rows. Training now has Copy and QR. The four former dashboard links open actual complete source-template questions, including conditional sections and inspectable option lists, at:

- `review/contact.html`
- `review/referral-outcome.html`
- `review/provider-register.html`
- `review/service-point.html`

These routes require no account or module grant, contain no record reader, and do not activate collection. Inputs, save, export, clearing and location are disabled. Source questions, consent and safeguarding text remain source-authored. EN/NE template switching reuses existing dictionaries and explicitly retains the Nepali draft status. Proposed save/publication descriptions are qualified as source workflow text, not current functionality.

The parked originals remain untouched. A reproducible generator copies their markup, inline styles, literal local vocabularies and existing dictionary blocks, but never includes their executable form runtime. Allowed scripts are only the inert renderer, shared code lists and dictionary. There is no L1, Firebase, legacy bridge, PWA registration, preview staging writer or shared storage-using i18n runtime. CSP independently denies connections and form actions; capture handlers and native submit/requestSubmit fences prevent submission. All disabled select choices can be read in adjacent Options disclosures without enabling a respondent input.

`all-forms.html` redirects to the canonical directory while preserving query/hash. Printable `cards.html` remains the existing single-5Ws sheet; its inaccurate automatic-delivery and offline assurances were removed, not broadened into an all-eight distribution sheet. The directory itself no longer initializes Firebase or displays its delivery strip. Existing root 5Ws, Training, PHQ-9 and Self-report bytes and their controls/meanings are unchanged. Clinical item translation and backend permissions are unchanged.

## Executed verification

- `python -B -m unittest -v test_directory_correction`: **7 passed**. Exact source-control tuples/question labels, byte-locked four root forms and parked originals, safe script allowlist/CSP, eight routes and reproducible generation.
- Four superseding directory/QR gates plus those seven: **11 passed**. Obsolete single-form exposure/QR gates now assert the authorised eight-route boundary; the printable-sheet restriction remains unchanged.
- Existing 45 venv Playwright: **60 result records**, 320/390/1280 × EN/NE; 8 cards and 8 distinct actual-click destinations in each variant, all Copy/QR destinations match their form, actual question controls render, no document overflow, page errors or HTTP errors. All 24 held-template cases refuse event/native/Enter submits with **zero Storage, IndexedDB, fetch, XHR, beacon or WebSocket calls**, no non-GET requests and no Firebase/L1/PWA writer loads. Reload returns an empty, disabled template. Screenshots were captured after reload rather than adversarial synthetic field mutation.
- QR generator and checker run in **OpenCV decode mode: 9/9 matrices** (directory plus eight instruments), including actual review-route paths. The SVG quiet zone now uses four modules. Printable 5Ws QR still exists.
- `git diff --check`: passed.
- SW `v45` and `tools/precache.sha` regenerated together with the existing fingerprint generator, against unchanged shared assets matching Hub `28620a7c3e47038548404ac5469c8cc1115fc680`. Added the directory dictionary to precache. No offline acceptance claim; held review pages are deliberately not precached.

Evidence: `51-operational-closure/directory-functional-correction/browser-evidence/` (screenshots and `browser-results.json`); baseline/candidate suite logs beside it. Run browser regression with `MHPSS_EVIDENCE=<output-directory> ...45-automatic-baseline/.venv/bin/python tools/directory-browser-check.py`; default sibling shared assets are `publication/all-homes` and can be overridden by `MHPSS_HUB`.

## Separate remaining gates / inherited issues

Independent review and publication belong to the parent. This is a local component candidate, not a published release or clinical collection activation. Training receipt path was preserved byte-for-byte, not re-certified by sending a production report. 5Ws transport integration belongs to the parallel backend/parent lanes. PHQ-9 and Self-report collection/storage semantics are not altered or newly certified.

Full historical root discovery: candidate **32 tests, 3 failures and 3 errors**. All six residual findings also reproduce at the exact base (with its git source history available): deleted historical English-page assumptions; sibling `publication/hub` absent in this checkout for two fingerprint tests; obsolete translation-review index expecting retired contact/referral shell links; old pre-v7 5Ws byte-parity fixture; and existing `preview.html` Nepali-default assumption. Base: **25 tests, 6 failures and 3 errors**. No new failure identity remains. The paired fingerprint generator was explicitly exercised through its module with the real shared-assets root, without editing or symlinking a sibling publication repository. The existing text-setting CLI likewise assumes absent `publication/hub`; it is not reported as passing.

Function/contract gate: passed for this bounded directory and inert review surface. Visual/layout gate: shared existing style retained; screenshots and geometry available, independent visual acceptance remains open. Data gate: no held-template collection activated, no private-record read, zero reviewed-template side-effect calls observed.

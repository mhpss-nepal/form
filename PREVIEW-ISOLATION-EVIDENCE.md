# Preview isolation — reviewers can open every form, nothing can reach Layer 2

Task `t_d1360320` · tenant `mhpss-nepal` · 2026-09-20
Status: **DONE — REVIEW ARTIFACT**

## Base / head

| | |
|---|---|
| Worktree | `/root/mhpss-nepal-work/form-frontend` |
| Branch | `design/preview-isolation` (created from `design/form-frontend`) |
| Base | `9c3a41eeccc768fcef5d8f241430ba831e8ad9a8` — *docs: one indexed page with a link to every form, for human review* |
| Implementing commit | `6d378eca0c37884b6d9844e51ee07477eff7fd9b` — *Preview isolation: render every form for review, none able to reach Layer 2* |
| Head | this note is amended into the branch head, so the head is not written into its own text (that can only ever be one commit stale). Recorded in the task metadata, and read it with: `git rev-parse HEAD` on `design/preview-isolation` |
| Production refs | unchanged: public `68bf197`, form `9032bb7`, hub `ff2d4e2` |
| Pushed / PR / deployed | **no** |
| Hub paths touched in this worktree | **0** |
| Worktree | clean except untracked files belonging to OTHER lanes (`design-preview/apply_ne_drafts.py`, `design-preview/translate_all_missing.py` — the translation worker writing into `hub/assets/i18n-strings.js`). Not mine, deliberately left uncommitted |

## The problem this closes

Adib's direction, 20 Sep 2026: reviewers must be able to OPEN and TRY the real forms,
so a screenshot is not evidence. But nothing they do may reach Layer 2.

The existing review index (`design-preview/translation-review-index.html`, added at the
base commit) linked the **bare page files** directly:

```
<a href="../form-frontend/contact.html">Open form</a>
```

Every one of those pages loads `../hub/assets/fb.js` with
`window.FB_COLLECTION = "submissions"` — the LIVE register. A reviewer typing a trial
answer into that page was writing to the collection the Hub counts. The review index was
therefore itself the route from review to Layer 2. That is the leak this task closes.

## The mechanism (the seam that already existed)

`hub/assets/fb.js` line 30 reads the collection **once, at load**:

```js
var COLL = window.FB_COLLECTION || "submissions";
```

Every read and write goes through `COLL` (lines 237, 267, 292), and the Hub reads the same
constant. A build can therefore be pointed at a separate collection by setting
`window.FB_COLLECTION` before `fb.js` loads. That is the seam, and this task uses it rather
than inventing a second one. `kind` is left as the secondary discriminator it already is.

## What was built

| File | Role |
|---|---|
| `preview-mode.js` | Pins `FB_COLLECTION` to `submissions_preview`; renders the bilingual banner; removes the misleading `#fbbar`; replaces `FB.publish` with a function that always refuses |
| `preview.html` | The one URL a reviewer opens, `?preview_form=<file>`. Direct URL only: not linked from the field landing page, not precached |
| `preview-shell.js` | Renders the committed page's own markup, styles and scripts inside the frame, with the bridge re-pointed **immediately before that page's `fb.js` executes** |
| `preview-shell.css` | Styles the frame only; the instrument is deliberately not restyled |
| `test_preview_isolation.py` | 9 failing-first contracts |
| `tools/preview-isolation-render-check.py` | Real-browser evidence: banner, legibility, width, overflow, and the write target of an actual submit |
| `tools/firestore-rules-probe.py` | Read-only, count-only probe of what the live rules permit |
| `tools/preview-live-write-probe.py` | One synthetic staging write through the real frame, reporting whether the rules accepted it |
| `tools/precache-drift-diagnose.py` | Characterises the pre-existing precache-fingerprint drift (see *Carried over*) |

### Why a shell rather than six copied pages

Six verbatim copies would drift from the originals the moment a page changes, and a
reviewer would then be judging a stale instrument. The shell injects the page's own
markup, styles and scripts **from the file on disk**, so what a reviewer tries is what is
committed. Nothing about the instrument is duplicated.

Load order inside the frame, which is the part that makes the boundary hold:

```
preview-mode.js      window.FB_COLLECTION = "submissions_preview"
  fb-config.js       <- from the page; resets FB_COLLECTION = "submissions"
  preview-shell.js   <- re-pins FB_COLLECTION = "submissions_preview"
  fb.js              <- reads COLL once; captures the STAGING collection
```

`fb.js` is deliberately **not** blocked. Blocking it would have been easier and wrong:
the collection constant is only captured if the real bridge runs, and a page that loaded
the bridge by a route the shell did not anticipate would then have written wherever
`fb-config.js` said. Re-pointing the real bridge is the guarantee.

## Requirement by requirement

1. **Staging collection** — `submissions_preview`, distinct from `submissions`. All
   preview-mode writes go there. Proven by `test_preview_isolation.py` and, in a real
   browser, by `tools/preview-isolation-render-check.py`, which intercepts the actual
   Firestore write and reads the document path out of the WebChannel body:
   `[{"collection": "submissions_preview", "method": "POST"}]`.
2. **Visible on the page** — a bilingual banner, EN and NE on the same band, rendered by
   `preview-mode.js` so it appears on every review page rather than only the ones someone
   remembered to edit. It is re-asserted as the first child of `<body>` and re-mounted on
   `preview:ready`, because `fb.js` and `pwa.js` both insert their own strips at the front.
3. **Nothing in staging may be counted** — the Hub's reader names `submissions` and
   nothing else, so a preview record is structurally invisible to every Hub figure. The
   second door, `public_stats`, is closed in the frame: `FB.publish` is replaced with a
   function that always refuses, and the rendered check confirms
   `rejected: preview mode cannot publish: nothing from submissions_preview may reach
   submissions or public_stats`. Ties to `t_33c20f5c` on the publish path.
4. **The Hub must label the difference** — the safer choice was taken and is documented in
   the review index and in this note: **the Hub does not read preview records by default.**
   Making it display them would be a separate, labelled feature and is not proposed.
5. **Field exposure unchanged** — verified rather than assumed, below.
6. **Both languages exercisable** — the page's own engine is used, so the reviewer
   exercises the real ENG/NEP switch; the shell adds a language rail only as a fallback for
   a page with no engine. Every rendered page reports `lang=ne` with the toggle mounted.

## Field exposure re-verified (requirement 5)

Byte-parity against the base, per file:

```
same: 5ws-report.html   contact.html   phq9.html   referral.html   selfreport.html
same: 4ws-report.html   index.html     cards.html  sw.js  manifest.webmanifest
same: pwa.js  qr-trial.js  5ws-report-b2.html
```

- `index.html` exposes exactly one form link (`5ws-report.html`) plus `cards.html`; no
  link to any of the four unapproved forms; no preview page linked.
- `sw.js` precache unchanged, cache `mhpss-np-field-v41`, and it contains **no** reference
  to `preview.html`, `preview-mode.js` or `translation-review-index.html`.
- The distributed 4Ws QR still works offline: `tools/4ws-offline-redirect-check.py` →
  **exit 0**, redirected to the 5Ws form with `?qr=distributed-4ws&lang=ne#field-copy`
  preserved, both hops served by the service worker.
- `tools/trial-scope-render-check.py` → **exit 0**; `tools/5ws-still-works.py` → **exit 0**.
- `test_trial_scope.py` → 7 pass, **1 pre-existing failure** (below).

## Test results

| Command | Result |
|---|---|
| `python3 test_preview_isolation.py` | **9 passed** (7 failed / 2 passed before the implementation — see below) |
| `python3 tools/preview-isolation-render-check.py http://127.0.0.1:8791` | **exit 0** |
| `python3 test_trial_scope.py` | 7 pass, 1 fail — pre-existing, not caused here |
| `python3 tools/sw-precache-check.py` | exit 0 |
| `python3 tools/i18n-check.py` | exit 0 |
| `python3 tools/text-setting-check.py` | exit 0 (was already exit 1 at base; the reported defect is fixed) |
| `python3 tools/qr-check.py` | exit 0 |
| `python3 tools/4ws-offline-redirect-check.py` | exit 0 |
| `python3 tools/5ws-still-works.py` | exit 0 |
| `python3 tools/trial-scope-render-check.py` | exit 0 |
| `design-preview`: `test_b2_preview` + `test_institutional_preview` | **48 passed** |

### The failing-first record

With the review index left as committed and no implementation present,
`test_preview_isolation.py` fails **7 of 9**:

```
FAIL test_preview_runtime_sets_collection_before_shared_bridge
FAIL test_preview_runtime_pins_the_bridge_only_for_the_collection
FAIL test_preview_runtime_has_visible_bilingual_non_real_data_banner
FAIL test_preview_runtime_refuses_publication_and_live_collection
FAIL test_preview_submit_cannot_be_counted_by_default_hub_collection
FAIL test_review_routes_only_through_the_preview_shell
FAIL test_review_shell_names_a_writing_page_it_can_open
Ran 9 tests — FAILED (failures=7)
```

The two that pass at base are the field-exposure invariants, which this task must *not*
change — correct, and they stay green throughout.

### Rendered evidence (a real DOM, not source text)

```
mobile 390    5ws-report.html    banner=yes lines=4 coll=submissions_preview form=True  selects=8   lang=ne overflow=390
mobile 390    5ws-report-b2.html banner=yes lines=4 coll=submissions_preview form=True  selects=10  lang=ne overflow=390
mobile 390    4ws-report.html    banner=yes lines=4 coll=submissions_preview form=False selects=0   lang=None overflow=390
mobile 390    contact.html       banner=yes lines=4 coll=submissions_preview form=True  selects=11  lang=ne overflow=390
mobile 390    phq9.html          banner=yes lines=4 coll=submissions_preview form=True  selects=5   lang=ne overflow=390
mobile 390    referral.html      banner=yes lines=4 coll=submissions_preview form=True  selects=14  lang=ne overflow=390
mobile 390    selfreport.html    banner=yes lines=4 coll=submissions_preview form=True  selects=2   lang=ne overflow=390
   (identical at 1280 px)

submit inside the review frame (Firestore requests aborted before send):
  collection seen by the page: submissions_preview
  records queued locally:      1
  publish() attempt:           rejected: preview mode cannot publish: …
  intercepted write targets:   [{"collection": "submissions_preview", "method": "POST"}]
```

The check asserts, per page and per width: the banner is present, is the first and
top-pinned element, spans the full width, every text line is ≥12 px, and there is no
horizontal overflow. It aborts the write at the network layer so **no production document
can be created by the check itself**.

## The rules question — answered

The authoritative Firestore rules are not stored anywhere readable (established during
`t_9f626bd6`), so this is answered **by behaviour**, and stated as such.

**What the rules must allow for staging to work in production** (the decision the rules
owner has to make): a **stated, signed-in reviewer** write to `submissions_preview`, and a
read that a reviewer can use. It must **not** be a public write, and it must **not** be
publicly readable.

**What happens TODAY** — verified, not inferred:

```
tools/firestore-rules-probe.py            (unauthenticated read)
  submissions          HTTP 403  PERMISSION_DENIED
  submissions_preview  HTTP 403  PERMISSION_DENIED
  public_stats         HTTP 200  READABLE, at least 0 document(s)

tools/preview-live-write-probe.py         (one synthetic record, through the real frame)
  collection the page writes to : submissions_preview
  records queued on the device  : 1   (0 = the write was accepted)
  explicit flush()              : {"sent":0,"left":1}
  publish() attempt             : rejected: preview mode cannot publish
```

Read the last two together. The staging write was **refused by the rules**: the record
stayed in the device queue (`left: 1`, `sent: 0`), and a re-read of the collection still
shows it as not readable. The rules are deny-by-default for any collection they do not
name, and they do not name `submissions_preview`.

**Conclusion: the write fails safe today.** No rule was weakened, and no rule needs to be
weakened for safety — only to make review *usable* end to end.

**BLOCKED — DECISION (for the owner of the Firestore rules):**

> Should the security rules name a new collection `submissions_preview`, writable by a
> signed-in reviewer and readable by coordination, so that a review submit reaches the
> staging collection rather than sitting in the device queue?
>
> - **If yes** — reviews become fully usable end to end and preview isolation is complete.
>   The rules must also state that nothing in `submissions_preview` may be read by the
>   public, and must keep `public_stats` unreachable from it.
> - **If no** — review is still possible and still safe; a reviewer's record remains on
>   their own device and is exported by hand, which is what happens today.

Until that is answered, no reviewer loses anything: the form opens, validates, saves
locally, exports, and switches language. Only the last network hop is refused.

### One residual risk, stated plainly

A reviewer signed in as a `coordinator` and using a **Hub** page — not a review page — can
still publish `public_stats`. That is the coordinator role working as designed, it sits
outside this task's boundary, and it is the subject of `t_33c20f5c`. What this task
guarantees is narrower and exact: **a review frame cannot publish and cannot write the
live collection.**

## Carried over, not caused here

- `test_trial_scope.py::test_precache_fingerprint_matches_current_form_and_hub_assets`
  fails at the **base commit too** (confirmed by stashing all changes and re-running).
  `tools/precache.sha` records `34b515c7…` and the tree computes `77a2c8f1…`. The tracked
  inputs are unchanged since the hash was written, so the drift is in the **untracked
  shared `hub/assets/`** files this worktree only reads
  (`i18n-strings.js` and `i18n.js` are much newer than the rest) — a hub-repository
  change, not a form change. `tools/precache-drift-diagnose.py` reproduces it and prints
  the form-only digest. **Not repaired**: regenerating the fingerprint would mask which
  repository moved.
- `tools/text-setting-check.py` failed at base on one selector in the review index
  (`th, td { text-align:left }`). Fixed here, because this task rewrites that file:
  `th` and `td` now carry their own declarations. The tool reports exit 0.
- `design-preview/apply_ne_drafts.py` and `design-preview/translate_all_missing.py` are
  untracked and appeared in the working tree while this task ran (the translation lane
  writing into `hub/assets/i18n-strings.js`, and the most likely author of the fingerprint
  drift above). They are **not** mine and are deliberately left alone and uncommitted.

## Honest limits

- **Verified** (by running): the staging collection constant the page ends up with; the
  document path of an attempted write; the banner's presence, position, width and
  legibility at 390 px and 1280 px on all seven review targets; the refusal of `publish`;
  the refusals the live rules issued to the read and write probes; the byte-parity of every
  field page; the 4Ws offline redirect.
- **Inferred, not verified**: that the rules will keep refusing `submissions_preview` after
  a rule change — which is exactly why the decision above is put to the rules owner rather
  than assumed.
- **Not attempted**: publishing to `public_stats`; writing to `submissions`; any check of a
  real record body. No real or synthetic record was left in the live register.
- A passing suite is not evidence about what a page *shows*; every claim about the rendered
  page in this note comes from the browser check, not from source text.
- **Edge case, named not hidden.** If a reviewer's browser already has the field service
  worker installed (because they opened the field app first), that worker keeps controlling
  `/form/`. A review page is served network-first, so it still loads normally with signal —
  but a review page opened with NO signal would fall back to the worker's cached
  `index.html`, and the review banner would be absent. The review frame cannot unregister a
  worker it did not register. Opening the review URL while online, which is how review is
  done, is unaffected.

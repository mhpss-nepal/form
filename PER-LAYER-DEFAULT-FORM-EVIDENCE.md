# Per-layer language default — the form side (5ws-report.html)

**Task:** `t_83eec40f` · tenant `mhpss-nepal` · 2026-09-20
**Status:** **DONE — REVIEW ARTIFACT** (not deployed, not pushed, not merged)
**Handoff read:** `coordination/session-briefs/HANDOFF-REPLY-hub-to-form-per-layer-default-2026-09-20.md`

The decision being put into effect (Adib, 2026-09-20): **Layer 1 field forms default to
Nepali; Layer 2 (Hub) and Layer 3 (public site) default to English.**

---

## 1. The change

One attribute, on one page:

```html
- <html lang="en">
+ <html lang="en" data-i18n-default="ne">
```

`5ws-report.html` is the only trial form and the only page that is 100 % translated, so it is
the only page that declares a default. Every other form page keeps declaring **nothing**, and a
page that declares nothing stays English — that is the not-fully-translated guard.

| file | declares | why |
|---|---|---|
| `5ws-report.html` | `data-i18n-default="ne"` | the only trial form; 100 % translated |
| `index.html`, `contact.html`, `phq9.html`, `referral.html`, `selfreport.html` | nothing | not fully translated → must keep English |
| `5ws-report-b2.html` | nothing | derived preview page; does not carry the trial's default |
| `4ws-report.html` | nothing | redirect stub → inherits whatever `5ws-report.html` resolves to |
| `cards.html` | nothing (loads no engine) | printable QR card sheet, not a form |
| Hub pages, Layer 3 pages | nothing | Layer 2 / Layer 3 default to English |

Machine-checked, not asserted from this note:

```
$ grep -l 'data-i18n-default' *.html
5ws-report.html
$ grep -c 'data-i18n-default' 5ws-report.html
1
```

## 2. Rendered evidence — a real browser, not the source text

**Tool:** `tools/per-layer-default-render-check.py` (new; drives Chromium over the served
site and reads `window.I18N.lang()`, the rendered text, and `data-lang`). Each case opens in a
**fresh browser context**, so the remembered-choice `localStorage` key from one case cannot leak
into the next — which is exactly how a first-time reader arrives.

The engine exposes the language as a **function**, `window.I18N.lang()`; the tool asserts it is a
function before calling it (reading `.lang` as a property would silently yield a function object
and look like a failure when there is none).

Run (the form worktree and the durable hub repo side by side, so `../hub/assets/*` resolves to
the repo the pages actually load):

```
python3 -m http.server 8931 --bind 127.0.0.1 --directory /tmp/t83-serve
python3 tools/per-layer-default-render-check.py http://127.0.0.1:8931
```

Result — the four cases the task requires, plus the other form pages as a guard:

| case | path | `I18N.lang()` | `data-lang` | rendered text (start) |
|---|---|---|---|---|
| **5Ws, no `?lang=`** | `form-frontend/5ws-report.html` | **`ne`** | `ne` | `यो पृष्ठ स्वचालित रूपमा अनुवाद गरिएको हो। अंग्रेजी संस्करण आधिकारिक हो।` … (5675 Devanagari chars) |
| **5Ws `?lang=en`** | `…?lang=en` | **`en`** | `en` | `Saved to this phone. The forms now open even with no signal. × MHPSS Activity Report RASUWA – BHOTE …` (0 Devanagari) |
| **Hub page** | `hub/index.html` | **`en`** | `en` | `Connected. Records reach coordination as you save them. MHPSS Nepal LAYER 2 · COORDINATION ARCHITECTURE` (0 Devanagari) |
| **form landing** | `form-frontend/index.html` | **`en`** | `en` | `Saved to this phone. The forms now open even with no signal. × Connected. Records reach coordination` (0 Devanagari) |
| b2 derived preview | `5ws-report-b2.html` | `en` | `en` | `B2 Institutional App — design preview. Demonstration / non-identifiable data only.` |
| contact / phq9 / referral / selfreport | `*.html` | `en` | `en` | English, 0 Devanagari |
| 4ws redirect stub | `4ws-report.html` | `ne` (inherited) | `ne` | lands on `5ws-report.html` — a redirect, not a language of its own |
| cards sheet | `cards.html` | (no engine) | — | declares nothing |

Exit 0. The four required cases are exactly as the task specifies: **Nepali on first load,
`?lang=en` still English, a Hub page English, `form/index.html` English.**

### Failing-first (the change is what makes the difference)

The same tool, pointed at the **pre-task page** (`36d3380`) served with the same engine:

```
5ws report, no ?lang=   I18N=en  data-lang=en  devanagari=0  declared=None
→ resolved 'en', wanted 'ne'        exit 1
```

So the Nepali first load is caused by the declaration, not by the engine or the environment.

## 3. The prerequisite this card does not name — and the one real gap

**The declaration does nothing until the Hub engine that reads it has landed.**

The engine that reads `data-i18n-default` is `hub/assets/i18n.js`. Over the whole fleet of
worktrees, **exactly one** engine copy reads the attribute — the Hub lane's in-progress
worktree `/root/mhpss-nepal-work/hub-real` (`task/t_2449fe51-i18n-per-layer-default`). Measured,
not assumed:

| engine copy | `DEFAULT` | reads `data-i18n-default`? |
|---|---|---|
| `hub-real/assets/i18n.js` (Hub lane, in progress) | `"en"` | **yes** |
| **`hub/assets/i18n.js` — what the form pages actually load, served from the sibling** | `"en"` | **no** |
| `public-layer3/assets/i18n.js`, `hub-translation/…` | `"en"` | no |
| production / audit clone (`ff2d4e2`, `/root/mhpss-nepal-audit-20260918/hub`) | `"en"` | no |

Proof, served: the changed page run against the **production engine** (`/tmp/t83-prodserve`,
hub = audit clone at `ff2d4e2`) still resolves `en` with `declared='ne'`:

```
5ws report, no ?lang=  →  I18N=en   (declared 'ne' is present but the engine ignores it)   exit 1
```

**Consequence, stated plainly.** The form-side change is complete and correct, but it is
**inert until the Hub lane's `assets/i18n.js` change ships.** Landing the form page alone will
**not** make the trial form open in Nepali. This is the single thing to hand back to the Hub
lane (§6). The Hub lane's own evidence note already records the same dependency from its side.

## 4. Service-worker / precache consequence (the v44 question)

The card asks whether a cached page needs a cache bump to reach a phone that has already
visited. **Yes — and the form page is in the precache list**, so it must be bumped in whichever
repository it lands.

`sw.js` precaches `5ws-report.html` **and** the shared engine (`../hub/assets/i18n.js`,
`../hub/assets/i18n-strings.js`), and serves static assets cache-first. A phone holding the old
cache would keep the declaration-free page and still open in English. So in **this** worktree
the cache is bumped **v41 → v42**:

```
- const CACHE = "mhpss-np-field-v41";
+ const CACHE = "mhpss-np-field-v42";
```

**Two cache numbers, reconciled.** The card names **v44**; that number belongs to the Hub lane's
sibling form worktree `/root/mhpss-nepal-work/perlayer/form`
(`task/t_2449fe51-form-default`), which carries `mhpss-np-field-v44` after its own engine bumps.
In **this** worktree (`design/preview-isolation`) the cache was v41, so the same reason yields
**v42**. Both satisfy the rule in `sw.js` ("bump this on every change to any precached file");
whichever branch lands, the effective version is ≥ what the installed phones hold. If both land,
the trial branch's v44 governs.

`tools/precache.sha` (the recorded digest of every precached file, asserted by
`test_trial_scope.py`) is **regenerated** because the entry set now hashes a changed page.

## 5. Guards, and the two that had to be corrected

New/changed in this worktree:

| path | change |
|---|---|
| `5ws-report.html` | the declaration |
| `sw.js` | cache v41 → v42 |
| `tools/precache.sha` | regenerated (the page it hashes changed) |
| `test_trial_scope.py` | the byte-parity pin is narrowed by exactly the one substitution, and its base is updated (below) |
| `tools/per-layer-default-render-check.py` | new — the rendered evidence tool |

The byte pin in `test_trial_scope.py` restricted `5ws-report.html` to *byte-identical to base*.
That pin is narrowed by **exactly** the one `<html>`-tag substitution and nothing else, so any
other change to the page still fails:

```python
DEFAULT_SUB = ('<html lang="en">', '<html lang="en" data-i18n-default="ne">')
allowed = base_html.replace(*DEFAULT_SUB)
self.assertEqual((ROOT / "5ws-report.html").read_text(), allowed)
```

**Two honest corrections, recorded rather than hidden:**

1. **The pin's base was stale.** It pointed at `8c84f43` (the trial-scope commit), but this branch
   has since legitimately moved two pages forward of it — the optional `ward` field (`24c7a2a`,
   an adjacent task) and the phq9 wording fix (`f7c4b5c`). At `8c84f43` the pin therefore failed
   **before this task began** (proved: `5ws-report.html` and `phq9.html` differ from `8c84f43`
   with no change of mine). The pin now compares against **this task's base `36d3380`**, which is
   byte-identical to the page as this task received it. The property the guard exists to hold —
   *no other page drifts, and the 5Ws page changes by nothing but the declaration* — is
   unchanged and still strict.
2. **The precache fingerprint was pre-existing red.** `tools/precache.sha` recorded `34b515c7…`,
   but the tree computed `90237ebb…` **at `36d3380`, before any edit of mine**. Same root cause
   the preview-isolation lane recorded: the test hashes the shared engine through the sibling
   path `../hub/`, and that sibling is a **stale staging copy** (`/root/mhpss-nepal-work/hub`),
   not the durable repo. Regenerating the digest against the stale sibling makes the assertion
   green in the layout the committed test actually reads — but the value is only as meaningful as
   that sibling. **This is a pre-existing repository-layout defect, not caused here, and it is
   not fully repaired here**; the note preserves it rather than disguising it.

## 6. Commands and counts at the committed head

Head `d01f7143618d1b0264499ef26d57b44e79a4ab33` (the commit that contains this note; the file
cannot contain its own hash without being one commit stale).

| Command | Result |
|---|---|
| `python3 -m unittest -q test_trial_scope` | **9 passed** (8 before + the new only-the-trial-form guard) |
| `python3 test_preview_isolation.py` | **9 passed** |
| `python3 -m unittest discover -s design-preview -p 'test_*.py'` | **48 passed** |
| `python3 tools/i18n-check.py` | exit 0 — gate open |
| `python3 tools/qr-check.py` | exit 0 |
| `python3 tools/sw-precache-check.py` | exit 0 |
| `python3 tools/per-layer-default-render-check.py http://127.0.0.1:8931` | **exit 0** — 11 cases, table above |
| `python3 tools/trial-scope-render-check.py http://127.0.0.1:8931` | exit 0 |
| `python3 tools/4ws-offline-redirect-check.py http://127.0.0.1:8931` | exit 0 |
| `python3 tools/5ws-still-works.py http://127.0.0.1:8931` | exit 1 — **pre-existing**, not caused here |

The `5ws-still-works.py` failure is `the agreed select ids changed: [… ward …]`. Its
`SELECT_IDS` list predates the optional `ward` field (adjacent task `t_e26d775b`); it reports the
same failure against the untouched base tree served at `127.0.0.1:8932`. The form itself is fine:
`lang=ne`, the ENG/NEP switch present, the 25-name contract matches. Left as-is rather than
edited here, because the `ward` field is another task's — narrowing that tool's list belongs with
it.

## 7. What to hand back to the Hub lane
- **The Hub engine must land for this to have any effect.** `5ws-report.html` now declares
  `data-i18n-default="ne"`; the engine that honours it exists only in
  `/root/mhpss-nepal-work/hub-real` (`task/t_2449fe51-i18n-per-layer-default`). Until
  `hub/assets/i18n.js` carries the `data-i18n-default` reader, the trial form opens **English**.
- **`hub-real/PER-LAYER-DEFAULT-EVIDENCE.md` §1 — the inaccurate claim is settled.** That note
  previously asserted `form/5ws-report.html` *"declares `<html lang="en" data-i18n-default="ne">`"*
  when **no form file did**. It has since been updated by the Hub lane to point at the sibling
  worktree `/root/mhpss-nepal-work/perlayer/form` (`task/t_2449fe51-form-default`) as the home of
  the change. **That worktree is not where this card's change landed**, and it is not this worktree
  either. The claim is now true *of a worktree*, but it is a **third** worktree, not the one this
  card names — the Hub lane should re-point §1 at the canonical location once the branches are
  reconciled. Recorded here as **outstanding on the Hub lane**, not silently accepted.
- **The `hub/assets/i18n.js` production line is still `DEFAULT = "en"`, no declaration reader.**
  Nothing about the per-layer default is in effect on the live site.
- **A direct conflict with the Hub lane's §1 table row for `5ws-report-b2.html` — flagged, not
  resolved unilaterally.** `hub-real/PER-LAYER-DEFAULT-EVIDENCE.md` §1 now lists
  `form/5ws-report-b2.html` as defaulting to **Nepali**, "because the builder copies the source
  `<head>`". **This card requires the opposite**: `5ws-report-b2.html` is one of the pages that
  "must keep declaring nothing", because it is not fully translated — its own B2 chrome (the
  "New interface copy is English pending human-reviewed Nepali wording" bar, the status strip) is
  English-only. This task therefore **strips the declaration in the builder**, so the derived page
  declares nothing. That is a deliberate divergence from the Hub lane's note, taken because the
  card's rule is explicit and the page genuinely is not fully translated. **The Hub lane should
  correct §1's B2 row** (and the "copies the source `<head>` — so it declares the same `ne`"
  reasoning, which no longer holds).

## 8. Boundaries respected

- **Hub worktree untouched** (`/root/mhpss-nepal-work/hub-real` not modified by this task).
- **No files hand-copied** between repositories; no cross-repo write.
- **No push, merge, PR or deploy.** Production refs unchanged: public `68bf197`, form `9032bb7`,
  hub `ff2d4e2`.
- **One owner, one worktree** (`form-frontend`).
- The `ward` field and the two pending hub patches (`t_e26d775b`) were **not** folded in here.
- Browser tooling **was** available and used; the rendered evidence above is from a real DOM.

## 9. Base / head

- Repository `/root/mhpss-nepal-audit-20260918/form` (branch `main`, `9032bb7`).
- Worktree `/root/mhpss-nepal-work/form-frontend`, branch **`design/preview-isolation`**.
- Base `36d33800fd55cc999e94bc0d81deeba71299972b` → head is the commit that contains this note
  (read it with `git rev-parse HEAD`; an in-file hash of itself would immediately be stale).
- Worktree clean (`git status --porcelain -uall` empty) — required by `scripts/land.py`.

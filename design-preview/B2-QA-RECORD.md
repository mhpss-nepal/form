# B2 Institutional App — QA record

**Page:** `5ws-report-b2.html` (preview only; **not** linked from `index.html`, **not** in the
service-worker precache). The shipped page remains `5ws-report.html`.
**Branch:** `design/form-frontend` · **Base:** `9032bb7a3e198882cce8ca1bf350621aba856db7`
**Last updated:** 2026-09-20

---

## Why this record exists

Three separate independent reviews failed B2. Two of those failures were real defects that the
**contract test suites could not see**, because those suites assert that CSS *text* is present —
they never render the page. That gap is now closed by `check_a11y_geometry.py`, which drives a real
Chromium, renders every step, runs axe-core (WCAG 2.1 A + AA) and measures every interactive
element with `getBoundingClientRect()`.

The lesson worth keeping: **a passing test suite is not evidence that the page works.** Measure the
rendered result.

---

## What the reviews found, and the verified state of each

| # | Finding | Status | Evidence |
|---|---------|--------|----------|
| 1 | Saved-list controls (Export CSV / Export JSON / Clear all) rendered **38.1px**, under the 44px standard | **Fixed** | `body.fx .btn.sm{min-height:38px}` (form.css:223) outranked the bare `.iu-saved .btn.sm`. Qualifying with `body.iu` wins. Now 44px at all widths. |
| 2 | Help copy under the saved list at **4.42:1** | **Fixed** | 5.51:1 |
| 3 | Five male disaggregation inputs **33.3px** at 320px | **Not reproducible** | Measured 55.1px at 320px and ≥54px at every width — wider than Direction B's 52.7px, because the inputs sit in ≥44px label wrappers. The reported 33.3px is the inner `<input>` rect, not the tap target. |
| 4 | `.iu-picker-val` **2.95:1**, `.iu-stepnote` **3.53:1** | **Fixed** | Now 6.68:1 and 5.32:1 |
| 5 | Help/hint blocks at **4.22:1** and **4.42:1** | **Fixed** | One `#f`-scoped rule covers every such block: ≥4.9:1 |
| 6 | Saved-records table a **640px** non-focusable scroll region on a phone | **Fixed** | Ported Direction B's card layout. `tbl-wrap` scrollWidth == clientWidth at 320/390/768/1280. |
| 7 | `dateAD` collapsed to **36.7px** at 768/1280 | **Fixed** | Root cause: a **duplicate** `.iu-date-row` grid rule. The stale copy came later in the file and won. Removed; the date row is side-by-side only when the field is genuinely wide. |
| 8 | `aria-required` on `role="group"` — invalid ARIA | **Fixed** | I introduced this during Direction B; the baseline had a bare `<div class="chks" id="tgs">`. Replaced with `aria-labelledby` on the real visible label. |

Findings 3 (not reproducible) and the three vision claims below were **checked by measurement and
rejected** — a screenshot impression is not a defect.

### Vision claims checked and disproved

| Claim | Measurement |
|-------|-------------|
| Step-circle number obscured by a progress bar | No element intersects the badge; 2× zoom of the stepper shows the number fully legible. |
| Step nav overflows / final step cut off | `scrollWidth == clientWidth`; active step fully inside the strip at every step. |
| "Date and place checked" button too short | Every control on the page is ≥44px. |

### Genuine defects the new gate found *after* the reviews

Both were on the **shipped page** (`5ws-report.html`), not the preview — the reviews had looked at the
preview and missed them:

- **Navy saved-records header at 2.5:1.** Direction B repainted the header navy (`#183039`) but did
  not restate the foreground, so it kept form.css's `--fx-slate` `#5b6b76`. An axe failure at 768px
  and 1280px. Now white on navy = 13.8:1.
- **Machine-translation notice buttons at 27.8px.** Created at runtime by the shared
  `hub/assets/i18n.js`, so they appear on **every** page once the notice shows. Raised to a 44px
  minimum.

---

## Verified state

- **Any test failures? No.** B2 28/28, Direction B 18/18, plus `text-setting-check`, `i18n-check`,
  `sw-precache-check`, `check_language_rules.py`.
- **`check_a11y_geometry.py`:** both pages × 8 widths (320/360/375/390/414/621/768/1280), every
  step: zero page overflow, every control ≥44px, **axe-core WCAG 2.1 AA clean**.
- **Form contract:** 76 ids and 24 names at the base; now 77 ids and 24 names. The single added id is
  `tgsLab` on a `<label>` (needed for `aria-labelledby`). **Zero control `(id, name)` pairs added or
  removed.** The form block in the preview is byte-identical to the shipped page.
- **No horizontal page overflow** at any tested width.
- **No push, no PR, no merge, no deploy.** Production Firebase/GCP untouched.

---

## Language behaviour

- A first-time reader lands on **Nepali**; English is one tap away, and `?lang=en` / `?lang=ne` both
  win over the default.
- **Stored output stays English-only.** Verified empirically, not assumed: with the interface in
  Nepali, a saved record and its exported CSV contain **no Devanagari at all** — records store codes
  (`activity:"1.1"`), and `store.js` builds labels from the English `name` field, never from the
  language-aware `label()`.
- The 5Ws form is **214 of 225** label/help/heading nodes already Nepali. The remainder are
  organisation proper nouns (CMC-Nepal, KOSHISH, NRCS), which must not be translated.
- Safety and operational wording with no reviewed Nepali string is **flagged in place**, never
  silently emitted in English.

---

## Known blocker (not a code defect)

The English-default → Nepali-default change lives in `hub/assets/i18n.js`, and:

- `hub/` has **no git repository at all** on this host;
- the `form` repository tracks **zero** `hub/` paths.

So it is applied to a local staging copy and **works in preview, but is not durable**. The exact
one-line diff is recorded in `PENDING-hub-i18n-default-ne.patch.md`, together with the 44px
tap-target fix for the same file. Both must be applied in the hub repository by its owner.

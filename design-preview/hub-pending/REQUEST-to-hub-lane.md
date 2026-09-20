# Request to the hub lane — 5 changes that make Layer 1 live, in Nepali

**To:** the owner of `mhpss-nepal/hub` (Layer 2 / hub lane)
**From:** form-frontend lane (`design/preview-isolation`, tenant `mhpss-nepal`)
**Status:** three patches below are verified `git apply --check` clean against hub
`origin/main` (`ff2d4e2`). **The hub tree has not been modified.** Two items are
not patches and need the hub lane's own action.

Adib has closed the 5Ws case and asked for two outcomes in production:

1. **Layer 1's landing page is Nepali by default** — his words: *"landing page
   NEPAL!"*.
2. **Every form we have built is shown on an "all forms" page again** — they were
   hidden, and he wants the case closed with what was agreed.

Neither can reach production from the form side alone, because the form pages load
`../hub/assets/*` and the all-forms listing lives in `hub/forms.html`.

## The five changes, in the order they must land

| # | change | where | how |
|---|---|---|---|
| 1 | 44px min-height on the machine-translation notice buttons | hub `assets/i18n.js` | `i18n.js.notice-44px.patch` |
| 2 | three UI strings for the new Ward field (`f4.wardLab`, `f4.wardHelp`, `f4.optional`) | hub `assets/i18n-strings.js` | `i18n-strings.js.ward-only.patch` |
| 3 | four missing palika ward counts | hub `assets/codes.js` | `codes.js.ward-counts.patch` |
| 4 | the per-layer default engine | hub `assets/i18n.js` | **already built** — land `t_2449fe51`, branch `task/t_2449fe51-i18n-per-layer-default`, HEAD `8273e90` |
| 5 | an "all forms" listing that includes every instrument | hub `forms.html` | `forms.html.review-listing.*.patch` — see below |

### 1–3: apply and go

```bash
cd /path/to/hub          # on a branch, not on main
git apply /path/to/form/design-preview/hub-pending/i18n.js.notice-44px.patch
git apply /path/to/form/design-preview/hub-pending/i18n-strings.js.ward-only.patch
git apply /path/to/form/design-preview/hub-pending/codes.js.ward-counts.patch

# then confirm the dictionary is still complete and grew by exactly three keys
node -e 'global.window={};require("./assets/i18n-strings.js");
  const S=window.I18N_STRINGS;
  console.log(Object.keys(S.en).length,"en",Object.keys(S.ne).length,"ne");
  console.log("ward strings:",["f4.wardLab","f4.wardHelp","f4.optional"]
    .filter(k=>S.en[k]&&S.ne[k]).length,"of 3");'
```

- **#1 is an accessibility fix, not a style choice.** The buttons are created at
  runtime by the shared engine and measured 27.8px, under the 44px minimum. They
  sit outside the form container, so no form-side rule can reach them.
- **#2 is required or the Ward label renders as the raw text `f4.wardLab`.**
- **#3 is required or the ward dropdown is hidden for four palikas.** Each count
  was confirmed from at least two independent sources; Shahid Lakhan from its own
  municipal website ("जम्मा वडा संख्या : ९"). A guessed count would offer ward
  numbers that do not exist.

### 4: land `t_2449fe51`, and do NOT apply a global Nepali default

The per-layer engine is already written and correct:

```html
<html lang="en" data-i18n-default="ne">
```

with the global kept at `var DEFAULT = "en"` and *"a page that declares nothing
keeps English"*.

**A global `DEFAULT = "ne"` must not be applied.** The Hub pages load the same
`assets/i18n.js` (`index.html`, `forms.html`, `access.html` verified), so a global
Nepali default would turn Layer 2 Nepali, which the decision forbids. Adib's
decision is per layer: Nepali for Layer 1, English for Layer 2 and Layer 3.

The form side has already declared its own default, so **once #4 lands, Layer 1
opens in Nepali with no further form change**:

| form page | declares | result |
|---|---|---|
| `form/index.html` | `ne` | Nepali — the landing page |
| `form/5ws-report.html` | `ne` | Nepali |
| `form/selfreport.html` · `phq9` · `referral` · `contact` · `cards` | nothing | English, as decided |

### 5: the all-forms listing — built, in two variants, and it fixes a live violation

**`hub/forms.html` on `origin/main` currently breaks the hub lane's own rule.** It
carries four direct links to unapproved forms (`../form/contact.html`,
`referral.html`, `phq9.html`, `selfreport.html`), which its own
`tools/hub-trial-scope-render-check.py` fails on: *anything under `/form/` other
than `/form` and `/form/5ws-report.html` fails*. The fix for that is written but
only on a branch (`15d35b3`, task `t_46e4cb25`). So there are two bases, and a
patch for each:

| variant | base | produces |
|---|---|---|
| `forms.html.review-listing.from-main.patch` | hub `origin/main` | 0 direct form links, 1 review link |
| `forms.html.review-listing.from-trialscope.patch` | after `15d35b3` (the "Not open during the trial" spans) | 0 direct form links, 5 review links |

```bash
# pick the one whose base matches your tree
git apply /path/to/form/design-preview/hub-pending/forms.html.review-listing.from-main.patch
# or
git apply /path/to/form/design-preview/hub-pending/forms.html.review-listing.from-trialscope.patch
```

Both verified by applying to a scratch copy of their own base and checking the
rendered-equivalent result: **0 direct links to an unapproved form, and the review
page is linked**. Both pass `git apply --check` against their base.

What the patch does:

- adds one line to `forms.html`: a *Supervised trial* note saying only the 5Ws is
  open in the field, and that a reviewer can open all of them together on the
  review page;
- points every per-form button at `../form/all-forms.html` — the **review page**
  — instead of at the instrument itself.

**No direct link to `contact.html` / `phq9.html` / `referral.html` /
`selfreport.html` is added anywhere, and no default Hub navigation or rail entry
changes.** The four sections still describe the instruments and read what comes
back from them. The rail group is untouched, so the hub's rail assertion (exactly
`["./#reports", "forms.html", "../form/"]`) still holds.

```bash
# the checks this must keep passing
python3 tools/hub-trial-scope-render-check.py   # 0 offenders at 390 and 1280
python3 -m unittest test_trial_scope             # the static + render rule tests
```

### 5a: one prerequisite in the form repository — please read

The review link resolves to `/form/all-forms.html`, which **is not in
`form/origin/main` yet**; it is on `form`'s `design/preview-isolation` branch
(`55b3196`), together with the review frame it uses (`preview.html`,
`preview-mode.js`, `preview-shell.js`, `preview-shell.css` — none of these are in
`form/origin/main` either).

So **land the form branch before or with this patch**, or the Hub's review link
will 404. The form pages themselves do not otherwise depend on the Hub, so the
ordering within this request is flexible; this one is not.

The build was verified on the form side by a real browser at 390 and 1280: the
landing page still exposes exactly one actionable form card, the card sheet still
carries only the `5ws` QR, and the review page opens all five instruments through
the frame with no direct address and no unapproved QR.

## What must not happen

- no global `DEFAULT = "ne"` (see #4);
- no link to `contact.html` / `phq9.html` / `referral.html` / `selfreport.html`
  from default Hub navigation, a QR, or the card sheet;
- no change to field names, value semantics, storage, queue/sync, `_rid`, the
  service worker, or the manifest — none of these patches touch them.

## How this was verified on the form side

- all three patches: `git apply --check` clean against hub `origin/main` `ff2d4e2`;
- the hub tree was checked read-only and left untouched;
- the dictionary after #2 is `en` 727 / `ne` 180 (was 725/177), i.e. **exactly the
  three ward keys**, verified with the repo's own `tools/i18n-check.py`;
- `tools/trial-scope-render-check.py` over a real browser at 390 and 1280: the
  landing page still exposes exactly one actionable form card, the card sheet
  still carries only the `5ws` QR, and the review sheet opens all five through the
  frame with no direct address and no unapproved QR;
- the language gate, the a11y/geometry gate, and the form test suites all pass.

## Related, already recorded

- Adib's ruling that machine Nepali is authorised (human review after) is on the
  translation lane's own cards: `t_2cfc3bab` comment 60, `t_93e4a525` comment 61.
  The hub lane should read those before deciding what to do with the 677 additional
  machine values, which are **not** in the patches above on purpose.
- The form branch depends on #1–#4; it is pushed at `design/preview-isolation`.

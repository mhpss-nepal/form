# Request to the hub lane — what is left of the 5 changes

**To:** the owner of `mhpss-nepal/hub` (Layer 2 / hub lane)
**From:** form-frontend lane (`design/preview-isolation`, tenant `mhpss-nepal`)
**Status:** re-checked against `hub` `origin/main` (`42f308c`) after the lane's own
PRs #1 and #2. **Two changes are already in, two are still needed, one was never
needed.** The hub tree has not been modified by this lane.

Adib closed the 5Ws case and asked for two outcomes in production:

1. **Layer 1's landing page is Nepali by default** — his words: *"landing page
   NEPAL!"*.
2. **Every form we have built is shown on an "all forms" page again.**

## Where each change stands on `hub` `origin/main` (`42f308c`)

| # | change | state |
|---|---|---|
| 1 | 44px on the machine-translation notice buttons | ❌ **still needed** — `min-height:44px` count is **0**; the live buttons measure **28px** |
| 2 | the Nepali dictionary (775 values) | ❌ **still needed** — origin/main is `en 728 / ne 180` |
| 3 | four missing palika ward counts | ✅ **already applied** (`e7c5a61`) — 0 palikas without wards |
| 4 | the per-layer default engine | ✅ **already applied** — `data-i18n-default` is read from the page, global stays `"en"` |
| 5 | the all-forms review listing | ✅ **already applied** (PR #2, `8d01dac`) — `forms.html` has 0 direct form links and 5 review links |

## The two remaining patches

Both verified `git apply --check` clean against `42f308c`:

```bash
cd /path/to/hub            # on a branch, never straight on main
git apply /path/to/form/design-preview/hub-pending/i18n.js.notice-44px.patch
git apply /path/to/form/design-preview/hub-pending/i18n-strings.js.add-ne-775.patch

# confirm: complete, exactly the expected growth, nothing lost
node -e 'global.window={};require("./assets/i18n-strings.js");
  const S=window.I18N_STRINGS, en=Object.keys(S.en), ne=Object.keys(S.ne);
  console.log(en.length,"en",ne.length,"ne");
  console.log("ne without en:",ne.filter(k=>!en.includes(k)).length,"(must be 0)");
  console.log("en without ne:",en.filter(k=>!ne.includes(k)).length,"(must be 0)");'
python3 tools/i18n-check.py
```

### 1 — the 44px notice buttons (accessibility, not style)

The machine-translation notice buttons are created **at runtime** by the shared
`assets/i18n.js`. They sit outside the form container, so no form-side rule can
reach them. Measured on the live site after PR #1: **28px**, under the 44px
minimum. The patch is two lines.

### 2 — the Nepali dictionary

**This is why Layer 1 opens in Nepali but reads mostly English today.** PR #1
landed the per-layer default, so `form/` and `form/5ws-report.html` **do** serve
`lang="ne"`. But the live dictionary has no Nepali for the keys the landing page
is built from (`ml.p036`, `ml.p030`, `ml.p049`, …), so the page is a Nepali shell
around English text. Measured on the live site:

| live page | Nepali body text now | with this patch |
|---|---|---|
| `form/` (landing) | 8% | **82%** |
| `form/all-forms.html` | 9% | **93%** |
| `form/5ws-report.html` | 81% | 83% |

**Add-only by construction.** The generator refuses to build if any key it would
touch already exists with a different value. Applied to a scratch copy of
`origin/main` and driven in a real browser: `en` 728 → 955, `ne` 180 → 955,
**0 keys lost, 0 existing values changed**, no key present in one table and not
the other, `_meta` structure and rationale comments preserved verbatim.

Two guards inside it, both from findings while building it:

**`f4.wardLab` is not overwritten — your value wins.** You removed the
`<span class="opt">` markup from it because the form renders that key with
`data-i18n` (not `data-i18n-html`), so the markup would show as literal text on
screen. You were right; this lane's copy was wrong. It was the only value
conflict between the two dictionaries.

**19 strings are held in English, not translated.** `phq9.item*`, `consent.*`,
`safeguard.*` and `clinical.*` are named in your own file as *"strings that NO
machine may translate"*. This lane's values for them are machine drafts, so they
are excluded:

```
clinical.phq9ValidatedTextWarning   consent.label      consent.phq9
phq9.item1 … phq9.item9             phq9.item9Instruction
phq9.itemDifficulty                 phq9.itemInstruction
safeguard.checkLabel                safeguard.confirmation
safeguard.consequence               safeguard.referralExclusion
```

The PHQ-9 cut-off ≥10 belongs to specific validated wording (Kohrt et al., BMC
Psychiatry 2016). Machine wording there is a **clinical risk**, not a quality
issue. The validated instrument this lane rescued from the open-access supplement
is a separate artifact — `design-preview/references/phq9-nepal-REVIEW.md` — for
the team to adopt deliberately, not to be merged as machine text.

## Already applied, kept here only as the record

`codes.js.ward-counts.patch` and `forms.html.review-listing.*.patch` are **no
longer needed** — the lane applied equivalents itself. Do not re-apply them.

For the record of what was proposed: each ward count was confirmed from at least
two independent sources, Shahid Lakhan from its own municipal website ("जम्मा वडा
संख्या : ९"), because a guessed count would offer ward numbers that do not exist.
And the review listing was written to keep the hub's own rail assertion (exactly
`["./#reports", "forms.html", "../form/"]`) intact while removing every direct
link to an unapproved form.

## What must not happen

- **no global `DEFAULT = "ne"`.** The Hub pages load the same `assets/i18n.js`
  (`index.html`, `forms.html`, `access.html`), so a global Nepali default would
  turn Layer 2 Nepali, against the per-layer decision. The declared
  `<html lang="en" data-i18n-default="ne">` mechanism is the correct one and is
  already in place;
- no link to `contact.html` / `phq9.html` / `referral.html` / `selfreport.html`
  from default Hub navigation, a QR, or the card sheet;
- no change to field names, value semantics, storage, queue/sync, `_rid`, the
  service worker, or the manifest — none of these patches touch them.

## Not needed, and deliberately left alone

`form/cards.html` is a **print sheet**. It carries English and Nepali together on
each card on purpose, because a printed card cannot switch language, and it does
not load `assets/i18n.js` at all. Its side-by-side pairing is the design, so it
needs no translation work and should not be "fixed".

## Related, already recorded

- Adib's ruling that machine Nepali is authorised (human review after) is on the
  translation lane's own cards: `t_2cfc3bab` comment 60, `t_93e4a525` comment 61.
- The form branch is pushed at `design/preview-isolation`.

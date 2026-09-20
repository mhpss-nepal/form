# Two conflicts the form-frontend lane found while trying to publish

Date: 2026-09-20. Lane: `form-frontend` (`design/preview-isolation`), tenant `mhpss-nepal`.

Context: Adib asked for all forms to go live if everything passes, and ruled on the
translation policy (971 machine Nepali values acceptable, humans review later) and on
the production freeze ("buka" = open). While verifying the way in, this lane found two
conflicts that make the straightforward "merge it" answer wrong. Both are recorded
here rather than acted on unilaterally.

## Conflict A — two lanes hold opposite translation policies

| | this session | the translation lane |
|---|---|---|
| rule | machine Nepali is fine; a human team reviews on the live pages | *"no dictionary string leaves English without a human decision"* |
| evidence | Adib's instruction, 2026-09-20 | `form-translation` `task/t_2cfc3bab` commits `6376742`, `b95a3d3`, `ef76883` |
| state | `ne` = 971 | `ne` = 294, 100 disagreements held in English, *"proofread NOT OBTAINED"* |

Adib ruled for the machine path, but **the ruling has not reached that lane**. Applying
this session's dictionary to the shared file would silently reverse that lane's work.
This lane did **not** touch that branch.

Relevant measurement: of the 294 Nepali values that lane holds, **294 are byte-identical
to this session's and 0 differ**, and its provenance for them is `machine`, not `human`.
So the 971 overwrite destroys **no human review** — none exists on either side yet.

## Conflict B — the global Nepali default is the wrong mechanism

This lane had set `DEFAULT = "ne"` in `hub/assets/i18n.js`. The registry records that
Adib's decision is **per layer**: Nepali for Layer 1 (5Ws), English for Layer 2 and
Layer 3. The Hub pages (`index.html`, `forms.html`, `access.html`) do load
`assets/i18n.js`, so a global `"ne"` would violate that decision.

Task **`t_2449fe51`** (running, `task/t_2449fe51-i18n-per-layer-default`, HEAD
`8273e90`, not yet in hub main) already implements it correctly: the page declares
`<html lang="en" data-i18n-default="ne">`, the global stays `"en"`, and *"a page that
declares nothing keeps English"*.

**Consequence for this lane:** the form pages should declare `data-i18n-default="ne"`
on their own `<html>` once that engine lands, instead of depending on a global
constant. The global change should not be applied to the hub.

## What this lane did instead

- delivered the hub dependency as a **reviewable patch set** with provenance
  (`design-preview/hub-pending/`), both patches `git apply --check` clean against hub
  `origin/main` `ff2d4e2`, hub tree untouched;
- kept the machine Nepali work in three independent places (pushed branch, timestamped
  backup, `i18n-ne-fill.json` draft) so a concurrent writer cannot lose it again — an
  earlier concurrent write did drop `ne` from 405 to 301;
- did **not** merge, deploy, or press Publish.

## Correction carried forward

A global `DEFAULT = "ne"` had been applied by this lane on the earlier reading that the
whole interface should default to Nepali. That reading was superseded by the per-layer
decision above. It was **not** re-applied; the file currently in the staging tree should
be treated as carrying the wrong mechanism.


## Update — Adib resolved conflict A the same day

Adib ruled: **machine English→Nepali translation is authorised** for the field forms,
with the human team reviewing the Nepali on the live pages and sending corrections
afterwards. The ruling was recorded on the translation lane's own cards
(`t_2cfc3bab` comment 60, `t_93e4a525` comment 61) **without modifying their branch**.

Consequence for the ship: the machine dictionary is no longer contested *by policy*,
but it is still delivered separately from the three strings the form strictly needs
(`design-preview/hub-pending/i18n-strings.js.ward-only.patch`), so the safe subset can
land first.

Conflict B stands as written: the form pages declare their own
`data-i18n-default="ne"`, and no global default is flipped.

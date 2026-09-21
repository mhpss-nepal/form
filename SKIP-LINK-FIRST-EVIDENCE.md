# Skip link first in every language — evidence

**Task:** `t_e504a356` — *Skip link is NOT the first tab stop in English: #pwabar (pwa.js) beats
it; i18n.js fix only runs when lang !== "en"*
**Status:** the live defect is FIXED and VERIFIED. This branch adds the gate that keeps it fixed.
**Worktree:** `/tmp/mhpss-fix-20260921/form` (throwaway clone of `main`), branch
`fix/skip-link-first-gate`, base `eb66aba`.
**Deployed:** hub `16383d1` (merge of PR #20) is live on `https://mhpss-nepal.github.io/`.

---

## 1. The card's own acceptance evidence, on the LIVE site, after the fix

For each of the six pages, in the Nepali default view and `?lang=en`, with `#pwabar` forced
visible (`document.getElementById('pwabar').hidden = false`), headless Chromium, a fresh context
per measurement, cache-busted URL, one `Tab`:

```
PAGE                               LANG       FIRST TAB STOP             IS SKIP   PASS
form/5ws-report.html               ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/5ws-report.html               en         A.a11y-skip 'Skip to the form'  True   PASS
form/contact.html                  ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/contact.html                  en         A.a11y-skip 'Skip to the form'  True   PASS
form/referral.html                 ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/referral.html                 en         A.a11y-skip 'Skip to the form'  True   PASS
form/phq9.html                     ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/phq9.html                     en         A.a11y-skip 'Skip to the form'  True   PASS
form/selfreport.html               ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/selfreport.html               en         A.a11y-skip 'Skip to the form'  True   PASS
form/index.html                    ne_default A.a11y-skip 'फारममा जानुहोस्'  True   PASS
form/index.html                    en         A.a11y-skip 'Skip to the form'  True   PASS

12/12 measurements pass.
```

Before the fix the same measurement was **6 of 12**: every English case reported
`BUTTON.x '×' [pwabar]`, exactly as the card describes.

`python3 tools/skip-link-first-render-check.py https://mhpss-nepal.github.io` → **exit 0**,
12 measurements, 0 failing.

## 2. Where the fix actually came from

It did **not** come from this branch. While this task was running, the same defect was found and
fixed on the hub side: **hub#20** (`e3a5a0c`, merged as `16383d1`,
`fix/skip-link-all-languages`). It moved the re-ordering out of `mountNotice()` into
`keepSkipFirst()`, called from `start()` in every language, and deliberately left `form/pwa.js`
alone because that file is byte-pinned by `test_trial_scope.py`.

So the engine half is done and live. This branch is the **gate** half: without a rendered
regression check, nothing in the source stops this from silently regressing again — which is
precisely how the first attempt shipped (green in Nepali, broken in English, invisible to every
source-level test).

## 3. Failing-first, proven

Same check, same command, engine switched:

| engine under `../hub` | result |
|---|---|
| `e3a5a0c~1` (pre-fix) | **exit 1** — 6 of 12 fail, all six **English**, first stop `BUTTON.x` in `#pwabar` on every page; body order `['pwabar', 'fbbar', 'a11y-skip', 'ribbon']` |
| `16383d1` (merged fix, PR #20) | **exit 0** — 12 of 12 |

## 4. Beyond the card: 47 more measured cases, live, all green

The card's assumption is "one injector, one language". Three injectors and two languages were
measured instead — strip shown by `pwa.js` itself, the notice pre-dismissed, the notice present,
reviewer mode (`?i18n=marks`), a runtime `ne → en → ne` toggle, and the review frame:

**47 checks, 0 failures** (live and against the merged tree). In the review frame, where the page
is injected inside `#shell-page` so the frame's own controls legitimately come first, the
in-frame order is `['a11y-skip', 'ribbon', 'top', 'wrap', …]` — the page's own skip link is first
within the page.

## 5. Two gaps this leaves open — NOT fixed here, NOT silently bundled

**5a. `form/tools/precache.sha` is stale, and the field cache is not bumped.**
`../hub/assets/i18n.js` is on `PRECACHE`, and hub#20 changed it. On `main` today:

```
$ python3 tools/precache-fingerprint.py
precache fingerprint OUT OF DATE
  recorded 8a338b3d581a6397dd58df746656ee776e503d1da37bd2fc3bbdea75d1467bc1
  computed c0f4c1e1ee95435baa311ca0a03c77f065c204731ffd27ec29bf006f130eedc6
exit 1
```

This is the exact class of failure `sw.js` warns about in its own header: *"the fix was deployed
and had no effect on any device until this line changed."* A phone that has already opened the
forms keeps the **v43** engine — `mountNotice()`-scoped re-ordering and all — so on a field
handset the English tab order is still broken even though the origin is correct. Needs a
maintainer decision because the bump usually accompanies a `pwa.js` change, and `pwa.js` is
byte-pinned by `test_trial_scope.py`.

**5b. The engine's own deadline gap (hub#20).**
`watchBodyOrder()` is **defined but never called** — dead code. And in `start()`,
`keepSkipFirst()` (line 849) runs *before* the `i18n:changed` dispatch (line 864). So anything that
reacts to that event and injects at the front of `<body>` runs after the last re-assert. That path
exists: the review frame's `preview-shell.js` dispatches `preview:ready` → `preview-mode.js`
`enforce()` → `bannerFirst()` → `insertBefore(banner, body.firstElementChild)`. Wiring the
observer that was written for this (or moving the call after the dispatch) closes it.

**Do not** fix 5b by calling `keepSkipFirst()` from `preview-mode.js`: its `enforce()` is itself a
body-mutation observer that re-inserts the banner at the front, so that would re-trigger it and
loop. This branch leaves `preview-mode.js` untouched for that reason.

## 6. Not touched

The disability block, the store, the CSV — as the card requires.

## 7. Reproduce

```bash
python3 -m http.server 8791 --bind 127.0.0.1     # from the parent of both repos
python3 tools/skip-link-first-render-check.py http://127.0.0.1:8791
```

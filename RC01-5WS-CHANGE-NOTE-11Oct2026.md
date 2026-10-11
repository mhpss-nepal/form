# 5Ws field form (RC01) — two additions, 11 October 2026

Patched file: `5ws-report.html`, to replace `review-5ws-v2/form/5ws-report.html` in the `form`
repository. Built on `origin/main` **3971595** (read 11 Oct 2026). Base file
`fb172c3c…c938f`, 719,784 bytes → patched `84232c29…9d9e`, 727,869 bytes.
**Nothing was pushed. The repository is untouched.**

## What was added

**1 · New people today.** A required block under *For whom*: girls and boys under 18, women and
men 18 and over, other at any age, and of those, women and men 60 and over. The counts are bounded
by the session's own sex × age table — the form refuses a figure larger than the group it comes
from, and refuses a total larger than attendance. Without this block nothing in the form can yield
*people reached*; attendance alone only ever yields contacts.

**2 · Joint activity safeguard.** A new question beside *Joint activity with*: **we led it — we
report the numbers**, or **we took part — the lead organisation reports the numbers**. Choosing the
second switches off attendance, the sex × age tables, the new-people block, the *seen at the
session* counts, the disability cells and every activity count, sets attendance to zero, and marks
the record `countsHeldByLead: true`. A partner report is refused unless the lead organisation is
named. This is the only mechanism that stops two organisations reporting the same people from one
session.

## What was already there, and was left alone

Checked against the decisions of 27 September before touching anything:

- **Other sex** — already present, as a separately declared advanced table beside Female and Male;
  the contract carries `female, male, other, unknown`.
- **Age bands** — already `0–4 · 5–9 · 10–17 · 18–59 · 60+`, version-locked in the record as
  `nepal-age-04-5to9-10to17-18to59-60/1`. The 10–19 and 20–59 bands appear only in the read-only
  historical sample, marked never to be re-binned.
- **Consistency** — the form already refuses a sex × age table whose total differs from its own
  attendance, an activity attendance above the session, an activity cell above the session cell,
  and disability subsets above their sex-age group.
- **Capacity building** — the activity list already excludes group 5.

## Contract

Both additions are **optional keys** in the wire contract (`newToday`, `reportingRole`,
`countsHeldByLead`), so records written before today still validate. The requirement is enforced at
the form, not in the stored shape. No schema or version string was changed.

## Before this is released

`release-manifest.json`, `review-5ws-admin-test-v35/releases/native-test-rc01-20261011/candidate-manifest.json`
and the `release_sha256` digest pin the old bytes, so `tests/rc01/check_release.py` will fail until
the release is re-cut. That re-cut belongs to whoever owns the RC01 package — the hashes were not
rewritten here, because a hand-edited digest would defeat the guard it exists to provide.

## Verified

Run in Chromium against the package's own assets, with all outbound network blocked and nothing
submitted anywhere: 13 checks, 0 failures — the block appears and is required; a count above its
group is refused; the record carries the new keys; partner mode locks every count, demands the lead
organisation, and flags the record; switching back to lead unlocks; the Nepali repaint carries the
new labels (machine draft, for a translator).

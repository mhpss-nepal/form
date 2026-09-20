# Handoff — a `ward` field was added to the 5Ws record, and it reaches Layer 2

**From:** Form Frontend session (`design/form-frontend`, workspace `/root/mhpss-nepal-work/form-frontend`)
**To:** the hub/backend and V2 architecture lane
**Date:** 2026-09-20
**Status:** implemented in the form frontend, **not yet landed into the monorepo**

Please read this before landing anything from this branch. It changes what a field
report carries, which changes what Layer 2 has to read and report.

---

## 1. What changed

The 5Ws form now records an **optional** `ward`.

```
record() { … ward: $("ward").value, … }
```

| | |
|---|---|
| Field name | `ward` |
| Type | string; `""` when not given, otherwise `"1"`…`"N"` |
| Required? | **no** — deliberately optional |
| Blank means | the whole palika, or the ward is not known |
| Appears when | a palika is selected (palika-level report, or an unlisted site) |
| Options | built from the palika's own `wards` count in `codes.js`, so it cannot drift |
| Contract | no existing field changed, was renamed, or removed |

## 2. Why it was added

MoH asked for the area dropdowns to follow NDRRMA's affected-area list. NDRRMA
publishes impact **by ward** — Bidur 1/4/5/9/10, Uttargaya 1–5, Gosaikunda 1/2/3/5,
Tarakeshwor 4 and 6, Kispang 5, Kalika 1, Galchhi 6 (1/2/4/8 partial).

The app already stored `ward` **per site** in `codes.js`, but never asked the
reporter, so a palika-level report could not say which ward was affected. Without
the field, an NDRRMA comparison is only possible for reports whose site happens to
map to one ward.

Optional rather than required, on purpose: a report may cover a whole palika, or an
unlisted site whose ward nobody knows, and a required field would manufacture a
guess. Guessed geography is worse than absent geography because it looks usable.

## 3. What Layer 2 needs to know

1. **A new field will appear in the record.** Anything that enumerates or validates
   record fields must accept `ward`, and must treat `""` as "not stated" rather than
   as missing or invalid.
2. **Do not sum by ward and treat it as a denominator.** `ward` is often blank by
   design, so ward-level totals will not reconcile against palika totals.
3. **Aggregation floor is unaffected** — `ward` is a location attribute, not a
   count, so it adds no new reconstruction risk. It does make some ward-level
   breakdowns possible that were not before, so if ward-level output is ever
   published, the existing below-floor suppression has to be applied at that grain
   too.
4. **If a dashboard adds a ward filter**, the same rule as the district filter
   applies: a record with no ward must be *stated* as such, not silently dropped.

## 4. Data gap the backend lane should own

**4 of the 20 palikas in `codes.js` carry no `wards` count:**
Aamachhodingmo, Shahid Lakhan, Gandaki, Ichchhakamana.

Aamachhodingmo is one NDRRMA names as affected (all wards cut off, ward 1 directly
affected), so this is a real hole. For these palikas the ward control **stays
hidden** rather than offering a wrong count. The fix belongs in `codes.js`
(`PALIKAS[].wards`), which is owned in the hub/monorepo, not in the form.

## 5. How this reaches production, and what not to do

The form does not reach the monorepo by copying files. `scripts/land.py` is the
only supported path, and it imports **one exact commit SHA** from a source repo and
proves byte-for-byte parity.

So: **do not hand-copy `5ws-report.html` or `codes.js` into the monorepo.** Land the
frontend commit, or land a `codes.js` change through the hub lane — whichever owns
that file — and let `land.py` verify it.

Relevant commits on `design/form-frontend`:

| commit | what |
|---|---|
| `24c7a2a` | feat: optional ward field (the field, the list, the record) |
| `f7c4b5c` | PHQ-9 page: validated Nepali wording, and the record flag guard |
| `78cd35b` | validated Nepali PHQ-9 recovered from the published source |
| `25f16cb` | all 559 machine Nepali drafts applied — dictionary coverage 971/971 |

## 6. Two things the other lane may disagree with — please say so

1. **The dictionary.** This session translated **all 971** keys into Nepali (559 by
   machine) because Adib relayed a team decision that everything is machine
   translated so a human team can review it on the live pages and send corrections.
   The hub i18n lane has the opposite standing rule — recorded in commit
   `f454803`, *"no dictionary string leaves English without a human decision"* — and
   currently holds 294 Nepali strings. **These two cannot both stand.** Adib needs to
   rule on it; I am not overwriting the hub lane's branch.
2. **Which `codes.js` is authoritative.** District and site lists exist in the
   form-frontend's staging copy, in the monorepo (`apps/hub/assets/` and
   `apps/public/assets/`), and in the hub worktrees. `codes.js` also records its own
   open questions (`D-S24` Nawalparasi East/West, `D-S14` whether the DAO list joins
   the denominator), so the data workstream may already own this. **Please say which
   file is the source of truth** before anyone edits a list.

## 7. What I did NOT do

- Did not add **Nawalparasi West**. This session's first audit called it a gap; on
  reading `codes.js` it is already tracked as open question **D-S24** ("NAW carries
  the official name and keeps 'Nawalpur' as an alias"), so it is a workstream
  decision, not an oversight. My earlier report was corrected.
- Did not edit any district, palika or site list.
- Did not touch the i18n lane's branch.
- Did not push, merge, or deploy anything.

# Dropdown audit against NDRRMA — what is needed, and what is missing

**Asked by:** MoH, via Adib — should the organisation and area dropdowns follow the affected-area
list on the NDRRMA page, instead of the generic list built from what has already been submitted?

**Answer:** the lists are close, but three real gaps were found. One is a *missing field*, not a
missing name. Details and evidence below.

---

## 1. The reference used

NDRRMA / MoHA, **Rasuwa–Bhotekoshi Flood: Search, Rescue and Relief Response, Situation Report #01**,
1 September 2026 — `ndrrma.gov.np/mediafiles/rasuwa/Rasuwa_Flood_SitRep_Temp_ENG_01_01092026.pdf`
(CC source, 9 pages, 2.7 MB — downloaded and parsed).

Context from the same report: ~1.6 million people impacted; 3 moderately affected districts (Dhading,
Gorkha, Chitwan); 15 affected municipalities; 30 holding centres sheltering 3,930 people across
Nuwakot and Rasuwa.

---

## 2. Districts — **gap found**

NDRRMA SitRep #01 names: **Rasuwa, Nuwakot, Dhading, Gorkha, Chitwan**, and lists areas in
Nawalparasi East and West and Tanahun under road/access impacts.

| District | In app? |
|---|---|
| Rasuwa, Nuwakot, Dhading, Gorkha, Chitwan, Tanahun, Nawalparasi East | yes |
| **Nawalparasi West** | **no** |

The app has a single `NAW` entry, "Nawalparasi (Bardaghat Susta East)". NDRRMA treats East and West
as separate districts. A reporting organisation working in Nawalparasi **West** currently has no entry
and would have to fall back to "Other — specify", which loses the district code.

The app also carries **Kathmandu** and **Sindhupalchok**, which are not in the SitRep #01 impact list
(Kathmandu appears as a relief collection point; Sindhupalchok for B.P. Highway disruption). Keeping
them is reasonable — they are legitimate reporting locations — so this is an addition, not a removal.

**Needed:** add `Nawalparasi West`.

---

## 3. Local levels (palika) — **no gap**

All 11 local levels in the NDRRMA needs table resolve to an app entry. One looked missing and is not:

| NDRRMA spelling | App spelling | Same? |
|---|---|---|
| Tarkeshwar Rural Municipality (Nuwakot) | **Tarakeshwor** Rural Municipality (NUW) | yes — spelling only |
| Uttargaya, Gosaikunda, Aamachhodingmo, Kalika (Rasuwa) | all present | yes |
| Kispang, Bidur (Nuwakot) | present | yes |
| Galchhi, Gajuri, Benighat Rorang, Siddhalek (Dhading) | present | yes |

The app's 20 palikas also use official **pcode** identifiers (`NP0329403`, from COD-AB NPL v02), so
they are not ad-hoc — they follow the national local-level list. `PALIKAS` is therefore *ahead* of the
SitRep here, not behind. No change needed.

---

## 4. Holding centres (sites) — **gap found**

**The app has no Rasuwa holding centres of its own.** The 14 `RAS-*` sites are mostly schools and
localities; the SitRep's Rasuwa holding centres are not in the list. Nuwakot and Dhading centres are
better covered.

NDRRMA-named holding centres and whether the app has them:

| NDRRMA holding centre | District | In app? |
|---|---|---|
| Maliung (Hydro Area) | Rasuwa | **no** |
| Nikantha Secondary School, Bogattar | — | app has "Nilkantha Secondary School", no "Bogattar" |
| Himalayan Campus (Kalkastan) | — | **no** |
| Ramche (Ramche School) | — | **no** |
| Syafrubesi (Syafra School) | Rasuwa | app has "Komin, Syafrubesi", not this school |
| Dadagau (Nearty School) | — | **no** |
| Khaidi Gaun | — | **no** |
| Ronga | — | **no** |
| Dhunche (City Hall Center) | Rasuwa | likely the app's "District Coordination Committee, Rasuwa (Dhunche)" — needs confirming |
| Tamang Plaza, Bidur-4, Battar | Nuwakot | yes |
| Karki Manakamana Basic School, Karkigaun | Nuwakot | yes |
| Indrayani Basic School, Vidur-1 | Nuwakot | yes |

The SitRep also states **30 holding centres across Nuwakot and Rasuwa**; the app carries 41 Nuwakot
sites and 14 Rasuwa, so the counts are not directly comparable — the app's list is broader.

**Needed:** the authoritative holding-centre list, which the SitRep does not print in full. The site
list is derived from "the holding-centre roster of the daily reporting workbook" (per the form's own
footnote), so the roster needs updating from NDRRMA's current centre list.

---

## 5. **Ward — missing as a field (gap found)**

NDRRMA's needs table gives an **affected-area** per local level in *wards*:

| Local level | Affected wards (NDRRMA) |
|---|---|
| Uttargaya RM, Rasuwa | 1, 2, 3, 4, 5 |
| Gosaikunda RM, Rasuwa | 1, 2, 3, 5 |
| Aamachhodingmo RM, Rasuwa | all wards; ward 1 directly affected |
| Kalika RM, Rasuwa | 1 |
| Tarkeshwar RM, Nuwakot | 4 and 6 |
| Kispang RM, Nuwakot | 5 |
| Bidur Municipality, Nuwakot | 1, 4, 5, 9, 10 |
| Galchhi RM, Dhading | 6; 1, 2, 4, 8 partially affected |
| Benighat Rorang RM, Dhading | 5 wards |

The app stores `ward` **per site** in `codes.js` (e.g. `RAS-01` → ward 6), but there is **no ward
dropdown in the form**. A report that covers a whole palika, or a site not on the roster, cannot say
which ward was affected the way NDRRMA does.

This is a **data-model change**, not a list update: it adds a field to the record, so it needs
integration control rather than being applied quietly.

---

## 6. Recommendation — and what must not be done silently

| # | Change | Kind | Can I do it? |
|---|---|---|---|
| 1 | Add `Nawalparasi West` district | list addition | yes — but see the note below |
| 2 | Add the NDRRMA-named holding centres | list addition; needs the authoritative centre list | yes, once the list is supplied |
| 3 | Add a **ward** field | **form/schema change** | **needs approval** |
| 4 | Verify spelling variants (Tarkeshwar/Tarakeshwor, Nikantha/Nilkantha, Dhunche City Hall) | list cleanup | yes |

**Important:** I cannot verify that `codes.js` is the source the live site serves. The app loads
`hub/assets/codes.js`, but `codes.js` is **not tracked by the form repository** and `hub/` has no git
repo on this server — the same blocker already recorded for `i18n-strings.js`. Editing it here would
change the preview but not necessarily anything real. That question needs the hub repo owner.

**Not affected by any of this:** the organisation list. NDRRMA does not publish an organisation list;
the app's 9 entries come from the MHPSS Technical Working Group. If MoH wants that list extended, the
membership list has to come from them, not from NDRRMA.

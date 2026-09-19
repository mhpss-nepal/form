# 5Ws form preservation inventory

- Inventory version: `2.0.0`
- Executor: ☁️ Thar Lay/server
- Branch / base: `design/form-frontend` / `9032bb7a3e198882cce8ca1bf350621aba856db7`
- Selected active form: **MHPSS Activity Report — 5Ws**
- Scope: contract-preservation guardrail for the selected preview; `5ws-report.html` has presentation, accessibility, and truthful-status changes only. Field/schema/storage/sync/PWA contracts remain unchanged.

## Controls: 49 static + 1 dynamic group

| # | Scope | Element | Type | ID | Name | Label | Constraints |
|---:|---|---|---|---|---|---|---|
| 1 | f | select | select | org | org | Reporting organisation | — |
| 2 | f | input | text | orgOther | orgOther | Name of organisation | — |
| 3 | f | input | text | focalName | focalName | Focal point name | — |
| 4 | f | input | tel | focalPhone | focalPhone | Focal point phone | — |
| 5 | f | input | email | focalEmail | focalEmail | Focal point email — optional | — |
| 6 | f | select | select | cadre | cadre | Cadre delivering the activity | — |
| 7 | f | input | text | cadreOther | cadreOther | Which cadre? | — |
| 8 | f | input | text | partners | partners | Joint activity with — optional | — |
| 9 | f | input | date | dateAD | dateAD | Date — Gregorian (AD) | — |
| 10 | f | input | time | sessionTime | sessionTime | Start time — optional | — |
| 11 | f | input | text | dateBS | dateBS | Date — Bikram Sambat — optional | pattern=\d{4}-\d{2}-\d{2} |
| 12 | f | select | select | district | district | District | — |
| 13 | f | input | text | districtOther | districtOther | Which district? | — |
| 14 | f | select | select | site | site | Site | — |
| 15 | f | input | text | siteOther | siteOther | Name of site | — |
| 16 | f | select | select | palika | palika | Palika (local level) | — |
| 17 | f | select | select | modality | modality | Service setting — where the activity took place | — |
| 18 | f | input | text | modalityOther | modalityOther | Where was it? | — |
| 19 | f | select | select | activity | activity | Activity | — |
| 20 | f | input | text | activityOther | activityOther | Describe the activity | — |
| 21 | f | select | select | status | status | Status | — |
| 22 | f | textarea | textarea | description | description | One-line description — optional | maxlength=220 |
| 23 | f | input | text | targetGroupOther | targetGroupOther | Which other group? | — |
| 24 | f | input | number | reachedTotal | reachedTotal | Attendance | min=0, step=1, inputmode=numeric |
| 25 | f | input | number | f04 | — | Female, age 0 to 4 | min=0, step=1, inputmode=numeric |
| 26 | f | input | number | m04 | — | Male, age 0 to 4 | min=0, step=1, inputmode=numeric |
| 27 | f | input | number | o04 | — | Sex not recorded, age 0 to 4 | min=0, step=1, inputmode=numeric |
| 28 | f | input | number | f514 | — | Female, age 5 to 14 | min=0, step=1, inputmode=numeric |
| 29 | f | input | number | m514 | — | Male, age 5 to 14 | min=0, step=1, inputmode=numeric |
| 30 | f | input | number | o514 | — | Sex not recorded, age 5 to 14 | min=0, step=1, inputmode=numeric |
| 31 | f | input | number | f1549 | — | Female, age 15 to 49 | min=0, step=1, inputmode=numeric |
| 32 | f | input | number | m1549 | — | Male, age 15 to 49 | min=0, step=1, inputmode=numeric |
| 33 | f | input | number | o1549 | — | Sex not recorded, age 15 to 49 | min=0, step=1, inputmode=numeric |
| 34 | f | input | number | f5059 | — | Female, age 50 to 59 | min=0, step=1, inputmode=numeric |
| 35 | f | input | number | m5059 | — | Male, age 50 to 59 | min=0, step=1, inputmode=numeric |
| 36 | f | input | number | o5059 | — | Sex not recorded, age 50 to 59 | min=0, step=1, inputmode=numeric |
| 37 | f | input | number | f60 | — | Female, age 60 and over | min=0, step=1, inputmode=numeric |
| 38 | f | input | number | m60 | — | Male, age 60 and over | min=0, step=1, inputmode=numeric |
| 39 | f | input | number | o60 | — | Sex not recorded, age 60 and over | min=0, step=1, inputmode=numeric |
| 40 | f | input | number | ofChildAlone | — | Children without an adult with them | min=0, step=1, inputmode=numeric |
| 41 | f | input | number | ofPreg | — | Pregnant women or women with an infant | min=0, step=1, inputmode=numeric |
| 42 | f | input | number | ofPwd | — | Visible disability or needing help to move | min=0, step=1, inputmode=numeric |
| 43 | f | input | number | ofInjured | — | Visibly injured or unwell | min=0, step=1, inputmode=numeric |
| 44 | f | input | number | ofDistress | — | In acute distress — needed one-to-one attention | min=0, step=1, inputmode=numeric |
| 45 | f | button | submit | — | — | Save report | — |
| 46 | page | button | button | reset | — | Clear | — |
| 47 | page | button | button | expCsv | — | Export CSV | — |
| 48 | page | button | button | expJson | — | Export JSON | — |
| 49 | page | button | button | wipe | — | Clear all saved reports | — |
| 50 | f | input | checkbox | generated in #tgs | — | One per C.TARGET_GROUPS | at least one required |

## Exact collected record keys

`dateAD`, `sessionTime`, `dateBS`, `district`, `palika`, `site`, `siteOther`, `siteSource`, `org`, `orgOther`, `donors`, `districtOther`, `cadreOther`, `modalityOther`, `activityOther`, `targetGroupOther`, `partners`, `iascSub`, `focalName`, `focalPhone`, `focalEmail`, `cadre`, `activity`, `modality`, `status`, `targetGroups`, `description`, `reachedTotal`, `countBasis`, `distinctPeople`, `f04`, `m04`, `o04`, `f514`, `m514`, `o514`, `f1549`, `m1549`, `o1549`, `f5059`, `m5059`, `o5059`, `f60`, `m60`, `o60`, `ofChildAlone`, `ofPreg`, `ofPwd`, `ofInjured`, `ofDistress`

## Programmatic validation rules

- **required** — org; site; dateAD; activity; modality; focalName; focalPhone
- **conditional Other text** — `org=OTHER → orgOther`; `site=OTHER → siteOther`; `cadre=OTH → cadreOther`; `modality=OTHER → modalityOther`; `district=OTHER → districtOther`; any current activity marked `other → activityOther`; `targetGroups` containing `TG-OTH → targetGroupOther`
- **activity current** — activity must resolve in C.activityByCode and not be retired
- **session time format** — if present, HH:MM 24-hour
- **free-text privacy** — reject 7+ consecutive digits or @
- **palika** — site=PALIKA requires palika; any palika must match ^NP\d{7}$
- **partners privacy** — organisation names only; reject 7+ consecutive digits or @
- **date** — dateAD cannot be later than STORE.todayLocal()
- **target group** — at least one target group required
- **attendance** — reachedTotal required; enter 0 if nobody attended
- **count basis** — countBasis required and form fixes it to CONTACTS; distinctPeople is fixed to empty string on this form
- **disaggregation** — sum may not exceed attendance; if nonzero it must equal attendance; partial undercount is rejected
- **of-whom bounds** — each optional value may not exceed attendance; values are not added together

## Runtime DOM hooks

- **progress** — #steps, a[data-step=s1…s5], #s1, #s2, #s3, #s4, #s5
- **conditional_wrappers** — #orgOtherWrap, #cadreOtherWrap, #districtOtherWrap, #siteOtherWrap, #palikaWrap, #modalityOtherWrap, #activityOtherWrap, #tgOtherWrap
- **dynamic_help** — #siteHelp, #activityHelp, #descCount, #storeWarn
- **validation_feedback** — #problems, #toast
- **target_groups** — #tgs, codes:relabel, i18n:changed
- **disaggregation_rows** — #r04, #r514, #r1549, #r5059, #r60
- **disaggregation_columns** — #cF, #cM, #cO, #cAll, #tally, #tallyVal, #rollU18, #roll18
- **saved_device_list** — #tbl tbody, #emptyMsg, #cnt
- **actions** — #f submit button[form=f], #reset, #expCsv, #expJson, #wipe, #wipeYes dynamic, #wipeNo dynamic
- **version** — #ver
- **generated_status_strips** — #pwabar by pwa.js, #fbbar by fb.js

## Persistence and sync boundary

- Local records: `mhpss-np-4ws-v1`; reporter defaults: `mhpss-np-reporter`; queue: `mhpss-np-queue-v1`.
- Save order is device copy first, then a remote attempt. Device persistence is not delivery.
- The form submit handler does not await or inspect the remote promise; its toast confirms local save/update only.
- Firestore acknowledgement drops the queued `_rid`; during the supervised pilot, appearance in the Hub is the delivery confirmation.
- Hosted register copies strip focal-point contact fields and omit empty/history/archive fields.

## PWA/cache values locked

- Service worker: `sw.js`, scope `./`, `updateViaCache: none`; cache `mhpss-np-field-v39`.
- Precache entries: 30 exact paths (listed in the YAML inventory).
- Manifest start/scope `./`, display `standalone`, orientation `portrait-primary`.

## Locked without an approved Interface Change Request

- field ids, names, control types, value semantics, validation, defaults, schema and exact record keys
- storage/remembering/queue keys and persistence behavior
- record identity, revisions, register filtering, queue, retry, acknowledgement and _rid behavior
- submit handlers and success/error contracts
- service worker, precache, cache version and manifest
- analytics/KPI logic, authentication/authorization, deployed Firebase/GCP state

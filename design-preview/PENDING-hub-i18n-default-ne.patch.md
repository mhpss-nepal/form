# Patch: default the MHPSS Nepal interface to Nepali

**Status:** PENDING — must be applied in the hub repository, not here.
**Applies to:** `hub/assets/i18n.js` (one line)
**Requested by:** Adib, 2026-09-20

## Why this patch exists instead of a direct commit

`hub/assets/i18n.js` is **not under version control in this workspace**.
`/root/mhpss-nepal-work/hub/` contains no `.git`, and the form repository
(`mhpss-nepal/form`) tracks zero `hub/` paths. The authoritative file lives
in the hub repository, which is not cloned on this server.

A one-line change to the default language is an **interface change** with a
visible effect on every field page, so it must not be delivered from a
untracked staging copy. It is written here as a reviewable patch instead.

## The change

```diff
--- a/assets/i18n.js
+++ b/assets/i18n.js
@@ -65,7 +65,19 @@
     return null;
   }
   var KEY = "mhpss-np-lang";
-  var DEFAULT = "en";
+  /* Nepali is the default. This is a national-ministry platform for field
+     teams, and the 5Ws form is almost fully translated, so a first-time
+     reader should land on Nepali rather than English.
+     English remains one tap away and is remembered: ?lang=en, the ENG
+     button, or a browser set to English all still work, and whichever the
+     reader picks is stored under KEY and used from then on.
+     The URL keeps winning, so either language stays shareable and
+     bookmarkable -- which is what lets the Ministry bookmark the Nepali
+     page and a coordination colleague bookmark the English one.
+
+     This does NOT affect the data: codes, ids, names and the exported CSV
+     stay in English regardless of the interface language. */
+  var DEFAULT = "ne";
 
   /* ---------- which language ------------------------------------------
      The URL wins, so a link can be shared in either language and the
```

## Resolution order after the patch (unchanged)

`pick()` already resolves in this order, so the patch only moves the last
fallback and nothing else needs editing:

1. `?lang=ne` / `?lang=en` in the URL — wins, so either language stays
   shareable and bookmarkable
2. `localStorage["mhpss-np-lang"]` — the reader's remembered choice
3. `navigator.language` — a browser set to Nepali still lands on Nepali
4. `DEFAULT` — now `"ne"` instead of `"en"`

## Verified behaviour in the local preview

Measured on this server with the staging copy patched:

| Scenario | Result |
|---|---|
| Fresh reader, no preference, no `?lang` | `ne` |
| `?lang=en` | `en` |
| `?lang=ne` | `ne` |
| Fresh reader on the B2 preview page | `ne` |
| Fresh reader on `index.html` | `ne` |
| Named choice, then plain reload | `ne` (remembered) |

## Why this is safe for the data

The chosen interface language **never reaches the record**. Verified: the
`5ws-report` record and the exported CSV contain **zero Devanagari
characters** with the interface in Nepali, because:

- the record stores **codes**, not labels (`activity:"1.1"`, `site:"NUW-02"`)
- `store.js` builds `activityLabel` / `activityLayer` / `iascReading` from the
  English `.name` field, not from the language-aware `label()`

So a Nepali-reading field worker and an English-reading coordination officer
produce byte-comparable records and exports.

## Translation coverage that justifies the default

Measured on the 5Ws form with the interface in Nepali: **214 of 225**
label / help / heading / option nodes render Devanagari script. The
remainder are organisation proper nouns (CMC-Nepal, CWIN Nepal, KOSHISH,
Nepal Red Cross Society…), which are correctly left untranslated.

## Still to confirm before or during the hub patch

- Whether any other page relying on `DEFAULT === "en"` exists in the hub
  repository. In this workspace, **no hub page loads `i18n.js`**, so the
  blast radius is the eight `form-frontend` pages only.
- Human-reviewed Nepali for copy that is still English, notably the B2
  preview's own device/delivery status strip. That strip already renders a
  visible `English operational text — Nepali translation pending review.`
  flag when the interface is Nepali, so the gap is disclosed rather than
  hidden.

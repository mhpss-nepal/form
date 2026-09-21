#!/usr/bin/env python3
"""Frozen union guard for the post-trial branch reconciliation (t_aafcf25f).

Two unmerged form branches touched the same four files and would silently
revert each other:

    A = design/preview-isolation          (all-forms review page, per-layer default)
    B = task/t_2449fe51-form-default       (engine bumps, ward field, b2 preview)

The live `main` (18d9104) already holds the wanted content of BOTH. This guard
pins that union so a later merge of either stale branch — which is *older* than
main on every shared path — cannot quietly undo it:

  * A's stale gate allowed only ONE page to declare Nepali, and A's copy of
    5ws-report.html predates the ward field; A's render-check expects the
    Layer 1 landing page to be English.
  * B predates the trial-scope landing rule: it would DELETE all-forms.html,
    the preview isolation files and the evidence docs, and STRIP the ward field
    off 5ws-report.html, and it would make the derived b2 page declare Nepali.

Each assertion below is one of those reversions. Breaking any of them must be a
test failure, not a silent regression.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent / "hub"


def page(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def html_tag(name: str) -> str:
    m = re.search(r"<html[^>]*>", page(name))
    if m is None:
        raise AssertionError(f"{name} has no <html> tag")
    return m.group(0)


class ReconciledUnionTest(unittest.TestCase):
    # ---- A's wanted content, which B would delete -------------------------
    def test_the_all_forms_review_page_survives(self) -> None:
        """A added all-forms.html; B predates it and would delete it."""
        self.assertTrue(
            (ROOT / "all-forms.html").is_file(),
            "all-forms.html is missing — a stale merge of branch B would delete it",
        )

    # ---- the per-layer default union (the declared LIST, not one file) ----
    def test_every_layer_one_surface_that_must_open_in_nepali_declares_it(self) -> None:
        """The decision (Adib, 20 Sep): the Layer 1 landing page, the trial form
        and the review listing open in Nepali. A one-file rule (branch A) and a
        no-landing-page rule (branch B) are both wrong here."""
        for name in ("index.html", "5ws-report.html", "all-forms.html"):
            self.assertIn(
                'data-i18n-default="ne"', html_tag(name),
                f"{name} must declare its Nepali default",
            )

    def test_pages_that_stay_english_declare_nothing(self) -> None:
        """The negative half: a not-fully-keyed page must not open in Nepali,
        and the derived b2 preview keeps its own English chrome (branch B tried
        to make it declare Nepali)."""
        for name in ("contact.html", "phq9.html", "referral.html",
                     "selfreport.html", "4ws-report.html", "5ws-report-b2.html"):
            self.assertNotIn(
                "data-i18n-default", page(name),
                f"{name} must not declare a language default",
            )

    # ---- B's wanted content, which the stale gate A would reject ----------
    def test_the_trial_form_still_carries_the_ward_field(self) -> None:
        """B added the optional ward field (NDRRMA publishes impact by ward).
        The current 5ws page must keep it; branch B's own tip predates the
        landing rule and its stale copy must not be merged verbatim."""
        body = page("5ws-report.html")
        self.assertIn('id="wardWrap"', body)
        self.assertIn('id="ward"', body)
        self.assertIn('name="ward"', body)

    def test_the_offline_cache_ships_the_shared_engine_and_the_4ws_stub(self) -> None:
        """The per-layer default and the feedback channel live in the shared
        engine at ../hub/assets/i18n.js. A cache bump only reaches a phone if
        that engine is *precached*; and the distributed 4Ws redirect stub must
        stay precached. (The patch's own CACHE number is deliberately not pinned
        here — it advances whenever a precached file changes, the last time to
        v43 for the hub store.js header correction; what must not regress is
        that the engine is fetched at install, with one consistent cache name.)"""
        sw = page("sw.js")
        self.assertIsNotNone(re.search(r'const\s+CACHE\s*=\s*"[^"]+"', sw),
                             "sw.js has no CACHE constant")
        m = re.search(r"const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;", sw, re.S)
        assert m is not None
        entries = re.findall(r'"([^"]+)"', m.group(1))
        self.assertIn("../hub/assets/i18n.js", entries,
                      "the shared language engine must be precached or a phone "
                      "gets the page with no words on it, offline")
        self.assertIn("4ws-report.html", entries,
                      "the distributed 4Ws redirect must stay precached")

    # ---- the gate itself must be the reconciled one ----------------------
    def test_the_trial_scope_gate_is_the_declared_list_not_a_one_file_rule(self) -> None:
        """Branch A's gate asserted that ONE page may declare a default; that is
        red against the reconciled tree and must not be re-imported."""
        gate = (ROOT / "test_trial_scope.py").read_text(encoding="utf-8")
        self.assertIn("NEPALI_DEFAULT_PAGES", gate,
                      "the gate must check a declared list, not a single filename")
        self.assertNotIn("test_only_the_trial_form_declares_a_language_default",
                         gate,
                         "branch A's weaker one-file gate was re-imported")

    # ---- the fingerprint is measured against the durable sibling ---------
    def test_recorded_precache_fingerprint_matches_the_tree(self) -> None:
        """The fingerprint is a property of the *deployed* sibling layout, where
        form and hub are siblings. Recompute it here so a merge that swaps in a
        fingerprint measured from a different hub copy is caught."""
        import hashlib

        sw = page("sw.js")
        block = re.search(r"const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;", sw, re.S)
        if block is None:
            self.fail("PRECACHE list is missing from sw.js")
            return
        entries = re.findall(r'"([^"]+)"', block.group(1))
        digest = hashlib.sha256()
        for entry in entries:
            if entry == "./":
                asset = ROOT / "index.html"
            elif entry.startswith("../hub/"):
                asset = HUB / entry.removeprefix("../hub/")
            else:
                asset = ROOT / entry
            digest.update(entry.encode("utf-8"))
            digest.update(asset.read_bytes())
        recorded = (ROOT / "tools" / "precache.sha").read_text(encoding="utf-8").strip()
        self.assertEqual(recorded, digest.hexdigest(),
                         "tools/precache.sha is stale for this tree")


if __name__ == "__main__":
    unittest.main()

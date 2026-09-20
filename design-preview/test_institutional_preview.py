#!/usr/bin/env python3
"""Regression guards for the selected 5Ws Institutional Utility preview."""

from __future__ import annotations

import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "9032bb7a3e198882cce8ca1bf350621aba856db7"
PAGE = ROOT / "5ws-report.html"


class FormContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.form_stack: list[str] = []
        self.controls: list[tuple[str, str, str, str, str]] = []
        self.script_sources: list[str] = []
        self.stylesheet_sources: list[str] = []
        self.ids: set[str] = set()
        self.body_classes: set[str] = set()
        self.style_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        element_id = a.get("id") or ""
        if element_id:
            self.ids.add(element_id)
        if tag == "body":
            self.body_classes.update((a.get("class") or "").split())
        if tag == "form":
            self.form_stack.append(a.get("id") or "")
        if tag in {"input", "select", "textarea", "button"}:
            control_type = a.get("type") or (
                "select" if tag == "select" else "textarea" if tag == "textarea" else "button" if tag == "button" else "text"
            )
            owner = (a.get("form") or "") or (self.form_stack[-1] if self.form_stack else "")
            self.controls.append((tag, control_type, a.get("id") or "", a.get("name") or "", owner))
        if tag == "script" and a.get("src"):
            self.script_sources.append(a.get("src") or "")
        if tag == "link" and "stylesheet" in (a.get("rel") or ""):
            self.stylesheet_sources.append(a.get("href") or "")
        if tag == "style" and a.get("id"):
            self.style_ids.add(a.get("id") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self.form_stack:
            self.form_stack.pop()


def parse(text: str) -> FormContractParser:
    parser = FormContractParser()
    parser.feed(text)
    return parser


def at_base(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True
    )


class InstitutionalPreviewContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.current_text = PAGE.read_text(encoding="utf-8")
        cls.current = parse(cls.current_text)
        cls.baseline = parse(at_base("5ws-report.html"))

    def test_selected_direction_shell_exists(self) -> None:
        self.assertIn("institutional-utility", self.current.body_classes)
        self.assertIn("institutional-utility-preview", self.current.style_ids)
        self.assertIn("iuSyncStatus", self.current.ids)
        self.assertIn("iuPreviewNotice", self.current.ids)
        self.assertIn("institutional-utility-status", self.current.ids)
        self.assertIn("InstitutionalPreviewStatus", self.current_text)

    def test_form_controls_are_preserved_exactly(self) -> None:
        """No baseline control may disappear, and only approved additions may appear.

        The baseline is the pre-redesign page. This guards the field contract:
        a form control that vanishes or is renamed breaks the record schema.

        One addition is approved: the optional `ward` select, so a report can
        carry the ward NDRRMA publishes impact against. It is declared here
        rather than by loosening the check, so any *other* added or removed
        control still fails.
        """
        approved_additions = {"ward"}

        missing = {c for c in self.baseline.controls if c not in self.current.controls}
        added = {c for c in self.current.controls if c not in self.baseline.controls}

        self.assertEqual(missing, set(), "a baseline form control disappeared")
        # tuple shape is (tag, type, id, name, owner) -- the identity is the id
        self.assertEqual(
            {c[2] for c in added}, approved_additions,
            f"unapproved control(s) added: {sorted(c[2] for c in added)}",
        )

    def test_runtime_asset_call_sites_are_preserved_exactly(self) -> None:
        self.assertEqual(self.baseline.script_sources, self.current.script_sources)
        self.assertEqual(self.baseline.stylesheet_sources, self.current.stylesheet_sources)

    def test_locked_pwa_files_are_byte_identical_to_base(self) -> None:
        for relative in ("pwa.js",):
            with self.subTest(relative=relative):
                self.assertEqual(at_base(relative), (ROOT / relative).read_text(encoding="utf-8"))

    def test_status_copy_does_not_claim_unproven_delivery(self) -> None:
        preview_copy = self.current_text.split('<style id="institutional-utility-preview"', 1)[-1]
        forbidden = ("nothing is lost", "delivery confirmed", "received by coordination")
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, preview_copy.lower())

    def test_validation_focuses_the_assertive_error_summary(self) -> None:
        self.assertIn('box.focus({ preventScroll: true })', self.current_text)
        self.assertIn('box.classList.add("has-errors")', self.current_text)
        self.assertIn('box.scrollIntoView({ behavior: "auto"', self.current_text)
        self.assertIn('#problems.has-errors', self.current_text)

    def test_target_group_hit_areas_and_disaggregation_names_are_explicit(self) -> None:
        self.assertIn('body.institutional-utility label.chk input', self.current_text)
        for control_id in ("f04", "m04", "o04", "f60", "m60", "o60"):
            with self.subTest(control_id=control_id):
                self.assertRegex(
                    self.current_text,
                    rf'id="{control_id}"[^>]+aria-label="[^"]+"',
                )

    def test_status_copy_is_flagged_when_nepali_is_selected(self) -> None:
        self.assertIn('updateUntranslatedCopy', self.current_text)
        self.assertIn('English operational text — Nepali translation pending review.', self.current_text)

    def test_save_bar_waits_until_form_entry_begins(self) -> None:
        self.assertIn('iu-entry-active', self.current_text)
        self.assertIn('f.addEventListener("focusin", activateEntry)', self.current_text)

    def test_online_status_does_not_imply_delivery(self) -> None:
        self.assertIn('Online · queue empty; delivery not confirmed', self.current_text)

    def test_preview_does_not_trigger_queue_or_sync_actions(self) -> None:
        self.assertNotIn("FB.flush", self.current_text)

    def test_status_observes_existing_storage_warning_without_new_writes(self) -> None:
        status_script = self.current_text.split('<script id="institutional-utility-status">', 1)[1]
        status_script = status_script.split('</script>', 1)[0]
        self.assertNotIn("localStorage", status_script)
        self.assertIn('document.getElementById("storeWarn")', status_script)

    def test_reset_clears_the_error_visual_state(self) -> None:
        self.assertIn('$("problems").classList.remove("has-errors")', self.current_text)

    def test_empty_toast_never_obscures_operational_guidance(self) -> None:
        self.assertIn('body.institutional-utility #toast:empty:not(.show)', self.current_text)
        self.assertIn('display:none', self.current_text)

    def test_keyboard_focus_is_kept_above_the_action_bar(self) -> None:
        self.assertIn('body.institutional-utility:has(#f :focus) .actions', self.current_text)
        self.assertNotIn('body.institutional-utility:has(#f :focus-visible) .actions', self.current_text)
        self.assertIn('body.institutional-utility .actions{', self.current_text)
        self.assertIn('position:static; margin:0 -12px', self.current_text)
        self.assertIn("keepFocusVisible", self.current_text)
        self.assertIn("afterNativeFocusScroll", self.current_text)
        self.assertIn('target.scrollIntoView({ block: "center", behavior: "auto" })', self.current_text)

    def test_nepali_errors_use_existing_translated_field_labels_and_flag_english_detail(self) -> None:
        self.assertIn("problemField", self.current_text)
        self.assertIn("fieldLabel", self.current_text)
        self.assertIn("English validation guidance — Nepali translation pending review.", self.current_text)

    def test_mobile_entry_action_precedes_the_long_guidance(self) -> None:
        start_at = self.current_text.index('class="iu-start"')
        safety_at = self.current_text.index('class="banner stop"')
        self.assertLess(start_at, safety_at)
        self.assertIn('href="#s1"', self.current_text[start_at : start_at + 240])
        self.assertIn('body.institutional-utility #pwabar .x', self.current_text)

    def test_mobile_step_hints_wrap_within_the_viewport(self) -> None:
        self.assertIn('body.institutional-utility .step .hint{', self.current_text)
        self.assertIn('width:auto; max-width:calc(100% - 38px)', self.current_text)
        self.assertIn('white-space:normal', self.current_text)
        self.assertNotIn('width:max-content', self.current_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

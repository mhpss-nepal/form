#!/usr/bin/env python3
"""Contract-preservation guards for the B2 "Institutional App" 5Ws preview.

The B2 page is generated from the committed Direction B page, so it must
inherit every field, runtime hook and reviewed accessibility fix, while its
own presentation shell stays additive.

Run: python3 -m unittest -v design-preview/test_b2_preview.py
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
B2 = REPO / "5ws-report-b2.html"
CORE = REPO / "design-preview" / "5ws-preview-core.js"
CSS = REPO / "design-preview" / "5ws-preview.css"
STATUS = REPO / "design-preview" / "5ws-preview-status.js"
BASE = "9032bb7a3e198882cce8ca1bf350621aba856db7"

# The exact control set the 5Ws record depends on.
REQUIRED_CONTROLS = [
    "org", "orgOther", "orgOtherWrap", "focalName", "focalPhone", "focalEmail",
    "cadre", "cadreOther", "cadreOtherWrap", "partners", "dateAD", "sessionTime",
    "dateBS", "district", "districtOther", "districtOtherWrap", "site", "siteOther",
    "siteOtherWrap", "palika", "palikaWrap", "modality", "modalityOther",
    "modalityOtherWrap", "activity", "activityOther", "activityOtherWrap", "status",
    "description", "reachedTotal", "tgs", "tgOtherWrap",
]
# Count fields the schema and exports read.
COUNT_IDS = [
    "f04", "m04", "o04", "f514", "m514", "o514", "f1549", "m1549", "o1549",
    "f5059", "m5059", "o5059", "f60", "m60", "o60",
]
OF_WHOM_IDS = ["ofChildAlone", "ofPreg", "ofPwd", "ofInjured", "ofDistress"]
LOCKED_PWA = ["pwa.js", "sw.js", "manifest.webmanifest"]


def git_show(path: str, ref: str = BASE) -> str:
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=REPO,
        capture_output=True, text=True, check=True,
    ).stdout


class B2PreviewContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b2 = B2.read_text(encoding="utf-8")
        cls.core = CORE.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        # The B2 page must embed the form exactly as the committed page has it.
        src = git_show("5ws-report.html", cls.head)
        m = re.search(r'<form id="f"[\s\S]*?</form>', src)
        cls.form_expected = m.group(0)
        m2 = re.search(r'<form id="f"[\s\S]*?</form>', cls.b2)
        cls.form_actual = m2.group(0) if m2 else ""

    # ---------------------------------------------------------------- structure
    def test_form_is_byte_identical_to_committed_page(self) -> None:
        """The whole <form> block is copied verbatim, so no field can drift."""
        self.assertEqual(
            hashlib.sha256(self.form_expected.encode()).hexdigest(),
            hashlib.sha256(self.form_actual.encode()).hexdigest(),
            "the B2 <form> block differs from the committed Direction B page",
        )

    def test_every_required_control_is_present_once(self) -> None:
        for cid in REQUIRED_CONTROLS + COUNT_IDS + OF_WHOM_IDS:
            n = len(re.findall(rf'\bid="{re.escape(cid)}"', self.b2))
            self.assertEqual(n, 1, f"{cid} appears {n} times, expected exactly 1")

    def test_name_attributes_are_unchanged(self) -> None:
        """name= is what a future backend reads; it must survive the re-skin."""
        for cid in REQUIRED_CONTROLS + COUNT_IDS + OF_WHOM_IDS:
            in_src = re.search(rf'id="{re.escape(cid)}"[^>]*\bname="([^"]*)"', self.form_expected)
            in_b2 = re.search(rf'id="{re.escape(cid)}"[^>]*\bname="([^"]*)"', self.form_actual)
            src_name = in_src.group(1) if in_src else None
            b2_name = in_b2.group(1) if in_b2 else None
            self.assertEqual(src_name, b2_name, f"name= drifted for {cid}")

    def test_no_duplicate_ids_anywhere(self) -> None:
        ids = re.findall(r'\bid="([^"]+)"', self.b2)
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        self.assertEqual(dupes, [], f"duplicate ids introduced: {dupes}")

    def test_clone_helper_strips_identity_if_used(self) -> None:
        """If a clone is ever built, it must not carry id/name/for."""
        if "cloneNode" in self.core:
            self.assertIn("removeAttribute", self.core)

    # -------------------------------------------------------- runtime integrity
    def test_runtime_scripts_are_unchanged(self) -> None:
        for asset in ("codes.js", "store.js", "fb-config.js", "fb.js", "mark.js",
                      "icons.js", "i18n-strings.js", "i18n.js", "pwa.js"):
            self.assertIn(asset, self.b2, f"{asset} missing from the B2 page")

    def test_locked_pwa_files_are_byte_identical_to_base(self) -> None:
        for f in LOCKED_PWA:
            self.assertEqual(
                hashlib.sha256(git_show(f).encode()).hexdigest(),
                hashlib.sha256((REPO / f).read_bytes()).hexdigest(),
                f"{f} changed; the service worker, precache and manifest are locked",
            )

    @staticmethod
    def _code_only(js: str) -> str:
        """Strip comments and string literals so the check reads executable code."""
        no_block = re.sub(r"/\*[\s\S]*?\*/", " ", js)
        no_line = re.sub(r"(?m)^\s*//.*$", " ", no_block)
        no_str = re.sub(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", '""', no_line)
        return no_str

    def test_preview_never_touches_storage_queue_or_sync(self) -> None:
        """A preview may describe these, but must never call them."""
        for src, label in ((self.core, "core"), (self.status, "status")):
            code = self._code_only(src)
            for forbidden in ("localStorage", "sessionStorage", "indexedDB",
                              "FB.submit", "FB.flush", "STORE.save", "STORE.clearAll",
                              "serviceWorker.register", "caches.open",
                              "addDoc", "setDoc", "updateDoc"):
                self.assertNotIn(forbidden, code,
                                 f"preview {label} must not call {forbidden}")

    def test_save_button_is_the_pages_own_control(self) -> None:
        """The real Save/Clear row is moved into the last screen, not replaced.

        Nothing synthetic was added, so the existing submit handler and its
        success/error contract are the only code that can run on save.
        """
        self.assertIn("iu-real-actions", self.core)
        self.assertIn('.actions', self.core)
        # The original row still exists in the page and keeps its handler hook.
        self.assertIn('class="actions"', self.b2)
        self.assertIn('type="submit"', self.b2)
        self.assertIn('id="reset"', self.b2)

    def test_enhancements_write_through_real_events(self) -> None:
        """Chips, dates and steppers must drive the real controls."""
        self.assertIn("new Event(type, { bubbles: true })", self.core)
        self.assertIn('fire(node, type || "input")', self.core)
        self.assertIn('fire(node, "change")', self.core)

    # ------------------------------------------------------------ inherited a11y
    def test_error_summary_keeps_its_reviewed_accessibility(self) -> None:
        m = re.search(r'<div id="problems"[^>]*>', self.b2)
        self.assertIsNotNone(m)
        tag = m.group(0)
        self.assertIn('role="alert"', tag)
        self.assertIn('aria-live="assertive"', tag)
        self.assertIn('tabindex="-1"', tag)

    def test_clear_removes_the_error_visual_state(self) -> None:
        self.assertIn('classList.remove("has-errors")', self.b2)

    def test_nepali_validation_flagging_is_preserved(self) -> None:
        self.assertIn("English validation guidance", self.b2)

    # ------------------------------------------------------------ presentation
    def test_preview_assets_are_content_stamped(self) -> None:
        """A stale preview asset must be impossible to serve."""
        for name in ("5ws-preview.css", "5ws-preview-core.js", "5ws-preview-status.js"):
            h = hashlib.sha256((REPO / "design-preview" / name).read_bytes()).hexdigest()[:10]
            self.assertIn(f"{name}?h={h}", self.b2,
                          f"{name} is not stamped with its current content hash")

    def test_direction_b_page_html_is_not_modified(self) -> None:
        """Direction B and the production page stay as committed."""
        for f in ("5ws-report.html",):
            self.assertEqual(
                subprocess.run(["git", "status", "--porcelain", "--", f], cwd=REPO,
                               capture_output=True, text=True).stdout.strip(),
                "", f"{f} has uncommitted changes",
            )

    def test_year_jump_reaches_the_deep_years(self) -> None:
        self.assertIn("YEAR_MIN = 1940", self.core)
        self.assertIn("Jump to year", self.core)

    def test_typed_date_entry_is_not_reintroduced(self) -> None:
        """The team rejected typed dates; the native control is the mechanism."""
        self.assertNotIn("iu-date-typed", self.core)
        self.assertNotIn("dl-date-typed", self.css)

    def test_bikram_sambat_is_not_auto_converted(self) -> None:
        self.assertIn('isBS', self.core)
        self.assertNotIn("bsToAd", self.core)
        self.assertNotIn("adToBs", self.core)

    def test_no_misleading_delivery_wording(self) -> None:
        text = (self.status + self.css).lower()
        for bad in ("nothing is lost", "your report was sent",
                    "successfully submitted", "delivered to the hub"):
            self.assertNotIn(bad, text)
        self.assertIn("delivery not confirmed", self.status)

    def test_chips_carry_radio_semantics(self) -> None:
        self.assertIn('setAttribute("role", "radiogroup")', self.core)
        self.assertIn('setAttribute("role", "radio")', self.core)
        self.assertIn("aria-checked", self.core)

    def test_picker_exposes_listbox_semantics(self) -> None:
        self.assertIn('"aria-haspopup", "listbox"', self.core)
        self.assertIn('setAttribute("role", "listbox")', self.core)

    def test_touch_and_overflow_guards_are_declared(self) -> None:
        self.assertIn("min-height: 48px", self.css)
        self.assertIn("overflow-x: auto", self.css)
        self.assertIn("prefers-reduced-motion", self.css)

    def test_repo_text_setting_rule_is_respected(self) -> None:
        self.assertNotIn("overflow-wrap: anywhere", self.css)
        self.assertNotIn("overflow-wrap:anywhere", self.css)

    # -------------------------------------------------------- build & language
    def test_language_slot_is_a_toggle_slot_not_a_reserved_id(self) -> None:
        """i18n.js skips mounting the ENG/NEP switch when id="i18nbar" exists.

        Giving the slot that id therefore removed the language switch entirely
        from the page. The slot must be [data-i18n-toggle].
        """
        import re as _re
        self.assertRegex(self.b2, r'<[a-zA-Z][^>]*\bdata-i18n-toggle\b')
        self.assertIsNone(
            _re.search(r'<[a-zA-Z][^>]*\bid="i18nbar"', self.b2),
            "the language slot must not own id=i18nbar",
        )

    def test_build_script_reproduces_the_committed_page(self) -> None:
        """The page is generated, so a rebuild must be deterministic."""
        before = self.b2
        subprocess.run([sys.executable, "design-preview/build_b2.py"], cwd=REPO,
                       capture_output=True, text=True, check=True)
        after = (REPO / "5ws-report-b2.html").read_text(encoding="utf-8")
        self.assertEqual(before, after, "rebuilding the page produced a different file")

    def test_build_script_guards_the_form_block(self) -> None:
        src = (REPO / "design-preview" / "build_b2.py").read_text(encoding="utf-8")
        self.assertIn("is not byte-identical", src)
        self.assertIn("duplicate ids", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)

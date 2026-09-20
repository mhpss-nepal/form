#!/usr/bin/env python3
"""Failing-first contracts for review-form isolation from Layer 2."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREVIEW_COLLECTION = "submissions_preview"
LIVE_COLLECTION = "submissions"
WRITING_FORMS = (
    "5ws-report.html",
    "contact.html",
    "phq9.html",
    "referral.html",
    "selfreport.html",
)
REVIEW_TARGETS = WRITING_FORMS + ("4ws-report.html", "5ws-report-b2.html")


class ReviewIndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


class PreviewIsolationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Read as text so a MISSING file is a test FAILURE with a readable
        # message, rather than a collection error. That distinction matters
        # for the failing-first record: before this task, preview-mode.js
        # did not exist at all, and the run must show the contract failing
        # rather than the run being unrunnable.
        def read(name):
            path = ROOT / name
            if not path.exists():
                return "<MISSING FILE: %s>" % name
            return path.read_text(encoding="utf-8")

        cls.preview = read("preview-mode.js")
        cls.shell = read("preview-shell.js")
        cls.page = read("preview.html")
        cls.index = read("design-preview/translation-review-index.html")
        cls.sw = read("sw.js")
        cls.landing = read("index.html")

    def test_preview_runtime_sets_collection_before_shared_bridge(self) -> None:
        self.assertIn(f'var PREVIEW_COLLECTION = "{PREVIEW_COLLECTION}"', self.preview)
        self.assertIn("window.FB_COLLECTION = PREVIEW_COLLECTION", self.preview)
        self.assertNotIn(f'window.FB_COLLECTION = "{LIVE_COLLECTION}"', self.preview)
        # The shell must re-pin the constant immediately before a page's own
        # fb.js executes, because fb-config.js resets it to "submissions".
        self.assertIn("COLLECTION_BRIDGE", self.shell)
        self.assertIn("window.FB_COLLECTION = PREVIEW_COLLECTION", self.shell)

    def test_preview_runtime_pins_the_bridge_only_for_the_collection(self) -> None:
        shell = self.shell
        # pwa.js must not run in a review frame; fb.js and fb-config.js MUST,
        # because re-pointing the real bridge is the mechanism.
        self.assertIn('BLOCKED_SCRIPTS = ["pwa.js"]', shell)
        for blocked in ("fb.js", "fb-config.js"):
            self.assertNotIn(f'BLOCKED_SCRIPTS = ["pwa.js", "{blocked}"]', shell)
        self.assertIn('COLLECTION_BRIDGE = "fb.js"', shell)

    def test_review_shell_names_a_writing_page_it_can_open(self) -> None:
        for name in ("5ws-report.html", "contact.html", "phq9.html", "referral.html", "selfreport.html"):
            self.assertIn(f'"{name}"', self.shell)
        self.assertIn("preview_form", self.shell)
        # The one page a reviewer opens must load the runtime that pins the
        # collection, and must load it BEFORE the shell that injects fb.js.
        # Matched as TAGS, not bare names: preview.html mentions both files in
        # its comments, which would defeat a plain substring search.
        mode_tag = '<script src="preview-mode.js">'
        shell_tag = '<script src="preview-shell.js">'
        self.assertIn(mode_tag, self.page)
        self.assertIn(shell_tag, self.page)
        self.assertLess(self.page.index(mode_tag), self.page.index(shell_tag))

    def test_review_routes_only_through_the_preview_shell(self) -> None:
        """Every review link must go through preview.html.

        The bare page files remain on the host and would write to the live
        register if opened directly, so a review index that links them
        directly is the leak this task exists to close.
        """
        parser = ReviewIndexParser()
        parser.feed(self.index)
        preview = {href for href in parser.links if "preview_form=" in href}
        expected = {f"../preview.html?preview_form={name}" for name in REVIEW_TARGETS}
        self.assertEqual(preview, expected)
        for href in parser.links:
            if not href.endswith(".html") and "preview_form=" not in href:
                continue
            self.assertNotRegex(
                href,
                r"^\.\./(form-frontend|preview)\.\./|^\.\./form-frontend/[a-z0-9\-]+\.html",
                "a review link bypasses preview.html",
            )

    def test_preview_runtime_has_visible_bilingual_non_real_data_banner(self) -> None:
        for phrase in (
            "DEMO / REVIEW",
            "not real data",
            "not counted anywhere",
            "डेमो / समीक्षा",
            "वास्तविक डेटा होइन",
            "कुनै गणनामा समावेश हुँदैन",
        ):
            self.assertIn(phrase, self.preview)
        self.assertIn('"preview-mode-banner"', self.preview)
        self.assertIn('"role", "status"', self.preview)

    def test_preview_runtime_refuses_publication_and_live_collection(self) -> None:
        self.assertIn('LIVE_COLLECTIONS = ["submissions", "public_stats"]', self.preview)
        self.assertIn("window.FB.publish", self.preview)
        self.assertIn("Promise.reject", self.preview)
        self.assertIn("preview mode cannot publish", self.preview)

    def test_preview_submit_cannot_be_counted_by_default_hub_collection(self) -> None:
        self.assertEqual(PREVIEW_COLLECTION, "submissions_preview")
        self.assertNotEqual(PREVIEW_COLLECTION, LIVE_COLLECTION)
        self.assertIn("The Hub does not read preview records by default", self.index)
        self.assertIn("public_stats", self.index)

    def test_preview_pages_are_not_field_exposed_or_precached(self) -> None:
        for forbidden in ("preview.html", "preview-mode.js", "translation-review-index.html"):
            self.assertNotIn(forbidden, self.landing)
            self.assertNotIn(f'"{forbidden}"', self.sw)
        for page in ("contact.html", "phq9.html", "referral.html", "selfreport.html"):
            self.assertNotIn(f'"{page}"', self.sw)

    def test_field_landing_still_exposes_only_5ws(self) -> None:
        hrefs = re.findall(r'href="([^"]+\.html)"', self.landing)
        self.assertEqual(sorted(hrefs), ["5ws-report.html", "cards.html"])
        self.assertEqual(hrefs.count("5ws-report.html"), 1)
        for page in ("contact.html", "phq9.html", "referral.html", "selfreport.html"):
            self.assertNotIn(page, self.landing)
        self.assertIn('"4ws-report.html"', self.sw)


if __name__ == "__main__":
    unittest.main(verbosity=2)

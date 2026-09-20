#!/usr/bin/env python3
"""Failing-first contract tests for the 5Ws-only field trial build."""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE = "8c84f43c4d0829266e86f4be0ba9bac96b1fdb22"
FORMS = ("contact.html", "phq9.html", "referral.html", "selfreport.html")
UNAPPROVED_PAGES = (*FORMS, "4ws-report.html")
TRIAL_QR_KEYS = ("master", "5ws")


class LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.form_links: list[str] = []
        self.form_urls: list[str] = []
        self.qr_keys: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        href = values.get("href")
        data_url = values.get("data-url")
        data_qr = values.get("data-qr")
        if href in ("5ws-report.html", *UNAPPROVED_PAGES):
            self.form_links.append(href)
        if data_url:
            self.form_urls.append(data_url)
        if data_qr:
            self.qr_keys.append(data_qr)


class TrialScopeContractTest(unittest.TestCase):
    def test_form_pages_and_unrelated_pwa_runtime_keep_byte_parity(self) -> None:
        for relative in ("5ws-report.html", *UNAPPROVED_PAGES, "pwa.js"):
            baseline = subprocess.run(
                ["git", "show", f"{BASE}:{relative}"],
                cwd=ROOT,
                capture_output=True,
                check=True,
            ).stdout
            self.assertEqual(
                (ROOT / relative).read_bytes(),
                baseline,
                f"{relative} changed even though this task does not edit form content or pwa.js",
            )

    def test_landing_exposes_exactly_one_form_and_no_unapproved_entrypoint(self) -> None:
        parser = LandingParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

        self.assertEqual(parser.form_links, ["5ws-report.html"])
        self.assertEqual(parser.form_urls, ["./", "5ws-report.html"])
        self.assertEqual(parser.qr_keys, ["5ws"])
        landing = (ROOT / "index.html").read_text(encoding="utf-8")
        for page in FORMS:
            self.assertNotIn(page, landing)

    def test_printable_card_sheet_emits_only_the_5ws_code(self) -> None:
        cards = (ROOT / "cards.html").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'data-qr="([a-z0-9]+)"', cards), ["5ws"])
        self.assertEqual(re.findall(r'data-qu="([a-z0-9]+)"', cards), ["5ws"])
        self.assertNotIn("All five forms", cards)
        for page in FORMS:
            self.assertNotIn(page, cards)

    def test_service_worker_and_manifest_do_not_advertise_unapproved_pages(self) -> None:
        sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        for page in UNAPPROVED_PAGES:
            self.assertNotIn(f'"{page}"', sw)

        manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["shortcuts"], [
            {"name": "Activity report (5Ws)", "url": "5ws-report.html"},
        ])
        for shortcut in manifest["shortcuts"]:
            self.assertNotIn(shortcut["url"], UNAPPROVED_PAGES)

    def test_qr_generator_and_card_check_are_trial_scoped(self) -> None:
        builder = (ROOT / "tools" / "qr-build.py").read_text(encoding="utf-8")
        targets = re.search(r"TARGETS\s*=\s*\[(.*?)\]", builder, re.DOTALL)
        if targets is None:
            self.fail("TARGETS list is missing from tools/qr-build.py")
        self.assertEqual(
            re.findall(r'\("([a-z0-9]+)"\s*,\s*"(/form/[^\"]*)"\)', targets.group(1)),
            [("master", "/form/"), ("5ws", "/form/5ws-report.html")],
        )
        checker = (ROOT / "tools" / "qr-check.py").read_text(encoding="utf-8")
        self.assertIn('ALLOWED_CARD_KEYS = {"5ws"}', checker)
        qr_asset = (ROOT / "qr-trial.js").read_text(encoding="utf-8")
        self.assertEqual(
            tuple(re.findall(r'^"([a-z0-9]+)":\{', qr_asset, re.MULTILINE)),
            TRIAL_QR_KEYS,
        )
        self.assertNotIn("../hub/assets/qr.js", (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("../hub/assets/qr.js", (ROOT / "cards.html").read_text(encoding="utf-8"))
        for page in UNAPPROVED_PAGES:
            self.assertNotIn(page, builder)
            self.assertNotIn(page, qr_asset)


if __name__ == "__main__":
    unittest.main(verbosity=2)

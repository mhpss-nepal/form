#!/usr/bin/env python3
"""Failing-first contract tests for the 5Ws-only field trial build."""
from __future__ import annotations

import json
import importlib.util
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent / "hub"
BASE = "8c84f43c4d0829266e86f4be0ba9bac96b1fdb22"
FORMS = ("contact.html", "phq9.html", "referral.html", "selfreport.html")
UNAPPROVED_PAGES = (*FORMS, "4ws-report.html")



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
        self.assertNotIn("../hub/forms.html", landing)
        for page in FORMS:
            self.assertNotIn(page, landing)

    def test_trial_landing_does_not_route_through_hub_form_advertising(self) -> None:
        landing = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("../hub/forms.html", landing)
        hub_forms = HUB / "forms.html"
        if hub_forms.is_file():
            advertised = hub_forms.read_text(encoding="utf-8")
            self.assertTrue(any(page in advertised for page in FORMS))

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
        entries = re.findall(
            r'^"([a-z0-9]+)":\{\s*"n":\d+,\s*"url":"([^"]+)"',
            qr_asset,
            re.MULTILINE,
        )
        self.assertEqual(entries, [
            ("master", "https://mhpss-nepal.github.io/form/"),
            ("5ws", "https://mhpss-nepal.github.io/form/5ws-report.html"),
        ])
        self.assertNotIn("../hub/assets/qr.js", (ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("../hub/assets/qr.js", (ROOT / "cards.html").read_text(encoding="utf-8"))
        for page in UNAPPROVED_PAGES:
            self.assertNotIn(page, builder)
            self.assertNotIn(page, qr_asset)

    def test_qr_checker_rejects_any_extra_asset_entry(self) -> None:
        checker_path = ROOT / "tools" / "qr-check.py"
        spec = importlib.util.spec_from_file_location("trial_qr_check", checker_path)
        if spec is None or spec.loader is None:
            self.fail("cannot load tools/qr-check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)

        original = (ROOT / "qr-trial.js").read_text(encoding="utf-8")
        five_ws = original.split('"5ws":{', 1)[1].split("\n}", 1)[0]
        extra = '"contact":{' + five_ws
        mutated = original.replace("\n};\nwindow.QR._base", "\n},\n" + extra + "\n};\nwindow.QR._base")
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as asset:
            asset.write(mutated)
            asset.flush()
            setattr(checker, "QRJS", asset.name)
            self.assertEqual(checker.main(["qr-check.py"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

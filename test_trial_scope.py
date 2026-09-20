#!/usr/bin/env python3
"""Failing-first contract tests for the 5Ws-only field trial build."""
from __future__ import annotations

import json
import importlib.util
import contextlib
import io
import re
import subprocess
import tempfile
import unittest
import warnings
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent / "hub"
# The committed base of this trial build. Unapproved pages and pwa.js must not
# drift from it at all. (The original pin pointed at an earlier commit that this
# branch has since moved past: the optional `ward` field and the phq9 wording
# fix landed on the pages, so that earlier pin was red for reasons unrelated to
# any trial-scope change -- see the task evidence note.)
BASE = "36d33800fd55cc999e94bc0d81deeba71299972b"
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
    # The one change this task makes to a field-form page: declare the page's
    # own language default. It is a single attribute on <html>, so the byte pin
    # below is narrowed by exactly that substitution and nothing else --
    # 5ws-report.html still has to be byte-identical to its base apart from
    # this, and the four unapproved pages and pwa.js stay untouched.
    DEFAULT_SUB = ('<html lang="en">', '<html lang="en" data-i18n-default="ne">')

    def test_form_pages_and_unrelated_pwa_runtime_keep_byte_parity(self) -> None:
        base_html = subprocess.run(
            ["git", "show", f"{BASE}:5ws-report.html"],
            cwd=ROOT, capture_output=True, check=True,
        ).stdout.decode("utf-8")
        allowed = base_html.replace(*self.DEFAULT_SUB)
        self.assertNotEqual(allowed, base_html,
                            "the authorized default declaration did not apply")
        self.assertEqual((ROOT / "5ws-report.html").read_text(encoding="utf-8"),
                         allowed,
                         "5ws-report.html changed beyond declaring its language default")

        for relative in (*UNAPPROVED_PAGES, "pwa.js"):
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

    # Pages that open in Nepali, and the ONLY ones allowed to. This is the
    # per-layer decision applied to Layer 1: Nepali for the field surface a
    # Nepali-speaking officer reads, English everywhere the coordination
    # team works. It is a declared LIST rather than a rule about one file,
    # because the decision is about which pages a reader stands in front of,
    # not about a particular filename.
    #
    #   index.html       the Layer 1 landing page a field officer opens first
    #   5ws-report.html  the trial activity report
    #   all-forms.html   the review listing, whose reader is the reviewer
    #
    # Everything else declares nothing and therefore opens in English. That
    # includes contact, referral, phq9, selfreport and the b2 preview: a page
    # that is not fully keyed must not open in Nepali, and 5ws-report-b2 is a
    # derived demonstration surface.
    NEPALI_DEFAULT_PAGES = ("index.html", "5ws-report.html", "all-forms.html")

    def test_only_the_declared_pages_open_in_nepali(self) -> None:
        """Adib's per-layer decision, machine-checked against the real pages.

        Nepali is for the Layer 1 field surface, English for the coordination
        team. The declaration is what decides, so the check is: every declared
        page is on the list, every listed page declares, and no other page
        declares anything.

        A source-text check alone is not proof the page OPENS in Nepali -- the
        engine decides that at runtime. tools/per-layer-default-render-check.py
        drives a real browser for that half.
        """
        pages = sorted(ROOT.glob("*.html"))
        self.assertTrue(pages, "no HTML pages found; the check would be vacuous")

        for page in pages:
            declares = 'data-i18n-default' in page.read_text(encoding="utf-8")
            if page.name in self.NEPALI_DEFAULT_PAGES:
                self.assertTrue(
                    declares,
                    f"{page.name} must declare its Nepali default, or a field "
                    f"officer opens it in English",
                )
            else:
                self.assertFalse(
                    declares,
                    f"{page.name} declares a language default but is not on the "
                    f"Nepali list; a page that is not fully keyed must not open "
                    f"in Nepali",
                )

        # The list is worthless if it names a page that does not exist.
        present = {page.name for page in pages}
        for name in self.NEPALI_DEFAULT_PAGES:
            self.assertIn(name, present, f"the Nepali list names a missing page: {name}")

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
        self.assertNotIn("forms.html", landing)
        # The trial landing page must not embed the Hub's form catalogue, which
        # advertises the unapproved pages, and must not describe the card sheet
        # as carrying every form.
        self.assertNotIn("ml.p031", landing)
        self.assertNotIn("ml.p077", landing)
        self.assertNotIn("ml.p079", landing)

    def test_printable_card_sheet_emits_only_the_5ws_code(self) -> None:
        cards = (ROOT / "cards.html").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'data-qr="([a-z0-9]+)"', cards), ["5ws"])
        self.assertEqual(re.findall(r'data-qu="([a-z0-9]+)"', cards), ["5ws"])
        self.assertNotIn("All five forms", cards)
        for page in FORMS:
            self.assertNotIn(page, cards)

    def test_service_worker_and_manifest_do_not_advertise_unapproved_pages(self) -> None:
        sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        for page in FORMS:
            self.assertNotIn(f'"{page}"', sw)

        # 4ws-report.html is a content-free redirect kept for already-printed
        # cards. It must be cached for offline resolution but not advertised
        # by any landing, manifest, card, or generated QR entrypoint.
        self.assertIn('"4ws-report.html"', sw)

        manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["shortcuts"], [
            {"name": "Activity report (5Ws)", "url": "5ws-report.html"},
        ])
        for shortcut in manifest["shortcuts"]:
            self.assertNotIn(shortcut["url"], UNAPPROVED_PAGES)

    def test_precache_fingerprint_matches_current_form_and_hub_assets(self) -> None:
        import hashlib

        sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        match = re.search(r"const\s+PRECACHE\s*=\s*\[(.*?)\]\s*;", sw, re.DOTALL)
        if match is None:
            self.fail("PRECACHE list is missing from sw.js")
        entries = re.findall(r'"([^"]+)"', match.group(1))
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
        self.assertEqual(recorded, digest.hexdigest())

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
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                with contextlib.redirect_stdout(io.StringIO()):
                    rejected = checker.main(["qr-check.py"])
            self.assertEqual(rejected, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

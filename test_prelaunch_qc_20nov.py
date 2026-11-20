import os
"""Pre-launch QC of 20 Nov 2026: each fixed problem is locked here so it cannot come back.
Static checks only; they run anywhere (no network, no browser, no server paths)."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


class LegacyWriterClosed(unittest.TestCase):
    """PHQ-9 and Self-report wrote straight into the old database (rules v3 let anyone create and
    overwrite). Rules v5 close that path; the pages say so and keep phone drafts downloadable."""
    def test_legacy_pages_load_no_writer(self):
        for page in ("phq9.html", "selfreport.html"):
            s = read(page)
            for banned in ("fb.js", "fb-config.js", "l1.js", "firestore"):
                self.assertNotIn(banned, s, page + " must not load " + banned)
            self.assertIn('href="index.html"', s)
            self.assertIn("noindex", s)
            self.assertIn("Download saved answers", s)

    def test_legacy_pages_never_delete_phone_drafts(self):
        for page in ("phq9.html", "selfreport.html"):
            self.assertNotIn("removeItem", read(page))


class SenderBehaviour(unittest.TestCase):
    def setUp(self):
        self.s = read("lib/form-send.js")

    def test_organisation_comes_from_the_access_card(self):
        self.assertIn("window.FORM_SEND_ORG", self.s)
        g = read("preview/grief-early-assessment.html")
        self.assertNotRegex(g, r'\$\("#org"\)\.value="CMC"[;}]')
        self.assertEqual(g.count("FORM_SEND_ORG()"), 3)

    def test_a_refused_record_does_not_hold_back_the_queue(self):
        body = self.s[self.s.index("async function sendAll"):]
        body = body[:body.index("finally")]
        self.assertIn("if (e.permanent)", body)
        self.assertIn("continue;", body)

    def test_name_and_phone_leave_the_phone_after_the_receipt(self):
        self.assertIn("CFG.sent(r)", self.s)
        g = read("preview/grief-early-assessment.html")
        m = re.search(r"sent:function\(r\)\{.*?write\(l\)\}", g, re.S)
        self.assertTrue(m)
        kept = re.search(r"l\[i\]=\{(.*?)\}", m.group(0)).group(1)
        for field in ("name:", "phone:", "bestTime:", "reach:", "initials:"):
            self.assertNotIn(field, kept)
        self.assertIn("&&!r._sent", g)

    def test_new_version_reloads_when_nothing_typed(self):
        for p in ("lib/form-send.js", "pwa.js"):
            s = read(p)
            self.assertIn("controllerchange", s)
            self.assertRegex(s, r"typed\) return;|\|\| typed\) return;")

    def test_sender_parses(self):
        for p in ("lib/form-send.js", "pwa.js", "lib/store.js"):
            subprocess.check_call(["node", "-e", "new Function(require('fs').readFileSync(%r,'utf8'))" % str(ROOT / p)])


class CsvFormulaGuard(unittest.TestCase):
    def test_form_exports_neutralise_formulas(self):
        for p in ("preview/grief-early-assessment.html", "preview/referral-directory.html"):
            self.assertIn("""replace(/^([=+\\-@\\t\\r])/,"'$1")""", read(p), p)
        self.assertIn("/^[=+@\\-\\t\\r]/.test(s)", read("lib/store.js"))


class FiveWsStatusIsTruthful(unittest.TestCase):
    def test_no_false_device_only_or_preview_banner(self):
        s = read("5ws-report.html")
        for phrase in ("Institutional Utility design preview", "Reconnection does not deliver",
                       "automatic delivery unavailable", "immutable pending revisions"):
            self.assertNotIn(phrase, s)
        self.assertIn("Saved on this phone first", s)



class MonitoringNotReview20Nov(unittest.TestCase):
    def test_referral_destination_required_when_referred(self):
        s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview", "grief-early-assessment.html"), encoding="utf-8").read()
        self.assertIn('multi("refTo").length>0&&!!radio("refAccepted")', s)

    def test_status_received_not_waiting_for_review(self):
        s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "form-send.js"), encoding="utf-8").read()
        self.assertIn('pending: ["send.st.pending", "Received"', s)
        self.assertNotIn('"Waiting for review"', s)


class GriefConversation03(unittest.TestCase):
    def setUp(self):
        self.s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview", "grief-early-assessment.html"), encoding="utf-8").read()
    def test_name_and_schema(self):
        self.assertIn('<h1 data-i18n="grief.003">Grief Conversation</h1>', self.s)
        self.assertIn('schema:"np-grief-early-0.3"', self.s)
        self.assertIn('r.schema==="np-grief-early-0.2"||r.schema==="np-grief-early-0.3"', self.s)
    def test_state_now_required_and_phq9_optional_uses_validated_nepali(self):
        self.assertIn('7:radio("stateNow")&&', self.s)
        self.assertIn('NE["phq9.item"+i]', self.s)
        self.assertIn('NE["phq9.scale"+v]', self.s)
        self.assertIn('(radio("selfharm")==="yes"||p9)&&radio("triage")!=="redflag"', self.s)

if __name__ == "__main__":
    unittest.main()

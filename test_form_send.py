"""The grief and referral directory forms send to the Cloud Run receivers (19 Nov 2026).
Locks: the exact routes and protocols the backend contracts accept, the non-preview schemas,
coded option values (so a Nepali page never stores Nepali text), sign-in through the 5Ws auth,
and "sent" only after the server's receipt."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRIEF = (ROOT / "preview" / "grief-early-assessment.html").read_text(encoding="utf-8")
DIRF = (ROOT / "preview" / "referral-directory.html").read_text(encoding="utf-8")
SEND = (ROOT / "lib" / "form-send.js").read_text(encoding="utf-8")


class FormSend(unittest.TestCase):
    def test_pages_wire_the_sender_after_auth(self):
        for page, route, proto in [(GRIEF, "/grief/intake", "grief-submit/1"),
                                   (DIRF, "/directory/servicepoints2/intake", "directory-submit/2")]:
            auth = page.index("review-current-v51/current-auth.js")
            api = page.index("hub/assets/access-api.js")
            cfg = page.index("window.FORM_SEND=")
            self.assertLess(auth, api); self.assertLess(api, cfg)
            lib = page.index("../lib/form-send.js")
            self.assertLess(auth, cfg); self.assertLess(cfg, lib)
            self.assertIn('route:"%s"' % route, page)
            self.assertIn('protocol:"%s"' % proto, page)
            self.assertIn("FORM_SEND_AFTER_SAVE", page)

    def test_schemas_are_the_released_ones(self):
        # 20 Nov 2026: Grief Conversation 0.3 (state now, optional Nepal PHQ-9); 0.2 records already queued still send
        self.assertIn('schema:"np-grief-early-0.3"', GRIEF)
        self.assertIn('r.schema==="np-grief-early-0.2"||r.schema==="np-grief-early-0.3"', GRIEF)
        self.assertIn('r.schema="np-directory-0.2"', DIRF)
        self.assertNotIn("-preview\"", GRIEF + DIRF)

    def test_options_carry_codes(self):
        for code in ["HOME", "GROUP", "IND", "HF", "HC", "OTH"]:
            self.assertRegex(GRIEF, r'<option value="%s" data-i18n="grief\.\d+"' % code)
        for code in ["FREE", "SOME", "FEE"]:
            self.assertRegex(DIRF, r'<option value="%s" data-i18n="dirf\.\d+"' % code)
        # no translatable <option> left without a value attribute
        for page in (GRIEF, DIRF):
            self.assertEqual(re.findall(r"<option data-i18n=", page), [])

    def test_sent_only_after_receipt(self):
        self.assertIn("body.stored !== true", SEND)
        self.assertIn("body.reportId !== r.id", SEND)
        self.assertIn("body.revision !== rev", SEND)
        self.assertIn("request_sha256", SEND)
        self.assertIn('"X-Selected-Org"', SEND)
        self.assertIn("var BASE = A.BASE", SEND)
        api = ROOT.parent / "hub" / "assets" / "access-api.js"
        if api.exists():
            self.assertIn("https://mhpss5ws-tdp3xtfnsq-as.a.run.app", api.read_text(encoding="utf-8"))
        # the password is never stored
        self.assertNotRegex(SEND, r"localStorage\.setItem\([^)]*[Pp]ass")

    def test_directory_message_no_longer_says_unconnected(self):
        self.assertNotIn("Until the form is connected", DIRF)


if __name__ == "__main__":
    unittest.main()


class OwnRecords(unittest.TestCase):
    """19 Nov 2026 20:25 NPT decisions: field staff see their own records with the coordinator's
    decision, and a returned record reopens in the form as the next version of the same record."""
    def test_my_records_and_correction(self):
        self.assertIn("A.griefEntries", SEND); self.assertIn("A.dirMine", SEND)
        self.assertIn("Returned — please correct", SEND)
        self.assertIn("CFG.load(r.payload)", SEND)
        self.assertIn("const ed=window.__edit;r.id=ed?ed.id:", GRIEF)
        self.assertIn("if(ix>=0)l[ix]=r;else l.push(r)", GRIEF)
        for page in (GRIEF, DIRF):
            self.assertIn("title:function(p)", page); self.assertIn("load:function(p)", page)

    def test_sign_in_by_email_link_first(self):
        api = (ROOT.parent / "hub" / "assets" / "access-api.js")
        if api.exists():
            s = api.read_text(encoding="utf-8")
            self.assertLess(s.index("Email me a sign-in link"), s.index("Use a password instead"))

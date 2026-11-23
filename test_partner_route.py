"""Partner route for the Referral Directory (owner decision, 23 Nov 2026).

A verified email without an access card may send its own directory entries; the server
marks it with me.partner. The send card must accept that for the directory only, and
never treat a partner as a card holder for any other form.
"""
import pathlib, re, unittest

SRC = (pathlib.Path(__file__).resolve().parent / "lib" / "form-send.js").read_text(encoding="utf-8")


class PartnerRoute(unittest.TestCase):
    def test_partner_is_scoped_to_the_form_the_server_names(self):
        self.assertIn("me.partner.forms.indexOf(CFG.form) >= 0", SRC)
        self.assertIn("function canSend() { return !!(me && (me.role || isPartner())); }", SRC)

    def test_sending_uses_canSend_not_role(self):
        self.assertIn("if (!canSend()) throw new Error(", SRC)
        self.assertNotIn("if (!me || !me.role) throw", SRC)

    def test_partner_skips_the_card_organisation_check_only(self):
        self.assertIn('if (me.role && me.role !== "admin" && p.org !== me.org)', SRC)


if __name__ == "__main__":
    unittest.main()

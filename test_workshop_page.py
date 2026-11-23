"""Workshop entry page (owner decision, 23 Nov 2026): no sign-in, write-only holding area.

The page must not load sign-in or access scripts, must send only to the workshop route, and
must say that entries are checked with CMC-Nepal before anything is published."""
import pathlib, unittest

HERE = pathlib.Path(__file__).resolve().parent
PAGE = (HERE / "preview" / "referral-directory-workshop.html").read_text(encoding="utf-8")
JS = (HERE / "lib" / "workshop-send.js").read_text(encoding="utf-8")


class WorkshopPage(unittest.TestCase):
    def test_no_sign_in_scripts(self):
        for s in ("current-auth.js", "access-api.js", "form-send.js", "fb-config.js"):
            self.assertNotIn(s, PAGE)
        self.assertIn('<script src="../lib/workshop-send.js"></script>', PAGE)

    def test_sends_only_to_the_workshop_route_without_identity(self):
        self.assertIn('var ROUTE = "/directory/workshop/intake";', JS)
        self.assertNotIn("Authorization", JS)
        self.assertNotIn("servicepoints2", JS)

    def test_states_the_check_before_publication(self):
        self.assertIn("checked with CMC-Nepal before anything appears", PAGE)
        self.assertIn('content="noindex"', PAGE)

    def test_one_button_sends_and_says_so(self):
        # 23 Nov 2026 (owner): one button that sends at once; the box under it says whether it was sent.
        self.assertIn('<button type="submit" class="btn" id="wsSubmit">Send to the coordination team</button>', PAGE)
        self.assertNotIn("Save entry on this device", PAGE)
        self.assertNotIn("Send saved entries", JS)
        self.assertIn("✓ Sent.", JS)
        self.assertIn("Not sent yet.", JS)
        self.assertIn('document.getElementById("saved")', JS)

    def test_msp_part_hidden_for_participants(self):
        # 23 Nov 2026 (owner): participants are not the MSP mapping team.
        self.assertIn('id="mspCard" hidden style="display:none"', PAGE)
        self.assertIn('<li data-s="7" style="display:none">', PAGE)
        self.assertIn('id="exportBtn" hidden', PAGE)


if __name__ == "__main__":
    unittest.main()

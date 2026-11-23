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

    def test_save_box_shows_the_sending_state(self):
        # 23 Nov 2026: the green box under the save button must say whether the entry was sent,
        # and must not keep the regular form's sign-in sentence.
        self.assertIn("Sent and received by the coordination team.", JS)
        self.assertIn('document.getElementById("saved")', JS)
        self.assertIn("Signed in, the record is sent to the server", JS)  # removed from the box
        self.assertIn("split(x).join", JS)


if __name__ == "__main__":
    unittest.main()

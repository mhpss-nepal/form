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
        self.assertIn('<script src="../lib/workshop-send.js?v=20261124a"></script>', PAGE)

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

    def test_incomplete_message_names_sections(self):
        # 23 Nov 2026 (owner): "complete section 8" pointed at a number no longer shown; name the section instead.
        self.assertIn("#steps li[data-s=", PAGE)
        self.assertNotIn('miss.join(", ")', PAGE)

    def test_missing_answers_are_marked_in_red(self):
        # 23 Nov 2026 (owner): participants must see where the missing answers are.
        self.assertIn(".ws-miss{outline:3px solid #d93025", PAGE)
        self.assertIn("Please fill in the parts marked in red.", PAGE)
        self.assertIn('scrollIntoView({behavior:"smooth",block:"center"})', PAGE)

    def test_pin_and_safe_house_guards(self):
        # 23 Nov 2026 (owner): participants sit in Kathmandu, far from their services;
        # safe houses and child shelters are not recorded on this open page.
        self.assertIn('id="gps" hidden style="display:none"', PAGE)
        self.assertIn("VALLEY_D={KTM:1,LAL:1,BHA:1}", PAGE)
        self.assertIn('var SECRET=["SAFEHOUSE","CHILDSHELTER"];', PAGE)
        self.assertIn("e.stopImmediatePropagation()", PAGE)

    def test_map_moves_to_the_chosen_district(self):
        # 23 Nov 2026: participants place the pin far from where they sit; the map jumps to the district.
        import json, re
        dc = json.loads(re.search(r"var DC=(\{.*?\});", PAGE).group(1))
        geo = json.loads(re.search(r"const GEO = (\{.*?\});\n", PAGE, re.S).group(1))
        self.assertEqual(set(dc), {d["c"] for d in geo["districts"]})
        for lat, lng in dc.values():
            self.assertTrue(26.0 <= lat <= 30.6 and 80.0 <= lng <= 88.3)
        self.assertIn("map.setView(c,10)", PAGE)



class TrimmedText(unittest.TestCase):
    # 24 Nov 2026: entries were refused with "bounded trimmed text required" (trailing space, Enter).
    def test_payload_is_cleaned_before_sending(self):
        self.assertIn("function clean(v)", JS)
        self.assertIn("CFG.payload = function (r) { return clean(rawPayload(r)); };", JS)
        self.assertIn(".trim()", JS)


if __name__ == "__main__":
    unittest.main()

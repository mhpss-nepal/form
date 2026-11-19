"""Locks the 19 Nov 2026 field-form decisions: one page (no tab bar) for the grief and directory
forms; grief form registration by name or anonymous with an automatic code; 5Ws age groups with the
form kept adults only; safety question wording untouched until clinical review."""
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent
G = (ROOT / 'preview' / 'grief-early-assessment.html').read_text(encoding='utf-8')
D = (ROOT / 'preview' / 'referral-directory.html').read_text(encoding='utf-8')


class OnePageForms(unittest.TestCase):
    def test_no_tab_bar(self):
        for name, s in (('grief', G), ('directory', D)):
            self.assertNotIn('<nav class="tabs"', s, name)
            self.assertNotIn('id="tab-map"', s, name)
            self.assertNotIn('id="tab-dir"', s, name)

    def test_review_marks_not_live(self):
        self.assertNotIn("class='chg'", G)


class GriefRegistration(unittest.TestCase):
    def test_choice_by_name_or_anonymous(self):
        self.assertEqual(re.findall(r'name="reg" value="([a-z]+)"', G), ['byname', 'anon'])
        for k in ('id="pName"', 'id="pPhone"', 'id="pInit"', 'id="codeOut"'):
            self.assertIn(k, G)

    def test_code_is_automatic_and_device_unique(self):
        self.assertIn('function devTag()', G)
        self.assertIn('${o}-${d}-${t}-${devTag()}-', G)
        self.assertIn('r.code=ed?ed.code:code()', G)  # new records get code(); a corrected record keeps its code (19 Nov 2026)

    def test_names_stay_with_the_organisation(self):
        self.assertIn('never sent to coordination or shown on the dashboard', G)


class GriefAgeGroups(unittest.TestCase):
    def test_same_groups_as_5ws_and_adults_only(self):
        self.assertEqual(re.findall(r'name="age" value="([^"]+)"', G), ['0-4', '5-9', '10-17', '18-59', '60+'])
        self.assertIn('["18-59","60+"].includes(radio("age"))', G)
        self.assertIn('id="ageWarn"', G)


class SafetyWordingUntouched(unittest.TestCase):
    def test_self_harm_question_waits_for_clinical_review(self):
        self.assertIn('In the past month, has the person had thoughts of ending their life or harming themselves?', G)


if __name__ == '__main__':
    unittest.main()

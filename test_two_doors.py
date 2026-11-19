"""Two-door contract (19 Nov 2026): /form/ is the only field door; it never lists
forms that write to the legacy store, and preview forms say they send nothing."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class FieldDoorTest(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()

    def test_legacy_writer_forms_are_not_offered(self):
        for page in ('phq9.html', 'selfreport.html'):
            self.assertNotIn(page, self.html)

    def test_main_group_has_the_four_field_forms(self):
        main = self.html[:self.html.index('<details class="d2-more">')]
        self.assertEqual(re.findall(r'<a href="([^"]+)" data-i18n="dir.open"', main),
                         ['5ws-report.html', 'training-report.html',
                          'preview/referral-directory.html', 'preview/grief-early-assessment.html'])

    def test_previews_exist_and_are_not_indexed(self):
        for page in ('preview/referral-directory.html', 'preview/grief-early-assessment.html'):
            text = (ROOT / page).read_text()
            self.assertIn('noindex', text)

    def test_no_internal_status_wording_on_the_door(self):
        for phrase in ('pilot not open', 'not commissioned', 'activation held', 'Layer 1 ·'):
            self.assertNotIn(phrase, self.html)

    def test_every_key_on_the_door_has_english(self):
        import json, subprocess
        mod = (ROOT / 'lib/directory-status-20261119.js').read_text()
        out = subprocess.check_output(['node', '-e', 'global.window={};' + mod +
              ';console.log(JSON.stringify(window.I18N_STRINGS.en))'], text=True)
        labels = json.loads(out)
        for key in re.findall(r'data-i18n="((?:d2|dir)\.[^"]+)"', self.html):
            self.assertTrue(labels.get(key), key)


if __name__ == '__main__':
    unittest.main()

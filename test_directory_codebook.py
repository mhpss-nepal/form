"""The Referral Directory form uses the same cadre, age and target-group lists as the
5Ws form (agreed with EDCD, 17 Sep 2026). Lock that so the two cannot drift."""
import json, re, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORM = ROOT / 'preview' / 'referral-directory.html'
CODES = ROOT.parent / 'hub' / 'assets' / 'codes.js'


def codebook():
    js = ('global.window={};const fs=require("fs");eval(fs.readFileSync(process.argv[1],"utf8")+'
          '";console.log(JSON.stringify({c:CADRES.filter(x=>!x.retired).map(x=>x.code),'
          't:TARGET_GROUPS.filter(x=>!x.retired).map(x=>x.code)}))")')
    return json.loads(subprocess.check_output(['node', '-e', js, str(CODES)], text=True))


@unittest.skipUnless(CODES.exists(), 'hub repository not checked out beside form')
class DirectoryUsesTheFiveWsLists(unittest.TestCase):
    def setUp(self):
        self.html = FORM.read_text(encoding='utf-8')
        self.cb = codebook()

    def test_cadres_match_the_5ws_list(self):
        form = [c['c'] for c in json.loads(re.search(r'const CADRES = (\[.*?\]);', self.html).group(1))]
        self.assertEqual(form, self.cb['c'])
        self.assertNotIn('SPSC', form)

    def test_target_groups_match_the_5ws_list(self):
        form = [c['c'] for c in json.loads(re.search(r'const GROUPS = (\[.*?\]);', self.html).group(1))]
        self.assertEqual(form, self.cb['t'])

    def test_age_groups_match_the_5ws_form(self):
        self.assertEqual(re.findall(r'name="age" value="([^"]+)"', self.html), ['0-4', '5-9', '10-17', '18-59', '60+'])
        fivews = (ROOT / '5ws-report.html').read_text(encoding='utf-8')
        self.assertIn('0&ndash;4, 5&ndash;9, 10&ndash;17, 18&ndash;59, 60+', fivews)

    def test_delivery_mode_and_msp_block_present(self):
        self.assertEqual(re.findall(r'name="delivery" value="([^"]+)"', self.html), ['inperson', 'remote', 'both'])
        self.assertIn('For MSP mapping only', self.html)
        self.assertIn('Optional · CMC-Nepal mapping team', self.html)


if __name__ == '__main__':
    unittest.main()

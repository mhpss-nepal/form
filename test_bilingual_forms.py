"""Locks the bilingual grief and directory forms (19 Nov 2026): every keyed sentence has English in
the shared dictionary, every non-protected key has a Nepali draft that is declared as machine draft,
consent / safety / clinical keys carry no Nepali until a human writes it, and the proofreading mode
is loaded."""
import json
import re
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent
HUB = ROOT.parent / 'hub' / 'assets' / 'i18n-strings.js'
PAGES = {'grief': ROOT / 'preview' / 'grief-early-assessment.html', 'dirf': ROOT / 'preview' / 'referral-directory.html'}
PROT = ('consent.', 'safeguard.', 'clinical.')


def dictionary():
    js = "global.window={};eval(require('fs').readFileSync(process.argv[1],'utf8'));const S=window.I18N_STRINGS;" \
         "console.log(JSON.stringify({en:S.en,ne:S.ne,machine:S._meta.source.machine,pro:S._meta.professionalOnly}))"
    return json.loads(subprocess.run(['node', '-e', js, str(HUB)], capture_output=True, text=True, check=True).stdout)


@unittest.skipUnless(HUB.exists(), 'hub repository not beside the form repository')
class BilingualForms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = dictionary()

    def keys(self, page):
        s = page.read_text(encoding='utf-8')
        return set(re.findall(r'data-i18n(?:-ph)?="([^"$]+)"', s)), s

    def test_pages_load_engine_and_proof_mode(self):
        for p in PAGES.values():
            s = p.read_text(encoding='utf-8')
            for src in ('../../hub/assets/i18n-strings.js', '../../hub/assets/i18n.js', '../lib/proof-mode.js'):
                self.assertIn('<script src="%s"></script>' % src, s, p.name)

    def test_every_key_has_english(self):
        for p in PAGES.values():
            ks, _ = self.keys(p)
            missing = [k for k in ks if k not in self.S['en']]
            self.assertEqual(missing, [], p.name)

    def test_nepali_drafts_declared_and_protected_kept_english(self):
        for pfx in ('grief', 'dirf'):
            mine = [k for k in self.S['en'] if k.startswith(pfx + '.') or re.match(r'^(consent|safeguard|clinical)\.%s\b' % pfx, k)]
            self.assertTrue(len(mine) > 150, pfx)
            for k in mine:
                if k.startswith(PROT):
                    self.assertNotIn(k, self.S['ne'], k)
                else:
                    self.assertIn(k, self.S['ne'], k)
                    self.assertIn(k, self.S['machine'], k)
        for p in PROT:
            self.assertIn(p, self.S['pro'])

    def test_proofreading_goes_to_the_proofreading_collection_only(self):
        s = (ROOT / 'lib' / 'proof-mode.js').read_text(encoding='utf-8')
        self.assertIn('/documents/formproof?key=', s)
        self.assertNotIn('/documents/feedback', s)
        self.assertIn('if (!q.has("proof")) return;', s)


if __name__ == '__main__':
    unittest.main()

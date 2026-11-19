"""Directory-only cache and missing-module regression contracts."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent
MODULE = 'lib/directory-status-20261119.js'


def dictionary(script):
    result = subprocess.check_output(['node', '-e',
        'global.window={I18N_STRINGS:{en:{},ne:{}}};' + script +
        ';console.log(JSON.stringify(window.I18N_STRINGS));'], text=True)
    return json.loads(result)


class DirectoryCacheHotfix(unittest.TestCase):
    def test_missing_module_bootstrap_matches_versioned_dictionary(self):
        html = (ROOT / 'index.html').read_text()
        fallback = next(s for s in re.findall(r'<script>(.*?)</script>', html, re.S)
                        if 'if (!window.DIRECTORY_STATUS_READY)' in s)
        expected = dictionary((ROOT / MODULE).read_text())
        self.assertEqual(dictionary(fallback), expected)
        for lang in ('en', 'ne'):
            labels = expected[lang]
            self.assertEqual([labels['dir.' + key] for key in ('open', 'copy', 'qr')],
                             ['Open form', 'Copy link', 'QR'])
            # Plain-language delivery rule: sent only on a server confirmation, Retry when offline.
            self.assertIn('server has received it', labels['d2.note'])
            self.assertIn('Retry', labels['d2.note'])
            self.assertNotIn('device-only', labels['d2.note'])
            for kind in ('directory', 'grief'):
                # Server receivers live since 19 Nov 2026: say how sending works, never "not sent yet".
                self.assertEqual('SIGN IN TO SEND', labels['dir.' + kind + '.tag'])
                self.assertIn('saved on this phone first', labels['dir.' + kind + '.status'])
                self.assertIn('only when the server confirms it', labels['dir.' + kind + '.status'])
                self.assertNotIn('Until the server connection opens', labels['dir.' + kind + '.status'])
            for kind in ('providers', 'servicepoints'):
                self.assertIn('before anything is published', labels['dir.' + kind + '.status'])
            self.assertIn('Nothing is saved or sent', labels['dir.contacts.status'])

    def test_versioned_asset_loads_before_engine_and_is_precached(self):
        html = (ROOT / 'index.html').read_text()
        sw = (ROOT / 'sw.js').read_text()
        self.assertNotIn('src="lib/directory-strings.js"', html)
        self.assertLess(html.index('src="' + MODULE + '"'),
                        html.index('src="../hub/assets/i18n.js"'))
        self.assertIn('"' + MODULE + '"', sw)
        cache_version = re.search(r'const CACHE = "mhpss-np-field-v(\d+)"', sw)
        self.assertIsNotNone(cache_version)
        self.assertGreaterEqual(int(cache_version.group(1)), 47)
        self.assertEqual(len(re.findall(r'data-i18n="dir.open"', html)), 7)


if __name__ == '__main__':
    unittest.main()

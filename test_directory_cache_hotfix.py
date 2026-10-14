"""Directory-only cache and missing-module regression contracts."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent
MODULE = 'lib/directory-status-20261013.js'


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
            self.assertIn('approved reporting access', labels['dir.delivery'])
            self.assertNotIn('device-only', labels['dir.delivery'])
            self.assertIn('not connected for automatic delivery', labels['dir.delivery'])
            for kind in ('providers', 'servicepoints'):
                self.assertIn('publication held', labels['dir.' + kind + '.status'])
            for kind in ('contacts', 'referrals'):
                self.assertIn('Review only', labels['dir.' + kind + '.status'])

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
        self.assertEqual(len(re.findall(r'data-i18n="dir.open"', html)), 8)


if __name__ == '__main__':
    unittest.main()

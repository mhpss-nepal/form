"""Guard the directory URL from the shared .u icon-class collision.

Actual 390/1280 EN/NE expanded-QR browser geometry is exercised by the
release verifier; this small guard keeps the collision out of future builds.
"""
import unittest
from pathlib import Path


class DirectoryQRLayout(unittest.TestCase):
    def test_url_uses_namespaced_auto_height_block(self):
        html = (Path(__file__).parent / 'index.html').read_text()
        self.assertNotIn('<div class="u">', html)
        self.assertIn('<div class="directory-qr-url">', html)
        self.assertIn('.qrbox .directory-qr-url{display:block;width:100%;height:auto;', html)
        self.assertIn('overflow-wrap:anywhere;', html)


if __name__ == '__main__':
    unittest.main()

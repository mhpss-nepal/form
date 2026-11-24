"""24 Nov 2026 lesson: client limits must match the server contract, or records are refused in the field.
Limits copied from directory2_contract.py and grief_contract.py (read 24 Nov 2026)."""
import pathlib, re, unittest
HERE = pathlib.Path(__file__).resolve().parent
DIR = {'placeName': 300, 'hours': 300, 'refPhone': 300, 'refName': 120, 'orgOther': 160, 'partners': 300, 'languages': 200, 'funder': 200, 'serviceOther': 300, 'criteria': 300, 'manualName': 200, 'refEmail': 200}

def maxlen(s, attr, val):
    m = re.search(r'<(?:input|textarea)[^>]*\b%s="%s"[^>]*>' % (attr, re.escape(val)), s)
    if not m: return None
    n = re.search(r'maxlength="(\d+)"', m.group(0)); return int(n.group(1)) if n else 0

class Limits(unittest.TestCase):
    def test_directory_text_fields_capped_at_server_limit(self):
        for page in ["preview/referral-directory.html", "preview/referral-directory-workshop.html"]:
            s = (HERE / page).read_text(encoding="utf-8")
            for k, n in DIR.items():
                got = maxlen(s, "name", k)
                if got is None: continue
                self.assertTrue(0 < got <= n, f"{page} {k}: maxlength {got}, server {n}")

    def test_grief_contact_fields(self):
        s = (HERE / "preview/grief-early-assessment.html").read_text(encoding="utf-8")
        self.assertEqual(maxlen(s, "id", "pName"), 120)
        self.assertEqual(maxlen(s, "id", "pTime"), 120)
        self.assertEqual(maxlen(s, "id", "pPhone"), 40)
        self.assertEqual(maxlen(s, "id", "pInit"), 4)
        self.assertIn('on("pPhone"', s); self.assertIn("0x966", s)
        self.assertIn('on("pInit"', s)

if __name__ == "__main__":
    unittest.main()

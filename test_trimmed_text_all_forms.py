"""24 Nov 2026 lesson: the server accepts only trimmed single-line text (contract text():
value == value.strip(), no control characters). Phones add trailing spaces and long boxes accept
Enter, so every sender must clean text before it sends. This test fails if a sender stops doing so,
or if a page sends through a sender that does not."""
import pathlib, re, shutil, subprocess, unittest

HERE = pathlib.Path(__file__).resolve().parent
SENDERS = {"lib/form-send.js": "form-send.js", "lib/workshop-send.js": "workshop-send.js"}


class EverySenderCleansText(unittest.TestCase):
    def test_senders_wrap_the_payload_with_clean(self):
        for rel in SENDERS:
            js = (HERE / rel).read_text(encoding="utf-8")
            self.assertIn("function clean(v)", js, rel)
            self.assertIn("return clean(rawPayload(r));", js, rel)

    def test_every_sending_page_uses_a_cleaning_sender(self):
        for page in HERE.rglob("*.html"):
            s = page.read_text(encoding="utf-8", errors="ignore")
            if "window.FORM_SEND=" not in s and "window.FORM_SEND =" not in s:
                continue
            used = re.findall(r'src="[^"]*lib/(form-send|workshop-send)\.js[^"]*"', s)
            self.assertTrue(used, f"{page.name} defines FORM_SEND but loads no cleaning sender")

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_clean_matches_the_server_rule(self):
        js = (HERE / "lib/form-send.js").read_text(encoding="utf-8")
        body = js[js.index("function clean(v)"):]
        body = body[:body.index("\n  }\n") + 4]
        probe = body + """
const cases = ["Clinical Psychologist ", " Ramp\\nLift  ", "a\\tb", "भित्र ", ["x "], {k: " y"}, 3, null];
const out = cases.map(clean);
const ok = s => typeof s !== "string" || (s === s.trim() && !/[\\u0000-\\u001F\\u007F]/.test(s));
const flat = JSON.stringify(out);
const all = []; (function walk(v){ if (Array.isArray(v)) v.forEach(walk); else if (v && typeof v === "object") Object.values(v).forEach(walk); else all.push(v); })(out);
if (!all.every(ok)) { console.log("BAD " + flat); process.exit(1); }
console.log(flat);
"""
        r = subprocess.run(["node", "-e", probe], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('"Clinical Psychologist"', r.stdout)
        self.assertIn('"Ramp Lift"', r.stdout)


if __name__ == "__main__":
    unittest.main()

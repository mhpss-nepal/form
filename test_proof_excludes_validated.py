"""Proofreading never lists the validated Nepal PHQ-9 (owner decision, 22 Nov 2026).

Round 1 showed the English back-translation of the PHQ-9 without its
validated Nepali, and the reviewer translated it afresh. The proofreading
list must leave out phq9.* and clinical.grief.phq.item*/scale* for good.
"""
import json, pathlib, re, subprocess, unittest

HERE = pathlib.Path(__file__).resolve().parent
PROOF = HERE / "lib" / "proof-mode.js"
STRINGS = HERE.parent / "hub" / "assets" / "i18n-strings.js"


class ProofExcludesValidated(unittest.TestCase):
    def test_lists_leave_out_the_validated_instrument(self):
        src = PROOF.read_text(encoding="utf-8")
        never = re.search(r"var NEVER = /(.+?)/;", src)
        self.assertIsNotNone(never, "proof-mode.js must declare the NEVER exclusion")
        self.assertEqual(src.count("!NEVER.test(k)"), 2, "both key sources must apply the exclusion")
        pfx = re.search(r'var PFX = FORM === "grief" \? (\[.*?\]) : (\[.*?\]);', src)
        grief, directory = json.loads(pfx.group(1)), json.loads(pfx.group(2))
        self.assertFalse([p for p in grief + directory if p.startswith("phq9")])
        rx = re.compile(never.group(1).replace("\\\\", "\\"))
        if STRINGS.exists():
            js = "global.window={};require(%s);process.stdout.write(JSON.stringify(Object.keys(window.I18N_STRINGS.en)))" % json.dumps(str(STRINGS))
            en = json.loads(subprocess.check_output(["node", "-e", js]))
            listed = [k for k in en if not rx.match(k) and any(k.startswith(p) for p in grief)]
            self.assertFalse([k for k in listed if k.startswith("phq9.") or re.match(r"clinical\.grief\.phq\.(item|scale)", k)])
            self.assertIn("clinical.grief.phq.src", listed, "PHQ-9 instructions (not the instrument) stay reviewable")


if __name__ == "__main__":
    unittest.main()

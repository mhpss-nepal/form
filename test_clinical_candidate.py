from pathlib import Path
import unittest
class ClinicalCandidate(unittest.TestCase):
 def test_native_collectors_wired_without_legacy_writes(self):
  for file in ['phq9.html','drafts/contact.html','drafts/referral-outcome.html']:
   s=Path(file).read_text()
   self.assertIn('window.ClinicalCollector',s)
   self.assertIn('clinical-form.js',s)
   self.assertNotIn('L.save(',s)
   self.assertNotIn('L.remember(',s)
   self.assertNotIn('assets/l1.js',s)
   self.assertNotIn('assets/fb.js',s)
 def test_memory_transport(self):
  s=Path('lib/clinical-api.js').read_text()
  self.assertIn('clinical-submit/1',s)
  self.assertNotIn('localStorage',s)
  self.assertNotIn('sessionStorage',s)
if __name__=='__main__':unittest.main()

"""Bounded directory contract: eight routes, inert questions, unchanged live forms."""
import importlib.util
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE='36e104cbf9f6f1b29aef0d95ace1d0454306316b'
DESTINATIONS=['5ws-report.html','phq9.html','selfreport.html','training-report.html','review/contact.html','provider-register.html','service-point.html']
class Controls(HTMLParser):
    def __init__(self): super().__init__();self.controls=[];self.labels=[];self.inlabel=False;self.current=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ['input','select','textarea','option']:self.controls.append((tag,tuple((k,a.get(k)) for k in ['id','name','type','value','required','pattern','maxlength'])))
        if tag=='label':self.inlabel=True;self.current=''
    def handle_data(self,data):
        if self.inlabel:self.current+=data
    def handle_endtag(self,tag):
        if tag=='label':self.inlabel=False;self.labels.append(' '.join(self.current.split()))
class DirectoryCorrection(unittest.TestCase):
    def test_eight_exact_open_copy_routes(self):
        s=(ROOT/'index.html').read_text()
        self.assertEqual(re.findall(r'<a href="([^"]+)" data-i18n="dir.open"',s),DESTINATIONS)
        self.assertEqual(re.findall(r'data-url="([^"]+)" onclick="COPY',s),DESTINATIONS)
        self.assertEqual(s.count('onclick="QRT(this)"'),7)
        self.assertNotIn('fb.js',s)
        self.assertNotIn('house=',s)
    def test_form_sources_byte_locked(self):
        for f in DESTINATIONS[:4]+['provider-register.html','service-point.html','pwa.js','template-review.js']:
            expected=subprocess.check_output(['git','show',BASE+':'+f],cwd=ROOT)
            self.assertEqual((ROOT/f).read_bytes(),expected,f)
    def test_source_controls_and_question_labels_preserved(self):
        for f in ['review/contact-instrument.html','review/referral-outcome.html']:
            name='contact' if 'contact-instrument' in f else 'referral-outcome'
            original=Controls();original.feed((ROOT/'tools/source-templates'/(name+'.txt')).read_text().split('<script')[0])
            review=Controls();review.feed((ROOT/f).read_text())
            self.assertEqual(original.controls,review.controls,f)
            self.assertEqual(original.labels,review.labels,f)
    def test_safe_script_allowlist_and_network_csp(self):
        for f in ['review/contact-instrument.html','review/referral-outcome.html']:
            s=(ROOT/f).read_text()
            self.assertEqual(re.findall(r'<script src="([^"]+)"',s),['../template-preview-20261014.js','../../hub/assets/codes.js','../../hub/assets/i18n-strings.js'])
            self.assertIn("connect-src 'none'; form-action 'none'",s)
            for word in ['L1.','L.save','localStorage','submissions_preview','fetch(','XMLHttpRequest']:
                self.assertNotIn(word,s)
    def test_reviews_are_reproducible(self):
        before={f:(ROOT/f).read_bytes() for f in DESTINATIONS[4:]}
        subprocess.run(['python','tools/build-template-review.py'],cwd=ROOT,check=True,capture_output=True)
        self.assertEqual(before,{f:(ROOT/f).read_bytes() for f in DESTINATIONS[4:]})
    def test_qr_scope_equals_open_routes(self):
        spec=importlib.util.spec_from_file_location('qr',ROOT/'tools/qr-check.py'); assert spec and spec.loader
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        self.assertEqual(set(mod.ALLOWED_QR_URLS.values()),{'/form/','/form/review/referral-outcome.html'}|{'/form/'+f for f in DESTINATIONS})
    def test_alternate_directory_is_redirect_only(self):
        s=(ROOT/'all-forms.html').read_text();self.assertIn("location.replace('./'+location.search+location.hash)",s)
        self.assertNotIn('preview.html',s)
if __name__=='__main__':unittest.main()

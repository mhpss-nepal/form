"""Source-bound privacy and question preservation, no production service calls."""
from pathlib import Path
import subprocess,re,hashlib
from html.parser import HTMLParser
ROOT=Path(__file__).parent;BASE='ffcc7f5d8721f886bb963c09db82707480a83961'
class Questions(HTMLParser):
 def __init__(self):super().__init__();self.keys=[];self.codes=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if a.get('data-i18n','').startswith('sr.') and a['data-i18n'] not in {'sr.p032','sr.p002','sr.p038','sr.p039'}:self.keys.append(a['data-i18n'])
  if t in ['input','option'] and 'value' in a:self.codes.append((t,a.get('name'),a['value']))
def test_source_questions_age_codes_bilingual_provenance():
 old=subprocess.check_output(['git','show',BASE+':selfreport.html'],cwd=ROOT).decode();now=(ROOT/'selfreport.html').read_text();a=Questions();b=Questions();a.feed(old);b.feed(now)
 assert a.keys==b.keys and a.codes==b.codes
 assert (ROOT/'lib/strings.js').read_bytes()==subprocess.check_output(['git','show',BASE+':lib/strings.js'],cwd=ROOT)
def test_no_respondent_auth_storage_export_backfill():
 page=(ROOT/'selfreport.html').read_text();js=(ROOT/'lib/selfreport-intake.js').read_text()
 assert 'fb-config.js' not in page and 'fb.js' not in page and 'pwa.js' not in page
 assert all(x not in js for x in ['localStorage','sessionStorage','L1.save','L1.all','BaselineAuth','email','geolocation'])
 assert 'csvBtn' not in page and "credentials:'omit'" in js and "cache:'no-store'" in js
 assert 'transport metadata' in page and 'anonymity is not absolute' in page

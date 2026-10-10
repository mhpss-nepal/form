#!/usr/bin/env python3
"""Verify immutable release serving bytes and complete static HTML references.
No operational/clinical reads; only local tracked application source/assets.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse
import hashlib,json,re,sys
R=Path(__file__).resolve().parent.parent
h=lambda b:hashlib.sha256(b).hexdigest()
def check(pin,manifest,base):
 assert set(pin)=={'release','manifest_sha256','worker_sha256'}
 assert h(json.dumps({k:pin[k] for k in ['manifest_sha256','worker_sha256']},separators=(',',':')).encode())==pin['release']
 raw=manifest.read_bytes();assert h(raw)==pin['manifest_sha256'];m=json.loads(raw);assert m['version']==2
 assert len({a['request'] for a in m['assets']})==len(m['assets']);lookup={a['request']:a for a in m['assets']}
 for a in m['assets']:
  b=(base/a['file']).read_bytes();assert len(b)==a['bytes'] and h(b)==a['sha256'],a['file']
  if a['type']=='text/html':
   for ref in re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+\.(?:js|css))["\']',b.decode(),re.I):
    u=urlparse(urljoin('https://fixture.invalid'+a['request'],ref))
    if u.netloc=='fixture.invalid':assert u.path in lookup,(a['request'],ref)
 return len(m['assets'])
def main():
 root=json.loads((R/'cache-control-v43.json').read_text());assert h((R/'sw.js').read_bytes())==root['worker_sha256'];n=check(root,R/'cache-manifests'/(root['manifest_sha256']+'.json'),R)
 B=R/'review-5ws-admin-test-v35/releases/native-test-20261009';pin=json.loads((B.parent.parent/'cache-control-v38.json').read_text());assert h((B/'coherent-sw.js').read_bytes())==pin['worker_sha256'];m=check(pin,B/'cache-manifests'/(pin['manifest_sha256']+'.json'),B)
 print(json.dumps({'root_assets':n,'native_assets':m,'pin_and_complete_references':'PASS'}));return 0
if __name__=='__main__':sys.exit(main())

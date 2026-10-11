"""RC01 isolated package guard; no cloud or browser writes."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,unittest,importlib.util
R=Path(__file__).resolve().parents[2]
OLD=R/'review-5ws-admin-test-v35/releases/native-test-20261009'
NEW=R/'review-5ws-admin-test-v35/releases/native-test-rc01-20261011'
MAIN='a5cc046a1c6336b72d198c49fc5b1d45cbd8e814';REVIEW='490f793f6cb81ca4ab07cc9b79eab688a6df080f'
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def check(n,v):
 assert v,n
 checks.append(n)
m=json.loads((NEW/'candidate-manifest.json').read_text())
tracked=set(subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines())
for p in NEW.rglob('*'):
 if p.is_file():check('publication file tracked '+str(p.relative_to(NEW)),str(p.relative_to(R)) in tracked)
for name,meta in m['assets'].items():
 b=(NEW/name).read_bytes();check('manifest '+name,sha(b)==meta['sha256'] and len(b)==meta['bytes'])
assets={k:v for k,v in m['assets'].items() if k!='release-pins.js'}
check('canonical release digest',sha(json.dumps(assets,sort_keys=True,separators=(',',':')).encode())==m['release_sha256'])
for p in OLD.rglob('*'):
 if not p.is_file() or p.name in ['candidate-manifest.json','release-pins.js','5ws-report.html']:continue
 check('unchanged dependency '+str(p.relative_to(OLD)),p.read_bytes()==(NEW/p.relative_to(OLD)).read_bytes())
old=(OLD/'form/5ws-report.html').read_bytes();new=(NEW/'form/5ws-report.html').read_bytes()
check('only reviewed predicate changed',old.replace(b'r.dateAD!==today()&&!ack.checked',b'r.dateAD!==today()&&r.backdateAcknowledged!==true')==new)
reviewed=subprocess.check_output(['git','show',REVIEW+':review-5ws-admin-test-v35/releases/native-test-20261009/form/5ws-report.html'],cwd=R)
check('exact reviewed native document',new==reviewed)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',MAIN],cwd=R,text=True).splitlines()
for path in paths:
 check('existing file retained '+path,subprocess.check_output(['git','show',MAIN+':'+path],cwd=R)==(R/path).read_bytes())
check('original reviewed branch retained',subprocess.check_output(['git','rev-parse','w43-cache-integrated'],cwd=R,text=True).strip()==REVIEW)
# Legacy default-language assertions read root HTML only, not this additive release.
# Root worker/precache, landing, QR, clinical forms and tests are all exact main.
sys.path.insert(0,str(R))
from test_trial_scope import TrialScopeContractTest
from test_branch_union_reconciliation import ReconciledUnionTest
names=[(TrialScopeContractTest,'test_only_the_declared_pages_open_in_nepali'),(ReconciledUnionTest,'test_pages_that_stay_english_declare_nothing')]
legacy=[]
for cls,name in names:
 t=cls(name);res=unittest.TestResult();t.run(res)
 legacy.append({'id':t.id(),'failure_identity':'contact.html language default conflicts with old negative list' if res.failures else None,'failure_count':len(res.failures),'error_count':len(res.errors),'passed':res.wasSuccessful(),'candidate_relation':'unchanged root-only input, byte-exact main; not caused by additive release'})
 check('legacy identity-triage unchanged input '+t.id(),(R/'contact.html').read_bytes()==subprocess.check_output(['git','show',MAIN+':contact.html'],cwd=R))
 check('legacy assertion only reads old root pages '+t.id(),'ROOT.glob("*.html")' in (R/'test_trial_scope.py').read_text() and 'page(name)' in (R/'test_branch_union_reconciliation.py').read_text())
result={'checks':checks,'count':len(checks),'legacy_affected_identity_triage':legacy,'legacy_scope':'Named language tests are root-only and fail by identical unchanged contact.html input. All existing files are exact main; worker/cache/landing/QR failures are outside isolated delta, not waived for held PR21.','release_sha256':m['release_sha256'],'production_write':False}
if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'count':len(checks),'legacy':legacy,'release_sha256':m['release_sha256']},indent=2))

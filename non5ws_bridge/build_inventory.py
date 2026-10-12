"""Build exact seven-instrument inventory from browser evidence and source bytes."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
from contract import adapt, MAPPINGS
ROOT=Path(__file__).resolve().parents[1]
PIN='3f89f6ed118398efeb71fe3219d8f0988088fac1'
BASE='c71b18c4f667f5b53ff4ff98334dd2a9b48f3db3'
evidence=json.loads((ROOT/'non5ws_bridge/evidence/browser.json').read_text())
assert len(evidence)==7
rows=[]
for entry in evidence:
    storage, records=next(iter(entry['records'].items()))
    raw=records[0]; result=adapt(raw); file=entry['file']
    src=subprocess.check_output(['git','show',f'{PIN}:{file}'],cwd=ROOT)
    base=subprocess.check_output(['git','show',f'{BASE}:{file}'],cwd=ROOT)
    sensitive=[k for k in raw if any(s in k.lower() for s in ['name','phone','email','code','note','text','lat','lon','q1','q9','barrier','age','sex','qualification','address'])]
    headers=next(csv.reader(io.StringIO(entry['csv'])))
    rows.append(dict(instrument=result.instrument,source_path=file,source_pin=PIN,source_blob=subprocess.check_output(['git','rev-parse',f'{PIN}:{file}'],cwd=ROOT,text=True).strip(),source_sha256=hashlib.sha256(src).hexdigest(),candidate_sha256=hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),changed_from_base=src!=base,schema=raw['schema'],unit=result.unit,grain=result.grain,fields={k:type(v).__name__ for k,v in raw.items()},save_path=storage,receiving_target=result.collection,classification=result.classification,sensitive_fields=sensitive,layer2_home={'training':'service-level training workspace','service_contact':'organisation-locked clinical workspace','referral':'organisation-locked referral follow-up','service_point':'moderated service directory','provider':'moderated provider directory','phq9':'organisation-locked clinical assessment','self_report':'anonymous feedback review workspace'}[result.instrument],role='PROPOSED, not a permission grant: '+('organisation-authorised clinical staff' if result.classification=='restricted-clinical' else 'authorised reporter / designated reviewer'),changed_mapping='explicit instrument/schema route; no 5Ws projection; legacy age bands kept verbatim; directory registration is not publication',csv_fields=headers,csv_omitted_fields=sorted(set(raw)-set(headers)),browser_collect_save_export=entry['saved'] and entry['exported'] and not entry['page_errors'],checks=entry['checks'],receiving_status='pure adapter exercised; backend transport/storage/authz NOT implemented'))
assert {r['instrument'] for r in rows}==set(MAPPINGS)
summary=dict(source_pin=PIN,base_pin=BASE,inventory_count=len(rows),local_collect_save_export_pass=sum(r['browser_collect_save_export'] for r in rows),mapped_count=len({r['receiving_target'] for r in rows}),production_operational_verified=0,synthetic_only=True,network_disabled=True,instruments=rows)
text=json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
(ROOT/'non5ws_bridge/inventory.json').write_text(text)
# Owner-requested checkpoint, within this lane only.
checkpoint=ROOT.parents[1]/'non5ws-bridge'
checkpoint.mkdir(exist_ok=True)
(checkpoint/'inventory.json').write_text(text)
print(json.dumps({k:v for k,v in summary.items() if k!='instruments'},indent=2))

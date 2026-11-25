"""Exact non-5Ws training payload. No permissive coercion or inferred counts."""
import copy,hashlib,json,re
from datetime import date,datetime,timezone
from frozen20.trusted_validator import CODES,members
SCHEMA='mhpss-np-training/0.1.0-draft'
MAX_INT=2147483647
FIELDS=set('schema kind iasc_sub org focal_name focal_phone partners reporting_role counts_held_by_lead event_kind topic topic_other title accreditation delivery_mode date_ad days facilitators facilitator_org venue_district venue_palika participants trained_total under_18 with_disability supervision supervision_frequency pre_post_assessed note'.split())
class Invalid(ValueError):pass

def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def text(value,minimum=0,maximum=220):
 if type(value) is not str or not minimum<=len(value)<=maximum or value!=value.strip() or any(ord(c)<32 or ord(c)==127 or 0xD800<=ord(c)<=0xDFFF for c in value):raise Invalid('bounded trimmed text required')

def count(value,minimum=0,maximum=MAX_INT,nullable=False):
 if value is None and nullable:return
 if type(value) is not int or not minimum<=value<=maximum:raise Invalid('bounded integer required')

def geography(district,palika,optional=False):
 if district not in members('DISTRICTS'):raise Invalid('district code required')
 if optional and palika=='':return
 p=next((p for p in CODES['PALIKAS'] if p['pcode']==palika),None)
 if not p or p['district']!=district:raise Invalid('coherent palika required')

def validate_payload(p):
 if type(p) is not dict or not FIELDS<=set(p) or not set(p)<=FIELDS|{'_saved'}:raise Invalid('exact training fields required')
 for k in FIELDS-{'partners','participants','counts_held_by_lead','days','facilitators','trained_total','under_18','with_disability'}:text(p[k],maximum=2000 if k=='note' else 80 if k=='focal_phone' else 220)
 if p['schema']!=SCHEMA or p['kind']!='training' or p['iasc_sub']!='11.3':raise Invalid('training instrument required')
 if p['org'] not in members('ORGS'):raise Invalid('known organisation required')
 for k in ['focal_name','title']:text(p[k],1)
 choices={'reporting_role':{'LEAD','PARTNER'},'event_kind':{'ORIENT','TRAIN'},'topic':{'5.1','5.2','5.3','5.4','5.9'},'accreditation':{'','NHTC','NO','UNK'},'delivery_mode':{'','INP','ONL','BLE'},'supervision':{'PROV','PLAN','NONE'},'pre_post_assessed':{'','Y','N'}}
 for k,values in choices.items():
  if p[k] not in values:raise Invalid('training code required')
 if bool(p['topic_other'])!=(p['topic']=='5.9') or (p['supervision']!='PROV' and p['supervision_frequency']):raise Invalid('conditional text mismatch')
 if p['facilitator_org'] not in members('ORGS')|{'','OTHER'}:raise Invalid('facilitator org refused')
 try:
  d=date.fromisoformat(p['date_ad'])
  if d.isoformat()!=p['date_ad'] or not date(1900,1,1)<=d<=datetime.now(timezone.utc).date():raise ValueError()
 except ValueError:raise Invalid('training date refused') from None
 if '_saved' in p:
  text(p['_saved'],1,40)
  try:
   stamp=datetime.fromisoformat(p['_saved'].replace('Z','+00:00'))
   if stamp.tzinfo is None:raise ValueError()
  except ValueError:raise Invalid('browser timestamp refused') from None
 count(p['days'],1,366);count(p['facilitators'],nullable=True)
 geography(p['venue_district'],p['venue_palika'],True)
 partners=p['partners']
 if type(partners) is not list or len(partners)>32:raise Invalid('bounded partners required')
 for v in partners:text(v,1)
 if len(set(partners))!=len(partners):raise Invalid('duplicate partner')
 rows=p['participants']
 if type(rows) is not list or len(rows)>100:raise Invalid('bounded participants required')
 count(p['trained_total'])
 for k in ['under_18','with_disability']:
  count(p[k],nullable=True)
  if p[k] is not None and p[k]>p['trained_total']:raise Invalid('optional count exceeds total')
 partner=p['reporting_role']=='PARTNER'
 if p['counts_held_by_lead'] is not partner:raise Invalid('held count flag mismatch')
 if partner:
  if not partners or rows or p['trained_total']!=0 or p['under_18'] is not None or p['with_disability'] is not None:raise Invalid('partner counts forbidden')
 else:
  seen=set();total=0
  for r in rows:
   if type(r) is not dict or set(r)!=set('district palika cadre female male other total'.split()):raise Invalid('exact participant fields required')
   for k in ['district','palika','cadre']:text(r[k],1)
   geography(r['district'],r['palika'])
   if r['cadre'] not in {c['code'] for c in CODES['CADRES'] if not c.get('retired')}:raise Invalid('cadre refused')
   key=(r['palika'],r['cadre'])
   if key in seen:raise Invalid('duplicate palika cadre')
   seen.add(key)
   for k in ['female','male','other','total']:count(r[k])
   if r['total']<1 or r['total']!=sum(r[k] for k in ['female','male','other']):raise Invalid('sex count mismatch')
   total+=r['total'];count(total)
  if not rows or total!=p['trained_total']:raise Invalid('event total mismatch')
 return copy.deepcopy(p)

def parse(raw):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise Invalid('duplicate key')
   out[k]=v
  return out
 try:
  v=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Invalid('nonfinite')))
  if type(v) is not dict or set(v)!={'protocol','reportId','revision','predecessor','payload'} or v['protocol']!='training-submit/1':raise Invalid('exact submission required')
  if type(v['reportId']) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',v['reportId']):raise Invalid('report ID refused')
  count(v['revision'],1,500)
  pred=v['predecessor']
  if v['revision']==1:
   if pred is not None:raise Invalid('initial predecessor refused')
  else:
   if type(pred) is not dict or set(pred)!={'revision','request_sha256'} or type(pred['revision']) is not int or pred['revision']!=v['revision']-1 or type(pred['request_sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',pred['request_sha256']):raise Invalid('correction predecessor refused')
  v['payload']=validate_payload(v['payload']);return v
 except (ValueError,TypeError,UnicodeError,RecursionError,KeyError):raise Invalid('strict training submission refused') from None

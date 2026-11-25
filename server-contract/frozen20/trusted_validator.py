"""Independent trusted serialized-wire validation candidate. Stdlib; no IO except CLI/source codes.
Not installed in Auth ingest or production. No proportional allocation, no clinical carrier.
"""
from pathlib import Path
import json,re,datetime,sys
MAX=9007199254740991
SCHEMA='mhpss-5ws-session/0.4.0-approved-joint-review'
VERSION='nepal-joint-sex-age/1-approved-review'
AGES=('age04','age5to9','age10to17','age18to59','age60');SEX=('female','male','other','unknown')
DIS=('disF0_17','disM0_17','disF18','disM18');OF=('ofChildAlone','ofPreg','ofPwd','ofInjured','ofDistress')
REQUIRED=set('schema jointSexAgeVersion reviewMode reportingTypeVersion reportingType serviceSettingVersion serviceSetting deliveryModeVersion healthFacility ageBandVersion sexDisaggregationVersion status org province district palika site ward modality deliveryMode dateAD dateBS sessionTime backdateAcknowledged attendance sessionJointSexAge activities cadres targetGroups partners activityStatus description coordinationNotes disability ofWhom'.split())
OPTIONAL=set('orgOther districtOther modalityOther siteOther targetGroupsOther'.split())
CODES=json.loads((Path(__file__).parent/'codes.json').read_text())
def obj(x,required,optional=(),path='object'):
 if type(x) is not dict:raise ValueError(path+' must be object')
 unknown=set(x)-set(required)-set(optional);missing=set(required)-set(x)
 if unknown or missing:raise ValueError(path+': unexpected '+str(sorted(unknown))+' missing '+str(sorted(missing)))
def integer(v,path='count'):
 if type(v) is not int or not 0<=v<=MAX:raise ValueError(path+' requires safe nonnegative integer (no bool/float/coercion)')
 return v
def checked(xs):
 total=0
 for x in xs:
  integer(x)
  if x>MAX-total:raise ValueError('Checked sum overflow')
  total+=x
 return total
def text(v,path,limit,nullable=False):
 if nullable and v is None:return
 if type(v) is not str or len(v)>limit:raise ValueError(path+' invalid text')
def derive(matrix,attendance):
 integer(attendance,'attendance')
 if matrix is None:return {'knownSubtotal':None,'unknownSubtotal':attendance,'girls':None,'boys':None,'women':None,'men':None,'total':None,'sex':None,'age':None}
 obj(matrix,SEX,path='jointSexAge')
 for s in SEX:
  obj(matrix[s],AGES,path='jointSexAge.'+s)
  for a in AGES:integer(matrix[s][a],s+'.'+a)
 sex={s:checked(matrix[s][a] for a in AGES) for s in SEX};age={a:checked(matrix[s][a] for s in SEX) for a in AGES};total=checked(sex.values())
 if total!=attendance:raise ValueError('Joint total must equal own attendance including zero')
 return {'knownSubtotal':total,'unknownSubtotal':0,'total':total,'sex':sex,'age':age,'girls':checked(matrix['female'][a] for a in AGES[:3]),'boys':checked(matrix['male'][a] for a in AGES[:3]),'women':checked(matrix['female'][a] for a in AGES[3:]),'men':checked(matrix['male'][a] for a in AGES[3:])}
def members(name):return {x['code'] for x in CODES[name] if not x.get('retired')}
def array(x,path,nonempty=False):
 if type(x) is not list or (nonempty and not x):raise ValueError(path+' must be '+('nonempty ' if nonempty else '')+'array')
def unique(xs,path):
 if len(set(xs))!=len(xs):raise ValueError('Duplicates: '+path)
def _validate(r):
 obj(r,REQUIRED,OPTIONAL,'wire')
 versions={'schema':SCHEMA,'jointSexAgeVersion':VERSION,'ageBandVersion':'nepal-age-04-5to9-10to17-18to59-60/1','sexDisaggregationVersion':'nepal-sex-female-male-other-unknown/1','reviewMode':'GUIDE_ALIGNMENT_REVIEW','status':'PROPOSAL_REVIEW','reportingTypeVersion':'sormas-20260929-reporting-type/1-review','serviceSettingVersion':'edcd-20260917-setting/1-retained','deliveryModeVersion':'sormas-20260929-delivery/1-review'}
 for k,v in versions.items():
  if r[k]!=v:raise ValueError('Unsupported '+k)
 for k,c in [('org','ORGS'),('district','DISTRICTS'),('modality','MODALITIES'),('activityStatus','STATUS')]:
  if r[k] not in members(c):raise ValueError('Unsupported code '+k)
 if r['serviceSetting']!=r['modality']:raise ValueError('Service setting mismatch')
 districts={x['code']:x for x in CODES['DISTRICTS']}
 if r['province'] not in {x.get('province') for x in CODES['DISTRICTS']}:raise ValueError('Unsupported province')
 if districts[r['district']].get('province') and districts[r['district']]['province']!=r['province']:raise ValueError('District province mismatch')
 palikas={x['pcode']:x for x in CODES['PALIKAS']}
 if r['palika'] not in palikas or palikas[r['palika']]['district']!=r['district']:raise ValueError('Palika district mismatch')
 if r['ward'] is not None:
  if type(r['ward']) is not str or not re.fullmatch(r'[1-9][0-9]*',r['ward']) or int(r['ward'])>palikas[r['palika']].get('wards',0):raise ValueError('Invalid optional ward')
 if r['reportingType'] not in ['HOSPITAL','SHELTER','COMMUNITY_OUTREACH','OTHER']:raise ValueError('Invalid reporting type')
 if r['deliveryMode'] not in ['INDIVIDUAL_IN_PERSON','INDIVIDUAL_REMOTE','GROUP_IN_PERSON','GROUP_REMOTE']:raise ValueError('Invalid delivery mode')
 if r['reportingType']=='HOSPITAL':
  obj(r['healthFacility'],['directoryStatus','code','draftName'],path='healthFacility')
  if r['healthFacility']['directoryStatus']!='UNAVAILABLE' or r['healthFacility']['code'] is not None:raise ValueError('No invented facility directory')
  text(r['healthFacility']['draftName'],'draftName',220)
  if not r['healthFacility']['draftName'].strip():raise ValueError('Draft facility name required')
 elif r['healthFacility'] is not None:raise ValueError('Hidden facility payload refused')
 if r['reportingType']=='SHELTER':
  sites={x['code']:x for x in CODES['FORM_SITES'] if not x.get('retired')}
  if r['site']!='OTHER' and (r['site'] not in sites or sites[r['site']]['district']!=r['district'] or sites[r['site']]['palika']!=r['palika']):raise ValueError('Site geography mismatch')
 elif r['site'] is not None:raise ValueError('Hidden site payload refused')
 if type(r['backdateAcknowledged']) is not bool:raise ValueError('Date acknowledgement bool required')
 if type(r['dateAD']) is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',r['dateAD']):raise ValueError('AD date required')
 d=datetime.date.fromisoformat(r['dateAD']);today=datetime.date.today()
 if d>today:raise ValueError('Future session refused')
 if d!=today and not r['backdateAcknowledged']:raise ValueError('Backdate acknowledgement required')
 text(r['dateBS'],'dateBS',32,True)
 if r['sessionTime'] is not None and (type(r['sessionTime']) is not str or not re.fullmatch(r'(?:[01][0-9]|2[0-3]):[0-5][0-9]',r['sessionTime'])):raise ValueError('Invalid session time')
 text(r['description'],'description',1000);text(r['coordinationNotes'],'coordinationNotes',220)
 for k in OPTIONAL:
  if k in r:
   text(r[k],k,220)
   if not r[k].strip():raise ValueError('Blank '+k)
 conditions={'orgOther':r['org']=='OTHER','districtOther':r['district']=='OTH','modalityOther':r['modality']=='OTH','siteOther':r['reportingType'] in ['COMMUNITY_OUTREACH','OTHER'] or (r['reportingType']=='SHELTER' and r['site']=='OTHER'),'targetGroupsOther':type(r['targetGroups']) is list and 'TG-OTH' in r['targetGroups']}
 for k,condition in conditions.items():
  if condition!=(k in r):raise ValueError('Conditional text presence mismatch '+k)
 array(r['targetGroups'],'targetGroups');array(r['partners'],'partners')
 for x in r['targetGroups']:
  if type(x) is not str or x not in members('TARGET_GROUPS'):raise ValueError('Invalid target group')
 unique(r['targetGroups'],'targetGroups')
 for x in r['partners']:text(x,'partner organisation code/label',220)
 derived=derive(r['sessionJointSexAge'],r['attendance'])
 array(r['activities'],'activities',True);array(r['cadres'],'cadres',True)
 allowed={x['code']:x for x in CODES['ACTIVITIES'] if not x.get('retired') and x.get('group') not in ['5','6']}
 for a in r['activities']:
  obj(a,['code','attendance','jointSexAge'],['other'],'activity')
  if a['code'] not in allowed:raise ValueError('Invalid activity')
  derive(a['jointSexAge'],a['attendance'])
  if a['attendance']>r['attendance']:raise ValueError('Activity exceeds session attendance')
  if bool(allowed[a['code']].get('other'))!=('other' in a):raise ValueError('Activity Other presence mismatch')
  if 'other' in a:
   text(a['other'],'activity.other',160)
   if not a['other'].strip():raise ValueError('Other activity requires text')
  if a['jointSexAge'] is not None and r['sessionJointSexAge'] is not None:
   for s in SEX:
    for age in AGES:
     if a['jointSexAge'][s][age]>r['sessionJointSexAge'][s][age]:raise ValueError('Activity joint cell exceeds session: '+s+'.'+age)
 unique([a['code'] for a in r['activities']],'activities');checked(a['attendance'] for a in r['activities'])
 for c in r['cadres']:
  obj(c,['code','count'],['other'],'cadre');integer(c['count'],'cadre.count')
  if c['code'] not in members('CADRES'):raise ValueError('Invalid cadre')
  if (c['code']=='OTH')!=('other' in c):raise ValueError('Cadre Other presence mismatch')
  if 'other' in c:
   text(c['other'],'cadre.other',160)
   if not c['other'].strip():raise ValueError('Other cadre requires text')
 unique([c['code'] for c in r['cadres']],'cadres');checked(c['count'] for c in r['cadres'])
 obj(r['ofWhom'],OF,path='ofWhom')
 for k,v in r['ofWhom'].items():
  if v is not None:
   integer(v,k)
   if v>r['attendance']:raise ValueError('Subset exceeds attendance '+k)
 if r['disability'] is not None:
  if 'TG-DIS' not in r['targetGroups']:raise ValueError('Hidden disability hold')
  obj(r['disability'],['asked','counts'],path='disability');obj(r['disability']['counts'],DIS,path='disability.counts')
  if r['disability']['asked'] not in ['', 'Y','N']:raise ValueError('Asked status invalid')
  bounds=dict(zip(DIS,[derived['girls'],derived['boys'],derived['women'],derived['men']]))
  for k,v in r['disability']['counts'].items():
   if v is not None:
    integer(v,k)
    if bounds[k] is not None and v>bounds[k]:raise ValueError('Corresponding disability subset bound '+k)
  if checked(v for v in r['disability']['counts'].values() if v is not None)>r['attendance']:raise ValueError('Disability known sum exceeds attendance')
 elif 'TG-DIS' in r['targetGroups']:raise ValueError('Selected disability requires asked/counts object with nullable counts')
 return derived

def validate(record):
 try:_validate(record);return []
 except (ValueError,KeyError,TypeError,OverflowError) as e:return [str(e)]
if __name__=='__main__':
 r=json.loads(Path(sys.argv[1]).read_text());errors=validate(r);print(json.dumps({'valid':not errors,'errors':errors,'derived':None if errors else derive(r['sessionJointSexAge'],r['attendance'])},indent=2));sys.exit(bool(errors))

"""Referral Directory service point, form v2.2 (np-directory-0.2, 19 Nov 2026).
Service types follow MSP Tool 3B plus the Protection Cluster referral pathway; cadre, age and target
group lists are the EDCD-approved 5Ws lists. Fields arrive as the form's FormData plus computed keys;
unknown keys are refused, optional text may be absent or empty."""
import copy,json,re
from datetime import date,datetime,timedelta,timezone
from training_contract import Invalid,digest,text,count,geography
from frozen20.trusted_validator import CODES,members
SCHEMA='np-directory-0.2'
SERVICES={str(n) for n in range(1,11)}
CROSS={'CM-GBV','CM-CP','CMR','SAFEHOUSE','CHILDSHELTER','LEGAL','LJC','POLICE','HOTLINE','REHAB','TRACING'}
SENSITIVE_CROSS={'SAFEHOUSE','CHILDSHELTER'}
OTHER={'Housing or shelter repair','Livelihood or skills','Cash or financial assistance','Material assistance (non-food items)','Nutrition','Education','Physical health care','Physical rehabilitation'}
TRAINING={'PFA','MHGAP','MANUAL','CM','CMR','NONE'}
FACILITY={'FAC-HF':'FAC','FAC-GOV':'FAC','HC':'HC','ORG':'OTH','COM':'COM','TEL':'TEL','OTH':'OTH'}
LISTS={'services','crossServices','otherServices','cadres','gender','age','groups','delivery','entry','refVia','training','missingRoles','mspActivities'}
REQUIRED={'schema','id','savedOn','org','province','district','palika','placeName','facility','pinVisibility','refPhone','hours','cost','status','continuity',
          'consentPublish','consentCorrect','lat','lng','pinAccuracyM','edcdSetting','integrated'}|LISTS
OPTIONAL_TEXT={'orgOther':160,'partners':300,'ward':2,'serviceOther':300,'capacity':10,'details':2000,'criteria':300,'languages':200,'access':1000,
               'refEmail':200,'refName':120,'until':7,'untilUnknown':3,'funder':200,'from':7,'mspMapping':3,'manualName':200,'supervision':10,
               'barriers':2000,'confName':120,'confRole':120,'focalEmail':200,'recordedBy':254}
EMAIL=re.compile(r'[A-Za-z0-9_+.-]+@[A-Za-z0-9-]+(?:[.][A-Za-z0-9-]+)+')


def _codes(name):return {x['code'] for x in CODES[name] if not x.get('retired')}


def _list(p,k,allowed):
    v=p[k]
    if type(v) is not list or len(v)>40 or any(type(x) is not str or x not in allowed for x in v) or len(set(v))!=len(v):raise Invalid('code list refused: '+k)


def _month(v):
    if v=='':return
    if type(v) is not str or not re.fullmatch(r'20[2-4][0-9]-(0[1-9]|1[0-2])',v):raise Invalid('month refused')


def validate_payload(p):
    if type(p) is not dict:raise Invalid('object required')
    keys=set(p)
    if not REQUIRED<=keys:raise Invalid('required directory fields missing')
    if not keys<=REQUIRED|set(OPTIONAL_TEXT)|{'staff'}:raise Invalid('unknown directory field')
    if p['schema']!=SCHEMA:raise Invalid('directory instrument required')
    if type(p['id']) is not str or not re.fullmatch(r'SP[A-Z0-9]{1,14}',p['id']):raise Invalid('device record id refused')
    for k,n in OPTIONAL_TEXT.items():
        if k in p:text(p[k],0,n)
    for k in ['placeName','refPhone','hours']:text(p[k],1,300)
    if p['org'] not in members('ORGS'):raise Invalid('organisation refused')
    if (p['org']=='OTHER')!=bool(p.get('orgOther','')):raise Invalid('other organisation name mismatch')
    geography(p['district'],p['palika'])
    if p['province'] not in {d.get('province') for d in CODES['DISTRICTS'] if d['code']==p['district']}:raise Invalid('province refused')
    if p.get('ward','')!='' and not re.fullmatch(r'[1-9][0-9]?',p['ward']):raise Invalid('ward refused')
    if p['facility'] not in FACILITY or p['edcdSetting']!=FACILITY[p['facility']]:raise Invalid('setting refused')
    if type(p['integrated']) is not bool or p['integrated']!=(p['facility'] in {'FAC-HF','FAC-GOV'} and p['continuity']=='permanent'):raise Invalid('integration flag refused')
    choices={'pinVisibility':{'public','palika','internal'},'cost':{'FREE','SOME','FEE'},'status':{'running','planned','paused'},'continuity':{'permanent','project','unknown'}}
    for k,allowed in choices.items():
        if p[k] not in allowed:raise Invalid('code refused: '+k)
    if p.get('capacity','') not in {'','open','waiting','full'} or p.get('supervision','') not in {'','yes','no','unknown'}:raise Invalid('code refused')
    if p.get('untilUnknown','') not in {'','yes'} or p.get('mspMapping','') not in {'','yes'}:raise Invalid('flag refused')
    _month(p.get('until',''));_month(p.get('from',''))
    if p['consentPublish']!='on' or p['consentCorrect']!='on':raise Invalid('confirmation required')
    if p.get('recordedBy','') and not re.fullmatch(r'[a-z0-9_+.-]+@[a-z0-9-]+(?:[.][a-z0-9-]+)+',p['recordedBy']):raise Invalid('recorder email refused')
    for k in ['refEmail','focalEmail']:
        if p.get(k,'') and not EMAIL.fullmatch(p[k]):raise Invalid('email refused')
    if not re.fullmatch(r'[0-9+()/. -]{4,80}',p['refPhone']):raise Invalid('phone refused')
    cadres=_codes('CADRES')-{'OTH'}
    _list(p,'services',SERVICES);_list(p,'crossServices',CROSS);_list(p,'otherServices',OTHER);_list(p,'cadres',cadres)
    _list(p,'gender',{'women','men','girls','boys'});_list(p,'age',{'0-4','5-9','10-17','18-59','60+'});_list(p,'groups',_codes('TARGET_GROUPS'))
    _list(p,'delivery',{'atplace','outreach','remote'});_list(p,'entry',{'walkin','appointment','referral'});_list(p,'refVia',{'phone','email','inperson','form'})
    _list(p,'training',TRAINING);_list(p,'missingRoles',cadres|{'CASEMGR','MEDLEGAL','FEMALE'})
    _list(p,'mspActivities',{'3.5','3.6','3.8','3.9','3.10','3.11','3.12','3.13','3.14'})
    if not p['services'] and not p['crossServices']:raise Invalid('at least one service required')
    if ('10' in p['services'])!=bool(p.get('serviceOther','')):raise Invalid('other service description mismatch')
    if not p['gender'] or not p['age']:raise Invalid('who the service is for is required')
    sensitive='4' in p['services'] or bool(set(p['crossServices'])&SENSITIVE_CROSS)
    if sensitive and p['pinVisibility']=='public':raise Invalid('exact pin of a safe space is never public')
    if p['continuity']=='project' and not p.get('until','') and p.get('untilUnknown','')!='yes':raise Invalid('funding end or unknown required')
    msp=p.get('mspMapping','')=='yes'
    if msp:
        st=p.get('staff',{})
        if type(st) is not dict or len(st)>20 or any(k not in cadres or type(v) is not dict or set(v)!={'ft','pt'} for k,v in st.items()):raise Invalid('staff counts refused')
        for v in st.values():count(v['ft'],0,99);count(v['pt'],0,99)
    else:
        if 'staff' in p or p['training'] or p['missingRoles'] or any(p.get(k,'') for k in ['supervision','barriers','manualName']):raise Invalid('MSP answers without MSP mapping')
    for k,lo,hi in [('lat',26.0,30.6),('lng',80.0,88.3)]:
        if type(p[k]) not in (int,float) or not lo<=p[k]<=hi:raise Invalid('pin outside Nepal')
    if p['pinAccuracyM'] is not None:count(p['pinAccuracyM'],0,100000)
    try:
        d=date.fromisoformat(p['savedOn'])
        if d.isoformat()!=p['savedOn'] or not date(2026,11,1)<=d<=datetime.now(timezone.utc).date()+timedelta(days=1):raise ValueError()
    except (ValueError,TypeError):raise Invalid('save date refused') from None
    return copy.deepcopy(p)


def parse(raw):
    def pairs(items):
        o={}
        for k,v in items:
            if k in o:raise Invalid('duplicate key')
            o[k]=v
        return o
    try:
        v=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Invalid('nonfinite')))
        if type(v) is not dict or set(v)!={'protocol','reportId','revision','predecessor','payload'} or v['protocol']!='directory-submit/2':raise Invalid('exact envelope required')
        if type(v['reportId']) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',v['reportId']):raise Invalid('report identity refused')
        count(v['revision'],1,500);pred=v['predecessor']
        if v['revision']==1:
            if pred is not None:raise Invalid('initial predecessor refused')
        elif type(pred) is not dict or set(pred)!={'revision','request_sha256'} or pred['revision']!=v['revision']-1 or type(pred['request_sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',pred['request_sha256']):raise Invalid('predecessor refused')
        v['payload']=validate_payload(v['payload']);return v
    except (ValueError,TypeError,UnicodeError,RecursionError,KeyError):raise Invalid('strict directory submission refused') from None

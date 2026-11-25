"""Exact Grief Early Assessment record (np-grief-early-0.2), owner decisions of 19 Nov 2026.
Adults only; registration by name (contact kept with the recording organisation) or anonymous with
a device-generated code; no score; safety answer forces the red-flag view. Unknown keys are refused."""
import copy,json,re
from datetime import date,datetime,timedelta,timezone
from training_contract import Invalid,digest,text,count,geography
from frozen20.trusted_validator import CODES,members
SCHEMA='np-grief-early-0.2'
# 20 Nov 2026 (owner decision): Grief Conversation adds an observed state right now and an optional
# Nepal PHQ-9 (Kohrt et al. 2016, validated Nepali wording, 4-level scale 0-3, total 0-27). Records of
# 0.2 already queued on phones stay valid.
NEW='np-grief-early-0.3'
SCHEMAS={SCHEMA,NEW}
STATE={'calm','upset','overwhelmed','confused'}
BASE={'schema','id','code','date','org','district','palika','ward','setting','worker','consent'}
ANSWERS={'sex','age','living','disability','who','nDied','nMissing','otherLoss','rites','obstacles','ritesHelp','rx','functioning','beyondExpected','support','needs','selfharm','childLostCarer','triage','action','refTo','refAccepted','reg'}
CONTACT={'name','phone','reach','bestTime'}
RX=['sad','yearn','intrusive','sleep','appetite','concentr','withdraw','body','voice','anger','compare']
ONE={'sex':{'F','M','O'},'age':{'18-59','60+'},'living':{'','home','displaced'},'disability':{'','yes','no','ns'},
     'rites':{'completed','adapted','waiting','blocked','na'},'ritesHelp':{'','yes','no','notnow'},
     'functioning':{'usual','difficulty','unable'},'beyondExpected':{'','yes','no','unsure'},
     'selfharm':{'no','yes','notasked'},'childLostCarer':{'','no','yes'},'triage':{'normal','acute','ptsd','redflag'},
     'refAccepted':{'','yes','no'},'reg':{'byname','anon'}}
MANY={'who':{'spouse','child','parent','sibling','relative','friend','none'},
      'otherLoss':{'house','land','livestock','livelihood','community','documents'},
      'obstacles':{'nobody','cost','priest','place','displaced','timing','other'},
      'support':{'family','neighbours','religious','group','org','nobody'},
      'needs':{'rites','news','talk','group','livelihood','health','documents','safety'},
      'action':{'listened','followup','referred','urgent'},
      'refTo':{'counsellor','mhgap','specialist','cp','protection','other'}}
SETTINGS={'HOME','GROUP','IND','HF','HC','OTH'}
CODE=re.compile(r'([A-Z]{2,12})-([A-Z]{3})-([0-9]{6})-[A-Z2-9]{3}-[0-9]{2,3}')


def _choices(p,k,allowed,required=True):
    v=p[k]
    if type(v) is not list or len(v)>len(allowed) or any(type(x) is not str or x not in allowed for x in v) or len(set(v))!=len(v):raise Invalid('code list refused: '+k)
    if required and not v:raise Invalid('answer required: '+k)


def validate_payload(p):
    if type(p) is not dict:raise Invalid('object required')
    keys=set(p)
    if not BASE<=keys:raise Invalid('base fields required')
    if p.get('schema') not in SCHEMAS:raise Invalid('grief instrument required')
    v3=p.get('schema')==NEW
    yes=p.get('consent')=='yes'
    if p.get('consent') not in {'yes','no','later'}:raise Invalid('consent code refused')
    keys=keys-{'recordedBy'}
    if 'recordedBy' in p:
        # Who filled the form in (decision 2A, 19 Nov 2026): may differ from the account that sends it,
        # e.g. a borrowed phone without signal. Declared, not verified; the sender account is kept separately.
        if type(p['recordedBy']) is not str or len(p['recordedBy'])>254 or not re.fullmatch(r'[a-z0-9_+.-]+@[a-z0-9-]+(?:[.][a-z0-9-]+)+',p['recordedBy']):raise Invalid('recorder email refused')
    if not yes:
        if keys!=BASE:raise Invalid('a declined conversation keeps the base fields only')
    else:
        req=ANSWERS|({'stateNow'} if v3 else set())
        extra=keys-BASE-req
        reg=p.get('reg')
        allowed_extra=(CONTACT if reg=='byname' else {'initials'} if reg=='anon' else set())|({'phq9'} if v3 else set())
        if not req<=keys or not extra<=allowed_extra:raise Invalid('exact grief fields required')
    if p['org'] not in members('ORGS') or p['org']=='OTHER':raise Invalid('known organisation required')
    geography(p['district'],p['palika'])
    if p['ward']!='':
        if type(p['ward']) is not str or not re.fullmatch(r'[1-9][0-9]?',p['ward']):raise Invalid('ward refused')
        pal=next(x for x in CODES['PALIKAS'] if x['pcode']==p['palika'])
        if pal.get('wards') and int(p['ward'])>pal['wards']:raise Invalid('ward beyond palika')
    if p['setting'] not in SETTINGS:raise Invalid('setting code refused')
    if p['worker'] not in {x['code'] for x in CODES['CADRES']} or p['worker']=='OTH':raise Invalid('worker role refused')
    try:
        d=date.fromisoformat(p['date'])
        if d.isoformat()!=p['date'] or not date(2026,8,26)<=d<=datetime.now(timezone.utc).date()+timedelta(days=1):raise ValueError()
    except (ValueError,TypeError):raise Invalid('conversation date refused') from None
    if type(p['id']) is not str or not re.fullmatch(r'G[A-Z0-9]{4,20}',p['id']):raise Invalid('device record id refused')
    m=CODE.fullmatch(p['code']) if type(p['code']) is str else None
    if not m or m.group(1)!=p['org'] or m.group(2)!=p['district'] or m.group(3)!=p['date'][2:].replace('-',''):raise Invalid('conversation code refused')
    if yes:
        for k,allowed in ONE.items():
            if p[k] not in allowed:raise Invalid('answer code refused: '+k)
        for k,allowed in MANY.items():
            _choices(p,k,allowed,required=k in {'who','support','action'})
        if len(p['needs'])>3:raise Invalid('up to three needs')
        if 'none' in p['who'] and len(p['who'])>1:raise Invalid('none excludes other losses')
        count(p['nDied'],0,30);count(p['nMissing'],0,30)
        if p['rites'] not in {'waiting','blocked'} and p['obstacles']:raise Invalid('obstacles only when ceremonies wait')
        rx=p['rx']
        if type(rx) is not dict or set(rx)!=set(RX) or any(type(v) is not int or v not in (0,1,2) for v in rx.values()):raise Invalid('reactions refused')
        if p['selfharm']=='yes' and p['triage']!='redflag':raise Invalid('safety answer requires the red-flag view')
        if v3:
            if p['stateNow'] not in STATE:raise Invalid('state code refused')
            if 'phq9' in p:
                q=p['phq9']
                if type(q) is not dict or set(q)!={'items','score'}:raise Invalid('phq9 refused')
                it=q['items']
                if type(it) is not list or len(it)!=9 or any(type(v) is not int or v not in (0,1,2,3) for v in it):raise Invalid('phq9 items refused')
                if type(q['score']) is not int or q['score']!=sum(it):raise Invalid('phq9 score refused')
                if it[8]>0 and p['triage']!='redflag':raise Invalid('phq9 item 9 requires the red-flag view')
        if not set(p['action'])&{'referred','urgent'} and (p['refTo'] or p['refAccepted']):raise Invalid('referral detail without referral')
        if p['reg']=='byname':
            text(p['name'],1,120);text(p['bestTime'],0,120)
            if p['reach'] not in {'','call','visit','trusted'}:raise Invalid('reach code refused')
            if p['phone']!='' and (type(p['phone']) is not str or not re.fullmatch(r'[0-9+()/. -]{6,40}',p['phone'])):raise Invalid('phone refused')
            if p['phone']=='' and p['reach']!='visit':raise Invalid('phone required unless a home visit')
        else:
            ini=p.get('initials','')
            if type(ini) is not str or not re.fullmatch(r'[A-Z]{0,4}',ini):raise Invalid('initials refused')
    return copy.deepcopy(p)


def public_view(p):
    """What a reader of the organisation's own list sees: everything, contact included."""
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
        if type(v) is not dict or set(v)!={'protocol','reportId','revision','predecessor','payload'} or v['protocol']!='grief-submit/1':raise Invalid('exact envelope required')
        if type(v['reportId']) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',v['reportId']):raise Invalid('report identity refused')
        count(v['revision'],1,50);pred=v['predecessor']
        if v['revision']==1:
            if pred is not None:raise Invalid('initial predecessor refused')
        elif type(pred) is not dict or set(pred)!={'revision','request_sha256'} or pred['revision']!=v['revision']-1 or type(pred['request_sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}',pred['request_sha256']):raise Invalid('predecessor refused')
        v['payload']=validate_payload(v['payload']);return v
    except (ValueError,TypeError,UnicodeError,RecursionError,KeyError):raise Invalid('strict grief submission refused') from None


def summarise(records,minimum=5):
    """Totals per palika for coordination. Palikas below `minimum` conversations are counted in the
    overall totals but returned without a name. No row, code, name or phone leaves this function."""
    by={};total={'conversations':0,'declined':0,'missing':0,'ritesPending':0,'redFlags':0,'referred':0,'phq9Done':0,'phq9Ten':0,'stateSevere':0}
    obstacles={};needs={};rx={k:0 for k in RX};withObstacle=0
    for p in records:
        g=by.setdefault(p['palika'],{'district':p['district'],'n':0,'declined':0,'missing':0,'ritesPending':0,'dailyLifeAffected':0,'referred':0,'obstacles':{},'needs':{}})
        if p['consent']!='yes':
            g['declined']+=1;total['declined']+=1;continue
        g['n']+=1;total['conversations']+=1
        pend=p['rites'] in {'waiting','blocked'}
        ref=bool(set(p['action'])&{'referred','urgent'})
        for key,flag in [('missing',p['nMissing']>0),('ritesPending',pend),('referred',ref)]:
            if flag:g[key]+=1;total[key]+=1
        if p['functioning']!='usual':g['dailyLifeAffected']+=1
        if p['triage']=='redflag':total['redFlags']+=1
        if p.get('stateNow') in {'overwhelmed','confused'}:total['stateSevere']+=1
        if 'phq9' in p:
            total['phq9Done']+=1
            if p['phq9']['score']>=10:total['phq9Ten']+=1
        if p['obstacles']:withObstacle+=1
        for o in p['obstacles']:g['obstacles'][o]=g['obstacles'].get(o,0)+1;obstacles[o]=obstacles.get(o,0)+1
        for o in p['needs']:g['needs'][o]=g['needs'].get(o,0)+1;needs[o]=needs.get(o,0)+1
        for k in RX:
            if p['rx'][k]==2:rx[k]+=1
    if total['conversations']<minimum:
        return {'protocol':'grief-summary/1','minimum':minimum,'suppressed':True,'palikas':[],'palikasHidden':len(by)}
    shown=[];hidden=0
    for code,g in sorted(by.items()):
        if g['n']<minimum:hidden+=1;continue
        shown.append({'palika':code,**g})
    return {'protocol':'grief-summary/1','minimum':minimum,'suppressed':False,'totals':total,'palikas':shown,'palikasHidden':hidden,
            'reactionsMostDays':rx,'obstacles':obstacles,'conversationsWithObstacle':withObstacle,'needs':needs}

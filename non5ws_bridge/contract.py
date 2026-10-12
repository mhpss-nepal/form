"""Pure receiving boundary; no network, persistence, grants or 5Ws projection.

A mapping result is NOT an accepted submission or backend acknowledgement.
"""
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal, TypedDict, overload, cast

Instrument = Literal['training', 'service_contact', 'referral', 'service_point', 'provider', 'phq9', 'self_report']

class Participant(TypedDict):
    district: str
    palika: str
    cadre: str
    female: int
    male: int
    other: int
    total: int

class TrainingRecord(TypedDict):
    kind: Literal['training']
    schema: str
    org: str
    reporting_role: Literal['LEAD', 'PARTNER']
    counts_held_by_lead: bool
    participants: list[Participant]
    trained_total: int
    under_18: int | None
    with_disability: int | None

@dataclass(frozen=True)
class Received:
    instrument: Instrument
    collection: str
    unit: str
    grain: str
    classification: str
    payload: dict[str, Any]
    metrics: dict[str, int | None]
    warnings: tuple[str, ...] = ()

class ContractError(ValueError):
    pass

MAPPINGS = {
    'training': ('mhpss-np-training/0.1.0-draft', 'training_events', 'people-trained-per-event', 'one training event; participant rows palika+cadre', 'internal-service'),
    'service_contact': ('mhpss-np-contact/0.1.0-draft', 'clinical_contacts', 'contact', 'one service contact with optional referral', 'restricted-clinical'),
    'referral': ('mhpss-np-referral-outcome/0.1.0-draft', 'clinical_referral_outcomes', 'referral-outcome', 'one outcome joined by org+contact_code+referral date', 'restricted-clinical'),
    'service_point': ('dir-sp-0.1.0', 'service_point_registrations', 'registration', 'one organisation service location', 'internal-directory-review'),
    'provider': ('dir-pv-0.1.0', 'provider_registrations', 'registration', 'one self-registered provider', 'restricted-directory-review'),
    'phq9': ('mhpss-np-phq9/0.1.0-draft', 'clinical_phq9', 'administration', 'one PHQ-9 administration', 'restricted-clinical'),
    'self_report': ('mhpss-np-selfreport/0.1.0-draft', 'anonymous_feedback', 'response', 'one anonymous response; no person join', 'restricted-unreviewed-feedback'),
}

@overload
def count(value: Any, name: str, nullable: Literal[False] = False) -> int: ...
@overload
def count(value: Any, name: str, nullable: Literal[True]) -> int | None: ...
def count(value: Any, name: str, nullable: bool = False) -> int | None:
    if nullable and value is None:
        return None
    if type(value) is not int or value < 0:
        raise ContractError(f'{name}: whole nonnegative integer required; unknown is null')
    return value

def adapt(raw: dict[str, Any]) -> Received:
    kind = raw.get('kind')
    if kind not in MAPPINGS:
        raise ContractError('unsupported instrument; never route to 5Ws')
    schema, collection, unit, grain, classification = MAPPINGS[kind]
    if raw.get('schema') != schema:
        raise ContractError('schema does not match instrument')
    payload = deepcopy(raw)
    metrics: dict[str, int | None] = {}
    warnings = []
    if kind == 'training':
        total = count(raw.get('trained_total'), 'trained_total')
        if raw.get('reporting_role') not in ('LEAD', 'PARTNER'):
            raise ContractError('explicit reporting role required')
        partner = raw['reporting_role'] == 'PARTNER'
        if raw.get('counts_held_by_lead') is not partner:
            raise ContractError('reporting role and held-count flag disagree')
        rows = raw.get('participants')
        if not isinstance(rows, list):
            raise ContractError('participants must be rows')
        if partner:
            if rows or total != 0 or raw.get('under_18') is not None or raw.get('with_disability') is not None:
                raise ContractError('partner reports must carry no participant counts')
            metrics = {'trained_total': None, 'under_18': None, 'with_disability': None}
        else:
            seen = set()
            for row in rows:
                key = (row.get('district'), row.get('palika'), row.get('cadre'))
                if not all(key) or key in seen:
                    raise ContractError('participant location/cadre required and unique')
                seen.add(key)
                sexes = [count(row.get(s), s) for s in ('female', 'male', 'other')]
                n = count(row.get('total'), 'row.total')
                if n != sum(sexes) or n == 0:
                    raise ContractError('row total must equal sex counts and be positive')
            if not rows or total != sum(row['total'] for row in rows):
                raise ContractError('event total must equal participant rows')
            metrics['trained_total'] = total
            for field in ('under_18', 'with_disability'):
                n = count(raw.get(field), field, nullable=True)
                if n is not None and n > total:
                    raise ContractError(f'{field} exceeds trained_total')
                metrics[field] = n
    if kind in ('service_contact', 'self_report'):
        age = raw.get('age_band')
        if age not in ('', None, '0-4', '5-9', '10-17', '18-59', '60+', 'NS', '10-19', '20-59'):
            raise ContractError('unrecognised age band')
        if age in ('10-19', '20-59'):
            warnings.append('legacy-age-band-preserved; cannot infer under-18 count')
    if kind == 'self_report':
        if raw.get('anonymous') is not True or raw.get('contact_code') is not None:
            raise ContractError('anonymous response must not carry person linkage')
        if any(raw.get(k) for k in ('name', 'phone', 'email', 'org', 'providerName', 'contactCode', 'user_id')):
            raise ContractError('identity field forbidden in anonymous response')
        if raw.get('free_text'):
            warnings.append('free text may identify someone; human review required before display')
    if kind == 'referral' and raw.get('record_type') != 'outcome':
        raise ContractError('legacy referral event is not an outcome; separate migration required')
    if kind == 'phq9':
        items = [count(raw.get(f'q{i}'), f'q{i}') for i in range(1, 10)]
        if any(n > 3 for n in items) or raw.get('total') != sum(items):
            raise ContractError('PHQ-9 complete item range and total required')
        if raw.get('item9_positive') is not (items[8] > 0) or raw.get('is_diagnosis') is not False:
            raise ContractError('PHQ-9 safety flags disagree')
    return Received(kind, collection, unit, grain, classification, payload, metrics, tuple(warnings))

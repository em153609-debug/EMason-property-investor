"""Safe, evidence-aware import of RentCast property lookup into underwriting assumptions.

No AVM is assumed to be a renovated ARV, and past sale prices are never
represented as current asking prices.
"""
from dataclasses import dataclass
from typing import Optional

KINDS = ('Single Family', 'Duplex', 'Triplex', 'Fourplex')

@dataclass(frozen=True)
class PropertyImport:
    property_type: Optional[str]
    asking_price: Optional[float]
    rent_estimate: Optional[float]
    value_estimate: Optional[float]
    asking_source: str
    notes: tuple[str, ...]


def money(value):
    """Accept numeric provider amounts but reject text/missing/invalid/nonpositive values."""
    if isinstance(value, bool):
        return None
    try:
        v = float(value)
    except (ValueError, TypeError):
        return None
    if not (0 < v < float('inf')):
        return None
    return v


def infer_kind(record):
    units = record.get('units')
    if isinstance(units, list):
        unit_count = len(units)
    else:
        try:
            unit_count = int(units)
        except (TypeError, ValueError):
            unit_count = None
    if unit_count in (2,3,4):
        return KINDS[unit_count-1]
    value = str(record.get('propertyType') or record.get('propertySubType') or '').casefold().replace('-', ' ')
    if 'fourplex' in value or 'quadplex' in value or '4 unit' in value:
        return 'Fourplex'
    if 'triplex' in value or '3 unit' in value:
        return 'Triplex'
    if 'duplex' in value or '2 unit' in value:
        return 'Duplex'
    if 'single family' in value or 'singlefamily' in value:
        return 'Single Family'
    if unit_count == 1 and ('residential' in value or 'single' in value):
        return 'Single Family'
    return None


def import_property_results(result):
    """Read provider response; only explicit current asking/list prices qualify.

    RentCast property records are not necessarily active sale listings; their
    `lastSalePrice` is intentionally never read as the asking price.
    """
    records = result.get('property') or []
    rec = records[0] if isinstance(records, list) and records and isinstance(records[0], dict) else {}
    val = result.get('value') if isinstance(result.get('value'), dict) else {}
    rental = result.get('rent') if isinstance(result.get('rent'), dict) else {}
    notes = []
    ask = None
    asking_source = 'Not available — enter current listing/offer price'
    for field in ('listingPrice', 'listPrice', 'askingPrice'):
        amount = money(rec.get(field))
        if amount is not None:
            ask = amount
            asking_source = f'Current asking price from property record ({field}); verify listing status'
            break
    if ask is None:
        notes.append('Current asking price was not supplied. Last sale price is not a current listing price.')
    kind = infer_kind(rec)
    if kind is None:
        notes.append('Property type could not be confidently identified; select it manually.')
    r = money(rental.get('rent'))
    if r is None:
        notes.append('Provider rent estimate unavailable; enter a supported rent assumption.')
    v = money(val.get('price')) or money(val.get('value'))
    if v is None:
        notes.append('Provider value estimate unavailable; derive ARV from renovated comps.')
    else:
        notes.append('Value AVM is not verified after-repair value (ARV). Apply it only deliberately.')
    return PropertyImport(kind,ask,r,v,asking_source,tuple(notes))


def apply_new_subject(deal, imported):
    """Clear prior subject numbers and evidence, preserve financing/risk preferences.

    Does not assume incoming source data is verified or change rehab scope.
    """
    deal.kind = imported.property_type or 'Single Family'
    deal.units = KINDS.index(deal.kind) + 1
    deal.price = imported.asking_price or 0.0
    deal.arv = 0.0
    deal.rent = imported.rent_estimate or 0.0
    deal.arv_confidence = 'Unverified'
    deal.rent_confidence = 'Unverified'
    return deal

"""Transparent, conservative comparable-property calculations; not an appraisal."""
from datetime import date, datetime
from statistics import median
from math import isfinite


def _positive(x):
    try:
        v = float(x)
        return v if isfinite(v) and v > 0 else None
    except (TypeError, ValueError):
        return None


def _months_since(value, as_of=None):
    if not value:
        return None
    try:
        dt = date.fromisoformat(str(value)[:10])
        today = as_of or date.today()
        return max(0, (today - dt).days / 30.44)
    except ValueError:
        return None


def evaluate_comps(records, kind, subject_sqft=None, subject_beds=None, as_of=None, max_age_months=12, max_radius_miles=None, require_known_distance=False):
    """Use only explicitly included, valid comps; return suggested range + auditable exclusions.

    Rows: address, amount, sqft, bedrooms, date, renovated, include. Sale comps
    MUST have renovated=True to count toward the renovated ARV suggestion.
    Rental comparables use monthly rent as amount (not price/sqft valuation).
    """
    subject_sqft = _positive(subject_sqft)
    selected, rejected = [], []
    for row in records:
        if not row.get('include', True):
            continue
        address = str(row.get('address') or 'Unspecified comp')
        amount = _positive(row.get('amount'))
        sqft = _positive(row.get('sqft'))
        months = _months_since(row.get('date'), as_of)
        if not amount:
            rejected.append((address, 'Missing or invalid sale price / monthly rent'))
            continue
        if kind == 'sale' and not row.get('renovated', False):
            rejected.append((address, 'Not verified as renovated / comparable condition'))
            continue
        if months is None:
            rejected.append((address, 'Missing valid sale/listing date'))
            continue
        if months > max_age_months:
            rejected.append((address, f'Older than {max_age_months} months'))
            continue
        distance = row.get('distance_miles')
        if max_radius_miles is not None:
            try:
                distance = float(distance) if distance is not None and str(distance).strip() else None
            except (ValueError, TypeError):
                distance = None
            if distance is None and require_known_distance:
                rejected.append((address, 'Distance unknown — cannot verify radius'))
                continue
            if distance is not None and distance > max_radius_miles:
                rejected.append((address, f'Beyond {max_radius_miles:g}-mile search radius'))
                continue
        if subject_sqft and sqft and not (.70 <= sqft / subject_sqft <= 1.30):
            rejected.append((address, 'Size outside 70–130% subject range'))
            continue
        beds = row.get('bedrooms')
        if subject_beds is not None and beds is not None:
            try:
                if abs(float(beds) - float(subject_beds)) > 1:
                    rejected.append((address, 'Bedroom difference greater than one'))
                    continue
            except (TypeError, ValueError):
                pass
        if kind == 'sale' and (not subject_sqft or not sqft):
            rejected.append((address, 'Square footage required for renovated ARV adjustment'))
            continue
        adjusted = amount * subject_sqft / sqft if kind == 'sale' else amount
        selected.append(dict(address=address, amount=amount, adjusted=adjusted, age_months=round(months,1), sqft=sqft, distance_miles=distance))
    values = sorted(c['adjusted'] for c in selected)
    n = len(values)
    if n:
        # Range of observed eligible comp indications, not a confidence interval.
        result = dict(estimate=median(values), low=values[0], high=values[-1])
    else:
        result = dict(estimate=None, low=None, high=None)
    recent = sum(c['age_months'] <= 6 for c in selected)
    if n >= 3 and recent >= 2:
        confidence = 'Moderate — verify proximity, condition and concessions'
    elif n:
        confidence = 'Low — too few recent eligible comparables'
    else:
        confidence = 'Insufficient evidence'
    return dict(**result, count=n, recent_count=recent, confidence=confidence,
                selected=selected, rejected=rejected,
                disclaimer='Not an appraisal. Radius is enforced only on measured coordinates or analyst-entered distance. No lot, basement, bathroom, condition-quality or concession adjustments are automated.')

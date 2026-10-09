"""RentCast AVM comparable-candidate normalization. Never labels a candidate verified."""
from datetime import datetime


def _date(value):
    if not value:
        return ''
    try:
        return datetime.fromisoformat(str(value)[:10]).date().isoformat()
    except ValueError:
        return ''


def normalize_avm_candidates(response, kind, subject_address='', max_rows=25):
    """Return editable evidence rows, not certified sale/lease comps.

    RentCast AVM comps are listing records, which may include asking/listing prices.
    A listing date or lastSeenDate does NOT establish an actual closing date.
    """
    if kind not in ('sale', 'rent'):
        raise ValueError('kind must be sale or rent')
    comps = response.get('comparables') or [] if isinstance(response, dict) else []
    result = []
    seen = set()
    for record in comps:
        if not isinstance(record, dict):
            continue
        addr = str(record.get('formattedAddress') or record.get('address') or '').strip()
        if not addr or addr.casefold() == str(subject_address).strip().casefold() or addr.casefold() in seen:
            continue
        amount = record.get('price') if kind == 'sale' else record.get('price', record.get('rent'))
        try:
            amount = float(amount)
            if amount <= 0:
                continue
        except (ValueError, TypeError):
            continue
        sqft = record.get('squareFootage') or 0
        bedrooms = record.get('bedrooms')
        row = {
            'include': False,  # always explicitly opt in after review
            'address': addr,
            'amount': amount,
            'sqft': float(sqft or 0),
            'bedrooms': int(bedrooms) if bedrooms is not None else None,
            'date': _date(record.get('lastSeenDate') or record.get('listedDate')),
            'renovated': False,
            'source': 'RentCast AVM candidate',
            'status': str(record.get('status') or 'Unknown'),
            'latitude': record.get('latitude'),
            'longitude': record.get('longitude'),
            'date_type': 'listing activity — not confirmed closing',
        }
        seen.add(addr.casefold())
        result.append(row)
        if len(result) >= max_rows:
            break
    return result


def candidate_summary(rows, kind):
    return {
        'found': len(rows),
        'unselected': sum(not r.get('include', False) for r in rows),
        'notes': ('Sale candidates may have LISTING prices, not verified closed-sale prices. '
                  'Verify public recorded sale price/date, renovation condition, proximity and concessions before using ARV.'
                  if kind == 'sale' else
                  'Rental candidates may be asking rents, not signed leases. Verify listing freshness, whole-building vs unit amounts, and utilities.'),
    }

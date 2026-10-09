"""Auditable, conservative renovated closed-sale scenarios. No automated appraisal."""
from core.comps import evaluate_comps

def _verified_closed(row):
    """Status and date types must expressly refer to a closed/recorded sale."""
    descriptor = str(row.get('date_type') or '').strip().casefold()
    if not descriptor or any(x in descriptor for x in ('listing','asking','active','pending','unknown')):
        return False
    return any(x in descriptor for x in ('recorded sale','closed sale','closing date','sale closing','recorded closing'))

def _quantile(values, portion):
    vals=sorted(values)
    at=(len(vals)-1)*portion
    lo=int(at)
    hi=min(len(vals)-1,lo+1)
    return vals[lo]+(vals[hi]-vals[lo])*(at-lo)

def arv_scenarios(rows, sqft, beds=None, age_months=6, radius_miles=2.0, strict_distance=True):
    """At least three reviewed renovated closed sales required for an ARV range.

    Range is illustrative empirical p20/median/p80 of size-scaled eligible comps;
    it is neither an appraisal nor a statistical confidence interval.
    """
    verified=[]
    rejected=[]
    for row in rows:
        if not row.get('include',False):
            continue
        if not _verified_closed(row):
            rejected.append((row.get('address','Unknown'), 'Verify RECORDED/CLOSED sale price and closing date; listing activity is not a closing'))
            continue
        verified.append(row)
    result=evaluate_comps(verified,'sale',subject_sqft=sqft,subject_beds=beds,
        max_age_months=age_months,max_radius_miles=radius_miles,require_known_distance=strict_distance)
    rejected.extend(result['rejected'])
    result['rejected']=rejected
    n=result['count']
    if n<3:
        return {'ready':False,'count':n,'confidence':'Insufficient verified closed renovated sales',
                'conservative':None,'base':None,'optimistic':None,
                'rejected':rejected,'selected':result['selected'],
                'reason':f'{n} eligible sales; at least 3 needed before producing a scenario range.'}
    amounts=[x['adjusted'] for x in result['selected']]
    recent=sum(x['age_months']<=6 for x in result['selected'])
    distances_known=sum(x.get('distance_miles') is not None for x in result['selected'])
    confidence='Moderate — human verification still required' if n>=5 and recent>=3 and distances_known==n else 'Low — limited or less recent comp evidence'
    return {'ready':True,'count':n,'confidence':confidence,'conservative':_quantile(amounts,.20),
            'base':_quantile(amounts,.50),'optimistic':_quantile(amounts,.80),
            'rejected':rejected,'selected':result['selected'],
            'reason':'20th/50th/80th percentiles of size-adjusted sold comparables (not predictions or confidence intervals).'}

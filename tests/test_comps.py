from datetime import date
from core.comps import evaluate_comps

NOW = date(2026,10,8)

def test_arv_excludes_unrenovated_and_stale():
    comps = [
        dict(address='A',amount=200000,sqft=1000,date='2026-08-01',renovated=True),
        dict(address='B',amount=500000,sqft=1000,date='2026-08-01',renovated=False),
        dict(address='C',amount=300000,sqft=1000,date='2024-01-01',renovated=True),
    ]
    result = evaluate_comps(comps,'sale',subject_sqft=1200,as_of=NOW)
    assert result['count'] == 1
    assert result['estimate'] == 240000
    assert len(result['rejected']) == 2

def test_rents_median_and_confidence():
    comps = [dict(address=str(i),amount=a,date='2026-09-10') for i,a in enumerate([1600,1700,1800])]
    result = evaluate_comps(comps,'rent',as_of=NOW)
    assert result['estimate'] == 1700
    assert result['count'] == 3
    assert result['confidence'].startswith('Moderate')

def test_invalid_and_future_robustness():
    assert evaluate_comps([dict(address='bad',amount='nope',date='2026-01-01')],'rent',as_of=NOW)['estimate'] is None

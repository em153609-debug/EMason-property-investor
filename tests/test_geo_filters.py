from datetime import date
from services.geo import coords, miles_between, attach_distances
from core.comps import evaluate_comps

NOW=date(2026,10,8)

def test_coordinates_and_distance():
    cle=coords({'latitude':41.48,'longitude':-81.80})
    assert cle==(41.48,-81.80)
    assert miles_between(cle,cle)==0
    assert miles_between(cle,(41.49,-81.8))>0
    assert coords({'latitude':'not-a-number','longitude':-81.8}) is None

def test_known_radius_and_unknown_handling():
    rows=[
      dict(address='near',include=True,amount=1800,date='2026-08-01',distance_miles=.8),
      dict(address='far',include=True,amount=2400,date='2026-08-01',distance_miles=4.4),
      dict(address='unknown',include=True,amount=1900,date='2026-08-01'),
    ]
    strict=evaluate_comps(rows,'rent',as_of=NOW,max_radius_miles=1,require_known_distance=True)
    assert strict['count']==1 and strict['estimate']==1800
    assert any('Distance unknown' in reason for _,reason in strict['rejected'])
    permissive=evaluate_comps(rows,'rent',as_of=NOW,max_radius_miles=1,require_known_distance=False)
    assert permissive['count']==2

def test_date_window_changes_acceptance():
    rows=[dict(address='old',amount=2000,date='2026-01-10'),dict(address='new',amount=1800,date='2026-09-10')]
    r=evaluate_comps(rows,'rent',as_of=NOW,max_age_months=6)
    assert r['count']==1 and r['estimate']==1800
    assert '6 months' in r['rejected'][0][1]

def test_distance_calculation_only_with_real_coordinates():
    rows=attach_distances([{'address':'A','latitude':41.48,'longitude':-81.8},{'address':'B'}],(41.48,-81.8))
    assert rows[0]['distance_miles']==0
    assert rows[1]['distance_miles'] is None

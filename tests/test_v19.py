from datetime import date
import pytest
from core.arv_range import arv_scenarios
from core.rehab_estimator import template, estimate_scope
def row(i,price,kind='recorded sale',renovated=True,inc=True):
    return dict(include=inc,address=f'Comp {i}',amount=price,sqft=1500,bedrooms=3,
         date='2026-08-01',date_type=kind,renovated=renovated,distance_miles=0.8)
def test_range_requires_three():
    x=arv_scenarios([row(1,180000),row(2,190000)],1500,3)
    assert not x['ready'] and x['base'] is None
def test_verified_range():
    x=arv_scenarios([row(1,180000),row(2,200000),row(3,220000),row(4,240000),row(5,260000)],1500,3)
    assert x['ready'] and x['base']==220000 and x['conservative']<x['base']<x['optimistic']
def test_listing_not_closed():
    x=arv_scenarios([row(1,180000,'listing activity'),row(2,200000),row(3,220000)],1500,3)
    assert not x['ready'] and any('closing' in reason.lower() for _,reason in x['rejected'])
def test_condition_not_verified():
    x=arv_scenarios([row(1,180000,renovated=False),row(2,190000),row(3,200000)],1500,3)
    assert not x['ready']
def test_unknown_distance_conservative():
    rows=[row(i,p) for i,p in enumerate((180000,200000,220000),1)]
    rows[0].pop('distance_miles')
    assert not arv_scenarios(rows,1500,3,strict_distance=True)['ready']
def test_rehab_template_safe():
    x=estimate_scope(template())
    assert x['cash_total']==0 and x['diy_hours']==0
def test_rehab_diy_labor_excluded_from_cash():
    rows=[dict(item='Paint',quantity=100,materials_per_unit=2,contractor_labor_per_unit=3,diy_labor_hours_per_unit=.1,method='DIY')]
    x=estimate_scope(rows,30)
    assert x['cash_total']==200 and x['diy_hours']==10 and x['economic_cost']==500
def test_rehab_contract_labor():
    rows=[dict(item='Paint',quantity=100,materials_per_unit=2,contractor_labor_per_unit=3,diy_labor_hours_per_unit=.1,method='Contractor')]
    x=estimate_scope(rows,30)
    assert x['cash_total']==500 and x['diy_hours']==0
def test_negative_quantities_rejected():
    with pytest.raises(ValueError): estimate_scope([dict(quantity=-2,method='DIY')])

from dataclasses import replace
import pytest
from core.engine import Deal, analyze
from core.offer_sensitivity import offer_range, offer_curve


def test_offer_curve_does_not_mutate_current_deal():
    d=Deal()
    before=d.price
    lo,hi,step=offer_range(d.price)
    values=offer_curve(d,lo,hi,step)
    assert d.price==before
    assert values[0]['Offer']==lo and values[-1]['Offer']==hi
    assert all(a['BRRRR cash flow / month']>=b['BRRRR cash flow / month'] for a,b in zip(values,values[1:]))
    assert all(a['Flip net profit']>=b['Flip net profit'] for a,b in zip(values,values[1:]))


def test_offer_range_supports_low_and_high_price():
    for price in (15000,150000,850000,3000000):
        low,high,step=offer_range(price)
        assert low>0 and high>price>low and step>0
        assert (high-low)//step<=1000


def test_sensitivity_agrees_with_engine():
    d=Deal(price=200000)
    expected=analyze(replace(d,price=180000))
    row=next(x for x in offer_curve(d,180000,182000,1000) if x['Offer']==180000)
    assert row['Flip net profit']==round(expected['flip']['profit'],2)
    assert row['BRRRR cash flow / month']==round(expected['brrrr']['monthly_cashflow'],2)


def test_reject_bad_ranges():
    with pytest.raises(ValueError):
        offer_curve(Deal(),0,10,1)
    with pytest.raises(ValueError):
        offer_range(0)

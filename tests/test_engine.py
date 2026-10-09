from dataclasses import replace
from core.engine import Deal,analyze,max_offer,payment,sensitivities

def test_payment_zero_rate(): assert abs(payment(120000,0,10)-1000)<.001

def test_cashflow_and_scores():
    result=analyze(Deal())
    assert 0<=result['brrrr']['score']<=100
    assert 0<=result['flip']['score']<=100
    assert result['shared']['cash_required']>0
    assert result['flip']['break_even_sale']>result['shared']['all_in']

def test_price_decline_improves_profit():
    d=Deal()
    assert analyze(replace(d,price=120000))['flip']['profit']>analyze(d)['flip']['profit']

def test_negative_refi_proceeds_not_free_cash():
    d=Deal(price=250000,arv=180000)
    r=analyze(d)
    assert r['brrrr']['recovery']==0
    assert r['brrrr']['cash_left']>r['shared']['cash_required']

def test_scenarios():
    s=sensitivities(Deal())
    assert s['Downside']['flip']['profit']<s['Base']['flip']['profit']
    assert s['Base']['flip']['profit']<s['Upside']['flip']['profit']

def test_max_offer():
    d=Deal(arv=300000,rent=3200)
    m=max_offer(d,'flip')
    assert m is not None
    assert analyze(replace(d,price=m-100))['flip']['passed']

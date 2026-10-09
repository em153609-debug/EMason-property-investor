"""Purchase-price sensitivity, without mutating the active investment scenario."""
from dataclasses import replace
from core.engine import analyze


def offer_range(current_price):
    """Return accessible slider bounds and sensible granularity for any US price."""
    if current_price <= 0:
        raise ValueError('Purchase price must be positive')
    step = 1000 if current_price < 500_000 else 5000
    low = max(step, int(current_price * .60 // step)*step)
    high = max(low + step, int((current_price * 1.40 + step - 1)//step)*step)
    return low, high, step


def offer_curve(deal, low=None, high=None, step=None):
    if low is None or high is None or step is None:
        low, high, step = offer_range(deal.price)
    if low <= 0 or step <= 0 or high < low:
        raise ValueError('Invalid offer range')
    if (high-low)//step > 1000:
        raise ValueError('Offer range is too large')
    rows=[]
    for price in range(low,high+1,step):
        r=analyze(replace(deal, price=float(price)))
        rows.append({'Offer':price, 'BRRRR cash flow / month':round(r['brrrr']['monthly_cashflow'],2), 'Flip net profit':round(r['flip']['profit'],2), 'BRRRR qualifies':r['brrrr']['passed'], 'Flip qualifies':r['flip']['passed']})
    return rows

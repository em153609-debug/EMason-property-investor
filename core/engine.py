"""Deterministic BRRRR and flip underwriting; all monetary figures USD."""
from dataclasses import dataclass, asdict
from math import pow

@dataclass
class Deal:
    address: str = ''
    kind: str = 'Single Family'
    units: int = 1
    price: float = 150000
    arv: float = 240000
    rent: float = 2100
    rehab: float = 35000
    contingency: float = .15
    acquisition_closing: float = .03
    acquisition_down: float = .25
    acquisition_rate: float = .09
    purchase_points: float = .01
    rehab_months: int = 3
    marketing_months: int = 2
    tax_annual: float = 3400
    insurance_annual: float = 1300
    utilities_monthly: float = 180
    vacancy: float = .05
    maintenance: float = .08
    capex: float = .08
    management: float = .08
    other_monthly: float = 40
    refi_ltv: float = .75
    refi_rate: float = .075
    refi_years: int = 30
    refinance_cost: float = .025
    sale_commission: float = .055
    sale_closing: float = .015
    seller_concession: float = .01
    rehab_reserve_extra: float = 0
    minimum_cashflow: float = 300
    minimum_recovery: float = .75
    minimum_dscr: float = 1.25
    flip_min_profit: float = 25000
    flip_min_roi: float = .20
    arv_confidence: str = 'Unverified'
    rent_confidence: str = 'Unverified'


def payment(principal, annual_rate, years):
    if principal <= 0: return 0.0
    n = max(1, years * 12)
    r = max(0, annual_rate) / 12
    return principal / n if r == 0 else principal * r / (1 - pow(1+r, -n))


def flag(name, observed, threshold, points, maximum, explanation, action, higher=True):
    passed = observed >= threshold if higher else observed <= threshold
    return dict(name=name, value=observed, threshold=threshold, score=int(round(points)), max=maximum,
                status='Good' if passed else 'Needs attention', why=explanation, action=action)

def analyze(d: Deal):
    if d.price <= 0 or d.arv <= 0: raise ValueError('Purchase price and ARV must exceed $0.')
    hold_months = max(1, d.rehab_months + d.marketing_months)
    rehab_total = d.rehab * (1 + d.contingency) + d.rehab_reserve_extra
    purchase_loan = d.price * (1-d.acquisition_down)
    acquisition_cash = d.price-d.price*(1-d.acquisition_down) + d.price*d.acquisition_closing
    points = purchase_loan*d.purchase_points
    monthly_interest = purchase_loan*d.acquisition_rate/12
    holding = hold_months*(monthly_interest+d.tax_annual/12+d.insurance_annual/12+d.utilities_monthly)
    cash_in = acquisition_cash+rehab_total+points+holding
    all_in = d.price + d.price*d.acquisition_closing + rehab_total + points + holding
    refi_loan = d.arv*d.refi_ltv
    refi_fees = refi_loan*d.refinance_cost
    net_refi = refi_loan-purchase_loan-refi_fees
    cash_returned = max(0, net_refi)
    gap = max(0,-net_refi)
    remaining = cash_in-cash_returned+gap
    recovery = cash_returned/cash_in if cash_in else 0
    monthly_debt = payment(refi_loan,d.refi_rate,d.refi_years)
    effective_rent = d.rent*(1-d.vacancy)
    expense_variable = d.rent*(d.maintenance+d.capex+d.management)
    operating = expense_variable+d.tax_annual/12+d.insurance_annual/12+d.other_monthly
    noi_month = effective_rent-operating
    cashflow = noi_month-monthly_debt
    dscr = noi_month/monthly_debt if monthly_debt else float('inf')
    coc = cashflow*12/remaining if remaining>0 else None
    sale_cost=d.arv*(d.sale_commission+d.sale_closing+d.seller_concession)
    flip_profit=d.arv-all_in-sale_cost
    flip_roi=flip_profit/cash_in if cash_in else 0
    monthly_burn=monthly_interest+d.tax_annual/12+d.insurance_annual/12+d.utilities_monthly
    breakeven_sale=all_in/max(.01,(1-d.sale_commission-d.sale_closing-d.seller_concession))
    # The larger of single-family minimum or $175/unit for multifamily.
    cf_target=max(d.minimum_cashflow, 175*d.units if d.units>1 else d.minimum_cashflow)
    # Threshold-derived scoring; low-comparables confidence triggers a separate review gate.
    def scale(value, target, cap): return min(cap,max(0, cap*value/target)) if target>0 else cap
    b=[
      flag('Monthly cash flow',cashflow,cf_target,scale(max(0,cashflow),cf_target,25),25,f'${cashflow:,.0f}/month versus ${cf_target:,.0f} minimum. Operating reserves and debt payment included.','Improve rent or reduce the purchase price.'),
      flag('Capital recovery',recovery,d.minimum_recovery,scale(recovery,d.minimum_recovery,25),25,f'{recovery:.0%} of peak invested cash returned under assumed refinance constraints.','Confirm maximum LTV, appraisal and lender seasoning restrictions.'),
      flag('Debt service coverage',dscr,d.minimum_dscr,scale(dscr,d.minimum_dscr,20),20,f'NOI/debt service = {dscr:.2f}; preferred >= {d.minimum_dscr:.2f}.','Validate property taxes, insurance and the lender DSCR definition.'),
      flag('Equity spread',d.arv-all_in,0,15 if d.arv>=all_in else max(0,15*(d.arv-all_in)/d.arv+8),15,f'ARV minus all-in project cost = ${d.arv-all_in:,.0f}.','Confirm renovated sold comparables, not only automated AVM.'),
      flag('Rehab buffer',d.contingency,.15,10 if d.contingency>=.15 else max(0,10*d.contingency/.15),10,f'Rehab contingency is {d.contingency:.0%}.','Verify system condition with contractors and inspection.'),
      flag('Rental evidence',1 if d.rent_confidence=='Verified comps' else 0,1,5 if d.rent_confidence=='Verified comps' else 1,5,'Rent evidence: '+d.rent_confidence+'.','Review multiple recent similar rented properties.')]
    f=[
      flag('Projected flip profit',flip_profit,d.flip_min_profit,scale(max(0,flip_profit),d.flip_min_profit,25),25,f'Pre-tax net profit after selling costs = ${flip_profit:,.0f}.','Renegotiate price or rehab budget if below target.'),
      flag('Flip cash ROI',flip_roi,d.flip_min_roi,scale(max(0,flip_roi),d.flip_min_roi,25),25,f'Estimated profit / peak cash invested = {flip_roi:.1%}.','Evaluate financing, rehab scope and sale cost.'),
      flag('Value margin',d.arv-all_in,0,20 if d.arv>=all_in else 0,20,f'ARV less project cost before resale fees = ${d.arv-all_in:,.0f}.','Validate renovated comparable sales.'),
      flag('Rehab buffer',d.contingency,.15,15 if d.contingency>=.15 else 15*d.contingency/.15,15,f'Current contingency {d.contingency:.0%}.','Get written bids and allow for surprises.'),
      flag('Resale evidence',1 if d.arv_confidence=='Verified comps' else 0,1,10 if d.arv_confidence=='Verified comps' else 2,10,'ARV evidence: '+d.arv_confidence+'.','Confirm close-date, quality, size and proximity of sold comps.'),
      flag('Project timeline',hold_months,6,5 if hold_months<=6 else max(0,5-(hold_months-6)),5,f'Assumed {hold_months} months from purchase through exit.','Include schedule slippage and additional carrying costs.',False)]
    b_score=sum(x['score'] for x in b); f_score=sum(x['score'] for x in f)
    b_pass=cashflow>=cf_target and recovery>=d.minimum_recovery and dscr>=d.minimum_dscr and d.arv>=all_in and net_refi>=0
    f_pass=flip_profit>=d.flip_min_profit and flip_roi>=d.flip_min_roi
    def label(passed,score): return 'Meets targets — verify evidence' if passed else ('Negotiate / adjust' if score>=55 else 'Pass at this price')
    return dict(brrrr=dict(score=b_score,verdict=label(b_pass,b_score),passed=b_pass,items=b,monthly_cashflow=cashflow,noi_month=noi_month,dscr=dscr,coc=coc,recovery=recovery,cash_left=remaining,refi_loan=refi_loan,net_refi=net_refi,mortgage=monthly_debt),
      flip=dict(score=f_score,verdict=label(f_pass,f_score),passed=f_pass,items=f,profit=flip_profit,roi=flip_roi,annualized_simple_roi=flip_roi*12/hold_months,break_even_sale=breakeven_sale,sale_cost=sale_cost),
      shared=dict(cash_required=cash_in,all_in=all_in,rehab_total=rehab_total,holding=holding,months=hold_months,acquisition_loan=purchase_loan,interest_per_month=monthly_interest,monthly_burn=monthly_burn),
      advisory='These results are estimates; loan proceeds, refinance seasoning, taxes, vacancy, repairs and sale proceeds must be verified.')


def max_offer(d: Deal, strategy: str, low=10000, high=None):
    # Monotonic binary search; do not silently assume all prices are viable.
    from dataclasses import replace
    high=high or max(d.arv*1.5,d.price*1.5)
    if not analyze(replace(d,price=low))[strategy]['passed']: return None
    for _ in range(45):
        mid=(low+high)/2
        if analyze(replace(d,price=mid))[strategy]['passed']: low=mid
        else: high=mid
    return round(low,-2)


def sensitivities(d):
    from dataclasses import replace
    return {name:analyze(replace(d,arv=d.arv*v,rent=d.rent*r,rehab=d.rehab*h,rehab_months=d.rehab_months+t)) for name,v,r,h,t in [('Upside',1.05,1.05,1,0),('Base',1,1,1,0),('Downside',.90,.90,1.20,3)]}

"""Plain-language, deterministic investment summary. No opaque AI scoring."""

def cash(v): return f'${v:,.0f}'


def build_insights(deal, result):
    b,f=result['brrrr'],result['flip']
    strengths=[];risks=[];verify=[]
    cashflow=b['monthly_cashflow']
    if cashflow>=deal.minimum_cashflow:
        strengths.append(f'BRRRR cash flow {cash(cashflow)}/month meets your {cash(deal.minimum_cashflow)} minimum.')
    else:
        risks.append(f'BRRRR cash flow {cash(cashflow)}/month is {cash(deal.minimum_cashflow-cashflow)} below your minimum.')
    if b['recovery']>=deal.minimum_recovery:
        strengths.append(f'BRRRR capital recovery {b["recovery"]:.0%} meets your {deal.minimum_recovery:.0%} goal.')
    else:
        risks.append(f'BRRRR capital recovery {b["recovery"]:.0%} misses your {deal.minimum_recovery:.0%} goal.')
    if b['dscr']>=deal.minimum_dscr:
        strengths.append(f'DSCR {b["dscr"]:.2f} meets the {deal.minimum_dscr:.2f} minimum.')
    else:
        risks.append(f'DSCR {b["dscr"]:.2f} is below the {deal.minimum_dscr:.2f} minimum.')
    if f['profit']>=deal.flip_min_profit:
        strengths.append(f'Flip pre-tax profit {cash(f["profit"])} meets the {cash(deal.flip_min_profit)} target.')
    else:
        risks.append(f'Flip profit {cash(f["profit"])} falls below the {cash(deal.flip_min_profit)} target.')
    if f['roi']>=deal.flip_min_roi:
        strengths.append(f'Flip cash ROI {f["roi"]:.1%} meets the {deal.flip_min_roi:.0%} target.')
    else:
        risks.append(f'Flip cash ROI {f["roi"]:.1%} misses the {deal.flip_min_roi:.0%} target.')
    if deal.arv_confidence!='Verified comps':verify.append('ARV is unverified; confirm renovated closed-sale comps, condition and concessions.')
    if deal.rent_confidence!='Verified comps':verify.append('Market rent is unverified; confirm unit count, active comparables and lease-level rent.')
    if deal.contingency<.15:verify.append('Rehab contingency below 15%; obtain contractor pricing and inspection allowances.')
    verify.append('Confirm lender seasoning, appraisal LTV limits, loan costs and refinance eligibility.')
    verify.append('Verify post-sale property taxes, insurance, municipal rules and utility responsibilities.')
    return {'strengths':strengths,'risks':risks,'verifications':verify}

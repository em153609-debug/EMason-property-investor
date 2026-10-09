import json
from dataclasses import asdict
from datetime import datetime, timezone
import streamlit as st
from core.engine import Deal, analyze, max_offer, sensitivities

st.set_page_config(page_title='EMason Property Investor',page_icon='🏠',layout='wide')
st.title('🏠 EMason Property Investor')
st.caption('Cleveland-area BRRRR + Fix & Flip | v1.0 • Preliminary underwriting; not an appraisal or loan approval')

@st.cache_data(ttl=86400,show_spinner=False)
def rentcast_data(address,key,valuations):
    from services.rentcast import fetch
    return fetch(address,key,valuations)

if 'deal' not in st.session_state: st.session_state.deal=Deal()
if 'lookup' not in st.session_state: st.session_state.lookup={}
d=st.session_state.deal
secrets=st.secrets
rentcast_key=secrets.get('RENTCAST_API_KEY','')
sb_url=secrets.get('SUPABASE_URL','')
sb_key=secrets.get('SUPABASE_PUBLISHABLE_KEY','')

with st.sidebar:
    st.header('Deal Settings')
    d.minimum_cashflow = st.number_input("Minimum monthly cash flow ($)", min_value=0.0, max_value=5000.0, value=float(d.minimum_cashflow), step=25.0)
    d.minimum_recovery = st.number_input("BRRRR cash recovery target (%)", min_value=0.0, max_value=100.0, value=float(d.minimum_recovery * 100), step=5.0) / 100
    d.minimum_dscr = st.number_input("Minimum DSCR", min_value=0.5, max_value=3.0, value=float(d.minimum_dscr), step=0.05)
    d.flip_min_profit = st.number_input("Flip minimum profit ($)", min_value=0.0, max_value=250000.0, value=float(d.flip_min_profit), step=1000.0)
    d.flip_min_roi = st.number_input("Flip minimum ROI (%)", min_value=0.0, max_value=100.0, value=float(d.flip_min_roi * 100), step=5.0) / 100

    st.info('Visitors can analyze anonymously. Saving requires an authenticated Supabase account.')

tabs=st.tabs(['🏠 Property & Comps','🔨 Rehab','💵 Finance & Operating','📊 Deal Verdict','💾 Saved Deals'])
with tabs[0]:
    st.subheader('1 · Property data')
    d.address=st.text_input('Property address',value=d.address,placeholder='123 Main St, Lakewood, OH 44107')
    c1,c2,c3,c4=st.columns(4)
    with c1: d.kind=st.selectbox('Type',['Single Family','Duplex','Triplex','Fourplex'],index=['Single Family','Duplex','Triplex','Fourplex'].index(d.kind))
    d.units={'Single Family':1,'Duplex':2,'Triplex':3,'Fourplex':4}[d.kind]
    with c2: d.price=st.number_input('Asking / offer price ($)',min_value=1000.,value=float(d.price),step=5000.)
    with c3: d.arv=st.number_input('After-repair value ($)',min_value=1000.,value=float(d.arv),step=5000.)
    with c4: d.rent=st.number_input('Total monthly rent, all units ($)',min_value=0.,value=float(d.rent),step=100.)
    with st.expander('Import available data from RentCast (uses API requests)',expanded=False):
        if not rentcast_key:
            st.warning('RentCast API key not configured. Manual entry works without it.')
        else:
            st.write('Property record lookup uses 1 API request. Value and rent estimates use up to 2 additional requests. Results are cached for 24 hours per address.')
            want_valuations=st.checkbox('Include value and rent AVMs (+2 requests)',value=False)
            if st.button('Lookup this address',disabled=not bool(d.address.strip())):
                try:
                    result=rentcast_data(d.address.strip(),rentcast_key,want_valuations)
                    st.session_state.lookup={'retrieved_at':datetime.now(timezone.utc).isoformat(),'data':result}
                    st.success('Data retrieved. Review the estimates before applying them.')
                except Exception as exc: st.error(f'Lookup failed: {exc}')
            lookup=st.session_state.lookup
            if lookup:
                st.caption('Retrieved at '+lookup['retrieved_at'])
                data=lookup['data']; prop=data.get('property',[])
                if isinstance(prop,list) and prop:
                    p=prop[0]
                    st.json({k:p.get(k) for k in ('formattedAddress','propertyType','bedrooms','bathrooms','squareFootage','yearBuilt','lastSalePrice','propertyTaxes')})
                value=data.get('value',{}); rent=data.get('rent',{})
                if value or rent:
                    c1,c2=st.columns(2)
                    v=value.get('price') or value.get('value')
                    r=rent.get('rent')
                    c1.metric('Provider value estimate',f'${v:,.0f}' if isinstance(v,(float,int)) else 'Unavailable')
                    c2.metric('Provider rent estimate',f'${r:,.0f}' if isinstance(r,(float,int)) else 'Unavailable')
                    if isinstance(v,(float,int)) and st.button('Use value estimate as provisional ARV'):
                        d.arv=float(v); st.rerun()
                    if isinstance(r,(float,int)) and st.button('Use rental estimate'):
                        d.rent=float(r); st.rerun()
                    st.warning('Provider value may reflect current condition. Not a verified renovated-property ARV. Review returned comparables before relying on it.')
                    for label,obj in [('Sales comparables',value),('Rental comparables',rent)]:
                        comps=obj.get('comparables',[]) if isinstance(obj,dict) else []
                        if comps:
                            st.markdown('**'+label+'**')
                            st.dataframe([{k:p.get(k) for k in ['formattedAddress','price','rent','squareFootage','bedrooms','bathrooms','lastSeenDate','correlation']} for p in comps],use_container_width=True,hide_index=True)
    a,b=st.columns(2)
    with a: d.arv_confidence=st.selectbox('ARV evidence',['Unverified','Verified comps'],index=['Unverified','Verified comps'].index(d.arv_confidence),help='Choose Verified comps only after you review recent comparable sold renovated properties.')
    with b: d.rent_confidence=st.selectbox('Rent evidence',['Unverified','Verified comps'],index=['Unverified','Verified comps'].index(d.rent_confidence))
    st.caption('For multifamily enter total property value and total projected monthly rent. Verify zoning and legal unit count independently.')
with tabs[1]:
    st.subheader('2 · Rehab planning')
    st.caption('Enter the actual contractor bids + DIY materials and out-of-pocket labor costs. Detailed line-item planning is supported below.')
    default_items={'Kitchen':12000.,'Bathrooms':8000.,'Flooring':4500.,'Paint':2500.,'Electrical / plumbing':4000.,'Exterior / other':4000.}
    if 'rehab_items' not in st.session_state: st.session_state.rehab_items=default_items.copy()
    c1,c2=st.columns(2)
    for i,(name,val) in enumerate(st.session_state.rehab_items.items()):
        with (c1 if i%2==0 else c2):
            st.session_state.rehab_items[name]=st.number_input(name,min_value=0.,value=float(val),step=500.,key='rehab_'+name)
    d.rehab=sum(st.session_state.rehab_items.values())
    st.metric('Base renovation budget',f'${d.rehab:,.0f}')
    d.contingency=st.slider('Contingency (%)',0,35,int(d.contingency*100))/100
    d.rehab_reserve_extra=st.number_input('Permits / special allowances ($)',0.,100000.,float(d.rehab_reserve_extra),step=500.)
    d.rehab_months=st.number_input('Rehab duration (months)',1,36,int(d.rehab_months))
    d.marketing_months=st.number_input('Rent-up / resale closing time (months)',0,18,int(d.marketing_months))
with tabs[2]:
    st.subheader('3 · Purchase, operations and refinance')
    with st.expander('Acquisition financing',expanded=True):
        c1,c2,c3=st.columns(3)
        with c1: d.acquisition_down=st.number_input('Purchase down payment (%)',0,100,int(d.acquisition_down*100))/100
        with c2: d.acquisition_rate=st.number_input('Purchase loan annual interest (%)',0.,30.,float(d.acquisition_rate*100),step=.25)/100
        with c3: d.purchase_points=st.number_input('Purchase loan points (%)',0.,10.,float(d.purchase_points*100),step=.25)/100
        d.acquisition_closing=st.number_input('Purchase closing costs (%)',0.,15.,float(d.acquisition_closing*100),step=.5)/100
    with st.expander('Rental operating costs',expanded=True):
        c1,c2,c3=st.columns(3)
        with c1:
            d.tax_annual=st.number_input('Annual property taxes ($)',0.,100000.,float(d.tax_annual),step=200.)
            d.vacancy=st.number_input('Vacancy (%)',0,50,int(d.vacancy*100))/100
            d.maintenance=st.number_input('Maintenance (%)',0,50,int(d.maintenance*100))/100
        with c2:
            d.insurance_annual=st.number_input('Annual insurance ($)',0.,100000.,float(d.insurance_annual),step=100.)
            d.capex=st.number_input('Capital reserve (%)',0,50,int(d.capex*100))/100
            d.management=st.number_input('Property management (%)',0,30,int(d.management*100))/100
        with c3:
            d.utilities_monthly=st.number_input('Utilities while rehabbing ($/mo)',0.,5000.,float(d.utilities_monthly),step=20.)
            d.other_monthly=st.number_input('Other recurring costs ($/mo)',0.,5000.,float(d.other_monthly),step=10.)
    with st.expander('Refinance assumptions',expanded=True):
        c1,c2,c3=st.columns(3)
        with c1: d.refi_ltv=st.number_input('Refinance LTV (%)',0,100,int(d.refi_ltv*100))/100
        with c2: d.refi_rate=st.number_input('Refinance interest (%)',0.,30.,float(d.refi_rate*100),step=.25)/100
        with c3: d.refi_years=st.number_input('Term (years)',5,40,int(d.refi_years),step=5)
        d.refinance_cost=st.number_input('Refinance costs as % of loan',0.,10.,float(d.refinance_cost*100),step=.25)/100
    with st.expander('Flip sale costs',expanded=True):
        c1,c2,c3=st.columns(3)
        with c1: d.sale_commission=st.number_input('Sales agent commission (%)',0.,12.,float(d.sale_commission*100),step=.25)/100
        with c2: d.sale_closing=st.number_input('Other sale closing costs (%)',0.,10.,float(d.sale_closing*100),step=.25)/100
        with c3: d.seller_concession=st.number_input('Buyer concessions (%)',0.,10.,float(d.seller_concession*100),step=.25)/100
with tabs[3]:
    st.subheader('4 · Investment decision')
    try:
        result=analyze(d)
        st.session_state.last_analysis={'inputs':asdict(d),'results':result,'timestamp':datetime.now(timezone.utc).isoformat()}
        b,f=result['brrrr'],result['flip']
        x,y=st.columns(2)
        with x:
            st.markdown('### 🏠 BRRRR')
            st.metric('Score',f"{b['score']}/100")
            st.write('**'+b['verdict']+'**')
            st.metric('Monthly cash flow',f"${b['monthly_cashflow']:,.0f}")
            st.metric('Capital recovered',f"{b['recovery']:.0%}")
            st.metric('Cash remaining in deal',f"${b['cash_left']:,.0f}")
            st.metric('DSCR',f"{b['dscr']:.2f}")
        with y:
            st.markdown('### 🔨 Fix & Flip')
            st.metric('Score',f"{f['score']}/100")
            st.write('**'+f['verdict']+'**')
            st.metric('Estimated pre-tax profit',f"${f['profit']:,.0f}")
            st.metric('Project cash ROI',f"{f['roi']:.1%}")
            st.metric('Break-even sale price',f"${f['break_even_sale']:,.0f}")
            st.metric('Time to exit',f"{result['shared']['months']} months")
        st.divider()
        if b['passed'] and f['passed']: st.success('Both strategies meet your financial targets. Compare risk and capital timelines.')
        elif b['passed']: st.success('BRRRR meets financial targets; flip does not.')
        elif f['passed']: st.success('Fix & Flip meets financial targets; BRRRR does not.')
        else: st.warning('Neither strategy meets every configured target at this price. Review maximum offers and missing evidence.')
        st.caption('Financial qualification is conditional: check lender seasoning, appraisal, unit legality, local tax reassessment and comparable evidence.')
        st.subheader('Maximum qualifying offer')
        q1,q2=st.columns(2)
        max_b=max_offer(d,'brrrr'); max_f=max_offer(d,'flip')
        q1.metric('BRRRR maximum offer',f'${max_b:,.0f}' if max_b is not None else 'No feasible price in range')
        q2.metric('Flip maximum offer',f'${max_f:,.0f}' if max_f is not None else 'No feasible price in range')
        st.caption('Calculated by testing prices against the hard financial targets; not a seller acceptance prediction.')
        for heading,section in [('BRRRR score explained',b),('Fix & Flip score explained',f)]:
            st.markdown('### '+heading)
            for i,item in enumerate(section['items']):
                with st.expander(f"{'✅' if item['status']=='Good' else '⚠️'} {item['name']} • {item['score']}/{item['max']} • {item['status']}",expanded=item['status']!='Good'):
                    st.write(item['why'])
                    st.write('**How to improve / verify:** '+item['action'])
                    st.write('**Observed:**',round(item['value'],3),'| **Target:**',round(item['threshold'],3))
        st.subheader('Stress test')
        stress=[]
        for label,s in sensitivities(d).items():
            stress.append({'Scenario':label,'BRRRR cash flow':round(s['brrrr']['monthly_cashflow']),'BRRRR recovery %':round(100*s['brrrr']['recovery'],1),'Flip net profit':round(s['flip']['profit']),'Flip ROI %':round(s['flip']['roi']*100,1)})
        st.dataframe(stress,use_container_width=True,hide_index=True)
        st.metric('Peak projected cash required',f"${result['shared']['cash_required']:,.0f}")
        st.caption('Simplified purchase loan interest-only model; assumes rehab funded from cash and the ARV can support the listed refinance. Not a lender quote.')
        st.download_button('Download full JSON snapshot',data=json.dumps(st.session_state.last_analysis,indent=2,default=str),file_name='deal-analysis.json',mime='application/json')
        try:
            from services.export import excel_report
            excel_bytes=excel_report(d,result)
            st.download_button('Download Excel underwriting report',excel_bytes,file_name='investment-analysis.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e: st.warning(f'Excel export unavailable: {e}')
    except ValueError as e: st.error(str(e))
with tabs[4]:
    st.subheader('5 · Private saved analyses')
    if not sb_url or not sb_key:
        st.info('Supabase is not configured. JSON/Excel downloads still work. Configure Supabase Secrets and run the included SQL migration to enable saving.')
    else:
        from services.storage import login,save_deal,list_deals
        if 'auth_token' not in st.session_state:
            st.caption('Log in using an email/password account created under Supabase Authentication → Users. Each user sees only their own deals.')
            with st.form('login'):
                email=st.text_input('Email'); password=st.text_input('Password',type='password')
                pressed=st.form_submit_button('Sign in')
                if pressed:
                    try:
                        token,uid=login(sb_url,sb_key,email,password)
                        st.session_state.auth_token=token;st.session_state.auth_uid=uid;st.rerun()
                    except Exception: st.error('Could not sign in. Check user credentials and email confirmation status.')
        else:
            if st.button('Sign out'):
                del st.session_state.auth_token;del st.session_state.auth_uid;st.rerun()
            if st.button('Save current analysis'):
                try:
                    payload=st.session_state.get('last_analysis') or {'inputs':asdict(d),'results':analyze(d)}
                    save_deal(sb_url,sb_key,st.session_state.auth_token,st.session_state.auth_uid,d.address or 'Untitled property',payload)
                    st.success('Saved to your private deals.')
                except Exception as exc: st.error(f'Could not save: {exc}')
            if st.button('Refresh my saved deals'):
                try: st.session_state.saved_deals=list_deals(sb_url,sb_key,st.session_state.auth_token)
                except Exception as exc: st.error(f'Could not load: {exc}')
            for saved in st.session_state.get('saved_deals',[]):
                with st.expander(f"{saved['title']} — {saved['created_at'][:10]}"):
                    st.json(saved['payload'])
            st.warning('V1 saves private per-user snapshots. Shared partner workspaces are planned for a later version; do not share passwords.')

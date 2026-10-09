import json
from dataclasses import asdict
from datetime import datetime, timezone
import streamlit as st
from core.engine import Deal, analyze, max_offer, sensitivities

st.set_page_config(page_title='EMason Property Investor',page_icon='🏘️',layout='wide', initial_sidebar_state='collapsed')
st.markdown("""<style>
/* V1.6 dark shell + light readable input surfaces */
:root {color-scheme: dark;}
.stApp, [data-testid="stAppViewContainer"] { background:#101b2a !important; color:#e8f0f8 !important; }
.block-container { max-width:1360px; padding-top:1.25rem; padding-bottom:4rem; }
[data-testid="stHeader"] {background:#101b2af0 !important;}
[data-testid="stSidebar"] {background:#152638 !important; border-right:1px solid #315067;}
[data-testid="stSidebar"] * {color:#e8f0f8;}
h1,h2,h3,h4,p,li,[data-testid="stMarkdownContainer"] {color:#e8f0f8;}
[data-testid="stCaptionContainer"], .stCaption {color:#a9bdce !important;}
[data-testid="stMetric"] {background:#1b3044 !important; padding:1.0rem 1.1rem; border:1px solid #365267; border-radius:14px;}
[data-testid="stMetricLabel"] {color:#bbd0dc !important; font-weight:650;}
[data-testid="stMetricValue"] {color:#f7fbff !important; font-weight:780;}
[data-testid="stTabs"] [role="tablist"] {background:#17293b; padding:6px; gap:5px; border-radius:12px;}
[data-testid="stTabs"] button[role="tab"] {border-radius:9px; padding:12px 16px; font-weight:700; color:#bbcfda;}
[data-testid="stTabs"] button[aria-selected="true"] {background:#264759; color:#73e6d1;}
[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {background:#17293b; border:1px solid #365267; border-radius:13px;}
/* Consistently visible fields, including select, numeric, text, dates and data editor */
/* Lighter input fields, high-contrast dark input text, and clearly outlined edges. */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {background:#DCEAF3 !important; border:1px solid #91AFC3 !important; border-radius:10px !important;}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-baseweb="select"] [role="combobox"],
[data-baseweb="input"] input {background:#DCEAF3 !important; color:#142A3A !important; caret-color:#142A3A !important; font-weight:650;}
[data-baseweb="input"] input::placeholder, textarea::placeholder {color:#5A7183 !important; opacity:1;}
[data-testid="stSelectbox"] [data-baseweb="select"] *, [data-testid="stMultiSelect"] [data-baseweb="select"] * {color:#142A3A !important;}
[data-testid="stNumberInput"] button {background:#C3D9E8 !important; border-color:#91AFC3 !important; color:#142A3A !important;}
[data-testid="stNumberInput"] button svg {fill:#142A3A !important; color:#142A3A !important;}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {outline:2px solid #43D0C0 !important; outline-offset:1px;}
/* Dropdown menus can remain dark; their options must have readable light text. */
[data-baseweb="popover"], [role="listbox"], [data-baseweb="menu"] {background:#243C53 !important; color:#F7FBFF !important;}
[data-baseweb="popover"] [role="option"], [role="listbox"] [role="option"] {color:#F7FBFF !important;}
[data-baseweb="popover"] [aria-selected="true"] {background:#315D70 !important;}
/* Explicitly avoid changing the text color of data-grid cells or metric cards. */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {border:1px solid #365267; border-radius:10px;}
label,[data-testid="stWidgetLabel"] {color:#d7e6f0 !important; font-weight:630;}
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {background:#0eaaa2 !important; color:#071b22 !important; border:0; font-weight:800; border-radius:10px;}
.stButton button[kind="secondary"], .stDownloadButton button {background:#28445b !important; color:#f2f8ff !important; border:1px solid #52758d !important; border-radius:10px; font-weight:670;}
.hero {padding:1.6rem 1.9rem; border-radius:19px; background:linear-gradient(113deg,#172d43,#214359 72%,#126b70); border:1px solid #426579; margin-bottom:1.25rem;}
.hero-kicker {font-weight:800; font-size:.74rem; color:#8af1dd; letter-spacing:.12em;}
.hero-title {font-size:2.05rem; font-weight:850; color:#fff; letter-spacing:-.045em; margin:.2rem 0;}
.hero-sub {color:#ccdeeb; font-size:.96rem;}
.section-eyebrow {color:#82e5d3 !important; font-size:.79rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase;}
.insight {background:#1a3044; border:1px solid #3a5870; border-radius:12px; padding:12px 16px; margin:7px 0; line-height:1.5; color:#e6f2fa;}
.insight.good {border-left:4px solid #3ed6a7;} .insight.risk {border-left:4px solid #ffb85c;} .insight.verify {border-left:4px solid #8eafe6;}
@media(max-width:760px) {.block-container {padding-left:.75rem;padding-right:.75rem;padding-top:1rem;} .hero{padding:1.2rem;} .hero-title{font-size:1.55rem;} [data-testid="stTabs"] button[role="tab"]{padding:8px 10px;}}
</style>""", unsafe_allow_html=True)
st.markdown("<div class='hero'><div class='hero-kicker'>PROPERTY UNDERWRITING · V1.6</div><div class='hero-title'>EMason Property Investor</div><div class='hero-sub'>Analyze, compare and explain BRRRR vs Fix & Flip opportunities.</div></div>", unsafe_allow_html=True)

@st.cache_data(ttl=86400,show_spinner=False)
def rentcast_data(address,key,valuations):
    from services.rentcast import fetch
    return fetch(address,key,valuations)

@st.cache_data(ttl=86400,show_spinner=False)
def geographic_data(address,key,radius,age_months,kind):
    from services.market_search import search_nearby
    return search_nearby(address,key,radius,age_months,kind=kind)

if 'deal' not in st.session_state: st.session_state.deal=Deal()
if 'lookup' not in st.session_state: st.session_state.lookup={}
if 'comp_import_version' not in st.session_state: st.session_state.comp_import_version=0
if 'address_last_imported' not in st.session_state: st.session_state.address_last_imported='' 
d=st.session_state.deal
secrets=st.secrets
rentcast_key=secrets.get('RENTCAST_API_KEY','')
sb_url=secrets.get('SUPABASE_URL','')
sb_key=secrets.get('SUPABASE_PUBLISHABLE_KEY','')

with st.sidebar:
    st.header('Deal Settings')
    d.minimum_cashflow=st.number_input('Minimum monthly cash flow ($)',min_value=0.0,max_value=5000.0,value=float(d.minimum_cashflow),step=25.0)
    d.minimum_recovery=st.number_input('BRRRR cash recovery target (%)',min_value=0.0,max_value=100.0,value=float(d.minimum_recovery*100),step=5.0)/100
    d.minimum_dscr=st.number_input('Minimum DSCR',0.5,3.0,float(d.minimum_dscr),step=.05)
    d.flip_min_profit=st.number_input('Flip minimum profit ($)',min_value=0.0,max_value=250000.0,value=float(d.flip_min_profit),step=1000.0)
    d.flip_min_roi=st.number_input('Flip minimum ROI (%)',min_value=0.0,max_value=100.0,value=float(d.flip_min_roi*100),step=5.0)/100
    st.info('Visitors can analyze anonymously. Saving requires an authenticated Supabase account.')

from core.offer_sensitivity import offer_curve, offer_range

def render_brief_verdict(deal):
    """Compact, preliminary verdict using current editable assumptions."""
    try:
        summary=analyze(deal)
    except ValueError:
        st.info('Enter a positive purchase price and ARV to preview the investment strategies.')
        return
    b=summary['brrrr']; f=summary['flip']
    st.markdown('<div class="section-eyebrow">Live decision preview</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2,gap='medium')
    with c1:
        with st.container(border=True):
            st.markdown('**🏘️ BRRRR / Buy & Hold**')
            a,b2=st.columns(2)
            a.metric('Score',f"{b['score']}/100")
            b2.metric('Cash flow / month',f"${b['monthly_cashflow']:,.0f}")
            st.caption(('✅ Targets met' if b['passed'] else '⚠️ Below one or more targets')+' · '+b['verdict'])
    with c2:
        with st.container(border=True):
            st.markdown('**🛠️ Fix & Flip**')
            a,b2=st.columns(2)
            a.metric('Score',f"{f['score']}/100")
            b2.metric('Pre-tax profit',f"${f['profit']:,.0f}")
            st.caption(('✅ Targets met' if f['passed'] else '⚠️ Below one or more targets')+' · '+f['verdict'])
    if b['passed'] and f['passed']:
        st.success('Both strategies meet modeled financial thresholds. Compare risks and assumptions before deciding.')
    elif b['passed']:
        st.success('BRRRR meets modeled financial targets; Fix & Flip does not.')
    elif f['passed']:
        st.success('Fix & Flip meets modeled financial targets; BRRRR does not.')
    else:
        st.warning('Neither strategy meets all modeled financial targets at this asking price.')
    if deal.arv_confidence!='Verified comps' or deal.rent_confidence!='Verified comps':
        st.caption('⚠️ Preliminary: ARV and/or rent evidence has not been verified. The full explanation is in Investment Decision.')
    else:
        st.caption('Evidence marked verified by user; lender terms, comps, permits and repairs still require independent confirmation.')

tabs=st.tabs(['🔎 Research','🛠 Renovation','💰 Assumptions','📈 Investment Decision','💾 Saved Deals'])
with tabs[0]:
    st.markdown('<div class="section-eyebrow">01 / Property research</div>',unsafe_allow_html=True)
    st.subheader('Find the property and its market evidence')
    st.caption('Enter a complete US address. One click retrieves available property details, value/rent estimates and nearby comparable candidates. Cleveland is the default focus, not a geographic restriction.')
    addr_col, lookup_col=st.columns([5,2],vertical_alignment='bottom')
    with addr_col:
        d.address=st.text_input('Property address',value=d.address,placeholder='123 Main St, Lakewood, OH 44107',help='Enter any US address supported by RentCast. Include city and state to avoid ambiguous results.')
    with lookup_col:
        search_pressed=st.button('🔎 Find property & comps',type='primary',use_container_width=True,disabled=not bool(rentcast_key and d.address.strip()))
    st.caption('Uses up to 3 RentCast requests per uncached address; 24-hour cache. Search only runs when you click. Imported comps start unselected and unverified.')
    if not rentcast_key:
        st.warning('Add RENTCAST_API_KEY to Streamlit Secrets to enable lookup. Manual underwriting is still available.')
    if search_pressed:
        from services.comp_discovery import normalize_avm_candidates
        from services.comp_merge import merge_comp_rows
        try:
            with st.spinner('Fetching property details and comparable candidates…'):
                result=rentcast_data(d.address.strip(),rentcast_key,True)
            fetched_addr=d.address.strip()
            old_addr=st.session_state.address_last_imported
            # When switching to a different address, do not silently attach the previous property's comps.
            replace_subject=bool(old_addr and old_addr.casefold()!=fetched_addr.casefold())
            from services.geo import coords, attach_distances
            property_record=(result.get('property') or [{}])[0]
            subject_coordinates=coords(property_record)
            st.session_state.subject_coordinates=subject_coordinates
            sales=attach_distances(normalize_avm_candidates(result.get('value',{}),'sale',fetched_addr),subject_coordinates)
            rentals=attach_distances(normalize_avm_candidates(result.get('rent',{}),'rent',fetched_addr),subject_coordinates)
            for comp_type, candidates in [('sale',sales),('rent',rentals)]:
                key='comp_rows_'+comp_type
                previous=[] if replace_subject else st.session_state.get(key,[])
                st.session_state[key]=merge_comp_rows(previous,candidates)
            st.session_state.comp_import_version+=1
            st.session_state.address_last_imported=fetched_addr
            st.session_state.lookup={'retrieved_at':datetime.now(timezone.utc).isoformat(),'address':fetched_addr,'data':result}
            st.success(f'Found {len(sales)} sale and {len(rentals)} rental candidates. They are in the comp workbench below, awaiting your review.')
        except Exception as exc:
            st.error(f'Property lookup failed: {exc}')
    with st.expander('Search additional nearby sold records and rental listings', expanded=False):
        st.caption('This performs a real radius search at RentCast, separate from the AVM candidates above. Each click can use two extra API requests (cached for 24 hours).')
        m1,m2,m3=st.columns([1,1,1.3])
        with m1:
            market_radius=st.selectbox('Actual API radius (miles)',[0.5,1.0,2.0,3.0,5.0,10.0],index=2,key='market_radius')
        with m2:
            market_age=st.selectbox('Sold lookback (months)',[3,6,9,12,18,24],index=1,key='market_age')
        with m3:
            market_max=st.selectbox('Maximum candidates per source',[10,20,30],index=1,key='market_limit',help='Limit applied locally after retrieval; the API is capped to 30 records per call.')
        st.caption('Sales come from property records showing past sale prices and dates; rental results are listing asking rents. Verify both before underwriting.')
        market_pressed=st.button('Search wider market by radius',disabled=not bool(rentcast_key and d.address.strip()),use_container_width=True)
        if market_pressed:
            from services.comp_merge import merge_comp_rows
            from services.geo import coords,attach_distances
            try:
                with st.spinner('Searching recently sold records and rental listings…'):
                    sr=geographic_data(d.address.strip(),rentcast_key,market_radius,market_age,d.kind)
                subject_coordinates=st.session_state.get('subject_coordinates')
                for category in ('sale','rent'):
                    key='comp_rows_'+category
                    candidates=attach_distances(sr[category][:market_max],subject_coordinates)
                    prev=st.session_state.get(key,[])
                    if st.session_state.get('market_import_address','').casefold() not in ('',d.address.strip().casefold()):
                        prev=[]
                    st.session_state[key]=merge_comp_rows(prev,candidates)
                st.session_state.market_import_address=d.address.strip()
                st.session_state.comp_import_version+=1
                st.success(f"Imported {min(market_max,len(sr['sale']))} sold-record and {min(market_max,len(sr['rent']))} rental-listing candidates. Review them below.")
            except Exception as exc:
                st.error(f'Market search failed: {exc}')
    c1,c2,c3,c4=st.columns(4)
    with c1: d.kind=st.selectbox('Type',['Single Family','Duplex','Triplex','Fourplex'],index=['Single Family','Duplex','Triplex','Fourplex'].index(d.kind))
    d.units={'Single Family':1,'Duplex':2,'Triplex':3,'Fourplex':4}[d.kind]
    with c2: d.price=st.number_input('Asking / offer price ($)',min_value=1000.,value=float(d.price),step=5000.)
    with c3: d.arv=st.number_input('After-repair value ($)',min_value=1000.,value=float(d.arv),step=5000.)
    with c4: d.rent=st.number_input('Total monthly rent ($)',min_value=0.,value=float(d.rent),step=100.)
    lookup=st.session_state.lookup
    if lookup and lookup.get('address','').casefold()==d.address.strip().casefold():
        data=lookup.get('data',{})
        prop=data.get('property',[])
        val=data.get('value',{}) or {}; rental=data.get('rent',{}) or {}
        v=val.get('price') or val.get('value'); r=rental.get('rent')
        with st.container(border=True):
            st.markdown('**Latest property research**')
            st.caption('Retrieved '+lookup['retrieved_at'][:19].replace('T',' ')+' UTC · Provider estimates are not renovated ARV or signed lease rents.')
            cc1,cc2,cc3=st.columns(3)
            cc1.metric('Value estimate',f'${v:,.0f}' if isinstance(v,(float,int)) else 'Unavailable')
            cc2.metric('Rent estimate',f'${r:,.0f}' if isinstance(r,(float,int)) else 'Unavailable')
            cc3.metric('Comparables retrieved',len(st.session_state.get('comp_rows_sale',[]))+len(st.session_state.get('comp_rows_rent',[])))
            if isinstance(prop,list) and prop:
                p=prop[0]
                st.caption(f"Property: {p.get('bedrooms','?')} beds · {p.get('bathrooms','?')} baths · {p.get('squareFootage','?')} sq ft · Built {p.get('yearBuilt','?')}")
            with st.expander('Review provider data and apply provisional estimates'):
                if isinstance(prop,list) and prop:
                    st.json({k:prop[0].get(k) for k in ('formattedAddress','propertyType','bedrooms','bathrooms','squareFootage','yearBuilt','lastSalePrice','propertyTaxes')})
                a1,a2=st.columns(2)
                if a1.button('Use provider value as provisional ARV',disabled=not isinstance(v,(float,int))):
                    d.arv=float(v)
                    st.rerun()
                if a2.button('Use provider rent as assumption',disabled=not isinstance(r,(float,int))):
                    d.rent=float(r)
                    st.rerun()
                st.warning('A provider value estimate is not verified renovated ARV. A rental estimate is not a signed lease.')
    elif lookup:
        st.info('The address has changed since the last lookup. Click Find property & comps to refresh this property.')
    a,b=st.columns(2)
    with a: d.arv_confidence=st.selectbox('ARV evidence',['Unverified','Verified comps'],index=['Unverified','Verified comps'].index(d.arv_confidence),help='Choose Verified comps only after you review recent comparable sold renovated properties.')
    with b: d.rent_confidence=st.selectbox('Rent evidence',['Unverified','Verified comps'],index=['Unverified','Verified comps'].index(d.rent_confidence))
    st.caption('For multifamily enter total property value and total projected monthly rent. Verify zoning and legal unit count independently.')
    st.divider()
    render_brief_verdict(d)

    st.divider()
    st.markdown('<div class="section-eyebrow">02 / Comparable screening</div>',unsafe_allow_html=True)
    st.subheader('Nearby comparable evidence')
    st.caption('Candidate comps are imported automatically when you click Find property & comps. Select and verify each one before using it for ARV or market rent.')
    from services.comp_discovery import normalize_avm_candidates
    sale_count=len(st.session_state.get('comp_rows_sale',[]))
    rent_count=len(st.session_state.get('comp_rows_rent',[]))
    a1,a2=st.columns(2)
    a1.metric('Sale candidates to review',sale_count)
    a2.metric('Rental candidates to review',rent_count)
    st.info('Only checked comps enter the calculations. Closed sales, renovation condition, proximity, date, and whole-building vs. unit rental comparability require human verification.')
    from core.comps import evaluate_comps
    subject_sqft = st.number_input('Subject finished above-grade square footage', min_value=0, value=0, step=50,
                                   help='Enter from assessor or listing and verify. Required for sale $/sqft adjustment.')
    subject_beds = st.number_input('Subject bedrooms', min_value=0, max_value=20, value=3, step=1)
    st.info('For 2–4 units, use whole-building sales and comparable whole-building square footage for ARV. Rental comps should represent comparable whole properties, or total the unit-level rents yourself. Do not mix per-unit and whole-property amounts.')
    with st.container(border=True):
        st.markdown('**Comparable screening preferences**')
        filter_a,filter_b,filter_c=st.columns([1,1,1.35])
        with filter_a:
            radius=st.selectbox('Workbench radius filter',options=[0.5,1.0,2.0,3.0,5.0,10.0],index=2,format_func=lambda x:f'{x:g} miles',help='Filters imported candidates when coordinates or analyst-entered distance are known. Does not change the provider API search radius.')
        with filter_b:
            age_window=st.selectbox('Maximum comp age',options=[3,6,9,12,18,24],index=1,format_func=lambda x:f'{x} months',help='Uses the row date; provider dates may represent listing activity rather than verified sale dates.')
        with filter_c:
            unknown_distance=st.checkbox('Exclude unknown-distance comps',value=False,help='When checked, comps without verifiable distance cannot be included in the indicated value/rent.')
        st.caption('These controls screen candidate rows after import. For an actual new API search radius, use Search additional nearby sold records and rental listings above. Each row identifies whether its date represents a recorded sale or listing activity.')
    for comp_type, label in [('sale','Renovated sale comps'), ('rent','Comparable rental listings / leases')]:
        with st.expander(label, expanded=False):
            st.write('Add or edit rows. Mark **renovated** only after you review condition/photos for sale comps. Enter ISO dates such as 2026-08-15. Only checked rows count.')
            key='comp_rows_'+comp_type
            if key not in st.session_state:
                st.session_state[key]=[{'include':True,'address':'','amount':0.0,'sqft':0.0,'bedrooms':3,'date':'','renovated':False}]
            changed=st.data_editor(st.session_state[key],num_rows='dynamic',use_container_width=True,
                                  key='editor_'+comp_type+'_'+str(st.session_state.comp_import_version),
                                  column_config={
                                    'include':st.column_config.CheckboxColumn('Use'),
                                    'address':st.column_config.TextColumn('Comp address'),
                                    'amount':st.column_config.NumberColumn('Sold price ($)' if comp_type=='sale' else 'Monthly rent ($)',min_value=0.0,format='$%.0f'),
                                    'sqft':st.column_config.NumberColumn('Sq ft',min_value=0.0),
                                    'bedrooms':st.column_config.NumberColumn('Beds',min_value=0),
                                    'date':st.column_config.TextColumn('Close/list date YYYY-MM-DD'),
                                    'renovated':st.column_config.CheckboxColumn('Renovated confirmed'),
                                    'distance_miles':st.column_config.NumberColumn('Miles away',min_value=0.0,format='%.2f'),
                                    'source':st.column_config.TextColumn('Source'),
                                    'date_type':st.column_config.TextColumn('Date meaning')})
            st.session_state[key]=changed
            comp_result=evaluate_comps(changed,comp_type,subject_sqft or None,subject_beds,max_age_months=age_window,max_radius_miles=radius,require_known_distance=unknown_distance)
            st.write(f"**Evidence:** {comp_result['count']} eligible comps ({comp_result['recent_count']} within 6 months) — {comp_result['confidence']}")
            if comp_result['estimate'] is not None:
                st.metric('Comp-derived '+('ARV indication' if comp_type=='sale' else 'rent indication'),f"${comp_result['estimate']:,.0f}")
                st.caption(f"Observed eligible range: ${comp_result['low']:,.0f}–${comp_result['high']:,.0f}. Sale indication uses simple $/sqft scaling, not full appraisal adjustments.")
                if st.button('Apply comp indication to '+('ARV' if comp_type=='sale' else 'monthly rent'),key='apply_comp_'+comp_type):
                    if comp_type=='sale':
                        d.arv=float(comp_result['estimate'])
                        st.info('ARV assumption updated in memory. Review the ARV evidence selector separately; this is not automatically verified.')
                    else:
                        d.rent=float(comp_result['estimate'])
                        st.info('Rental assumption updated in memory. Review the rent evidence selector separately.')
            if comp_result['rejected']:
                st.write('**Excluded comps and reasons**')
                st.dataframe([{'Address':a,'Reason':reason} for a,reason in comp_result['rejected']],hide_index=True,use_container_width=True)
            st.caption(comp_result['disclaimer'])
    st.warning('Comp analysis is decision support, not an appraisal. Verify property similarity, sales concessions, distance, renovation quality and local rent restrictions before treating figures as reliable.')
with tabs[1]:
    st.markdown('<div class="section-eyebrow">03 / Scope & budget</div>',unsafe_allow_html=True)
    st.subheader('Renovation planning')
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
    st.markdown('<div class="section-eyebrow">04 / Underwriting inputs</div>',unsafe_allow_html=True)
    st.subheader('Financing and operating assumptions')
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
    st.markdown('<div class="section-eyebrow">05 / Investment decision</div>',unsafe_allow_html=True)
    st.subheader('Which exit strategy makes more sense?')
    st.caption('Investment scores depend on your assumptions; the financial targets and evidence checks below explain the recommendation.')
    try:
        result=analyze(d)
        st.session_state.last_analysis={'inputs':asdict(d),'results':result,'timestamp':datetime.now(timezone.utc).isoformat(),
                                        'analysis_version':'1.6',
                                        'comparable_inputs':{'sales':st.session_state.get('comp_rows_sale',[]),'rentals':st.session_state.get('comp_rows_rent',[])}}
        b,f=result['brrrr'],result['flip']
        def money(value):
            return f'${value:,.0f}'
        x,y=st.columns(2, gap='large')
        with x:
            with st.container(border=True):
                st.markdown('### 🏘️ BRRRR · Hold & refinance')
                st.metric('Feasibility score',f"{b['score']}/100")
                st.caption('Financial screening: '+b['verdict'])
                m1,m2=st.columns(2)
                m1.metric('Monthly cash flow',money(b['monthly_cashflow']))
                m2.metric('Capital returned',f"{b['recovery']:.0%}")
                m3,m4=st.columns(2)
                m3.metric('Cash left invested',money(b['cash_left']))
                m4.metric('DSCR',f"{b['dscr']:.2f}")
                st.progress(min(100,max(0,int(b['score'])))/100,text=f"BRRRR score · {b['score']} out of 100")
        with y:
            with st.container(border=True):
                st.markdown('### 🛠️ Fix & Flip · Renovate & sell')
                st.metric('Feasibility score',f"{f['score']}/100")
                st.caption('Financial screening: '+f['verdict'])
                m1,m2=st.columns(2)
                m1.metric('Pre-tax profit',money(f['profit']))
                m2.metric('Project cash ROI',f"{f['roi']:.1%}")
                m3,m4=st.columns(2)
                m3.metric('Break-even sale',money(f['break_even_sale']))
                m4.metric('Estimated exit',f"{result['shared']['months']} months")
                st.progress(min(100,max(0,int(f['score'])))/100,text=f"Flip score · {f['score']} out of 100")
        st.divider()
        st.subheader('Side-by-side qualification')
        verdicts = [
            {'Strategy':'BRRRR', 'Score':f"{b['score']}/100", 'Cash / profit':f"${b['monthly_cashflow']:,.0f} / month", 'Critical checks': 'Cash flow, DSCR and 75% cash recovery', 'Financial target met': 'Yes' if b['passed'] else 'No'},
            {'Strategy':'Fix & Flip', 'Score':f"{f['score']}/100", 'Cash / profit':f"${f['profit']:,.0f} pre-tax profit", 'Critical checks': 'Net profit and project cash ROI', 'Financial target met': 'Yes' if f['passed'] else 'No'},
        ]
        st.dataframe(verdicts, hide_index=True, use_container_width=True)
        if d.arv_confidence != 'Verified comps' or d.rent_confidence != 'Verified comps':
            st.warning('Evidence confidence is not fully verified. Scores reflect assumed inputs, not a confirmed purchase recommendation.')
        else:
            st.info('Comps marked verified by analyst. Confirm recorded sales and executed rent comparability separately.')
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
        with st.container(border=True):
            st.markdown('### What if I offered a different price?')
            st.caption('Explore how purchase price changes projected monthly BRRRR cash flow and Fix & Flip net profit. All other assumptions remain fixed.')
            lower,upper,step=offer_range(d.price)
            trial=st.slider('Hypothetical purchase offer ($)',min_value=lower,max_value=upper,value=min(upper,max(lower,int(round(d.price/step)*step))),step=step,key='hypothetical_offer')
            from dataclasses import replace
            trial_result=analyze(replace(d,price=trial))
            sc1,sc2,sc3=st.columns(3)
            sc1.metric('Trial offer',f'${trial:,.0f}',delta=f'${trial-d.price:,.0f} vs current price',delta_color='off')
            sc2.metric('BRRRR cash flow',f"${trial_result['brrrr']['monthly_cashflow']:,.0f}/mo")
            sc3.metric('Flip profit',f"${trial_result['flip']['profit']:,.0f}")
            st.caption('The trial price is for exploration only—it does not overwrite the asking/offer price used elsewhere in the app.')
            curve=offer_curve(d,lower,upper,step)
            st.markdown('**Monthly BRRRR cash flow vs. purchase price**')
            st.line_chart(curve,x='Offer',y='BRRRR cash flow / month',x_label='Purchase / offer price ($)',y_label='Monthly cash flow ($)',color='#37CBB4')
            st.markdown('**Pre-tax Fix & Flip profit vs. purchase price**')
            st.line_chart(curve,x='Offer',y='Flip net profit',x_label='Purchase / offer price ($)',y_label='Flip profit ($)',color='#64A8ED')
            st.caption('Scenarios are estimates; the flip chart reflects the existing model’s financing, holding and sales assumptions. Negative values represent projected losses. This is not a quote or offer recommendation.')

        from core.insights import build_insights
        insights=build_insights(d,result)
        st.subheader('Decision explained — at a glance')
        st.caption('Prioritized findings from your actual inputs and scoring rules. Open the detailed category explanations below for formulas and thresholds.')
        ic1,ic2,ic3=st.columns(3,gap='medium')
        for col,label,klass,emoji,items in [
            (ic1,'Strengths','good','✅',insights['strengths']),
            (ic2,'Risks & shortfalls','risk','⚠️',insights['risks']),
            (ic3,'Verify before offering','verify','🔎',insights['verifications'])]:
            with col:
                st.markdown(f'#### {emoji} {label}')
                if not items: st.caption('None currently identified from the modeled inputs.')
                for msg in items[:5]:
                    import html
                    st.markdown(f'<div class="insight {klass}">{html.escape(msg)}</div>',unsafe_allow_html=True)
        st.divider()
        st.markdown('### Why each strategy scored this way')
        st.caption('Open any category to see actual results, thresholds, and actions that could improve confidence or economics.')
        for heading,section in [('BRRRR score explained',b),('Fix & Flip score explained',f)]:
            st.markdown('### '+heading)
            for i,item in enumerate(section['items']):
                with st.expander(f"{'✅' if item['status']=='Good' else '⚠️'} {item['name']} • {item['score']}/{item['max']} • {item['status']}",expanded=item['status']!='Good'):
                    st.write(item['why'])
                    st.write('**How to improve / verify:** '+item['action'])
                    st.write('**Observed:**',round(item['value'],3),'| **Target:**',round(item['threshold'],3))
        st.subheader('Evidence and execution gates')
        missing=[]
        if d.arv_confidence!='Verified comps': missing.append('ARV: review recent, similar renovated sold properties before relying on flip profit or refinancing.')
        if d.rent_confidence!='Verified comps': missing.append('Rent: verify rental comps before relying on cash flow and DSCR.')
        if d.contingency < .15: missing.append('Rehab contingency is below the suggested 15% starting allowance.')
        if missing:
            for issue in missing: st.warning(issue)
            st.caption('Passing financial thresholds with unverified evidence is conditional, not a purchase recommendation.')
        else:
            st.success('Evidence checkboxes were marked verified by the analyst. Validate their underlying source records independently.')
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
    st.markdown('<div class="section-eyebrow">06 / Your deal library</div>',unsafe_allow_html=True)
    st.subheader('Private saved analyses')
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

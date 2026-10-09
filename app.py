
import streamlit as st

st.set_page_config(
    page_title="Cleveland Property Investor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Cleveland Property Investor")
st.caption("BRRRR & Fix-and-Flip Investment Analyzer")

st.info(
    "Version 0.1 — Initial application setup. "
    "Full underwriting features are coming next."
)

st.header("Analyze a Property")

address = st.text_input(
    "Property Address",
    placeholder="123 Main St, Lakewood, OH 44107"
)

property_type = st.selectbox(
    "Property Type",
    [
        "Single Family",
        "Duplex",
        "Triplex",
        "Fourplex"
    ]
)

col1, col2 = st.columns(2)

with col1:
    purchase_price = st.number_input(
        "Purchase Price ($)",
        min_value=0,
        value=150000,
        step=5000
    )

    rehab_budget = st.number_input(
        "Estimated Rehab Budget ($)",
        min_value=0,
        value=35000,
        step=1000
    )

with col2:
    arv = st.number_input(
        "After Repair Value ($)",
        min_value=0,
        value=240000,
        step=5000
    )

    monthly_rent = st.number_input(
        "Estimated Monthly Rent ($)",
        min_value=0,
        value=2000,
        step=100
    )

st.divider()

st.subheader("Preliminary Property Overview")

total_cost = purchase_price + rehab_budget
equity_spread = arv - total_cost

metric1, metric2, metric3 = st.columns(3)

metric1.metric("Purchase + Rehab", f"${total_cost:,.0f}")
metric2.metric("Estimated ARV", f"${arv:,.0f}")
metric3.metric("Gross Equity Spread", f"${equity_spread:,.0f}")

st.warning(
    "The gross equity spread excludes closing costs, "
    "financing, carrying costs, selling expenses and taxes. "
    "It is NOT a profitability or feasibility score."
)

st.divider()

tab1, tab2 = st.tabs(["BRRRR Analysis", "Fix & Flip Analysis"])

with tab1:
    st.subheader("BRRRR Analyzer")
    st.write(
        "Coming in V1.0: rental cash flow, refinancing, "
        "capital recovery, DSCR, maximum offer, "
        "and explained investment scoring."
    )

with tab2:
    st.subheader("Fix & Flip Analyzer")
    st.write(
        "Coming in V1.0: selling expenses, financing, "
        "holding costs, net profit, ROI, maximum offer, "
        "and explained investment scoring."
    )

st.sidebar.header("About")
st.sidebar.write("Cleveland Property Investor")
st.sidebar.write("Version: 0.1.0")
st.sidebar.write("Status: Initial deployment")

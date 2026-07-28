import streamlit as st
import pandas as pd

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)


st.title("📄 Financial Reports Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    companies = load_table("companies")
    ratios = load_table("financial_ratios")
    pnl = load_table("profitandloss")
    cashflow = load_table("cashflow")
    peers = load_table("peer_percentiles")
    market_cap = load_table("market_cap")
    proscons = load_table("prosandcons")

except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Company Selection
# -------------------------

selected_company = st.selectbox(

    "Select Company",

    companies["company_name"]
    .dropna()
    .unique()

)


company_id = companies.loc[

    companies["company_name"] == selected_company,

    "id"

].iloc[0]



# -------------------------
# Prepare Report Data
# -------------------------

company_ratio = ratios[

    ratios["company_id"] == company_id

].sort_values("year")


company_pnl = pnl[

    pnl["company_id"] == company_id

].sort_values("year")


company_cash = cashflow[

    cashflow["company_id"] == company_id

].sort_values("year")


company_market = market_cap[

    market_cap["company_id"] == company_id

].sort_values("year")



# -------------------------
# Company Summary
# -------------------------

st.divider()

st.subheader(
    "🏢 Company Summary"
)


st.write(
    f"""
    **Company:** {selected_company}

    **Latest Financial Year:**
    {company_ratio['year'].max()
    if not company_ratio.empty else 'N/A'}
    """
)



# -------------------------
# Financial Health
# -------------------------

st.subheader(
    "📊 Financial Health"
)


if not company_ratio.empty:

    latest = company_ratio.iloc[-1]


    metrics = pd.DataFrame({

        "Metric":[

            "ROE",
            "ROCE",
            "ROA",
            "Net Profit Margin",
            "Operating Margin",
            "Quality Score"

        ],

        "Value":[

            latest["return_on_equity_pct"],
            latest["return_on_capital_employed_pct"],
            latest["return_on_assets_pct"],
            latest["net_profit_margin_pct"],
            latest["operating_profit_margin_pct"],
            latest["composite_quality_score"]

        ]

    })


    st.dataframe(

        metrics,

        use_container_width=True

    )



# -------------------------
# Growth Report
# -------------------------

st.divider()

st.subheader(
    "📈 Growth Analysis"
)


if not company_pnl.empty:

    growth = company_pnl[

        [
            "year",
            "sales",
            "net_profit"

        ]

    ]


    st.dataframe(

        growth,

        use_container_width=True

    )



# -------------------------
# Cash Flow
# -------------------------

st.divider()

st.subheader(
    "💵 Cash Flow Summary"
)


if not company_cash.empty:

    st.dataframe(

        company_cash,

        use_container_width=True

    )



# -------------------------
# Market Position
# -------------------------

st.divider()

st.subheader(
    "🏦 Market Position"
)


if not company_market.empty:

    st.dataframe(

        company_market,

        use_container_width=True

    )



# -------------------------
# Peer Position
# -------------------------

st.divider()

st.subheader(
    "👥 Peer Position"
)


company_peer = peers[

    peers["company_id"] == company_id

]


if not company_peer.empty:

    st.dataframe(

        company_peer,

        use_container_width=True

    )



# -------------------------
# Pros & Cons
# -------------------------

st.divider()

st.subheader(
    "⚖️ Pros & Cons"
)


company_pc = proscons[

    proscons["company_id"] == company_id

]


if not company_pc.empty:

    st.dataframe(

        company_pc,

        use_container_width=True

    )


# -------------------------
# CSV Export
# -------------------------

st.divider()

st.subheader(
    "⬇ Export Report"
)


report = {

    "Financial Metrics": metrics
    if not company_ratio.empty
    else pd.DataFrame(),

    "Growth": company_pnl,

    "Cash Flow": company_cash,

    "Market": company_market,

    "Peers": company_peer

}


csv_data = pd.concat(

    report.values(),

    ignore_index=True

).to_csv(index=False)



st.download_button(

    label="Download CSV Report",

    data=csv_data,

    file_name=f"{selected_company}_financial_report.csv",

    mime="text/csv"

)


st.success(
    "Financial Report Generated Successfully"
)
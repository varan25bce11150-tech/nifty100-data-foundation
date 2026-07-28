import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Home Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Nifty100 Financial Analytics Platform")


st.markdown(
    """
    ## Market Intelligence Dashboard

    Analytics platform covering:

    - Financial health
    - Growth analysis
    - Quality ranking
    - Sector intelligence
    - Market capitalization
    """
)



# -------------------------
# Load Database
# -------------------------

try:

    companies = load_table("companies")
    ratios = load_table("financial_ratios")
    peers = load_table("peer_percentiles")
    market_cap = load_table("market_cap")
    sectors = load_table("sectors")


except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Latest Year Data
# -------------------------

latest_year = ratios["year"].max()

latest_ratios = ratios[

    ratios["year"] == latest_year

]



# -------------------------
# Platform Statistics
# -------------------------

st.subheader(
    "📌 Platform Statistics"
)


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Companies Covered",
    companies["id"].nunique()
)


col2.metric(
    "Financial Records",
    len(ratios)
)


col3.metric(
    "Peer Rankings",
    len(peers)
)


col4.metric(
    "Financial Years",
    f"{ratios['year'].min()}-{latest_year}"
)



# -------------------------
# Market Health
# -------------------------

st.divider()

st.subheader(
    "📈 Market Health Snapshot"
)



col1, col2, col3, col4 = st.columns(4)



col1.metric(

    "Average ROE",

    f"{latest_ratios['return_on_equity_pct'].mean():.2f}%"

)



col2.metric(

    "Average ROCE",

    f"{latest_ratios['return_on_capital_employed_pct'].mean():.2f}%"

)



col3.metric(

    "Average Quality Score",

    f"{latest_ratios['composite_quality_score'].mean():.2f}"

)



col4.metric(

    "Market Cap Records",

    len(market_cap)

)



# -------------------------
# Sector Distribution
# -------------------------

st.divider()

st.subheader(
    "🏭 Sector Distribution"
)



sector_data = (

    sectors

    .groupby("sector")

    ["company_id"]

    .nunique()

    .reset_index()

)



sector_data.columns = [

    "Sector",

    "Companies"

]



fig = px.bar(

    sector_data,

    x="Sector",

    y="Companies",

    title="Companies Across Sectors"

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# -------------------------
# Top Quality Companies
# -------------------------

st.divider()

st.subheader(
    "🏆 Top Quality Companies"
)



quality = latest_ratios.merge(

    companies[

        [
            "id",
            "company_name"

        ]

    ],

    left_on="company_id",

    right_on="id",

    how="left"

)



quality_table = quality.sort_values(

    "composite_quality_score",

    ascending=False

).head(10)



st.dataframe(

    quality_table[

        [
            "company_name",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "composite_quality_score"

        ]

    ],

    use_container_width=True

)



# -------------------------
# Growth Leaders
# -------------------------

st.divider()

st.subheader(
    "🚀 Growth Leaders"
)



growth = quality.sort_values(

    "revenue_cagr_5yr",

    ascending=False

).head(10)



st.dataframe(

    growth[

        [
            "company_name",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr"

        ]

    ],

    use_container_width=True

)



# -------------------------
# Market Cap Preview
# -------------------------

st.divider()

st.subheader(
    "💰 Market Capitalization Preview"
)


st.dataframe(

    market_cap.head(10),

    use_container_width=True

)



st.success(
    "Home Dashboard Loaded Successfully"
)
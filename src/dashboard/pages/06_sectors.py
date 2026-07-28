import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Sector Analysis",
    page_icon="🏭",
    layout="wide"
)


st.title("🏭 Sector Analysis Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    sectors = load_table("sectors")
    ratios = load_table("financial_ratios")
    market_cap = load_table("market_cap")
    companies = load_table("companies")

except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Merge Sector Data
# -------------------------

sector_data = sectors.merge(

    ratios,

    on="company_id",

    how="left"

)


sector_data = sector_data.merge(

    companies[["id", "company_name"]],

    left_on="company_id",

    right_on="id",

    how="left"

)



# -------------------------
# Sector Overview
# -------------------------

st.subheader(
    "📌 Sector Overview"
)


sector_count = (

    sector_data

    .groupby("sector")

    ["company_id"]

    .nunique()

    .reset_index()

)


sector_count.columns = [

    "Sector",

    "Companies"

]


fig = px.bar(

    sector_count,

    x="Sector",

    y="Companies",

    title="Companies by Sector"

)


st.plotly_chart(

    fig,

    use_container_width=True

)



# -------------------------
# Sector Quality Ranking
# -------------------------

st.divider()

st.subheader(
    "🏆 Sector Quality Ranking"
)


quality = (

    sector_data

    .groupby("sector")

    .agg(

        Avg_ROE=(
            "return_on_equity_pct",
            "mean"
        ),

        Avg_ROCE=(
            "return_on_capital_employed_pct",
            "mean"
        ),

        Avg_Quality=(
            "composite_quality_score",
            "mean"
        )

    )

    .reset_index()

)



quality = quality.sort_values(

    "Avg_Quality",

    ascending=False

)



st.dataframe(

    quality,

    use_container_width=True

)



fig = px.bar(

    quality,

    x="sector",

    y="Avg_Quality",

    title="Average Sector Quality Score"

)


st.plotly_chart(

    fig,

    use_container_width=True

)



# -------------------------
# Market Cap Analysis
# -------------------------

st.divider()

st.subheader(
    "💰 Sector Market Capitalization"
)


sector_market = sectors.merge(

    market_cap,

    on="company_id",

    how="left"

)



market_summary = (

    sector_market

    .groupby("sector")

    ["market_cap"]

    .sum()

    .reset_index()

)



market_summary.columns = [

    "Sector",

    "Total Market Cap"

]



fig = px.bar(

    market_summary,

    x="Sector",

    y="Total Market Cap",

    title="Sector Market Cap Distribution"

)



st.plotly_chart(

    fig,

    use_container_width=True

)



# -------------------------
# Sector Filter
# -------------------------

st.divider()

st.subheader(
    "🔎 Sector Companies"
)


selected_sector = st.selectbox(

    "Select Sector",

    sorted(
        sector_data["sector"]
        .dropna()
        .unique()
    )

)


companies_in_sector = sector_data[

    sector_data["sector"] == selected_sector

]



st.dataframe(

    companies_in_sector[

        [
            "company_name",
            "industry",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "composite_quality_score"

        ]

    ],

    use_container_width=True

)



st.success(
    "Sector Analysis Loaded Successfully"
)
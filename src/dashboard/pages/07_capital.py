import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Capital Analysis",
    page_icon="💰",
    layout="wide"
)


st.title("💰 Capital Analysis Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    companies = load_table("companies")
    ratios = load_table("financial_ratios")
    cashflow = load_table("cashflow")
    market_cap = load_table("market_cap")


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



company_ratios = ratios[

    ratios["company_id"] == company_id

].sort_values("year")



company_cashflow = cashflow[

    cashflow["company_id"] == company_id

].sort_values("year")



company_market = market_cap[

    market_cap["company_id"] == company_id

].sort_values("year")



# -------------------------
# Capital Efficiency
# -------------------------

st.divider()

st.subheader(
    "📊 Capital Efficiency Metrics"
)


if not company_ratios.empty:


    latest = company_ratios.iloc[-1]


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "ROE",
        f"{latest['return_on_equity_pct']:.2f}%"
    )


    col2.metric(
        "ROCE",
        f"{latest['return_on_capital_employed_pct']:.2f}%"
    )


    col3.metric(
        "ROA",
        f"{latest['return_on_assets_pct']:.2f}%"
    )


    col4.metric(
        "Quality Score",
        f"{latest['composite_quality_score']:.2f}"
    )


else:

    st.warning(
        "No ratio data available"
    )



# -------------------------
# Capital Efficiency Trend
# -------------------------

st.divider()

st.subheader(
    "📈 Return Metrics Trend"
)


if not company_ratios.empty:


    fig = px.line(

        company_ratios,

        x="year",

        y=[
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "return_on_assets_pct"
        ],

        markers=True,

        title="ROE / ROCE / ROA Trend"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )



# -------------------------
# Cash Flow Analysis
# -------------------------

st.divider()

st.subheader(
    "💵 Cash Flow Analysis"
)


if not company_cashflow.empty:


    fig = px.bar(

        company_cashflow,

        x="year",

        y=[
            "operating_activity",
            "investing_activity",
            "financing_activity"
        ],

        title="Cash Flow Components"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    fig2 = px.line(

        company_cashflow,

        x="year",

        y="net_cash_flow",

        markers=True,

        title="Net Cash Flow Trend"

    )


    st.plotly_chart(

        fig2,

        use_container_width=True

    )


else:

    st.warning(
        "No cash flow data available"
    )



# -------------------------
# Market Cap vs Quality
# -------------------------

st.divider()

st.subheader(
    "🏦 Market Cap vs Quality"
)


if not company_market.empty and not company_ratios.empty:


    comparison = company_market.merge(

        company_ratios[

            [
                "year",
                "composite_quality_score"

            ]

        ],

        on="year",

        how="inner"

    )


    fig = px.scatter(

        comparison,

        x="market_cap",

        y="composite_quality_score",

        size="market_cap",

        hover_data=["year"],

        title="Market Cap vs Quality Score"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )



st.success(
    "Capital Analysis Loaded Successfully"
)
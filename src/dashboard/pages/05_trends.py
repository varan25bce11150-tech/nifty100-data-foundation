import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Market Trends",
    page_icon="📈",
    layout="wide"
)


st.title("📈 Market Trends Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    companies = load_table("companies")
    stocks = load_table("stock_prices")
    pnl = load_table("profitandloss")
    ratios = load_table("financial_ratios")
    market_cap = load_table("market_cap")


except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Company Detection
# -------------------------

company_col = None


for col in companies.columns:

    if "name" in col.lower() or "company" in col.lower():

        company_col = col
        break



if company_col is None:

    st.error(
        "Company column not found"
    )

    st.stop()



selected_company = st.selectbox(

    "Select Company",

    companies[company_col]
    .dropna()
    .unique()

)


company_id = companies.loc[

    companies[company_col] == selected_company,

    "id"

].iloc[0]



# -------------------------
# Stock Price Trend
# -------------------------

st.divider()

st.subheader(
    "📉 Stock Price Performance"
)


company_stock = stocks[

    stocks["company_id"] == company_id

]


if not company_stock.empty:


    company_stock = (
        company_stock
        .sort_values("date")
    )


    fig = px.line(

        company_stock,

        x="date",

        y="close_price",

        title="Closing Price Trend",

        markers=True

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


else:

    st.warning(
        "No stock data available"
    )



# -------------------------
# Revenue & Profit Trend
# -------------------------

st.divider()

st.subheader(
    "💰 Revenue and Profit Growth"
)


company_pnl = pnl[

    pnl["company_id"] == company_id

]


if not company_pnl.empty:


    company_pnl = (
        company_pnl
        .sort_values("year")
    )


    fig = px.line(

        company_pnl,

        x="year",

        y=[
            "sales",
            "operating_profit",
            "net_profit"
        ],

        markers=True,

        title="Financial Growth Trend"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


else:

    st.warning(
        "No financial data available"
    )



# -------------------------
# Profitability Trend
# -------------------------

st.divider()

st.subheader(
    "📊 Profitability Metrics"
)


company_ratios = ratios[

    ratios["company_id"] == company_id

]


if not company_ratios.empty:


    company_ratios = (
        company_ratios
        .sort_values("year")
    )


    fig = px.line(

        company_ratios,

        x="year",

        y=[
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "net_profit_margin_pct",
            "operating_profit_margin_pct"
        ],

        markers=True,

        title="Financial Ratio Trend"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


else:

    st.warning(
        "No ratio data available"
    )



# -------------------------
# Market Cap Trend
# -------------------------

st.divider()

st.subheader(
    "🏦 Market Capitalization Trend"
)


company_mc = market_cap[

    market_cap["company_id"] == company_id

]


if not company_mc.empty:


    company_mc = (
        company_mc
        .sort_values("year")
    )


    fig = px.bar(

        company_mc,

        x="year",

        y="market_cap",

        title="Market Cap Growth"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


else:

    st.warning(
        "No market cap data available"
    )


st.success(
    "Trends Dashboard Loaded Successfully"
)
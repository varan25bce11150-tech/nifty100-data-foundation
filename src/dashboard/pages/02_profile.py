import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
    layout="wide"
)


st.title("🏢 Company Profile Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    companies = load_table("companies")
    ratios = load_table("financial_ratios")
    pnl = load_table("profitandloss")
    stocks = load_table("stock_prices")
except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Detect Company Columns
# -------------------------

company_name_col = None


for col in companies.columns:

    if "name" in col.lower() or "company" in col.lower():

        company_name_col = col
        break


if company_name_col is None:

    st.error("Company name column not found")

    st.write(companies.columns.tolist())

    st.stop()



# -------------------------
# Company Selector
# -------------------------

selected_company = st.selectbox(

    "Select Company",

    companies[company_name_col]
    .dropna()
    .unique()

)



# Get Company ID

company_row = companies[
    companies[company_name_col] == selected_company
]


company_id = company_row.iloc[0]["id"]



# -------------------------
# Company Overview
# -------------------------

st.divider()

st.subheader("📌 Company Overview")


st.dataframe(
    company_row,
    use_container_width=True
)



# -------------------------
# Financial Metrics
# -------------------------

st.divider()

st.subheader(
    "📊 Financial Metrics"
)


company_ratios = ratios[
    ratios["company_id"] == company_id
]


if not company_ratios.empty:


    latest_ratio = (
        company_ratios
        .sort_values("year")
        .iloc[-1]
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "ROE",
            f"{latest_ratio['return_on_equity_pct']:.2f}%"
        )


    with col2:

        st.metric(
            "ROCE",
            f"{latest_ratio['return_on_capital_employed_pct']:.2f}%"
        )


    with col3:

        st.metric(
            "Debt / Equity",
            f"{latest_ratio['debt_to_equity']:.2f}"
        )


    with col4:

        st.metric(
            "Quality Score",
            f"{latest_ratio['composite_quality_score']:.2f}"
        )


    st.dataframe(
        company_ratios,
        use_container_width=True
    )


else:

    st.warning(
        "No financial ratio records found"
    )



# -------------------------
# Financial Trend
# -------------------------

st.divider()

st.subheader(
    "📈 Financial Trend"
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
            "net_profit"
        ],

        markers=True,

        title="Revenue and Net Profit Trend"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    st.dataframe(
        company_pnl,
        use_container_width=True
    )


else:

    st.warning(
        "No P&L records found"
    )



st.success(
    "Company Profile Loaded Successfully"
)
# -------------------------
# Stock Price Movement
# -------------------------

st.divider()

st.subheader(
    "📉 Stock Price Movement"
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
        "No stock price data available"
    )

# -------------------------
# Financial Strength Radar
# -------------------------

st.divider()

st.subheader(
    "🕸️ Financial Strength Radar"
)


if not company_ratios.empty:


    radar = (
        company_ratios
        .sort_values("year")
        .iloc[-1]
    )


    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "OPM",
        "Asset Turnover",
        "Revenue CAGR",
        "PAT CAGR",
        "Quality Score"
    ]


    values = [
        radar["return_on_equity_pct"],
        radar["return_on_capital_employed_pct"],
        radar["net_profit_margin_pct"],
        radar["operating_profit_margin_pct"],
        radar["asset_turnover"],
        radar["revenue_cagr_5yr"],
        radar["pat_cagr_5yr"],
        radar["composite_quality_score"]
    ]


    values = [
        0 if pd.isna(v) else float(v)
        for v in values
    ]


    values += values[:1]


    angles = np.linspace(
        0,
        2*np.pi,
        len(labels),
        endpoint=False
    ).tolist()


    angles += angles[:1]


    fig = plt.figure(
        figsize=(6,6)
    )


    ax = plt.subplot(
        111,
        polar=True
    )


    ax.plot(
        angles,
        values
    )


    ax.fill(
        angles,
        values,
        alpha=0.25
    )


    ax.set_xticks(
        angles[:-1]
    )


    ax.set_xticklabels(
        labels
    )


    st.pyplot(fig)


else:

    st.warning(
        "Radar data unavailable"
    )
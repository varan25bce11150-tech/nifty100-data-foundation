import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import load_table


st.set_page_config(
    page_title="Peer Analysis",
    page_icon="👥",
    layout="wide"
)


st.title("👥 Peer Analysis Dashboard")


# -------------------------
# Load Data
# -------------------------

try:

    companies = load_table("companies")
    peers = load_table("peer_percentiles")

except Exception as e:

    st.error(
        f"Database loading failed: {e}"
    )

    st.stop()



# -------------------------
# Detect Company Column
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



# -------------------------
# Company Selection
# -------------------------

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
# Peer Data
# -------------------------

company_peer = peers[

    peers["company_id"] == company_id

]



if company_peer.empty:

    st.warning(
        "No peer data found"
    )

    st.stop()



# -------------------------
# Peer Group
# -------------------------

st.divider()

st.subheader(
    "🏷️ Peer Group"
)


peer_group = (
    company_peer["peer_group_name"]
    .iloc[0]
)


st.info(
    peer_group
)



# -------------------------
# Metrics Table
# -------------------------

st.subheader(
    "📊 Peer Metrics"
)


latest_year = (
    company_peer["year"]
    .max()
)


latest_data = company_peer[

    company_peer["year"] == latest_year

]


st.dataframe(

    latest_data,

    use_container_width=True

)



# -------------------------
# Percentile Chart
# -------------------------

st.divider()

st.subheader(
    "📈 Percentile Ranking"
)


fig = px.bar(

    latest_data,

    x="metric",

    y="percentile_rank",

    title=
    "Company Percentile Performance"

)


st.plotly_chart(

    fig,

    use_container_width=True

)



# -------------------------
# Metric Comparison
# -------------------------

st.divider()

st.subheader(
    "🔎 Metric Details"
)


metric = st.selectbox(

    "Select Metric",

    latest_data["metric"]
    .unique()

)


metric_data = peers[

    peers["metric"] == metric

]


metric_data = (

    metric_data
    .sort_values(
        "percentile_rank",
        ascending=False
    )

)



st.dataframe(

    metric_data,

    use_container_width=True

)


st.success(
    "Peer Analysis Loaded Successfully"
)
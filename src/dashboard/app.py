import streamlit as st

from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.utils.constants import APP_TITLE


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📈",
    layout="wide"
)


render_sidebar()


st.title(
    "📈 Nifty100 Financial Analytics Platform"
)


st.markdown(
    """
    Welcome to the Nifty100 Financial Analytics Platform.

    Use the sidebar pages to explore:

    - Company Profiles
    - Financial Screener
    - Peer Analysis
    - Trends
    - Sector Analytics
    - Capital Analysis
    - Reports
    """
)
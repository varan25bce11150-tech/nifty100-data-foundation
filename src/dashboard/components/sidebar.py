import streamlit as st


def render_sidebar():

    st.sidebar.title("📊 Nifty100 Analytics")


    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "🏢 Company Profile",
            "🔍 Financial Screener",
            "👥 Peer Analysis",
            "📈 Trends",
            "🏭 Sector Analysis",
            "💰 Capital Analysis",
            "📄 Reports"
        ]
    )


    st.sidebar.divider()


    st.sidebar.caption(
        "Sprint 4 Dashboard v1.0"
    )


    return page
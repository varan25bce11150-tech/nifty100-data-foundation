import streamlit as st
import pandas as pd

from src.screener.engine import ScreenerEngine


st.set_page_config(
    page_title="Financial Screener",
    page_icon="🔍",
    layout="wide"
)


st.title("🔍 Financial Screener")


st.markdown(
    """
    Screen Nifty100 companies using
    Sprint 3 Financial Screener Engine.
    """
)



# -------------------------
# Initialize Engine
# -------------------------

try:

    engine = ScreenerEngine()

    config = engine.load_config()

    presets = list(config.keys())


except Exception as e:

    st.error(
        f"Failed loading screener engine: {e}"
    )

    st.stop()



# -------------------------
# Preset Selector
# -------------------------

st.subheader(
    "🎯 Investment Strategy"
)


selected_preset = st.selectbox(

    "Choose Screener",

    presets

)



# -------------------------
# Run Screener
# -------------------------

if st.button(
    "🚀 Run Screener"
):

    with st.spinner(
        "Analyzing Nifty100 companies..."
    ):


        try:

            result = engine.run_preset(
                selected_preset
            )


            st.session_state[
                "screener_result"
            ] = result


        except Exception as e:

            st.error(
                f"Screener failed: {e}"
            )



# -------------------------
# Display Results
# -------------------------

if "screener_result" in st.session_state:


    df = st.session_state[
        "screener_result"
    ]


    st.divider()


    st.subheader(
        "📊 Screening Results"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Companies Found",
            len(df)
        )


    with col2:

        st.metric(
            "Strategy",
            selected_preset.replace("_"," ").title()
        )



    st.dataframe(

        df,

        use_container_width=True

    )



    # -------------------------
    # Download
    # -------------------------

    st.divider()


    csv = df.to_csv(
        index=False
    )


    st.download_button(

        label="⬇ Download Results CSV",

        data=csv,

        file_name=
        f"{selected_preset}_screener.csv",

        mime="text/csv"

    )
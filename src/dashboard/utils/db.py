import sqlite3
import streamlit as st
import pandas as pd


DATABASE_PATH = "nifty100.db"


@st.cache_resource
def get_connection():
    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


@st.cache_data
def load_table(table_name):

    conn = get_connection()

    query = f"""
    SELECT *
    FROM {table_name}
    """

    return pd.read_sql(query, conn)


def run_query(query):

    conn = get_connection()

    return pd.read_sql(
        query,
        conn
    )
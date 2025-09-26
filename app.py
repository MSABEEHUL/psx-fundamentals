import streamlit as st
import pandas as pd

st.set_page_config(page_title="PSX Fundamentals (Auto)", layout="wide")
st.title("PSX Financial Results – Auto-Parsed Fundamentals")

@st.cache_data
def load():
    try:
        return pd.read_csv("data/latest_psx_pl.csv")
    except:
        return pd.DataFrame()

df = load()
if df.empty:
    st.info("No data yet. The GitHub Action will populate data/latest_psx_pl.csv on its first run.")
else:
    cols_show = [
        "announcement_title","revenue","gross_profit","admin","selling",
        "other_income","finance_cost","pbt","tax","pat","eps",
        "gross_margin_%","net_margin_%","finance_to_sales_%","fundamental_score_0_100","source_pdf","scraped_at_utc"
    ]
    cols_show = [c for c in cols_show if c in df.columns]
    st.dataframe(df[cols_show], use_container_width=True, height=520)

    st.subheader("Top by Fundamental Score")
    if "fundamental_score_0_100" in df.columns:
        top = df.sort_values("fundamental_score_0_100", ascending=False).head(15)
        st.bar_chart(top.set_index("announcement_title")["fundamental_score_0_100"])

    st.subheader("Net Margin % (Top 15)")
    if "net_margin_%" in df.columns:
        nm = df.sort_values("net_margin_%", ascending=False).head(15)
        st.bar_chart(nm.set_index("announcement_title")["net_margin_%"])

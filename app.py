import streamlit as st
import pandas as pd
import asyncio
from scraper_multi import run_scraper

st.set_page_config(
    page_title="Ausschreibung Scanner",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Ausschreibung Scanner")
st.subheader("Scan government tenders with AI-powered filtering (free & open‑source).")

st.markdown("---")

if st.button("🚀 Scan Now", type="primary"):
    with st.spinner("Scanning tenders… this may take up to 40 seconds"):
        df = asyncio.run(run_scraper())
        st.success(f"Scan completed! {len(df)} relevant tenders found.")
else:
    try:
        df = pd.read_excel("tenders.xlsx")
    except:
        df = pd.DataFrame()

st.markdown("## 📋 Results")

if df.empty:
    st.info("No tenders yet. Click 'Scan Now' to begin.")
else:
    search = st.text_input("🔎 Search tenders by keyword")
    filtered = df[df["title"].str.contains(search, case=False, na=False)]
    st.dataframe(filtered, use_container_width=True, height=500)

    st.download_button(
        "⬇ Download Excel",
        df.to_excel(index=False),
        file_name="tenders.xlsx"
    )

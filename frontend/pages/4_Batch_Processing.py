"""
pages/4_Batch_Processing.py
Demonstrates scaling the pipeline across a large product catalog at once,
instead of one product at a time.

Upload a CSV with columns: name, price (optional), website (optional),
raw_text (optional). Each row is run through the same extraction
pipeline. High-confidence fields are auto-approved; rows with any
low-confidence fields are flagged for manual review before being
saved to the database.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # frontend/
_APP_DIR = os.path.join(_THIS_DIR, "..", "app")
for p in (_THIS_DIR, _APP_DIR):
    if p not in sys.path:
        sys.path.append(p)

import streamlit as st
import pandas as pd
from common import load_css
from pipeline import run_pipeline
from database import insert_product

st.set_page_config(page_title="Batch Processing", page_icon="📦", layout="wide")
load_css()

st.markdown("""
<div class="hero-banner">
    <h1>📦 Batch Processing</h1>
    <p>Process an entire product catalog at once — demonstrates scaling beyond one item at a time.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Upload a CSV with these columns (only `name` is required):

| name | price | website | raw_text |
|---|---|---|---|
| Centrifugal Pump CP-100 | $320 | https://example.com/cp-100 | |
| LED Bulb X100 | | | 9W, 220V, 800 lumens |
""")

csv_file = st.file_uploader("Upload catalog CSV", type=["csv"])

if csv_file is not None:
    df = pd.read_csv(csv_file)
    st.write(f"Loaded **{len(df)}** product rows.")
    st.dataframe(df, use_container_width=True)

    if st.button("🚀 Run Batch Extraction", type="primary"):
        results = []
        progress = st.progress(0, text="Starting batch extraction...")

        for i, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            sources = []
            website = row.get("website")
            raw_text = row.get("raw_text")
            if isinstance(website, str) and website.strip():
                sources.append(website.strip())
            if isinstance(raw_text, str) and raw_text.strip():
                sources.append(raw_text.strip())

            if not sources:
                results.append({
                    "name": name, "category": "-", "status": "Skipped (no source provided)",
                    "auto_added": 0, "needs_review": 0, "record": None,
                })
                progress.progress((i + 1) / len(df), text=f"Skipped {name} (no source)")
                continue

            initial_data = {}
            price = row.get("price")
            if isinstance(price, str) and price.strip():
                initial_data["price"] = price.strip()
            elif not pd.isna(price):
                initial_data["price"] = str(price)

            try:
                result = run_pipeline(product_name=name, initial_data=initial_data, sources=sources)
                results.append({
                    "name": name,
                    "category": result["category"],
                    "status": "Ready" if not result["pending_review"] else "Needs Review",
                    "auto_added": len(result["attributes"]),
                    "needs_review": len(result["pending_review"]),
                    "record": result,
                })
            except Exception as e:
                results.append({
                    "name": name, "category": "-", "status": f"Error: {e}",
                    "auto_added": 0, "needs_review": 0, "record": None,
                })

            progress.progress((i + 1) / len(df), text=f"Processed {name} ({i + 1}/{len(df)})")

        st.session_state.batch_results = results
        progress.empty()

if "batch_results" in st.session_state:
    results = st.session_state.batch_results
    st.divider()
    st.markdown("### Batch Results")

    summary_df = pd.DataFrame([{
        "Product": r["name"],
        "Category": r["category"],
        "Status": r["status"],
        "Auto-Added Fields": r["auto_added"],
        "Needs Review": r["needs_review"],
    } for r in results])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    ready_count = sum(1 for r in results if r["status"] == "Ready")
    st.info(f"{ready_count} of {len(results)} products are fully ready (no low-confidence fields).")

    if st.button("💾 Save All 'Ready' Products to Database", type="primary"):
        saved = 0
        for r in results:
            if r["status"] == "Ready" and r["record"]:
                rec = r["record"]
                insert_product({
                    "name": rec["name"],
                    "category": rec["category"],
                    "initial_data": {k: v for k, v in rec.items() if k == "price"},
                    "attributes": rec["attributes"],
                    "confidence_scores": rec["confidence_scores"],
                    "source_reference": rec["source_reference"],
                    "validation_status": rec["validation_status"],
                })
                saved += 1
        st.success(f"Saved {saved} product(s) to the database. "
                   f"Products needing review were skipped — process those individually "
                   f"on the Extract Product page.")

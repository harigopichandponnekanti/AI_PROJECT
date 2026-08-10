"""
pages/2_🗂️_Product_Database.py
View, search, and manage verified product records saved from the
Extract Product page.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # frontend/
_APP_DIR = os.path.join(_THIS_DIR, "..", "app")
for p in (_THIS_DIR, _APP_DIR):
    if p not in sys.path:
        sys.path.append(p)

import streamlit as st
from common import load_css
from database import get_all_products, delete_product, get_product_count

st.set_page_config(page_title="Product Database", page_icon="🗂️", layout="wide")
load_css()

st.markdown("""
<div class="hero-banner">
    <h1>🗂️ Product Database</h1>
    <p>All verified product records — initial data + AI-extracted, human-approved attributes.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    search = st.text_input("🔎 Search by name or category", placeholder="e.g., Pump, Lighting...")
with col2:
    st.metric("Total Records", get_product_count())

products = get_all_products(search=search)

if not products:
    st.info("No products saved yet. Go to **Extract Product** and click "
            "**Verify & Save to Database** after reviewing a product.")
else:
    for p in products:
        with st.expander(f"**{p['name']}**  —  {p['category']}  (#{p['id']}, saved {p['created_at']})"):
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("**Initial Data (user-provided)**")
                if p["initial_data"]:
                    st.json(p["initial_data"])
                else:
                    st.caption("None provided")

                st.markdown("**Validation Status**")
                if p["validation_status"] == "Passed":
                    st.success(p["validation_status"])
                else:
                    st.warning(p["validation_status"])

            with c2:
                st.markdown("**Extracted & Verified Attributes**")
                st.json(p["attributes"])

                st.markdown("**Confidence Scores**")
                st.json(p["confidence_scores"])

            st.markdown("**Source References**")
            st.json(p["source_reference"])

            if st.button("🗑️ Delete Record", key=f"delete_{p['id']}"):
                delete_product(p["id"])
                st.rerun()

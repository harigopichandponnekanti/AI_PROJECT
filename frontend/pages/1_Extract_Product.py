"""
pages/1_🔍_Extract_Product.py
Main extraction workflow:
  1. Enter product name + any known initial data
  2. Drag & drop PDFs/images/Excel, or paste a website URL / raw text
  3. Run the AI pipeline
  4. High-confidence fields are shown as auto-added
  5. Low-confidence fields require Confirm / Edit / Reject
  6. "Verify & Save to Database" stores the final combined record
"""

import os
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # frontend/
_APP_DIR = os.path.join(_THIS_DIR, "..", "app")
for p in (_THIS_DIR, _APP_DIR):
    if p not in sys.path:
        sys.path.append(p)

import streamlit as st
from common import load_css, confidence_badge
from pipeline import run_pipeline
from database import insert_product

st.set_page_config(page_title="Extract Product", page_icon="🔍", layout="wide")
load_css()

st.markdown("""
<div class="hero-banner">
    <h1>🔍 Extract Product Intelligence</h1>
    <p>Give it a product name and any supporting material — the AI fills in the rest.</p>
</div>
""", unsafe_allow_html=True)

if "extraction_result" not in st.session_state:
    st.session_state.extraction_result = None
if "field_decisions" not in st.session_state:
    st.session_state.field_decisions = {}

# ---------------- Step 1: Inputs ----------------
st.markdown("### 1. Product Details")
col1, col2 = st.columns([2, 1])
with col1:
    product_name = st.text_input("Product Name", placeholder="e.g., Centrifugal Pump CP-100")
with col2:
    price = st.text_input("Price (optional)", placeholder="e.g., $320")

st.markdown("### 2. Supporting Sources")
st.caption("Drag and drop files below, or paste a website URL / raw description.")

uploaded_files = st.file_uploader(
    "Drop PDF, Image, or Excel files here",
    type=["pdf", "jpg", "jpeg", "png", "xlsx", "csv"],
    accept_multiple_files=True,
)

col3, col4 = st.columns(2)
with col3:
    website_url = st.text_input("Website URL (optional)", placeholder="https://...")
with col4:
    raw_text = st.text_area("Raw product description (optional)", height=100)

st.write("")
extract_clicked = st.button("🚀 Extract Product Intelligence", type="primary", use_container_width=True)

# ---------------- Step 3: Run pipeline ----------------
if extract_clicked:
    if not product_name:
        st.warning("Please enter a product name.")
    else:
        sources = []
        for uploaded_file in uploaded_files or []:
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                sources.append(tmp.name)
        if website_url:
            sources.append(website_url)
        if raw_text:
            sources.append(raw_text)

        if not sources:
            st.warning("Please provide at least one source: a file, a URL, or text.")
        else:
            with st.spinner("Detecting category, extracting attributes, validating..."):
                result = run_pipeline(
                    product_name=product_name,
                    initial_data={"price": price} if price else {},
                    sources=sources,
                )
            st.session_state.extraction_result = result
            st.session_state.field_decisions = {}

# ---------------- Step 4: Show results ----------------
result = st.session_state.extraction_result

if result:
    st.divider()
    st.markdown(f"### 3. Results — Category detected: **{result['category']}**")

    if result["attributes"]:
        st.markdown("#### ✅ Auto-Added (high confidence)")
        for attr, value in result["attributes"].items():
            conf = result["confidence_scores"].get(attr, 1.0)
            src = result["source_reference"].get(attr, "")
            st.markdown(
                f'<div class="info-card"><b>{attr}</b>: {value} &nbsp; {confidence_badge(conf)}'
                f'<br><span style="color:#666;font-size:0.85rem;">Source: {src}</span></div>',
                unsafe_allow_html=True,
            )

    if result["pending_review"]:
        st.markdown("#### ⚠️ Needs Your Confirmation (below 80% confidence)")
        for attr, details in result["pending_review"].items():
            with st.container():
                st.markdown(
                    f'<div class="info-card"><b>{attr}</b>: {details["value"]} '
                    f'&nbsp; {confidence_badge(details["confidence"])}'
                    f'<br><span style="color:#666;font-size:0.85rem;">Source: {details["source"]}</span></div>',
                    unsafe_allow_html=True,
                )
                c1, c2, c3 = st.columns([1, 2, 1])
                decision_key = f"decision_{attr}"
                with c1:
                    if st.button("✅ Confirm", key=f"confirm_{attr}"):
                        st.session_state.field_decisions[attr] = {"action": "confirm", "value": details["value"]}
                with c2:
                    edited_value = st.text_input("Edit value", value=details["value"], key=f"edit_input_{attr}", label_visibility="collapsed")
                    if st.button("✏️ Save Edit", key=f"save_edit_{attr}"):
                        st.session_state.field_decisions[attr] = {"action": "edit", "value": edited_value}
                with c3:
                    if st.button("❌ Reject", key=f"reject_{attr}"):
                        st.session_state.field_decisions[attr] = {"action": "reject", "value": None}

                if attr in st.session_state.field_decisions:
                    d = st.session_state.field_decisions[attr]
                    st.caption(f"→ Decision recorded: **{d['action']}**"
                               + (f" (value: {d['value']})" if d["action"] != "reject" else ""))

    if result["validation_warnings"]:
        st.markdown("#### 🚩 Validation Warnings")
        for w in result["validation_warnings"]:
            st.warning(w)
    else:
        st.info("No validation issues found.")

    if not result["attributes"] and not result["pending_review"]:
        st.error(
            "No attributes were extracted. Check your terminal for the raw model "
            "response — the source material may not have contained readable product info."
        )

    st.divider()
    st.markdown("### 4. Finalize")
    pending_unresolved = [a for a in result["pending_review"] if a not in st.session_state.field_decisions]
    if pending_unresolved:
        st.info(f"{len(pending_unresolved)} field(s) still need a decision above before saving "
                 f"(or they'll be excluded automatically).")

    if st.button("💾 Verify & Save to Database", type="primary", use_container_width=True):
        final_attributes = dict(result["attributes"])
        for attr, decision in st.session_state.field_decisions.items():
            if decision["action"] in ("confirm", "edit"):
                final_attributes[attr] = decision["value"]

        record = {
            "name": result["name"],
            "category": result["category"],
            "initial_data": {k: v for k, v in result.items() if k == "price"},
            "attributes": final_attributes,
            "confidence_scores": result["confidence_scores"],
            "source_reference": result["source_reference"],
            "validation_status": result["validation_status"],
        }
        product_id = insert_product(record)
        st.success(f"Saved! Product record #{product_id} added to the database.")
        st.balloons()
        if st.button("View in Database →"):
            st.switch_page("pages/2_🗂️_Product_Database.py")

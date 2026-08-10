"""
Home.py
Landing page. Run this file to start the app:
    streamlit run Home.py
Use the sidebar to navigate to "Extract Product" or "Product Database".
"""

import streamlit as st
from common import load_css
from database import get_product_count

st.set_page_config(
    page_title="AI Product Intelligence",
    page_icon="📦",
    layout="wide",
)
load_css()

st.markdown("""
<div class="hero-banner">
    <h1>📦 AI-Powered Product Intelligence</h1>
    <p>Turn limited product info into clean, structured, validated, commerce-ready data.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="info-card"><h3>🧩 Multi-format Input</h3>'
                'PDFs, images, Excel sheets, websites, or raw text — dropped in or pasted.</div>',
                unsafe_allow_html=True)
with col2:
    st.markdown('<div class="info-card"><h3>🎯 Category-aware Extraction</h3>'
                'Attributes adapt automatically — watts for lighting, ml for liquids, mm for hardware.</div>',
                unsafe_allow_html=True)
with col3:
    st.markdown('<div class="info-card"><h3>✅ Human-in-the-loop</h3>'
                'Fields below 80% confidence need your confirmation before they\'re saved.</div>',
                unsafe_allow_html=True)

col4, col5 = st.columns(2)
with col4:
    st.markdown('<div class="info-card"><h3>🔎 RAG-grounded Extraction</h3>'
                'Retrieves similar past verified products from the database for consistent, grounded results.</div>',
                unsafe_allow_html=True)
with col5:
    st.markdown('<div class="info-card"><h3>🕸️ Knowledge Graph</h3>'
                'Visualizes how categories, products, and attributes connect across the whole catalog.</div>',
                unsafe_allow_html=True)

st.write("")
st.subheader("Get Started")

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="info-card">'
                '<h4>🔍 Extract Product Intelligence</h4>'
                'Upload a product\'s documents/images and let AI build a structured record.'
                '</div>', unsafe_allow_html=True)
    if st.button("Go to Extract Page →", use_container_width=True):
        st.switch_page("pages/1_Extract_Product.py")

with c2:
    count = get_product_count()
    st.markdown('<div class="info-card">'
                f'<h4>🗂️ Product Database</h4>'
                f'{count} verified product record(s) saved so far.'
                '</div>', unsafe_allow_html=True)
    if st.button("Go to Database →", use_container_width=True):
        st.switch_page("pages/2_Product_Database.py")

c3, c4 = st.columns(2)
with c3:
    st.markdown('<div class="info-card">'
                '<h4>🕸️ Knowledge Graph</h4>'
                'See how your whole catalog connects — categories, products, and attributes.'
                '</div>', unsafe_allow_html=True)
    if st.button("Go to Knowledge Graph →", use_container_width=True):
        st.switch_page("pages/3_Knowledge_Graph.py")

with c4:
    st.markdown('<div class="info-card">'
                '<h4>📦 Batch Processing</h4>'
                'Process an entire catalog of products at once from a CSV upload.'
                '</div>', unsafe_allow_html=True)
    if st.button("Go to Batch Processing →", use_container_width=True):
        st.switch_page("pages/4_Batch_Processing.py")

st.write("")
st.caption("Use the sidebar at any time to switch between pages.")

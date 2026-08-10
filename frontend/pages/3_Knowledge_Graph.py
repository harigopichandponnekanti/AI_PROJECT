"""
pages/3_Knowledge_Graph.py
Builds and displays a knowledge graph connecting:
    Category -> Products -> Attributes
from the verified records in the database. This lets you (and judges)
see how product intelligence connects across the whole catalog, not
just one product at a time.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # frontend/
_APP_DIR = os.path.join(_THIS_DIR, "..", "app")
for p in (_THIS_DIR, _APP_DIR):
    if p not in sys.path:
        sys.path.append(p)

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from common import load_css
from database import get_all_products

st.set_page_config(page_title="Knowledge Graph", page_icon="🕸️", layout="wide")
load_css()

st.markdown("""
<div class="hero-banner">
    <h1>🕸️ Product Knowledge Graph</h1>
    <p>How categories, products, and attributes connect across your verified catalog.</p>
</div>
""", unsafe_allow_html=True)

products = get_all_products()

if not products:
    st.info("No verified products yet. Extract and save a few products first, "
            "then come back here to see them connected in a graph.")
else:
    max_attrs = st.slider("Max attributes shown per product (for readability)", 1, 8, 4)

    net = Network(height="650px", width="100%", bgcolor="#0e1420", font_color="white", directed=False)
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=120)

    added_categories = set()
    added_attr_nodes = set()

    for p in products:
        category = p["category"] or "General"
        product_node = f"product::{p['id']}::{p['name']}"

        if category not in added_categories:
            net.add_node(category, label=category, color="#3a7ca5", shape="box", size=28)
            added_categories.add(category)

        net.add_node(product_node, label=p["name"], color="#f2a541", shape="dot", size=20)
        net.add_edge(category, product_node)

        for i, (attr_name, attr_value) in enumerate(p["attributes"].items()):
            if i >= max_attrs:
                break
            attr_node = f"attr::{category}::{attr_name}"
            if attr_node not in added_attr_nodes:
                net.add_node(attr_node, label=attr_name, color="#5cb85c", shape="ellipse", size=14)
                added_attr_nodes.add(attr_node)
            value_label = f"{attr_name} = {attr_value}"
            value_node = f"value::{p['id']}::{attr_name}"
            net.add_node(value_node, label=str(attr_value), color="#888", shape="text", size=10)
            net.add_edge(product_node, attr_node)
            net.add_edge(attr_node, value_node)

    net.set_options("""
    {
      "nodes": {"font": {"size": 14}},
      "edges": {"color": {"color": "#3a4a5a"}, "smooth": false},
      "physics": {"stabilization": {"iterations": 150}}
    }
    """)

    html_path = os.path.join(os.path.dirname(__file__), "_graph_temp.html")
    net.write_html(html_path, notebook=False)
    with open(html_path, "r", encoding="utf-8") as f:
        graph_html = f.read()

    components.html(graph_html, height=670, scrolling=True)

    st.caption(
        "🔵 Category nodes → 🟠 Product nodes → 🟢 Attribute nodes → grey value labels. "
        "Drag nodes to rearrange, scroll to zoom."
    )

    st.divider()
    st.markdown("### Category Summary")
    from collections import Counter
    cat_counts = Counter(p["category"] or "General" for p in products)
    for cat, count in cat_counts.most_common():
        st.markdown(f"- **{cat}**: {count} product(s)")

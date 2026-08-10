"""
common.py
Shared setup used by every page: makes app/ importable, loads custom CSS,
and initializes the database once.
"""

import os
import sys
import streamlit as st

# Make ../app importable from any page (Home.py or pages/*.py)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.join(_THIS_DIR, "..", "app")
if _APP_DIR not in sys.path:
    sys.path.append(_APP_DIR)

from database import init_db  # noqa: E402

init_db()


def load_css():
    css_path = os.path.join(_THIS_DIR, "assets", "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def confidence_badge(confidence: float) -> str:
    pct = f"{confidence:.0%}"
    if confidence >= 0.80:
        return f'<span class="badge-high">✓ {pct} confidence</span>'
    return f'<span class="badge-low">⚠ {pct} confidence</span>'

"""
input_router.py
Detects the type of an incoming source file/input and routes it
to the correct extraction handler.
"""

import os
import pandas as pd
import requests
import pdfplumber
from PIL import Image
from bs4 import BeautifulSoup


def detect_input_type(source):
    """
    source: a file path (str) or a URL (str) or raw text (str)
    Returns one of: 'pdf', 'image', 'excel', 'website', 'text'
    """
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        return "website"

    if isinstance(source, str) and os.path.isfile(source):
        ext = os.path.splitext(source)[1].lower()
        if ext == ".pdf":
            return "pdf"
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            return "image"
        if ext in (".xlsx", ".xls", ".csv"):
            return "excel"

    # Fallback: treat as raw text
    return "text"


def read_pdf_as_text(file_path):
    """Extract all text from a PDF locally (no upload needed)."""
    pages_text = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(f"--- Page {i} ---\n{text}")
    return "\n".join(pages_text)


def load_image(file_path):
    """Load an image as a PIL.Image object, sent inline to Gemini (no upload)."""
    return Image.open(file_path)


def read_excel_as_text(file_path):
    """Convert an Excel/CSV file into a plain text table the AI can read."""
    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    return df.to_string(index=False)


def read_website_as_text(url):
    """Fetch and clean visible text content from a webpage."""
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def prepare_source_for_extraction(source):
    """
    Normalizes any supported input into a ready-to-send payload.
    Everything is sent INLINE (no File API / upload_file) to avoid
    network/discovery-API issues on restrictive networks.

    Returns a tuple: (input_type, payload)
      - pdf     -> payload is extracted plain text
      - image   -> payload is a PIL.Image object (sent inline)
      - excel   -> payload is plain text table
      - website -> payload is plain text
      - text    -> payload is the raw text itself
    """
    input_type = detect_input_type(source)

    if input_type == "pdf":
        return input_type, read_pdf_as_text(source)
    if input_type == "image":
        return input_type, load_image(source)
    if input_type == "excel":
        return input_type, read_excel_as_text(source)
    if input_type == "website":
        return input_type, read_website_as_text(source)
    return input_type, source  # raw text


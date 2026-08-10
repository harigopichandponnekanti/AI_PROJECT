"""
category_detector.py
Uses the Gemini model to classify a product into one of the known
categories so the correct attribute template can be applied.
"""

import json
import os

TEMPLATES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "category_templates", "category_templates.json"
)


def load_category_templates():
    with open(TEMPLATES_PATH, "r") as f:
        return json.load(f)


def detect_category(model, product_name, extra_context=""):
    """
    model: an initialized Gemini GenerativeModel instance
    Returns the best-matching category name from category_templates.json
    """
    templates = load_category_templates()
    category_names = list(templates.keys())

    prompt = f"""
    You are a product categorization assistant.
    Choose the SINGLE best matching category for this product
    from this exact list: {category_names}

    Product name: {product_name}
    Extra context: {extra_context}

    Respond with ONLY the category name, nothing else.
    If nothing fits well, respond with "General".
    """

    response = model.generate_content(prompt)
    category = response.text.strip()

    if category not in category_names:
        category = "General"

    return category, templates[category]["expected_attributes"]

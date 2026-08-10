"""
retrieval.py
Lightweight RAG (Retrieval-Augmented Generation) layer.

Before extracting a new product, this looks up previously VERIFIED
products in the same category from the database and feeds their
attributes to the AI as reference context. This helps the model be
more consistent (e.g., using the same units/field names it used for
similar products before) and grounds its answers in real prior data
instead of guessing from scratch every time.
"""

from database import get_all_products


def retrieve_similar_products(category: str, limit: int = 3):
    """
    Returns up to `limit` previously verified products from the same
    category, as a list of dicts: {name, attributes}.
    """
    all_products = get_all_products()
    same_category = [p for p in all_products if p.get("category") == category]
    return same_category[:limit]


def build_reference_context(category: str, limit: int = 3) -> str:
    """
    Builds a short text block summarizing similar past products,
    to be injected into the extraction prompt as grounding context.
    Returns an empty string if no prior products exist for this category.
    """
    similar = retrieve_similar_products(category, limit)
    if not similar:
        return ""

    lines = [
        f"Reference: {len(similar)} previously verified product(s) in the "
        f"'{category}' category (use these for consistent field naming/units, "
        f"NOT as facts about the current product):"
    ]
    for prod in similar:
        attrs_str = ", ".join(f"{k}={v}" for k, v in prod.get("attributes", {}).items())
        lines.append(f"- {prod['name']}: {attrs_str}")

    return "\n".join(lines)

"""
confidence_gate.py
Splits extracted attributes into "auto_add" and "needs_review" groups
based on a configurable confidence threshold (default 0.80).
"""

import os

DEFAULT_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.80))


def apply_confidence_gate(attributes: dict, threshold: float = DEFAULT_THRESHOLD):
    """
    attributes: dict of {attribute_name: {"value":..., "confidence":..., "source":...}}
    Returns (auto_add: dict, needs_review: dict)
    """
    auto_add = {}
    needs_review = {}

    for name, details in attributes.items():
        confidence = float(details.get("confidence", 0))
        if confidence >= threshold:
            auto_add[name] = details
        else:
            needs_review[name] = details

    return auto_add, needs_review

"""
pipeline.py
Main orchestration: ties together input routing, category detection,
extraction, confidence gating, and validation into one final
structured product record.

Usage:
    from pipeline import run_pipeline
    result = run_pipeline(
        product_name="Centrifugal Pump CP-100",
        initial_data={"price": "$320"},
        sources=["data/sample_inputs/datasheet.pdf", "data/sample_inputs/nameplate.jpg"]
    )
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

from input_router import prepare_source_for_extraction
from category_detector import detect_category
from extractor import extract_from_sources
from confidence_gate import apply_confidence_gate
from validator import validate_attributes, check_conflicts
from retrieval import build_reference_context

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"  # free-tier friendly, multimodal


def run_pipeline(product_name: str, initial_data: dict, sources: list, extra_context: str = ""):
    model = genai.GenerativeModel(MODEL_NAME)

    # Step 3: detect + prepare each source
    prepared_sources = [prepare_source_for_extraction(src) for src in sources]

    # Step 4: detect category
    category, expected_attributes = detect_category(model, product_name, extra_context)

    # RAG step: retrieve similar past verified products in this category
    # and use them as grounding context for more consistent extraction
    reference_context = build_reference_context(category)

    # Step 5: extract data with confidence scores
    extraction_result = extract_from_sources(
        model, product_name, category, expected_attributes, prepared_sources,
        reference_context=reference_context,
    )
    attributes = extraction_result.get("attributes", {})
    extra_attributes = extraction_result.get("extra_attributes", {})
    missing_fields = extraction_result.get("missing_fields", [])

    all_attributes = {**attributes, **extra_attributes}

    # Step 6: confidence gate
    auto_add, needs_review = apply_confidence_gate(all_attributes)

    # Step 7: validation
    validation_warnings = validate_attributes(all_attributes)
    conflicts = check_conflicts(initial_data, all_attributes)

    # Step 8 & 9: combine into final record
    final_record = {
        "name": product_name,
        "category": category,
        **initial_data,
        "attributes": {k: v["value"] for k, v in auto_add.items()},
        "pending_review": {k: v for k, v in needs_review.items()},
        "confidence_scores": {k: v["confidence"] for k, v in all_attributes.items()},
        "source_reference": {k: v["source"] for k, v in all_attributes.items()},
        "missing_fields": missing_fields,
        "validation_warnings": validation_warnings + conflicts,
        "validation_status": "Passed" if not (validation_warnings + conflicts) else "Needs Attention",
    }

    return final_record


if __name__ == "__main__":
    # Simple manual test run (requires a valid GEMINI_API_KEY in .env
    # and real files placed in data/sample_inputs/)
    result = run_pipeline(
        product_name="Centrifugal Pump CP-100",
        initial_data={"price": "$320"},
        sources=["data/sample_inputs/datasheet.pdf"],
    )
    import json
    print(json.dumps(result, indent=2))

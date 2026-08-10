"""
extractor.py
Sends product sources (PDF-as-text, image, raw text, excel-as-text,
website-as-text) to the Gemini API and asks it to extract structured
attributes with confidence scores, based on the category's expected
attribute list.

Note: images are sent INLINE (as PIL.Image objects) rather than via
genai.upload_file(), to avoid File API / discovery-API network issues
on restrictive networks.
"""

import json
import google.generativeai as genai


EXTRACTION_PROMPT_TEMPLATE = """
You are a product data extraction assistant for an industrial e-commerce catalog.

Product name: {product_name}
Detected category: {category}
Attributes expected for this category: {expected_attributes}

{reference_context}

From the attached source material, extract as many of the expected
attributes as possible. If you find additional useful attributes not
in the list, include them too under "extra_attributes".

For EVERY attribute you extract, include:
  - "value": the extracted value
  - "confidence": a number between 0 and 1 representing how sure you are
  - "source": a short description of where this value came from
    (e.g., "PDF page 2", "nameplate image", "inferred from similar product")

Return ONLY valid JSON in this exact structure, no extra text, no markdown
code fences:

{{
  "attributes": {{
    "attribute_name": {{"value": "", "confidence": 0.0, "source": ""}}
  }},
  "extra_attributes": {{
    "attribute_name": {{"value": "", "confidence": 0.0, "source": ""}}
  }},
  "missing_fields": []
}}
"""


def build_prompt(product_name, category, expected_attributes, reference_context=""):
    return EXTRACTION_PROMPT_TEMPLATE.format(
        product_name=product_name,
        category=category,
        expected_attributes=expected_attributes,
        reference_context=reference_context,
    )


def extract_from_sources(model, product_name, category, expected_attributes, sources, reference_context=""):
    """
    sources: list of tuples (input_type, payload) from input_router.py
             - pdf/text/excel/website payload is a text string
             - image payload is a PIL.Image object (sent inline)
    reference_context: optional RAG context string built from similar
             past verified products (see retrieval.py)
    Returns parsed JSON (dict) with attributes, extra_attributes, missing_fields
    """
    prompt = build_prompt(product_name, category, expected_attributes, reference_context)

    content_parts = [prompt]

    for input_type, payload in sources:
        if input_type == "image":
            # PIL.Image objects can be passed directly - Gemini sends them
            # inline in the request, no upload/File API needed.
            content_parts.append(payload)
        else:
            # pdf (already extracted as text), text, excel-as-text, website-as-text
            content_parts.append(f"\nSource ({input_type}):\n{payload}")

    response = model.generate_content(content_parts)

    raw_text = response.text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: return raw text wrapped so the pipeline doesn't crash.
        # print() so you can see exactly what the model returned in your terminal.
        print("---- RAW MODEL RESPONSE (could not parse as JSON) ----")
        print(raw_text)
        print("-------------------------------------------------------")
        return {
            "attributes": {},
            "extra_attributes": {},
            "missing_fields": [],
            "raw_response": raw_text,
        }


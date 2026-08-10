"""
validator.py
Basic rule-based + AI-assisted validation of extracted product attributes.
"""


def validate_attributes(attributes: dict):
    """
    attributes: dict of {attribute_name: {"value":..., "confidence":..., "source":...}}
    Returns a list of warning strings (empty list if nothing found).
    """
    warnings = []

    for name, details in attributes.items():
        value = str(details.get("value", "")).lower()

        # Simple sanity checks (extend this with more domain rules as needed)
        if "length" in name and "cm" in value:
            warnings.append(
                f"Possible unit issue in '{name}': value '{value}' uses cm, "
                f"expected mm for this category. Please verify."
            )

        if value in ("", "none", "n/a", "unknown"):
            warnings.append(f"'{name}' has an empty or unclear value.")

    return warnings


def check_conflicts(initial_data: dict, extracted_attributes: dict):
    """
    Compares initial user-provided data against extracted data
    to flag conflicting values (e.g., price mismatch).
    """
    conflicts = []
    for key, initial_value in initial_data.items():
        if key in extracted_attributes:
            extracted_value = extracted_attributes[key].get("value")
            if str(initial_value).strip() != str(extracted_value).strip():
                conflicts.append(
                    f"Conflict on '{key}': initial='{initial_value}' vs "
                    f"extracted='{extracted_value}'"
                )
    return conflicts

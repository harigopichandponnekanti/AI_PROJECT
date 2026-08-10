# AI-Powered Product Intelligence for Industrial Commerce

## 1. Problem Statement

Industrial manufacturers manage large volumes of product information spread across websites, catalogs, technical documents, and digital assets. This data is often fragmented, incomplete, and inconsistently formatted. Converting it into accurate, structured, commerce-ready product data is a time-consuming manual process that doesn't scale.

## 2. Objective

Build an AI-powered system that automatically **creates, enriches, and validates** structured product data from limited or fragmented input — while remaining explainable, traceable, and scalable across large product catalogs.

## 3. Core Idea (One-Line Summary)

> Give the system a product name plus any available supporting material (PDF, image, Excel, website, raw text). The system detects the product's category, extracts category-relevant attributes from all sources using AI, validates the data, asks for human confirmation when confidence is low, and outputs a clean, structured, source-traceable product record.

## 4. Key Design Principles

- **No fixed format required** — input can be a PDF, image, spreadsheet, website link, or plain text, in any combination.
- **No fixed schema per product** — attributes are dynamic and depend on product category (e.g., watts for lighting, ml for liquids, mm for hardware).
- **Category-based templates, not product-based templates** — a small, manageable set of category templates scales to unlimited products.
- **Human-in-the-loop** — the AI doesn't silently add uncertain data; it asks for confirmation when confidence is low.
- **Explainability** — every field in the final output is traceable to its source and carries a confidence score.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│ STEP 1: INITIAL INPUT                                     │
│ Product Name + any basic data available                   │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 2: SUPPORTING SOURCES                                │
│ PDF / Image / Raw Text / Excel / Website link              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 3: INPUT DETECTION & ROUTING                          │
│ Identify file type → send to correct extraction method     │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 4: CATEGORY DETECTION                                 │
│ AI identifies product category (Lighting, Hardware,        │
│ Personal Care, Pumps, etc.)                                │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 5: CATEGORY-TEMPLATE-GUIDED EXTRACTION                │
│ Extract only relevant attributes for that category          │
│ Assign a confidence score to each extracted field           │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 6: CONFIDENCE-BASED DECISION                          │
│ ≥ 80% confidence → Auto-add (with source shown)             │
│ < 80% confidence → Ask user to Confirm / Edit / Reject      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 7: VALIDATION                                          │
│ Check for wrong units, out-of-range values, conflicts       │
│ between sources → flag issues                               │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 8: COMBINE FINAL DATA                                  │
│ Merge initial data + approved extracted data                │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 9: FINAL STRUCTURED OUTPUT                              │
│ Complete, validated, source-traceable product record         │
└──────────────────────────────────────────────────────────┘
```

## 6. Technology Stack (Free / Low-Cost, Hackathon-Friendly)

| Layer | Tool | Purpose |
|---|---|---|
| Core extraction engine | **Gemini API (free tier)** | Multimodal — reads PDF, image, and text in one call |
| Backup local PDF text extraction | **pdfplumber / PyMuPDF** (Python) | Fast, free, no API needed for simple text PDFs |
| Backup OCR | **Tesseract OCR** | Free fallback if image quality is poor or API quota runs low |
| Excel handling | **pandas** | Convert Excel/CSV to structured text before feeding to AI |
| Website content | **requests + BeautifulSoup** | Scrape and clean website text before extraction |
| Backend | **Python (FastAPI/Flask)** | API layer connecting all components |
| Frontend (demo) | **Streamlit / React** | Simple UI to upload files and review AI suggestions |
| Data storage | **JSON / lightweight DB (SQLite)** | Store structured product records |
| Optional advanced layer | **Knowledge Graph (Neo4j)** | Link products to categories/attributes for richer intelligence |

## 7. Category Attribute Templates (Examples)

| Category | Typical Attributes |
|---|---|
| Lighting | Power (W), Voltage (V), Lumens, Color Temperature |
| Personal Care / Liquids | Volume (ml/L), Ingredients |
| Hardware / Fasteners | Length (mm), Diameter (mm), Material |
| Pumps / Motors | Power (kW/HP), Flow Rate (L/min), Pressure (bar) |
| Electronics | Voltage, Wattage, Battery Capacity |

New categories can be auto-suggested by the AI when a product doesn't match an existing template, growing the template library over time.

## 8. Confidence Scoring Logic

| Source of Value | Approx. Confidence | Action |
|---|---|---|
| Directly found in document/image | 90–100% | Auto-add |
| Matched from a similar product | 60–80% | Ask for confirmation (near threshold) |
| Pure AI inference, no direct source | Below 60% | Always ask for confirmation |

**Rule used in this project:** If confidence < 80%, the system pauses and asks the user to Confirm / Edit / Reject before adding the field to the final record.

## 9. Example Run

**Input:**
- Product Name: `Centrifugal Pump CP-100`
- Price: `$320`
- Attached: `datasheet.pdf`, `nameplate_photo.jpg`

**AI Output (before confirmation):**
```
✅ Flow Rate: 100 L/min   — Confidence: 95%  → Auto-added
✅ Material: Cast Iron    — Confidence: 92%  → Auto-added
⚠️ Power: 2.2 kW          — Confidence: 68%  → Needs confirmation
   (Reason: estimated from similar product CP-100X, not directly stated)
```

**Final Structured Output:**
```json
{
  "name": "Centrifugal Pump CP-100",
  "category": "Pumps > Centrifugal",
  "price": "$320",
  "attributes": {
    "flow_rate": "100 L/min",
    "material": "Cast Iron",
    "power": "2.2 kW"
  },
  "confidence_scores": {
    "flow_rate": 0.95,
    "material": 0.92,
    "power": 0.68
  },
  "human_review_needed": ["power"],
  "source_reference": "datasheet.pdf (page 2), nameplate_photo.jpg, similar product match",
  "validation_status": "Passed - no conflicts detected"
}
```

## 10. How This Meets the Challenge's Expected Outcomes

| Expected Outcome | How the Project Delivers It |
|---|---|
| Generate structured product intelligence from limited inputs | Steps 1–5: multi-format input handling + category-guided extraction |
| Improve product data quality and consistency | Category templates standardize attributes across all products |
| Validate and enrich information with traceable outputs | Step 7 validation + source references + confidence scores on every field |
| Scale efficiently across large product catalogs | Category-level templates (not per-product), reusable across thousands of items |

## 11. Future Scope

- Auto-expand category template library as new product types are encountered
- Add a knowledge graph layer to link related products, categories, and specs for smarter recommendations
- Batch-processing mode for uploading entire catalogs at once
- Analytics dashboard showing data quality improvement over time (before/after enrichment)

## 12. Conclusion

This project turns fragmented, inconsistent industrial product data into clean, structured, and trustworthy product intelligence. By combining multimodal AI extraction, category-based dynamic attributes, confidence-driven human-in-the-loop review, and full source traceability, the system is both scalable and explainable — directly addressing the core challenge of transforming limited product information into commerce-ready data.

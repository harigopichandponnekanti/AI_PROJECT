# AI-Powered Product Intelligence for Industrial Commerce

Turns limited, scattered product data (name + a PDF / image / Excel / website / raw text)
into clean, structured, validated, and explainable product records — using AI extraction,
category-based dynamic attributes, and confidence-based human-in-the-loop review.

See `docs/PROJECT_DOCUMENTATION.md` for the full project write-up, architecture, and workflow.

## Folder Structure

```
AI_Product_Intelligence/
├── app/
│   ├── input_router.py       # Detects input type (pdf/image/excel/website/text) and preps it
│   ├── category_detector.py  # AI-based product category detection
│   ├── extractor.py          # Core AI extraction with confidence scores + source tracing
│   ├── confidence_gate.py    # Splits results into auto-add vs needs-review (80% threshold)
│   ├── validator.py          # Rule-based validation + conflict checking
│   ├── database.py           # SQLite storage for verified product records
│   └── pipeline.py           # Orchestrates the full end-to-end workflow
├── frontend/
│   ├── Home.py                        # Landing page — run this to start the app
│   ├── common.py                      # Shared CSS + path setup
│   ├── assets/style.css               # Custom styling
│   └── pages/
│       ├── 1_🔍_Extract_Product.py     # Drag & drop upload, extraction, confirm/edit/reject flow
│       └── 2_🗂️_Product_Database.py    # Browse, search, and delete saved product records
├── data/
│   ├── category_templates/
│   │   └── category_templates.json   # Attribute checklist per product category
│   ├── sample_inputs/                # Put your test PDFs/images/Excel files here
│   └── product_intelligence.db       # Auto-created SQLite database (after first save)
├── docs/
│   └── PROJECT_DOCUMENTATION.md      # Full project write-up
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a free Gemini API key**
   Sign in at https://ai.google.dev and generate a free API key.

3. **Configure your environment**
   ```bash
   cp .env.example .env
   # then edit .env and paste your API key into GEMINI_API_KEY
   ```

4. **Add sample test files (optional)**
   Place a sample PDF/image/Excel file in `data/sample_inputs/`.

## Running the Demo (Streamlit UI)

```bash
cd frontend
streamlit run Home.py
```

If `streamlit` isn't recognized as a command, use:
```bash
python -m streamlit run Home.py
```

This opens a browser UI with a **landing page** and two sections in the sidebar:

- **🔍 Extract Product** — enter a product name, drag & drop a PDF/image/Excel file (or paste a
  website URL / raw text), and run extraction. High-confidence fields are auto-added; fields
  below 80% confidence show Confirm / Edit / Reject buttons. Once you're done reviewing, click
  **"Verify & Save to Database"** to store the final record.
- **🗂️ Product Database** — browse, search, and delete every verified product record. Each entry
  shows the original initial data side-by-side with the AI-extracted attributes, confidence
  scores, and source references.

The database is a local SQLite file created automatically at `data/product_intelligence.db`.

## Running the Pipeline Directly (Python)

```python
from app.pipeline import run_pipeline

result = run_pipeline(
    product_name="Centrifugal Pump CP-100",
    initial_data={"price": "$320"},
    sources=["data/sample_inputs/datasheet.pdf"]
)

print(result)
```

## How It Works (Quick Summary)

1. Take the product name + any basic known data
2. Add supporting sources: PDF / image / Excel / website / raw text
3. Detect input type and route to the right extraction method
4. Detect the product's category (Lighting, Hardware, Pumps, etc.)
5. Extract only the attributes relevant to that category, each with a confidence score
6. Auto-add high-confidence fields (≥80%); ask the user to confirm low-confidence fields (<80%)
7. Validate the data for unit errors, conflicts, or inconsistencies
8. Combine everything into one final, structured, source-traceable product record

## Notes

- The extraction engine uses Google's Gemini API (free tier) because it can read PDFs,
  images, and text natively in a single multimodal call.
- Category templates are stored in `data/category_templates/category_templates.json` and can
  be extended with new categories/attributes at any time.
- The confidence threshold (default 80%) is configurable via `.env`.

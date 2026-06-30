## Members and roles:

| Member # | Member Name | Member Role | Role Scope |
|-----------|-------------|-------------|------------|
| M1 | Kashish Dhanani | Research & Literature Lead | Literature gathering · Introduction · Background/Lit Review · Conclusion · APA references |
| M2 | Seulgi lee | Text Extraction Dev | pdfplumber + PyMuPDF pipeline · experiment logging · text pipeline methodology section |
| M3 | Abdullah Al Mahfuz | Vision Pipeline Dev | Vision API setup · PDF-to-image conversion · cost tracking · vision methodology section |
| M4 | Ved Dineshkumar Patel | Analysis & Media Lead | Comparison matrix · results · Critical Analysis · slides · video · Appendices A/C/D |

## Folder Structure

```text
AIP444NSC_G07_Research_PDF-Dilemma/
├── .env                  # API keys (Claude / GPT Key)
├── requirements.txt      # Python dependencies
│
├── pdfs/                 # Raw PDF test suite (M1/M4)
│
├── pipeline_text.py      # Text extraction pipeline (M2)
├── pipeline_vision.py    # Vision-based parsing pipeline (M3)
├── evaluate.py           # Evaluation and analysis script (M4)
│
└── outputs/              # Parsed outputs (.txt) & metrics (.csv)
```

## Getting Started

### 1. Install Dependencies
Install the required Python packages before running any scripts:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create or update your `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Run Pipelines
* **Text Extraction (Member 2)**: Place your PDF files inside the `pdfs/` directory, then run:
  ```bash
  python pipeline_text.py
  ```
* **Vision-Based Parsing (Member 3)**: Run the vision pipeline:
  ```bash
  python pipeline_vision.py
  ```
* **Evaluation & Analysis (Member 4)**: Run the evaluation script to compile the results:
  ```bash
  python evaluate.py
  ```

### 4. Metrics & Evaluation Rubric (Phase 1)
To compare both pipelines fairly, the following metrics are tracked per PDF per method:

| Metric | How to Measure | Code Variable |
|--------|----------------|---------------|
| **Processing time (s)** | Measured via `time.time()` before/after extraction | `time_sec` |
| **Output character count** | Measured via `len(extracted_text)` | `char_count` |
| **Table structure score (0–3)** | Manual rating using the rubric below | `table_preservation` |
| **API cost ($)** | Calculated based on input/output tokens (Gemini) | `cost_usd` |
| **Extraction failures** | Boolean flag tracking crashes or exceptions | `failed` |
| **Text Accuracy (%)** | Similarity ratio vs ground truth text | `accuracy` |

#### Table Preservation Rubric:
* **0 (Failure)**: Table not detected at all, or completely garbled/unusable structure.
* **1 (Partial)**: Some rows or columns captured, but the overall structure is broken.
* **2 (Mostly Correct)**: Table structure preserved, with minor misalignments or a few missing cells.
* **3 (Perfect)**: All rows, columns, headers, and values are fully intact.

A unified logging template is available at [evaluation_template.csv](file:///c:/Users/tmfrl/Downloads/AIP444/AIP444NSC_G07_Research_PDF-Dilemma/evaluation_template.csv) for logging Phase 2 results.


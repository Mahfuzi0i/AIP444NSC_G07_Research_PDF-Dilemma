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

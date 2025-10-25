# Entity & Relation Extraction (Assignment 1)

Extract Organisation, Person Name, and PAN entities, plus PAN_Of relations from a PDF. Outputs CSV files and an optional HTML report.

## Quickstart

1. Create venv and install deps
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run
```powershell
python -m src.main --pdf "Assignment 1 AI.pdf" --out outputs\results.csv --entities outputs\entities.csv --relations outputs\relations.csv --report reports\summary.html
```

## Features
- PDF text extraction per-page with layout preservation
- PAN detection with strict regex and validation
- Name and Organization detection via rules and spaCy NER fallback (optional)
- Relation linking PAN_Of using proximity and honorific boosts
- Deduplication and confidence scoring
- CSV export and minimal HTML report
- Hooks prepared for open-source LLM integration

## Notes
- For highest quality, you may add an open-source LLM (e.g., Mistral 7B) and implement prompts in `src/llm_integration.py` (left optional).

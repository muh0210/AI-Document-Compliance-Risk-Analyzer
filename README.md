# AI Document Compliance & Risk Analyzer

> AI-powered decision-support system for analyzing legal and business documents. Get instant compliance scoring, risk detection, clause analysis, and actionable recommendations.

## Features

- **Document Analysis** — Upload PDF, DOCX, or TXT files for instant analysis
- **12 Clause Types** — Detects payment terms, termination, liability, confidentiality, IP rights, and 7 more
- **7 Risk Categories** — Vague language, ambiguous obligations, liability exposure, unilateral terms, auto-renewal, deadline risk, missing signatures
- **Compliance Scoring** — Weighted 0-100 score with A+ to F grading
- **AI Explanations** — Business-impact narratives and prioritized action items
- **Smart Rewrites** — Suggests concrete replacements for risky language
- **PDF Reports** — Download professional multi-page compliance reports
- **Premium UI** — Dark glassmorphism design with animated gradients

## Architecture

```
User → Upload → Text Extraction → NLP Processing → Rule Engine → Risk Engine → Scoring → AI Explanation → Output
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3 + Flask |
| NLP | spaCy (en_core_web_sm) |
| PDF Reports | fpdf2 |
| Document Parsing | PyPDF2, python-docx |
| Frontend | Vanilla HTML/CSS/JS |
| Cloud | Streamlit Community Cloud |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Flask (local)
python app.py
# → http://localhost:5000

# Run with Streamlit
streamlit run streamlit_app.py
# → http://localhost:8501
```

## Project Structure

```
├── app.py                  # Flask API server
├── streamlit_app.py        # Streamlit cloud app
├── requirements.txt        # Python dependencies
├── utils/
│   ├── extractor.py        # PDF/DOCX/TXT ingestion
│   ├── cleaner.py          # NLP text cleaning & segmentation
│   ├── clause_detector.py  # 12 clause type detection
│   ├── risk_engine.py      # 7 risk category analysis
│   ├── scoring.py          # Weighted compliance scoring
│   ├── explanation.py      # AI explanation generator
│   ├── rewrite.py          # Smart rewrite suggestions
│   └── pdf_report.py       # PDF report generator
├── rules/
│   ├── contract_rules.py   # Contract compliance rules
│   └── policy_rules.py     # Policy compliance rules
├── static/
│   ├── index.html          # Premium frontend
│   ├── style.css           # Dark glassmorphism CSS
│   └── app.js              # Frontend logic
├── data/                   # Sample test documents
└── .streamlit/config.toml  # Streamlit theme config
```

## Sample Documents

The `data/` folder includes test documents:
- `sample_contract.txt` — Business contract with payment terms and liability
- `sample_sla.txt` — Service Level Agreement
- `sample_nda.txt` — Non-Disclosure Agreement
- `sample_freelance_agreement.txt` — Freelance consulting contract
- `sample_employment_contract.txt` — Employment agreement

## License

MIT

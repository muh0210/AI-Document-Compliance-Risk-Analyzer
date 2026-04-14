# 🛡️ AI Document Compliance & Risk Analyzer

A premium web-based decision-support system that analyzes business/legal documents for compliance risks, detects missing clauses, scores documents, and provides AI-powered explanations and rewrite suggestions.

## ✨ Features

- **📄 Multi-Format Upload** — PDF, DOCX, TXT with drag-and-drop
- **🔎 12+ Clause Detection** — Payment, termination, liability, confidentiality, IP, data protection, and more
- **🚨 7 Risk Categories** — Vague language, ambiguous obligations, liability exposure, deadline risks, etc.
- **📊 Weighted Compliance Scoring** — 0-100 score with A+ to F grades
- **🧠 AI Explanations** — Plain-English findings with business impact
- **✍️ Smart Rewrites** — Concrete suggestions to fix risky language
- **💡 Prioritized Actions** — Ranked recommendations for improvement

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Run the server
python app.py
```

Open **http://localhost:5000** in your browser.

## 🏗️ Architecture

```
User → Upload → Text Extraction → NLP Processing → Rule Engine
    → Risk Engine → Scoring Engine → AI Explanation → Premium UI
```

## 📁 Project Structure

```
├── app.py                  # Flask API server
├── requirements.txt        # Python dependencies
├── static/
│   ├── index.html          # Frontend UI
│   ├── style.css           # Premium dark glassmorphism theme
│   └── app.js              # Frontend logic
├── utils/
│   ├── extractor.py        # PDF/DOCX/TXT extraction
│   ├── cleaner.py          # Text cleaning & NLP segmentation
│   ├── clause_detector.py  # 12-clause detection engine
│   ├── risk_engine.py      # 7-category risk analysis
│   ├── scoring.py          # Weighted compliance scoring
│   ├── explanation.py      # AI explanation generator
│   └── rewrite.py          # Smart rewrite suggestions
├── rules/
│   ├── contract_rules.py   # Contract rule definitions
│   └── policy_rules.py     # Policy rule definitions
├── data/                   # Upload storage
└── outputs/                # Analysis outputs
```

## 🔧 Tech Stack

- **Backend**: Python 3 + Flask
- **NLP**: spaCy (en_core_web_sm)
- **Document Parsing**: PyPDF2, python-docx
- **Frontend**: Vanilla HTML/CSS/JS — dark glassmorphism design

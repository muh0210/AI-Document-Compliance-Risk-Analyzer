"""
AI Document Compliance & Risk Analyzer -- Flask API Server
Provides /api/analyze and /api/report endpoints.
"""

import os
import io
import traceback
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# In-memory store for last analysis (for PDF download)
_last_analysis = {}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_document():
    """Accept file upload, run full analysis pipeline, return JSON."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        f = request.files["file"]
        if not f.filename:
            return jsonify({"error": "No file selected."}), 400

        allowed = {".pdf", ".docx", ".doc", ".txt"}
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in allowed:
            return jsonify({"error": f"Unsupported type: {ext}"}), 400

        extraction = extract_text(f)
        raw = extraction["text"]
        if not raw or len(raw.strip()) < 20:
            return jsonify({"error": "Could not extract meaningful text."}), 400

        cleaned = clean_text(raw)
        clauses = detect_clauses(cleaned["cleaned"], cleaned["sentences"])
        risks = detect_risks(cleaned["sentences"], cleaned["cleaned"])
        score = compliance_score(clauses, risks, cleaned)
        explanations = generate_explanations(clauses, risks, score)
        rewrites = suggest_rewrites(risks["risks"])

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "document": {
                "filename": extraction["filename"],
                "file_type": extraction["file_type"],
                "page_count": extraction["page_count"],
                "word_count": extraction["word_count"],
                "char_count": extraction["char_count"],
                "sentence_count": len(cleaned["sentences"]),
                "paragraph_count": len(cleaned["paragraphs"]),
                "section_count": len(cleaned["section_headers"]),
            },
            "score": score,
            "clauses": clauses,
            "risks": risks,
            "explanations": explanations,
            "rewrites": rewrites,
            "text_preview": raw[:500] + ("..." if len(raw) > 500 else ""),
        }

        _last_analysis["result"] = result
        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/report", methods=["POST"])
def download_report():
    """Generate and return PDF compliance report."""
    try:
        if "result" not in _last_analysis:
            return jsonify({"error": "No analysis available. Analyze a document first."}), 400
        pdf_bytes = generate_pdf_report(_last_analysis["result"])
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"compliance_report_{datetime.now():%Y%m%d_%H%M%S}.pdf",
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  AI Document Compliance & Risk Analyzer")
    print("  Server running at http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

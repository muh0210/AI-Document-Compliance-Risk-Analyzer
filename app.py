"""
AI Document Compliance & Risk Analyzer — Flask API Server
v2.0.0 — Production-grade with security, logging, structured errors.
"""

import os
import io
import hashlib
import logging
import threading
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report
from utils.doc_type import detect_document_type

# ── App Config ───────────────────────────────────────────

VERSION = "2.0.0"

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

# Security: limit upload size to 5MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Security: restrict CORS to API routes only
CORS(app, resources={r"/api/*": {"origins": os.environ.get("ALLOWED_ORIGINS", "*").split(",")}})

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("compliance")

os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Thread-safe in-memory cache (hash → result)
_cache = {}
_cache_lock = threading.Lock()
MAX_CACHE = 20

ALLOWED_EXT = {".pdf", ".docx", ".doc", ".txt"}


# ── Helpers ──────────────────────────────────────────────

def _error(code: str, message: str, status: int = 400):
    """Standardised error response."""
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


# ── Routes ───────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": VERSION})


@app.route("/api/analyze", methods=["POST"])
def analyze_document():
    """Accept file upload, run full analysis pipeline, return JSON."""
    # Validate upload
    if "file" not in request.files:
        return _error("NO_FILE", "No file uploaded.")

    f = request.files["file"]
    if not f.filename:
        return _error("NO_FILE", "No file selected.")

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return _error("INVALID_FILE", f"Unsupported: {ext}. Use PDF, DOCX, or TXT.")

    try:
        raw_bytes = f.read()
        f.seek(0)
        doc_hash = _hash_bytes(raw_bytes)

        # Check cache
        with _cache_lock:
            if doc_hash in _cache:
                log.info("Cache hit for %s (%s)", f.filename, doc_hash)
                return jsonify(_cache[doc_hash])

        log.info("Analyzing: %s (%d bytes, hash=%s)", f.filename, len(raw_bytes), doc_hash)

        # Pipeline
        extraction = extract_text(f)
        raw = extraction["text"]
        if not raw or len(raw.strip()) < 20:
            return _error("EMPTY_DOC", "Could not extract meaningful text.")

        cleaned = clean_text(raw)
        doc_type = detect_document_type(raw, cleaned.get("section_headers", []))
        clauses = detect_clauses(cleaned["cleaned"], cleaned["sentences"])
        risks = detect_risks(cleaned["sentences"], cleaned["cleaned"])
        score = compliance_score(clauses, risks, cleaned, doc_type["type"])
        explanations = generate_explanations(clauses, risks, score)
        rewrites = suggest_rewrites(risks["risks"])

        result = {
            "success": True,
            "version": VERSION,
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
                "document_type": doc_type,
            },
            "score": score,
            "clauses": clauses,
            "risks": risks,
            "explanations": explanations,
            "rewrites": rewrites,
        }

        # Cache result (thread-safe, LRU-style eviction)
        with _cache_lock:
            if len(_cache) >= MAX_CACHE:
                oldest = next(iter(_cache))
                del _cache[oldest]
            _cache[doc_hash] = result

        log.info("Analysis complete: score=%d (%s), risks=%d",
                 score["score"], score["grade"], risks["summary"]["total_risks"])

        return jsonify(result)

    except ValueError as e:
        log.warning("Validation error: %s", e)
        return _error("VALIDATION", str(e))
    except Exception as e:
        log.exception("Analysis failed")
        return _error("INTERNAL", f"Analysis failed: {str(e)}", 500)


@app.route("/api/report", methods=["POST"])
def download_report():
    """Generate and return PDF compliance report."""
    try:
        # Use the most recent cached result
        with _cache_lock:
            if not _cache:
                return _error("NO_DATA", "No analysis available. Analyze a document first.")
            last_key = list(_cache.keys())[-1]
            data = _cache[last_key]

        log.info("Generating PDF report")
        pdf_bytes = generate_pdf_report(data)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"compliance_report_{datetime.now():%Y%m%d_%H%M%S}.pdf",
        )
    except Exception as e:
        log.exception("PDF generation failed")
        return _error("PDF_ERROR", f"PDF generation failed: {str(e)}", 500)


@app.route("/api/export/<fmt>", methods=["POST"])
def export_results(fmt):
    """Export analysis results as JSON or CSV."""
    import csv

    with _cache_lock:
        if not _cache:
            return _error("NO_DATA", "No analysis available.")
        last_key = list(_cache.keys())[-1]
        data = _cache[last_key]

    if fmt == "json":
        return jsonify(data)
    elif fmt == "csv":
        output = io.StringIO()
        w = csv.writer(output)
        w.writerow(["Category", "Item", "Value", "Details"])
        w.writerow(["Score", "Total", data["score"]["score"], data["score"]["label"]])
        for key, bd in data["score"]["breakdown"].items():
            w.writerow(["Breakdown", key, f"{bd['score']}/{bd['max']}", bd["details"]])
        for _, c in data["clauses"]["detected"].items():
            w.writerow(["Clause", c["label"], "Found" if c["found"] else "Missing", c["description"]])
        for r in data["risks"]["risks"]:
            w.writerow(["Risk", r["category_label"], r["severity"], r["description"]])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"compliance_export_{datetime.now():%Y%m%d_%H%M%S}.csv",
        )
    else:
        return _error("INVALID_FORMAT", f"Unsupported format: {fmt}. Use 'json' or 'csv'.")


# ── Error Handlers ───────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return _error("FILE_TOO_LARGE", "File exceeds 5MB limit.", 413)


@app.errorhandler(404)
def not_found(e):
    return _error("NOT_FOUND", "Resource not found.", 404)


@app.errorhandler(500)
def server_error(e):
    return _error("INTERNAL", "Internal server error.", 500)


# ── Main ─────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 50)
    log.info("  AI Document Compliance & Risk Analyzer v%s", VERSION)
    log.info("  http://localhost:5000")
    log.info("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)

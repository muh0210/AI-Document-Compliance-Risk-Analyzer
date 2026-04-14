"""
AI Document Compliance & Risk Analyzer — Flask API Server
"""

import os
import io
import json
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

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Store last analysis for PDF download
_last_analysis = {}


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Main analysis endpoint — accepts file upload, returns full analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded. Please select a document.'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected.'}), 400

        # Validate file type
        allowed = {'.pdf', '.docx', '.doc', '.txt'}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            return jsonify({'error': f'Unsupported file type: {ext}. Supported: PDF, DOCX, TXT'}), 400

        # ── Pipeline ──
        # 1. Extract text
        extraction = extract_text(file)
        raw_text = extraction['text']

        if not raw_text or len(raw_text.strip()) < 20:
            return jsonify({'error': 'Could not extract meaningful text from the document.'}), 400

        # 2. Clean and segment
        cleaned = clean_text(raw_text)

        # 3. Detect clauses
        clauses = detect_clauses(cleaned['cleaned'], cleaned['sentences'])

        # 4. Detect risks
        risks = detect_risks(cleaned['sentences'], cleaned['cleaned'])

        # 5. Calculate score
        score = compliance_score(clauses, risks, cleaned)

        # 6. Generate explanations
        explanations = generate_explanations(clauses, risks, score)

        # 7. Suggest rewrites
        rewrites = suggest_rewrites(risks['risks'])

        # Build response
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'document': {
                'filename': extraction['filename'],
                'file_type': extraction['file_type'],
                'page_count': extraction['page_count'],
                'word_count': extraction['word_count'],
                'char_count': extraction['char_count'],
                'sentence_count': len(cleaned['sentences']),
                'paragraph_count': len(cleaned['paragraphs']),
                'section_count': len(cleaned['section_headers']),
            },
            'score': score,
            'clauses': clauses,
            'risks': risks,
            'explanations': explanations,
            'rewrites': rewrites,
            'text_preview': raw_text[:500] + ('...' if len(raw_text) > 500 else '')
        }

        # Store for PDF download
        _last_analysis['result'] = result

        return jsonify(result)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/report', methods=['POST'])
def download_report():
    """Generate and download PDF compliance report."""
    try:
        if 'result' not in _last_analysis:
            return jsonify({'error': 'No analysis available. Please analyze a document first.'}), 400
        pdf_bytes = generate_pdf_report(_last_analysis['result'])
        filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '1.0.0', 'engine': 'AI Document Compliance & Risk Analyzer'})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  AI Document Compliance & Risk Analyzer")
    print("  Server running at http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

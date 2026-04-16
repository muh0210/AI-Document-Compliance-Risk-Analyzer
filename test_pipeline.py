"""Full pipeline test for v2.0"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.doc_type import detect_document_type
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report

class F:
    filename = 'sample_contract.txt'
    def read(self): return open('data/sample_contract.txt', 'rb').read()
    def seek(self, n): pass

e = extract_text(F())
print(f"1. EXTRACT: {e['word_count']} words")

c = clean_text(e['text'])
print(f"2. CLEAN: {len(c['sentences'])} sentences")

dt = detect_document_type(e['text'], c.get('section_headers', []))
print(f"3. DOC TYPE: {dt['type']} ({dt['label']}, {dt['confidence']}%)")

cl = detect_clauses(c['cleaned'], c['sentences'])
print(f"4. CLAUSES: {cl['summary']['found_count']}/{cl['summary']['total_clauses']}")

r = detect_risks(c['sentences'], c['cleaned'])
print(f"5. RISKS: {r['summary']['total_risks']} (H:{r['summary']['high']} M:{r['summary']['medium']} L:{r['summary']['low']})")

s = compliance_score(cl, r, c, dt['type'])
print(f"6. SCORE: {s['score']} ({s['grade']} - {s['label']})")
print(f"   Weights: {s['weights_used']}")

x = generate_explanations(cl, r, s)
reasons = x.get('score_reduction_reasons', [])
print(f"7. EXPLAIN: {len(x['action_items'])} actions, {len(x['critical_findings'])} critical, {len(reasons)} reasons")
for rs in reasons[:3]:
    print(f"   -{rs['points_lost']}pts: {rs['reason']}")

w = suggest_rewrites(r['risks'])
print(f"8. REWRITES: {len(w)} suggestions")

data = {
    'document': {'filename': 'test.txt', 'file_type': 'TXT',
        'page_count': None, 'word_count': e['word_count'],
        'char_count': e['char_count'], 'sentence_count': len(c['sentences']),
        'paragraph_count': len(c['paragraphs']), 'section_count': len(c['section_headers']),
        'document_type': dt},
    'score': s, 'clauses': cl, 'risks': r, 'explanations': x, 'rewrites': w}
pdf = generate_pdf_report(data)
print(f"9. PDF: {len(pdf)} bytes")
print("\nALL 9 TESTS PASSED")

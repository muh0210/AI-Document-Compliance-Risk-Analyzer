"""
AI Document Compliance & Risk Analyzer — Streamlit App
Premium Streamlit interface for cloud deployment.
"""

import streamlit as st
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report

# ═══════════════ PAGE CONFIG ═══════════════
st.set_page_config(
    page_title="AI Document Compliance & Risk Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════ CUSTOM CSS ═══════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp { background: linear-gradient(135deg, #0a0b1a 0%, #0f1029 50%, #130f2a 100%); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0f1029; }

.main-header {
    text-align: center; padding: 20px 0 10px;
}
.badge {
    display: inline-block; background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.25); padding: 4px 14px;
    border-radius: 100px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1.5px; color: #6c63ff;
    margin-bottom: 12px;
}
.main-title {
    font-size: 42px; font-weight: 800; line-height: 1.1; margin-bottom: 8px;
    background: linear-gradient(135deg, #fff 0%, #6c63ff 50%, #00d4aa 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
}
.main-sub { color: #9aa0b5; font-size: 15px; margin-bottom: 20px; }

.glass-card {
    background: rgba(255,255,255,0.03); backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;
    padding: 24px; margin-bottom: 20px;
}
.card-title {
    font-size: 18px; font-weight: 700; color: #e8eaed;
    margin-bottom: 16px; padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    font-family: 'Inter', sans-serif;
}
.score-big {
    font-size: 72px; font-weight: 900; text-align: center;
    font-family: 'JetBrains Mono', monospace; line-height: 1;
}
.score-label { text-align: center; color: #5f6580; font-size: 13px; margin-top: 4px; }
.grade-badge {
    display: inline-block; padding: 6px 20px; border-radius: 100px;
    font-size: 16px; font-weight: 800; text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.stat-box {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 14px; text-align: center;
}
.stat-value {
    font-size: 22px; font-weight: 800; color: #4fc3f7;
    font-family: 'JetBrains Mono', monospace;
}
.stat-label { font-size: 10px; color: #5f6580; text-transform: uppercase; letter-spacing: 0.5px; }

.clause-found { border-left: 3px solid #00e676; padding: 10px 14px; margin: 6px 0;
    background: rgba(0,230,118,0.04); border-radius: 0 8px 8px 0; }
.clause-missing { border-left: 3px solid #ff5252; padding: 10px 14px; margin: 6px 0;
    background: rgba(255,82,82,0.04); border-radius: 0 8px 8px 0; }
.clause-name { font-weight: 600; color: #e8eaed; font-size: 14px; }
.clause-desc { color: #5f6580; font-size: 11px; }

.risk-high { border-left: 3px solid #ff5252; padding: 12px 14px; margin: 6px 0;
    background: rgba(255,82,82,0.04); border-radius: 0 8px 8px 0; }
.risk-medium { border-left: 3px solid #ffab40; padding: 12px 14px; margin: 6px 0;
    background: rgba(255,171,64,0.04); border-radius: 0 8px 8px 0; }
.risk-low { border-left: 3px solid #ffd740; padding: 12px 14px; margin: 6px 0;
    background: rgba(255,215,64,0.04); border-radius: 0 8px 8px 0; }
.risk-cat { font-weight: 600; color: #e8eaed; font-size: 13px; }
.risk-desc { color: #9aa0b5; font-size: 12px; margin-top: 4px; }
.risk-sent { color: #5f6580; font-size: 12px; font-style: italic; margin-top: 4px;
    padding: 6px 10px; background: rgba(255,255,255,0.02); border-radius: 6px; }

.sev-badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 700; font-family: 'JetBrains Mono', monospace;
}
.sev-HIGH { background: rgba(255,23,68,0.15); color: #ff5252; }
.sev-MEDIUM { background: rgba(255,171,64,0.15); color: #ffab40; }
.sev-LOW { background: rgba(255,215,64,0.15); color: #ffd740; }

.action-item {
    display: flex; gap: 10px; padding: 10px 14px; margin: 6px 0;
    border: 1px solid rgba(255,255,255,0.06); border-radius: 10px;
    background: rgba(255,255,255,0.01);
}
.action-num {
    width: 26px; height: 26px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; font-size: 11px;
    font-weight: 800; font-family: 'JetBrains Mono', monospace; flex-shrink: 0;
}
.action-title { font-weight: 600; color: #e8eaed; font-size: 13px; }
.action-detail { color: #9aa0b5; font-size: 11px; margin-top: 2px; }

.rewrite-box { border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; margin: 8px 0; overflow: hidden; }
.rewrite-orig { padding: 10px 14px; background: rgba(255,82,82,0.04); font-size: 12px; color: #9aa0b5; }
.rewrite-impr { padding: 10px 14px; background: rgba(0,212,170,0.04); font-size: 12px; color: #e8eaed; }
.rewrite-lbl { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }

.footer-text { text-align: center; color: #5f6580; font-size: 12px; padding: 30px 0 10px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════ HEADER ═══════════════
st.markdown("""
<div class="main-header">
    <div class="badge">🟢 AI-Powered Analysis Engine</div>
    <div class="main-title">Document Compliance<br>& Risk Analyzer</div>
    <div class="main-sub">Upload any business document and get instant AI-powered compliance scoring, risk detection, and actionable recommendations.</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════ FILE UPLOAD ═══════════════
uploaded_file = st.file_uploader(
    "📄 Upload your document (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "doc", "txt"],
    help="Drag and drop or click to browse"
)

if uploaded_file is not None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze = st.button("🔍 Analyze Document", use_container_width=True, type="primary")

    if analyze:
        with st.spinner("🔄 Running AI analysis pipeline..."):
            try:
                # ── Analysis Pipeline ──
                extraction = extract_text(uploaded_file)
                raw_text = extraction['text']

                if not raw_text or len(raw_text.strip()) < 20:
                    st.error("Could not extract meaningful text from the document.")
                    st.stop()

                cleaned = clean_text(raw_text)
                clauses = detect_clauses(cleaned['cleaned'], cleaned['sentences'])
                risks = detect_risks(cleaned['sentences'], cleaned['cleaned'])
                score = compliance_score(clauses, risks, cleaned)
                explanations = generate_explanations(clauses, risks, score)
                rewrites = suggest_rewrites(risks['risks'])

                # Full result for PDF
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
                    'score': score, 'clauses': clauses, 'risks': risks,
                    'explanations': explanations, 'rewrites': rewrites,
                }

                st.session_state['analysis'] = result

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.stop()

    # ── RENDER RESULTS ──
    if 'analysis' in st.session_state:
        r = st.session_state['analysis']
        sc = r['score']
        doc = r['document']
        cl = r['clauses']
        rk = r['risks']
        ex = r['explanations']
        rw = r['rewrites']

        st.markdown("---")

        # ── SCORE ──
        st.markdown(f"""
        <div class="glass-card" style="text-align:center">
            <div class="card-title">📊 Compliance Score</div>
            <div class="score-big" style="color:{sc['color']}">{sc['score']}</div>
            <div class="score-label">OUT OF 100</div>
            <div style="margin-top:12px">
                <span class="grade-badge" style="background:{sc['color']}15;color:{sc['color']};border:1px solid {sc['color']}30">{sc['grade']} — {sc['label']}</span>
            </div>
            <div style="color:#9aa0b5;margin-top:12px;font-size:14px">{ex['overall_assessment']['narrative']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Score breakdown
        cols = st.columns(4)
        bd_items = [
            ('Clause Coverage', 'clause_coverage', '#6c63ff'),
            ('Risk Safety', 'risk_density', '#00d4aa'),
            ('Structure', 'structure', '#4fc3f7'),
            ('Language Clarity', 'clarity', '#ffab40'),
        ]
        for i, (lbl, key, clr) in enumerate(bd_items):
            b = sc['breakdown'][key]
            pct = int((b['score'] / b['max']) * 100) if b['max'] else 0
            with cols[i]:
                st.markdown(f"""
                <div class="stat-box">
                    <div style="color:{clr};font-weight:700;font-size:10px;text-transform:uppercase;letter-spacing:1px">{lbl}</div>
                    <div style="margin:6px 0;background:rgba(255,255,255,0.05);height:5px;border-radius:100px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:{clr};border-radius:100px"></div>
                    </div>
                    <div style="color:{clr};font-weight:700;font-family:'JetBrains Mono',monospace;font-size:13px">{b['score']}/{b['max']}</div>
                    <div style="color:#5f6580;font-size:10px">{b['details'][:50]}</div>
                </div>
                """, unsafe_allow_html=True)

        # PDF Download
        try:
            pdf_bytes = generate_pdf_report(r)
            st.download_button(
                "📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            pass

        # ── DOCUMENT INFO ──
        st.markdown(f'<div class="glass-card"><div class="card-title">📋 Document Overview — {doc["file_type"]}</div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, (v, l) in zip([c1, c2, c3, c4, c5], [
            (doc['word_count'], 'Words'), (doc['sentence_count'], 'Sentences'),
            (doc['paragraph_count'], 'Paragraphs'), (doc['section_count'], 'Sections'),
            (doc['char_count'], 'Characters')
        ]):
            with col:
                st.markdown(f'<div class="stat-box"><div class="stat-value">{v:,}</div><div class="stat-label">{l}</div></div>', unsafe_allow_html=True)

        # ── CRITICAL FINDINGS ──
        critical = ex.get('critical_findings', [])
        if critical:
            st.markdown(f'<div class="glass-card"><div class="card-title">🚨 Critical Findings — {len(critical)} Found</div>', unsafe_allow_html=True)
            for f in critical:
                st.markdown(f"""
                <div class="risk-high">
                    <span class="sev-badge sev-HIGH">CRITICAL</span>
                    <span class="risk-cat" style="margin-left:8px">{f.get('icon','')} {f.get('title','')}</span>
                    <div class="risk-desc">{f.get('explanation','')}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CLAUSES ──
        cs = cl['summary']
        st.markdown(f'<div class="glass-card"><div class="card-title">🔎 Clause Detection — {cs["found_count"]}/{cs["total_clauses"]}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (cid, c) in enumerate(cl['detected'].items()):
            with cols[i % 3]:
                css_class = "clause-found" if c['found'] else "clause-missing"
                status = f"✅ {c['confidence']}%" if c['found'] else "❌ Missing"
                st.markdown(f"""
                <div class="{css_class}">
                    <span class="clause-name">{c['icon']} {c['label']}</span> <span style="float:right">{status}</span>
                    <div class="clause-desc">{c['description']}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── RISKS ──
        rs = rk['summary']
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-title">⚠️ Risk Alerts — {rs['total_risks']} Risks</div>
            <div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap">
                <span class="sev-badge sev-HIGH" style="padding:6px 14px;font-size:12px">🔴 {rs['high']} High</span>
                <span class="sev-badge sev-MEDIUM" style="padding:6px 14px;font-size:12px">🔶 {rs['medium']} Medium</span>
                <span class="sev-badge sev-LOW" style="padding:6px 14px;font-size:12px">🟡 {rs['low']} Low</span>
            </div>
        """, unsafe_allow_html=True)
        for risk in rk['risks'][:12]:
            sev = risk['severity']
            css = f"risk-{sev.lower()}"
            st.markdown(f"""
            <div class="{css}">
                <span class="sev-badge sev-{sev}">{sev}</span>
                <span class="risk-cat" style="margin-left:8px">{risk['icon']} {risk['category_label']}</span>
                <div class="risk-sent">"{risk['sentence'][:150]}"</div>
                <div class="risk-desc">{risk['description']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── ACTIONS ──
        actions = ex.get('action_items', [])
        if actions:
            st.markdown(f'<div class="glass-card"><div class="card-title">💡 Recommended Actions — {len(actions)} Items</div>', unsafe_allow_html=True)
            for i, a in enumerate(actions, 1):
                sev = a.get('severity', 'MEDIUM')
                bg = 'rgba(255,23,68,0.15)' if sev == 'HIGH' else ('rgba(255,171,64,0.15)' if sev == 'MEDIUM' else 'rgba(255,215,64,0.15)')
                clr = '#ff5252' if sev == 'HIGH' else ('#ffab40' if sev == 'MEDIUM' else '#ffd740')
                st.markdown(f"""
                <div class="action-item">
                    <div class="action-num" style="background:{bg};color:{clr}">{i}</div>
                    <div>
                        <div class="action-title">{a.get('icon','')} {a.get('action','')}</div>
                        <div class="action-detail">{a.get('detail','')}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── REWRITES ──
        if rw:
            st.markdown(f'<div class="glass-card"><div class="card-title">✍️ Suggested Rewrites — {len(rw)}</div>', unsafe_allow_html=True)
            for item in rw[:8]:
                changes_html = ' '.join(f'<span style="background:rgba(0,212,170,0.1);color:#00d4aa;padding:1px 6px;border-radius:4px;font-size:10px;font-family:JetBrains Mono,monospace">{c}</span>' for c in item.get('changes', []))
                st.markdown(f"""
                <div class="rewrite-box">
                    <div class="rewrite-orig">
                        <div class="rewrite-lbl" style="color:#ff5252">✗ Original</div>
                        {item['original'][:180]}
                    </div>
                    <div class="rewrite-impr">
                        <div class="rewrite-lbl" style="color:#00d4aa">✓ Improved</div>
                        {item['rewritten'][:180]}
                        <div style="margin-top:6px">{changes_html}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── FOOTER ──
        st.markdown('<div class="footer-text">🛡️ AI Document Compliance & Risk Analyzer v1.0.0 — Built with NLP + Rule Engine + AI Explanation Engine</div>', unsafe_allow_html=True)

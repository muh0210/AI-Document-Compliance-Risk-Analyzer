"""
AI Document Compliance & Risk Analyzer -- Streamlit Cloud App
Premium UI with dark glassmorphism theme.
"""

import streamlit as st
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report

# ── Page config ──
st.set_page_config(page_title="AI Compliance Analyzer", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# ── CSS ──
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
.stApp{background:linear-gradient(135deg,#0a0b1a,#0f1029,#130f2a)}
[data-testid="stHeader"]{background:transparent}
.hdr{text-align:center;padding:20px 0 10px}
.badge{display:inline-block;background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.25);padding:4px 14px;border-radius:100px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:#6c63ff;margin-bottom:12px}
.title{font-size:38px;font-weight:800;line-height:1.1;margin-bottom:8px;background:linear-gradient(135deg,#fff,#6c63ff,#00d4aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'Inter',sans-serif}
.sub{color:#9aa0b5;font-size:15px;margin-bottom:20px}
.gc{background:rgba(255,255,255,.03);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:24px;margin-bottom:20px}
.ct{font-size:18px;font-weight:700;color:#e8eaed;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.08);font-family:'Inter',sans-serif}
.sb{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:14px;text-align:center}
.sv{font-size:22px;font-weight:800;color:#4fc3f7;font-family:'JetBrains Mono',monospace}
.sl{font-size:10px;color:#5f6580;text-transform:uppercase;letter-spacing:.5px}
.cf{border-left:3px solid #00e676;padding:10px 14px;margin:6px 0;background:rgba(0,230,118,.04);border-radius:0 8px 8px 0}
.cm{border-left:3px solid #ff5252;padding:10px 14px;margin:6px 0;background:rgba(255,82,82,.04);border-radius:0 8px 8px 0}
.rh{border-left:3px solid #ff5252;padding:12px 14px;margin:6px 0;background:rgba(255,82,82,.04);border-radius:0 8px 8px 0}
.rm{border-left:3px solid #ffab40;padding:12px 14px;margin:6px 0;background:rgba(255,171,64,.04);border-radius:0 8px 8px 0}
.rl{border-left:3px solid #ffd740;padding:12px 14px;margin:6px 0;background:rgba(255,215,64,.04);border-radius:0 8px 8px 0}
.ft{text-align:center;color:#5f6580;font-size:12px;padding:30px 0 10px}
</style>""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""<div class="hdr">
<div class="badge">AI-Powered Analysis Engine</div>
<div class="title">Document Compliance<br>& Risk Analyzer</div>
<div class="sub">Upload any business document for instant compliance scoring, risk detection, and actionable recommendations.</div>
</div>""", unsafe_allow_html=True)

# ── Upload ──
uploaded = st.file_uploader("Upload your document (PDF, DOCX, TXT)", type=["pdf","docx","doc","txt"])

if uploaded:
    _, c2, _ = st.columns([1,2,1])
    with c2:
        go = st.button("🔍 Analyze Document", use_container_width=True, type="primary")
    if go:
        with st.spinner("Running AI analysis..."):
            try:
                ext = extract_text(uploaded)
                raw = ext["text"]
                if not raw or len(raw.strip()) < 20:
                    st.error("Could not extract meaningful text."); st.stop()
                cl = clean_text(raw)
                clauses = detect_clauses(cl["cleaned"], cl["sentences"])
                risks = detect_risks(cl["sentences"], cl["cleaned"])
                score = compliance_score(clauses, risks, cl)
                expl = generate_explanations(clauses, risks, score)
                rw = suggest_rewrites(risks["risks"])
                st.session_state["r"] = {
                    "document": {"filename": ext["filename"], "file_type": ext["file_type"],
                        "page_count": ext["page_count"], "word_count": ext["word_count"],
                        "char_count": ext["char_count"], "sentence_count": len(cl["sentences"]),
                        "paragraph_count": len(cl["paragraphs"]), "section_count": len(cl["section_headers"])},
                    "score": score, "clauses": clauses, "risks": risks, "explanations": expl, "rewrites": rw}
            except Exception as e:
                st.error(f"Analysis failed: {e}"); st.stop()

    # ── Results ──
    if "r" in st.session_state:
        r = st.session_state["r"]
        sc, doc, ex = r["score"], r["document"], r["explanations"]
        st.markdown("---")

        # Score
        st.markdown(f"""<div class="gc" style="text-align:center">
        <div class="ct">Compliance Score</div>
        <div style="font-size:72px;font-weight:900;color:{sc['color']};font-family:'JetBrains Mono',monospace;line-height:1">{sc['score']}</div>
        <div style="color:#5f6580;font-size:13px;margin-top:4px">OUT OF 100</div>
        <div style="margin-top:12px"><span style="display:inline-block;padding:6px 20px;border-radius:100px;font-size:16px;font-weight:800;background:{sc['color']}15;color:{sc['color']};border:1px solid {sc['color']}30;font-family:'JetBrains Mono',monospace">{sc['grade']} - {sc['label']}</span></div>
        <div style="color:#9aa0b5;margin-top:12px;font-size:14px">{ex['overall_assessment']['narrative']}</div>
        </div>""", unsafe_allow_html=True)

        # Breakdown bars
        cols = st.columns(4)
        for i, (lbl, key, clr) in enumerate([("Clause Coverage","clause_coverage","#6c63ff"),("Risk Safety","risk_density","#00d4aa"),("Structure","structure","#4fc3f7"),("Clarity","clarity","#ffab40")]):
            b = sc["breakdown"][key]
            pct = int((b["score"]/b["max"])*100) if b["max"] else 0
            with cols[i]:
                st.markdown(f"""<div class="sb">
                <div style="color:{clr};font-weight:700;font-size:10px;text-transform:uppercase;letter-spacing:1px">{lbl}</div>
                <div style="margin:6px 0;background:rgba(255,255,255,.05);height:5px;border-radius:100px;overflow:hidden"><div style="width:{pct}%;height:100%;background:{clr};border-radius:100px"></div></div>
                <div style="color:{clr};font-weight:700;font-family:'JetBrains Mono',monospace;font-size:13px">{b['score']}/{b['max']}</div>
                </div>""", unsafe_allow_html=True)

        # PDF
        try:
            pdf = generate_pdf_report(r)
            st.download_button("📄 Download PDF Report", data=pdf, file_name=f"compliance_report_{datetime.now():%Y%m%d_%H%M%S}.pdf", mime="application/pdf", use_container_width=True)
        except Exception:
            pass

        # Doc stats
        c1,c2,c3,c4,c5 = st.columns(5)
        for col,(v,l) in zip([c1,c2,c3,c4,c5],[(doc['word_count'],'Words'),(doc['sentence_count'],'Sentences'),(doc['paragraph_count'],'Paragraphs'),(doc['section_count'],'Sections'),(doc['char_count'],'Characters')]):
            with col:
                st.markdown(f'<div class="sb"><div class="sv">{v:,}</div><div class="sl">{l}</div></div>', unsafe_allow_html=True)

        # Clauses
        cdata = r["clauses"]
        cs = cdata["summary"]
        st.markdown(f'<div class="gc"><div class="ct">Clause Detection - {cs["found_count"]}/{cs["total_clauses"]}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(cid,c) in enumerate(cdata["detected"].items()):
            with cols[i%3]:
                css = "cf" if c["found"] else "cm"
                st.markdown(f'<div class="{css}"><span style="font-weight:600;color:#e8eaed;font-size:14px">{c["label"]}</span> <span style="float:right">{"✅ "+str(c["confidence"])+"%" if c["found"] else "❌ Missing"}</span><div style="color:#5f6580;font-size:11px">{c["description"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Risks
        rs = r["risks"]["summary"]
        st.markdown(f'<div class="gc"><div class="ct">Risk Alerts - {rs["total_risks"]} Risks</div>', unsafe_allow_html=True)
        for risk in r["risks"]["risks"][:12]:
            sev = risk["severity"]
            css = f"r{sev[0].lower()}"
            st.markdown(f'<div class="{css}"><span style="font-weight:600;color:#e8eaed">[{sev}] {risk["category_label"]}</span><div style="color:#5f6580;font-size:12px;font-style:italic;margin-top:4px">"{risk["sentence"][:150]}"</div><div style="color:#9aa0b5;font-size:12px;margin-top:4px">{risk["description"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Actions
        actions = ex.get("action_items", [])
        if actions:
            st.markdown(f'<div class="gc"><div class="ct">Recommended Actions - {len(actions)} Items</div>', unsafe_allow_html=True)
            for i,a in enumerate(actions,1):
                sev = a.get("severity","MEDIUM")
                clr = '#ff5252' if sev=='HIGH' else ('#ffab40' if sev=='MEDIUM' else '#ffd740')
                st.markdown(f'<div style="display:flex;gap:10px;padding:10px 14px;margin:6px 0;border:1px solid rgba(255,255,255,.06);border-radius:10px;background:rgba(255,255,255,.01)"><div style="width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;background:{clr}20;color:{clr};flex-shrink:0">{i}</div><div><div style="font-weight:600;color:#e8eaed;font-size:13px">{a.get("action","")}</div><div style="color:#9aa0b5;font-size:11px;margin-top:2px">{a.get("detail","")}</div></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Rewrites
        rw = r["rewrites"]
        if rw:
            st.markdown(f'<div class="gc"><div class="ct">Suggested Rewrites - {len(rw)}</div>', unsafe_allow_html=True)
            for item in rw[:8]:
                st.markdown(f'<div style="border:1px solid rgba(255,255,255,.06);border-radius:10px;margin:8px 0;overflow:hidden"><div style="padding:10px 14px;background:rgba(255,82,82,.04);font-size:12px;color:#9aa0b5"><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#ff5252">Original</div>{item["original"][:180]}</div><div style="padding:10px 14px;background:rgba(0,212,170,.04);font-size:12px;color:#e8eaed"><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#00d4aa">Improved</div>{item["rewritten"][:180]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ft">AI Document Compliance & Risk Analyzer v1.0.0</div>', unsafe_allow_html=True)

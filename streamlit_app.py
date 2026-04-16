"""
AI Document Compliance & Risk Analyzer — Streamlit Cloud App v2.0
Production-grade with doc type detection, adaptive scoring, and export options.
"""

import streamlit as st
import os
import sys
import json
import csv
import io
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("compliance")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import extract_text
from utils.cleaner import clean_text
from utils.clause_detector import detect_clauses
from utils.risk_engine import detect_risks
from utils.scoring import compliance_score
from utils.explanation import generate_explanations
from utils.rewrite import suggest_rewrites
from utils.pdf_report import generate_pdf_report
from utils.doc_type import detect_document_type

VERSION = "2.0.0"

# ── Config ───────────────────────────────────────
st.set_page_config(page_title="Compliance Analyzer", page_icon="⚖️", layout="wide", initial_sidebar_state="collapsed")

# ── CSS ──────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
.stApp{background:#0e0f18}
[data-testid="stHeader"]{background:rgba(14,15,24,.85);backdrop-filter:blur(12px)}
h1{font-family:'Source Serif 4',Georgia,serif!important;color:#fff!important}
.eyebrow{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:#637dff;margin-bottom:8px}
.hero-desc{color:#8a8fa8;font-size:15px;max-width:500px;line-height:1.7}
.gc{background:#16172a;border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:24px;margin-bottom:16px}
.sec-t{font-family:'Source Serif 4',serif;font-size:20px;font-weight:600;color:#fff;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.06)}
.sb{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:8px;padding:14px;text-align:center}
.sv{font-size:20px;font-weight:700;color:#637dff;font-family:'JetBrains Mono',monospace}
.sl{font-size:10px;color:#5a5f78;text-transform:uppercase;letter-spacing:.5px}
.cf{border-left:3px solid #3dd6a5;padding:10px 14px;margin:5px 0;border-radius:0 8px 8px 0;background:rgba(61,214,165,.03)}
.cm{border-left:3px solid #f25a5a;padding:10px 14px;margin:5px 0;border-radius:0 8px 8px 0;background:rgba(242,90,90,.03);opacity:.7}
.rh{border-left:3px solid #f25a5a;padding:12px 14px;margin:5px 0;border-radius:0 8px 8px 0;background:rgba(242,90,90,.03)}
.rm{border-left:3px solid #e8a33d;padding:12px 14px;margin:5px 0;border-radius:0 8px 8px 0;background:rgba(232,163,61,.03)}
.rl{border-left:3px solid #ffd740;padding:12px 14px;margin:5px 0;border-radius:0 8px 8px 0;background:rgba(255,215,64,.03)}
.ft{text-align:center;color:#5a5f78;font-size:12px;padding:30px 0 10px}
.doc-chip{display:inline-block;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;background:rgba(61,214,165,.08);color:#3dd6a5;border:1px solid rgba(61,214,165,.15)}
</style>""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────
st.markdown('<p class="eyebrow">Document Intelligence</p>', unsafe_allow_html=True)
st.title("Know what's in your contracts _before_ you sign.")
st.markdown('<p class="hero-desc">Upload a legal document for instant compliance scoring, risk detection, and recommendations.</p>', unsafe_allow_html=True)

# ── Upload ───────────────────────────────────────
uploaded = st.file_uploader("Upload document", type=["pdf","docx","doc","txt"], label_visibility="collapsed")

if uploaded:
    go = st.button("Analyze Document →", type="primary", use_container_width=True)
    if go:
        with st.spinner("Running analysis pipeline..."):
            try:
                log.info("Analyzing: %s", uploaded.name)
                ext = extract_text(uploaded)
                raw = ext["text"]
                if not raw or len(raw.strip()) < 20:
                    st.error("Could not extract meaningful text."); st.stop()
                cl = clean_text(raw)
                dt = detect_document_type(raw, cl.get("section_headers", []))
                clauses = detect_clauses(cl["cleaned"], cl["sentences"])
                risks = detect_risks(cl["sentences"], cl["cleaned"])
                score = compliance_score(clauses, risks, cl, dt["type"])
                expl = generate_explanations(clauses, risks, score)
                rw = suggest_rewrites(risks["risks"])
                st.session_state["r"] = {
                    "version": VERSION,
                    "document": {"filename": ext["filename"], "file_type": ext["file_type"],
                        "page_count": ext["page_count"], "word_count": ext["word_count"],
                        "char_count": ext["char_count"], "sentence_count": len(cl["sentences"]),
                        "paragraph_count": len(cl["paragraphs"]), "section_count": len(cl["section_headers"]),
                        "document_type": dt},
                    "score": score, "clauses": clauses, "risks": risks, "explanations": expl, "rewrites": rw}
                log.info("Score: %d (%s), type: %s", score["score"], score["grade"], dt["type"])
            except Exception as e:
                log.exception("Analysis failed")
                st.error(f"Analysis failed: {e}"); st.stop()

    # ── Results ──────────────────────────────────
    if "r" in st.session_state:
        r = st.session_state["r"]
        sc, doc, ex = r["score"], r["document"], r["explanations"]
        dt = doc.get("document_type", {})
        st.markdown("---")

        # Score
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""<div class="gc" style="text-align:center">
            <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:#5a5f78;margin-bottom:8px">Compliance Score</div>
            <div style="font-size:64px;font-weight:700;color:{sc['color']};font-family:'JetBrains Mono',monospace;line-height:1">{sc['score']}</div>
            <div style="margin-top:8px"><span style="display:inline-block;padding:4px 14px;border-radius:100px;font-size:13px;font-weight:600;background:{sc['color']}12;color:{sc['color']};border:1px solid {sc['color']}25;font-family:'JetBrains Mono',monospace">{sc['grade']} — {sc['label']}</span></div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="gc">
            <div style="font-family:'Source Serif 4',serif;font-size:15px;color:#8a8fa8;font-style:italic;line-height:1.7;margin-bottom:12px">{ex['overall_assessment']['narrative']}</div>
            <span class="doc-chip">{dt.get('label','Document')}</span>
            <span style="font-size:12px;color:#5a5f78;font-family:'JetBrains Mono',monospace;margin-left:8px">{doc['word_count']:,} words · {doc['sentence_count']} sentences</span>
            </div>""", unsafe_allow_html=True)

        # Breakdown
        cols = st.columns(4)
        for i,(lbl,key,clr) in enumerate([("Clause Coverage","clause_coverage","#637dff"),("Risk Safety","risk_density","#3dd6a5"),("Structure","structure","#4fc3f7"),("Clarity","clarity","#e8a33d")]):
            b = sc["breakdown"][key]
            pct = int((b["score"]/b["max"])*100) if b["max"] else 0
            with cols[i]:
                st.markdown(f"""<div class="sb">
                <div style="color:{clr};font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:1px">{lbl}</div>
                <div style="margin:6px 0;background:rgba(255,255,255,.05);height:3px;border-radius:100px;overflow:hidden"><div style="width:{pct}%;height:100%;background:{clr};border-radius:100px"></div></div>
                <div style="color:{clr};font-weight:600;font-family:'JetBrains Mono',monospace;font-size:13px">{b['score']}/{b['max']}</div>
                <div style="font-size:10px;color:#5a5f78;margin-top:4px">{b['details']}</div>
                </div>""", unsafe_allow_html=True)

        # Score reduction
        reasons = ex.get("score_reduction_reasons", [])
        if reasons:
            st.markdown('<div class="gc"><div class="sec-t">Why the Score Was Reduced</div>', unsafe_allow_html=True)
            for rs in reasons:
                st.markdown(f'<div style="display:flex;gap:12px;padding:10px 14px;margin:6px 0;border:1px solid rgba(255,255,255,.06);border-radius:8px;background:rgba(232,163,61,.02)"><span style="font-family:\'JetBrains Mono\',monospace;font-weight:600;color:#e8a33d;min-width:50px">-{rs["points_lost"]}</span><span style="font-size:13px;color:#8a8fa8">{rs["reason"]}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Exports
        try:
            pdf = generate_pdf_report(r)
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                st.download_button("Download PDF Report", data=pdf,
                    file_name=f"compliance_report_{datetime.now():%Y%m%d_%H%M%S}.pdf",
                    mime="application/pdf", use_container_width=True)
            with ec2:
                st.download_button("Export JSON", data=json.dumps(r, indent=2, default=str),
                    file_name=f"compliance_export.json", mime="application/json", use_container_width=True)
            with ec3:
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow(["Category","Item","Value","Details"])
                w.writerow(["Score","Total",sc["score"],sc["label"]])
                for k,bd in sc["breakdown"].items():
                    w.writerow(["Breakdown",k,f"{bd['score']}/{bd['max']}",bd["details"]])
                st.download_button("Export CSV", data=buf.getvalue(),
                    file_name=f"compliance_export.csv", mime="text/csv", use_container_width=True)
        except Exception: pass

        # Clauses
        cdata = r["clauses"]
        st.markdown(f'<div class="gc"><div class="sec-t">Clause Coverage — {cdata["summary"]["found_count"]}/{cdata["summary"]["total_clauses"]}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(cid,c) in enumerate(cdata["detected"].items()):
            with cols[i%3]:
                css = "cf" if c["found"] else "cm"
                status = f'{c["confidence"]}%' if c["found"] else "Missing"
                st.markdown(f'<div class="{css}"><span style="font-weight:600;color:#dfe1e8;font-size:13px">{c["label"]}</span> <span style="float:right;font-family:\'JetBrains Mono\',monospace;font-size:11px;color:{"#3dd6a5" if c["found"] else "#f25a5a"}">{status}</span><div style="color:#5a5f78;font-size:11px">{c["description"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Risks
        rs = r["risks"]["summary"]
        st.markdown(f'<div class="gc"><div class="sec-t">Risk Alerts — {rs["total_risks"]} found</div>', unsafe_allow_html=True)
        for risk in r["risks"]["risks"][:12]:
            sev = risk["severity"]
            css = f"r{sev[0].lower()}"
            st.markdown(f'<div class="{css}"><div style="display:flex;justify-content:space-between"><span style="font-weight:600;color:#dfe1e8;font-size:13px">{risk["category_label"]}</span><span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;font-weight:600;color:{"#f25a5a" if sev=="HIGH" else "#e8a33d" if sev=="MEDIUM" else "#ffd740"}">{sev}</span></div><div style="font-family:\'Source Serif 4\',serif;font-style:italic;font-size:12px;color:#5a5f78;padding:6px 10px;margin:6px 0;border-left:2px solid rgba(255,255,255,.06);background:rgba(255,255,255,.01);border-radius:0 6px 6px 0">"{risk["sentence"][:150]}"</div><div style="font-size:12px;color:#8a8fa8">{risk["description"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Actions
        actions = ex.get("action_items", [])
        if actions:
            st.markdown(f'<div class="gc"><div class="sec-t">Recommended Actions — {len(actions)}</div>', unsafe_allow_html=True)
            for i,a in enumerate(actions,1):
                sev = a.get("severity","MEDIUM")
                clr = '#f25a5a' if sev=='HIGH' else ('#e8a33d' if sev=='MEDIUM' else '#ffd740')
                st.markdown(f'<div style="display:flex;gap:12px;padding:12px 14px;margin:6px 0;border:1px solid rgba(255,255,255,.06);border-radius:8px;background:rgba(255,255,255,.01)"><div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;background:{clr}18;color:{clr};flex-shrink:0;font-family:\'JetBrains Mono\',monospace">{i}</div><div><div style="font-weight:600;color:#dfe1e8;font-size:13px">{a.get("action","")}</div><div style="color:#8a8fa8;font-size:12px;margin-top:2px">{a.get("detail","")}</div>{"<div style=font-size:11px;color:#5a5f78;font-style:italic;margin-top:4px>If ignored: "+a.get("if_ignored","")+"</div>" if a.get("if_ignored") else ""}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Rewrites
        rw = r["rewrites"]
        if rw:
            st.markdown(f'<div class="gc"><div class="sec-t">Language Improvements — {len(rw)}</div>', unsafe_allow_html=True)
            for item in rw[:8]:
                st.markdown(f'<div style="border:1px solid rgba(255,255,255,.06);border-radius:8px;margin:8px 0;overflow:hidden"><div style="padding:10px 14px;background:rgba(242,90,90,.03);font-size:12px;color:#8a8fa8"><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#f25a5a">Original</div>{item["original"][:200]}</div><div style="padding:10px 14px;background:rgba(61,214,165,.03);font-size:12px;color:#dfe1e8"><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#3dd6a5">Improved</div>{item["rewritten"][:200]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="ft">Compliance Analyzer v{VERSION} · Built for legal clarity, not legal advice.</div>', unsafe_allow_html=True)

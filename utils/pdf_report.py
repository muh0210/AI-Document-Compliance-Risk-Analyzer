"""
PDF Compliance Report Generator
Generates a multi-page dark-themed PDF using fpdf2.

Design constraints:
  - Only cell(), multi_cell(), rect(), line() — NO rounded_rect().
  - All text goes through _s() to strip non-Latin-1 characters.
  - NO leading-space indentation in multi_cell text (causes crash).
  - Use set_x() for visual offsets instead.
"""

from fpdf import FPDF
from datetime import datetime
import unicodedata


def _s(text) -> str:
    """Strip non-Latin-1 characters so Helvetica never crashes."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", str(text))
    return "".join(ch if ord(ch) < 256 else "" for ch in t)


class _PDF(FPDF):
    BG   = (15, 16, 41)
    CARD = (22, 24, 55)
    W    = (232, 234, 237)
    M    = (154, 160, 181)
    A    = (108, 99, 255)
    G    = (0, 230, 118)
    R    = (255, 82, 82)
    O    = (255, 171, 64)
    Y    = (255, 215, 64)
    B    = (79, 195, 247)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(True, margin=20)

    def header(self):
        self.set_fill_color(*self.BG)
        self.rect(0, 0, 210, 297, "F")
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*self.M)
            self.set_xy(10, 8)
            self.cell(190, 5, "AI Document Compliance & Risk Analyzer", align="L")
            self.set_xy(10, 8)
            self.cell(190, 5, f"Page {self.page_no()}", align="R")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*self.M)
        self.cell(0, 10, _s(f"Generated {datetime.now():%Y-%m-%d %H:%M} | Compliance Analyzer v1.0"), align="C")

    def heading(self, title, badge=None, badge_clr=None):
        self.ln(6)
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.W)
        self.cell(0, 8, _s(title), ln=True)
        if badge:
            c = badge_clr or self.A
            self.set_fill_color(*c)
            bw = self.get_string_width(_s(badge)) + 10
            self.set_xy(196 - bw, y0)
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(255, 255, 255)
            self.cell(bw, 7, _s(badge), fill=True, align="C")
        self.set_draw_color(*self.A)
        self.line(14, self.get_y() + 2, 196, self.get_y() + 2)
        self.ln(6)

    def space_check(self, min_y=200):
        if self.get_y() > min_y:
            self.add_page()

    def text_cell(self, txt, font_style="", size=10, color=None, ln=True, align="L"):
        """Simple safe text cell — always full width, always starts at left margin."""
        self.set_x(self.l_margin)
        self.set_font("Helvetica", font_style, size)
        if color:
            self.set_text_color(*color)
        self.cell(0, max(size * 0.6, 5), _s(txt), ln=ln, align=align)

    def text_block(self, txt, font_style="", size=9, color=None):
        """Safe multi_cell — always full width, always starts at left margin."""
        self.set_x(self.l_margin)
        self.set_font("Helvetica", font_style, size)
        if color:
            self.set_text_color(*color)
        self.multi_cell(0, max(size * 0.5, 4), _s(txt))


def generate_pdf_report(data: dict) -> bytes:
    """Build and return a complete PDF report as bytes."""
    pdf = _PDF()
    pdf.set_margins(14, 14, 14)

    doc  = data.get("document", {})
    sc   = data.get("score", {})
    expl = data.get("explanations", {})
    clr  = _hex(sc.get("color", "#6c63ff"))

    # ══ PAGE 1: COVER ══
    pdf.add_page()
    pdf.ln(35)
    pdf.text_cell("AI-POWERED ANALYSIS ENGINE", "B", 9, _PDF.A, align="C")
    pdf.ln(4)
    pdf.text_cell("Document Compliance", "B", 28, _PDF.W, align="C")
    pdf.text_cell("& Risk Report", "B", 28, _PDF.W, align="C")
    pdf.ln(6)
    pdf.text_cell(f"Document: {doc.get('filename','Unknown')}", "", 11, _PDF.M, align="C")
    pdf.text_cell(f"Analyzed: {datetime.now():%B %d, %Y at %I:%M %p}", "", 11, _PDF.M, align="C")
    pdf.ln(10)

    # Big score
    pdf.set_font("Helvetica", "B", 56)
    pdf.set_text_color(*clr)
    pdf.cell(0, 24, _s(str(sc.get("score", 0))), align="C", ln=True)
    pdf.text_cell("OUT OF 100", "", 10, _PDF.M, align="C")
    pdf.ln(4)
    pdf.text_cell(f"{sc.get('grade','')} - {sc.get('label','')}", "B", 18, clr, align="C")
    pdf.ln(4)

    narrative = expl.get("overall_assessment", {}).get("narrative", "")
    if narrative:
        pdf.text_block(narrative, "", 10, _PDF.M)
    pdf.ln(8)

    # Stats row
    stats = [("Words", doc.get("word_count", 0)),
             ("Sentences", doc.get("sentence_count", 0)),
             ("Paragraphs", doc.get("paragraph_count", 0)),
             ("Sections", doc.get("section_count", 0))]
    if doc.get("page_count"):
        stats.append(("Pages", doc["page_count"]))
    cw = 180 // max(len(stats), 1)
    sx = 15
    for lbl, val in stats:
        y0 = pdf.get_y()
        pdf.set_fill_color(*_PDF.CARD)
        pdf.rect(sx, y0, cw - 3, 18, "F")
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*_PDF.B)
        pdf.set_xy(sx, y0 + 2)
        pdf.cell(cw - 3, 7, _s(str(val)), align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*_PDF.M)
        pdf.set_xy(sx, y0 + 9)
        pdf.cell(cw - 3, 5, lbl.upper(), align="C")
        sx += cw
    pdf.set_xy(14, pdf.get_y() + 22)

    # ══ PAGE 2: BREAKDOWN ══
    pdf.add_page()
    pdf.heading("Score Breakdown")
    bd = sc.get("breakdown", {})
    for lbl, key, c in [("Clause Coverage", "clause_coverage", _PDF.A),
                        ("Risk Safety", "risk_density", _PDF.G),
                        ("Structure", "structure", _PDF.B),
                        ("Language Clarity", "clarity", _PDF.O)]:
        b = bd.get(key, {})
        s_val, mx = b.get("score", 0), b.get("max", 1)
        pct = int((s_val / mx) * 100) if mx else 0

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*_PDF.W)
        pdf.cell(90, 6, _s(lbl))
        pdf.set_text_color(*c)
        pdf.cell(0, 6, _s(f"{s_val} / {mx}"), ln=True)

        bar_y = pdf.get_y()
        pdf.set_fill_color(40, 42, 70)
        pdf.rect(14, bar_y, 182, 4, "F")
        if pct > 0:
            pdf.set_fill_color(*c)
            pdf.rect(14, bar_y, max(4, int(182 * pct / 100)), 4, "F")
        pdf.set_y(bar_y + 6)

        pdf.text_cell(b.get("details", ""), "", 8, _PDF.M)
        pdf.ln(4)

    # Critical findings
    critical = expl.get("critical_findings", [])
    if critical:
        pdf.heading("Critical Findings", f"{len(critical)} FOUND", _PDF.R)
        for f in critical:
            pdf.text_cell(f"[!] {f.get('title','')}", "B", 10, _PDF.R)
            pdf.text_block(f.get("explanation", ""), "", 9, _PDF.M)
            ev = f.get("evidence", "")
            if ev:
                pdf.text_block(f'"{ev[:120]}"', "I", 8, _PDF.M)
            pdf.ln(3)

    # ══ PAGE 3: CLAUSES ══
    pdf.add_page()
    clauses = data.get("clauses", {})
    cs = clauses.get("summary", {})
    pdf.heading("Clause Detection", f"{cs.get('found_count',0)}/{cs.get('total_clauses',0)}", _PDF.A)

    for _, c in clauses.get("detected", {}).items():
        found = c.get("found", False)
        fc = _PDF.G if found else _PDF.R
        mark = "[Y]" if found else "[X]"
        conf = f"{c.get('confidence',0)}% confidence" if found else "MISSING"

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*fc)
        pdf.cell(10, 6, _s(mark))
        pdf.set_text_color(*_PDF.W)
        pdf.cell(90, 6, _s(c.get("label", "")))
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*fc)
        pdf.cell(0, 6, _s(conf), ln=True)
        pdf.text_cell(c.get("description", ""), "", 8, _PDF.M)
        pdf.ln(2)

    # ══ RISKS ══
    risks = data.get("risks", {})
    rs = risks.get("summary", {})
    rl = risks.get("risks", [])
    pdf.space_check(200)
    pdf.heading("Risk Alerts", f"{rs.get('total_risks',0)} RISKS", _PDF.O)

    pdf.set_font("Helvetica", "B", 9)
    for sev, cnt, c in [("HIGH", rs.get("high",0), _PDF.R),
                        ("MEDIUM", rs.get("medium",0), _PDF.O),
                        ("LOW", rs.get("low",0), _PDF.Y)]:
        pdf.set_text_color(*c)
        pdf.cell(40, 6, _s(f"{sev}: {cnt}"))
    pdf.ln(8)

    for r in rl[:15]:
        sev = r.get("severity", "MEDIUM")
        c = _PDF.R if sev == "HIGH" else (_PDF.O if sev == "MEDIUM" else _PDF.Y)
        pdf.text_cell(f"[{sev}] {r.get('category_label','')}", "B", 9, c)
        pdf.text_block(f"\"{r.get('sentence','')[:120]}\"", "I", 8, _PDF.M)
        pdf.text_block(r.get("description", ""), "", 8, _PDF.M)
        pdf.ln(2)
        pdf.space_check(260)

    # ══ ACTIONS ══
    actions = expl.get("action_items", [])
    if actions:
        pdf.space_check()
        pdf.heading("Recommended Actions", f"{len(actions)} ITEMS", _PDF.G)
        for i, a in enumerate(actions, 1):
            sev = a.get("severity", "MEDIUM")
            c = _PDF.R if sev == "HIGH" else (_PDF.O if sev == "MEDIUM" else _PDF.Y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*c)
            pdf.cell(8, 6, str(i))
            pdf.set_text_color(*_PDF.W)
            pdf.cell(0, 6, _s(a.get("action", "")), ln=True)
            pdf.text_block(a.get("detail", ""), "", 8, _PDF.M)
            pdf.ln(2)
            pdf.space_check(260)

    # ══ REWRITES ══
    rewrites = data.get("rewrites", [])
    if rewrites:
        pdf.space_check(180)
        pdf.heading("Suggested Rewrites", str(len(rewrites)), _PDF.A)
        for rw in rewrites[:10]:
            pdf.text_cell("ORIGINAL:", "", 8, _PDF.R)
            pdf.text_block(rw.get("original", "")[:150], "", 8, _PDF.M)
            pdf.ln(1)
            pdf.text_cell("IMPROVED:", "", 8, _PDF.G)
            pdf.text_block(rw.get("rewritten", "")[:150], "", 8, _PDF.W)
            pdf.ln(3)
            pdf.space_check(260)

    return pdf.output()


def _hex(h: str):
    h = h.lstrip("#")
    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (108, 99, 255)

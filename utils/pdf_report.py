"""
PDF Compliance Report Generator
Creates professional PDF reports from analysis results.
Uses fpdf2 for PDF generation.
"""

from fpdf import FPDF
from datetime import datetime
import os


class ComplianceReportPDF(FPDF):
    """Custom PDF class for compliance reports."""

    DARK_BG = (15, 16, 41)
    CARD_BG = (22, 24, 55)
    WHITE = (232, 234, 237)
    MUTED = (154, 160, 181)
    ACCENT = (108, 99, 255)
    GREEN = (0, 230, 118)
    RED = (255, 82, 82)
    ORANGE = (255, 171, 64)
    YELLOW = (255, 215, 64)
    BLUE = (79, 195, 247)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_fill_color(*self.DARK_BG)
        self.rect(0, 0, 210, 297, 'F')
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(*self.MUTED)
            self.set_xy(10, 8)
            self.cell(0, 5, 'AI Document Compliance & Risk Analyzer', align='L')
            self.set_xy(10, 8)
            self.cell(0, 5, f'Page {self.page_no()}', align='R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*self.MUTED)
        self.cell(0, 10, f'Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} | AI Document Compliance & Risk Analyzer v1.0', align='C')

    def _draw_card(self, y, h):
        self.set_fill_color(*self.CARD_BG)
        self.rounded_rect(12, y, 186, h, 4, 'F')

    def _section_title(self, icon, title, badge_text=None, badge_color=None):
        self.ln(6)
        y = self.get_y()
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*self.WHITE)
        self.cell(0, 8, f'  {icon}  {title}', ln=True)
        if badge_text:
            c = badge_color or self.ACCENT
            self.set_fill_color(*c)
            w = self.get_string_width(badge_text) + 8
            self.set_xy(200 - w, y)
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(255, 255, 255)
            self.cell(w, 7, badge_text, fill=True, align='C')
        self.set_draw_color(*self.ACCENT)
        self.line(14, self.get_y() + 2, 196, self.get_y() + 2)
        self.ln(6)


def generate_pdf_report(analysis_data):
    """
    Generate a premium PDF compliance report.

    Args:
        analysis_data: Full analysis result dict from the /api/analyze endpoint.

    Returns:
        bytes: PDF file contents.
    """
    pdf = ComplianceReportPDF()
    pdf.set_margins(14, 14, 14)

    # ═══════════════ PAGE 1: COVER ═══════════════
    pdf.add_page()

    # Title block
    pdf.ln(40)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*ComplianceReportPDF.ACCENT)
    pdf.cell(0, 6, 'AI-POWERED ANALYSIS ENGINE', align='C', ln=True)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(*ComplianceReportPDF.WHITE)
    pdf.cell(0, 14, 'Document Compliance', align='C', ln=True)
    pdf.cell(0, 14, '& Risk Report', align='C', ln=True)
    pdf.ln(6)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(*ComplianceReportPDF.MUTED)
    doc = analysis_data.get('document', {})
    pdf.cell(0, 6, f'Document: {doc.get("filename", "Unknown")}', align='C', ln=True)
    pdf.cell(0, 6, f'Analyzed: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', align='C', ln=True)
    pdf.ln(10)

    # Score circle area
    score_data = analysis_data.get('score', {})
    score_val = score_data.get('score', 0)
    grade = score_data.get('grade', 'N/A')
    label = score_data.get('label', '')
    color_hex = score_data.get('color', '#6c63ff')

    sc = _hex_to_rgb(color_hex)

    # Score display
    pdf.set_font('Helvetica', 'B', 56)
    pdf.set_text_color(*sc)
    pdf.cell(0, 24, str(score_val), align='C', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*ComplianceReportPDF.MUTED)
    pdf.cell(0, 5, 'OUT OF 100', align='C', ln=True)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*sc)
    pdf.cell(0, 10, f'{grade} - {label}', align='C', ln=True)
    pdf.ln(4)

    # Overall assessment
    expl = analysis_data.get('explanations', {})
    overall = expl.get('overall_assessment', {})
    narrative = overall.get('narrative', '')
    if narrative:
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*ComplianceReportPDF.MUTED)
        pdf.multi_cell(0, 5, narrative, align='C')

    pdf.ln(10)

    # Document stats bar
    stats = [
        ('Words', doc.get('word_count', 0)),
        ('Sentences', doc.get('sentence_count', 0)),
        ('Paragraphs', doc.get('paragraph_count', 0)),
        ('Sections', doc.get('section_count', 0)),
    ]
    if doc.get('page_count'):
        stats.append(('Pages', doc['page_count']))

    col_w = 182 / len(stats)
    pdf.set_x(14)
    for lbl, val in stats:
        pdf.set_fill_color(*ComplianceReportPDF.CARD_BG)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*ComplianceReportPDF.BLUE)
        x0 = pdf.get_x()
        y0 = pdf.get_y()
        pdf.rounded_rect(x0, y0, col_w - 2, 18, 3, 'F')
        pdf.set_xy(x0, y0 + 2)
        pdf.cell(col_w - 2, 7, str(val), align='C', ln=False)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*ComplianceReportPDF.MUTED)
        pdf.set_xy(x0, y0 + 9)
        pdf.cell(col_w - 2, 5, lbl.upper(), align='C', ln=False)
        pdf.set_xy(x0 + col_w, y0)

    # ═══════════════ PAGE 2: SCORE BREAKDOWN + CRITICAL ═══════════════
    pdf.add_page()

    # Score breakdown
    pdf._section_title('SCORE', 'Score Breakdown')
    breakdown = score_data.get('breakdown', {})
    items = [
        ('Clause Coverage', 'clause_coverage', ComplianceReportPDF.ACCENT),
        ('Risk Safety', 'risk_density', ComplianceReportPDF.GREEN),
        ('Structure', 'structure', ComplianceReportPDF.BLUE),
        ('Language Clarity', 'clarity', ComplianceReportPDF.ORANGE),
    ]
    for lbl, key, clr in items:
        b = breakdown.get(key, {})
        s = b.get('score', 0)
        m = b.get('max', 1)
        det = b.get('details', '')
        pct = int((s / m) * 100) if m else 0

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*ComplianceReportPDF.WHITE)
        pdf.cell(90, 6, f'  {lbl}', ln=False)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*clr)
        pdf.cell(0, 6, f'{s} / {m}', ln=True)

        # Progress bar
        bar_y = pdf.get_y()
        pdf.set_fill_color(40, 42, 70)
        pdf.rounded_rect(14, bar_y, 182, 4, 2, 'F')
        if pct > 0:
            pdf.set_fill_color(*clr)
            fill_w = max(4, int(182 * pct / 100))
            pdf.rounded_rect(14, bar_y, fill_w, 4, 2, 'F')

        pdf.ln(6)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*ComplianceReportPDF.MUTED)
        pdf.cell(0, 4, f'  {det}', ln=True)
        pdf.ln(4)

    # Critical findings
    critical = expl.get('critical_findings', [])
    if critical:
        pdf._section_title('!!', 'Critical Findings', f'{len(critical)} FOUND', ComplianceReportPDF.RED)
        for f in critical:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(*ComplianceReportPDF.RED)
            pdf.cell(0, 6, f'  {f.get("icon", "!")} {f.get("title", "")}', ln=True)
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(*ComplianceReportPDF.MUTED)
            pdf.multi_cell(0, 5, f'    {f.get("explanation", "")}')
            ev = f.get('evidence', '')
            if ev:
                pdf.set_font('Helvetica', 'I', 8)
                pdf.multi_cell(0, 4, f'    "{ev}"')
            pdf.ln(3)

    # ═══════════════ PAGE 3: CLAUSES ═══════════════
    pdf.add_page()
    clauses = analysis_data.get('clauses', {})
    c_summary = clauses.get('summary', {})
    detected = clauses.get('detected', {})

    pdf._section_title('CLAUSES', 'Clause Detection',
                       f'{c_summary.get("found_count", 0)}/{c_summary.get("total_clauses", 0)}',
                       ComplianceReportPDF.ACCENT)

    for cid, c in detected.items():
        found = c.get('found', False)
        icon = 'Y' if found else 'X'
        clr = ComplianceReportPDF.GREEN if found else ComplianceReportPDF.RED

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*clr)
        pdf.cell(6, 6, icon, ln=False)
        pdf.set_text_color(*ComplianceReportPDF.WHITE)
        pdf.cell(80, 6, f' {c.get("label", "")}', ln=False)

        if found:
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*ComplianceReportPDF.GREEN)
            pdf.cell(0, 6, f'{c.get("confidence", 0)}% confidence', ln=True)
        else:
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*ComplianceReportPDF.RED)
            pdf.cell(0, 6, 'MISSING', ln=True)

        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*ComplianceReportPDF.MUTED)
        pdf.cell(0, 4, f'    {c.get("description", "")}', ln=True)
        pdf.ln(2)

    # ═══════════════ RISKS ═══════════════
    risks = analysis_data.get('risks', {})
    r_summary = risks.get('summary', {})
    risk_list = risks.get('risks', [])

    pdf._section_title('RISKS', 'Risk Alerts',
                       f'{r_summary.get("total_risks", 0)} RISKS',
                       ComplianceReportPDF.ORANGE)

    # Summary badges
    pdf.set_font('Helvetica', 'B', 9)
    for sev, cnt, clr in [('HIGH', r_summary.get('high', 0), ComplianceReportPDF.RED),
                          ('MEDIUM', r_summary.get('medium', 0), ComplianceReportPDF.ORANGE),
                          ('LOW', r_summary.get('low', 0), ComplianceReportPDF.YELLOW)]:
        pdf.set_text_color(*clr)
        pdf.cell(40, 6, f'  {sev}: {cnt}', ln=False)
    pdf.ln(8)

    for r in risk_list[:15]:
        sev = r.get('severity', 'MEDIUM')
        if sev == 'HIGH':
            clr = ComplianceReportPDF.RED
        elif sev == 'MEDIUM':
            clr = ComplianceReportPDF.ORANGE
        else:
            clr = ComplianceReportPDF.YELLOW

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*clr)
        pdf.cell(0, 5, f'  [{sev}] {r.get("category_label", "")}', ln=True)

        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(*ComplianceReportPDF.MUTED)
        sentence = r.get('sentence', '')[:120]
        pdf.multi_cell(0, 4, f'    "{sentence}"')

        pdf.set_font('Helvetica', '', 8)
        pdf.multi_cell(0, 4, f'    {r.get("description", "")}')
        pdf.ln(2)

        if pdf.get_y() > 260:
            pdf.add_page()

    # ═══════════════ ACTIONS ═══════════════
    actions = expl.get('action_items', [])
    if actions:
        if pdf.get_y() > 200:
            pdf.add_page()
        pdf._section_title('ACTIONS', 'Recommended Actions',
                           f'{len(actions)} ITEMS', ComplianceReportPDF.GREEN)
        for i, a in enumerate(actions, 1):
            sev = a.get('severity', 'MEDIUM')
            clr = ComplianceReportPDF.RED if sev == 'HIGH' else (
                ComplianceReportPDF.ORANGE if sev == 'MEDIUM' else ComplianceReportPDF.YELLOW)

            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(*clr)
            pdf.cell(8, 6, str(i), ln=False)
            pdf.set_text_color(*ComplianceReportPDF.WHITE)
            pdf.cell(0, 6, f' {a.get("action", "")}', ln=True)
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*ComplianceReportPDF.MUTED)
            pdf.multi_cell(0, 4, f'    {a.get("detail", "")}')
            pdf.ln(2)

            if pdf.get_y() > 260:
                pdf.add_page()

    # ═══════════════ REWRITES ═══════════════
    rewrites = analysis_data.get('rewrites', [])
    if rewrites:
        if pdf.get_y() > 180:
            pdf.add_page()
        pdf._section_title('REWRITES', 'Suggested Rewrites', f'{len(rewrites)}', ComplianceReportPDF.ACCENT)
        for rw in rewrites[:10]:
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*ComplianceReportPDF.RED)
            pdf.cell(0, 4, '  ORIGINAL:', ln=True)
            pdf.set_text_color(*ComplianceReportPDF.MUTED)
            pdf.multi_cell(0, 4, f'    {rw.get("original", "")[:150]}')
            pdf.ln(1)
            pdf.set_text_color(*ComplianceReportPDF.GREEN)
            pdf.cell(0, 4, '  IMPROVED:', ln=True)
            pdf.set_text_color(*ComplianceReportPDF.WHITE)
            pdf.multi_cell(0, 4, f'    {rw.get("rewritten", "")[:150]}')
            pdf.ln(3)

            if pdf.get_y() > 260:
                pdf.add_page()

    return pdf.output()


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    try:
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (108, 99, 255)

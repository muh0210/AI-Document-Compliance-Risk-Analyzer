"""
Risk Detection Engine
Identifies 7 categories of document risk via pattern matching and structural analysis.
Each risk is classified as HIGH / MEDIUM / LOW severity.
"""

import re
from datetime import datetime

# ── Risk pattern definitions ─────────────────────────────

VAGUE_PATTERNS = [
    (r"\bapproximately\b", "Imprecise quantities create ambiguity"),
    (r"\breasonabl[ey]\b", "Subjective standard open to interpretation"),
    (r"\bgenerally\b", "Vague qualifier weakens obligation"),
    (r"\bmay\b(?!\s+not)", "Permissive language creates uncertainty"),
    (r"\bmight\b", "Speculative language weakens commitment"),
    (r"\bcould\b", "Ambiguous possibility language"),
    (r"\bshould\b(?!\s+not)", "Non-binding suggestion instead of obligation"),
    (r"\bprobably\b", "Lacks definite commitment"),
    (r"\bas\s+(?:needed|appropriate|necessary)\b", "Open-ended condition"),
    (r"\bfrom\s+time\s+to\s+time\b", "Undefined frequency"),
    (r"\bto\s+be\s+determined\b", "Unresolved term is a risk"),
    (r"\bat\s+(?:its|their|our)\s+(?:sole\s+)?discretion\b", "One-sided discretionary power"),
    (r"\bendeavou?r\b", "Best-effort, not binding commitment"),
    (r"\btry\b", "Non-binding effort language"),
]

OBLIGATION_PATTERNS = [
    (r"\bsolely\s+responsible\b", "One-sided responsibility allocation"),
    (r"\bbear\s+(?:all|full)\s+responsibilit", "Unlimited responsibility burden"),
    (r"\bwithout\s+(?:any\s+)?limit", "Uncapped obligation or liability"),
    (r"\bat\s+(?:its|their|our)\s+own\s+(?:cost|expense|risk)\b", "Risk/cost shifting to one party"),
    (r"\bfull\s+(?:and\s+complete\s+)?responsibilit", "Broad responsibility clause"),
]

LIABILITY_PATTERNS = [
    (r"\bunlimited\s+liabilit", "Uncapped financial exposure"),
    (r"\bno\s+(?:limit|cap)\s+(?:on|to)\b", "Absence of liability cap"),
    (r"\bwholly\s+liable\b", "Total liability on one party"),
]

UNILATERAL_PATTERNS = [
    (r"\breserves\s+the\s+right\b", "Unilateral power to act"),
    (r"\bmodify.*without\s+(?:prior\s+)?notice\b", "Changes without notification"),
    (r"\bsole\s+(?:and\s+absolute\s+)?discretion\b", "One-sided decision power"),
    (r"\bwithout\s+(?:prior\s+)?(?:written\s+)?consent\b", "No consent required"),
    (r"\bdeems?\s+appropriate\b", "Subjective standard for decisions"),
]

AUTO_RENEWAL_PATTERNS = [
    (r"\bauto[\s-]?renew", "Automatic contract extension"),
    (r"\bautomatically\s+(?:renew|extend)", "Silent renewal clause"),
    (r"\bindefinitely\b", "No defined end date"),
    (r"\bin\s+perpetuity\b", "Perpetual obligation"),
]


def detect_risks(sentences: list, full_text: str) -> dict:
    """
    Scan sentences for risk indicators across 7 categories.

    Returns dict with 'risks' list and 'summary' counts.
    """
    risks = []

    # 1 - Vague Language
    for sent in sentences:
        for pattern, desc in VAGUE_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                risks.append(_risk(
                    "vague_language", "Vague Language", "diamond_with_a_dot",
                    "MEDIUM", sent, m.group(), desc))

    # 2 - Ambiguous Obligations
    for sent in sentences:
        for pattern, desc in OBLIGATION_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                risks.append(_risk(
                    "ambiguous_obligation", "Ambiguous Obligation", "warning",
                    "HIGH", sent, m.group(), desc))

    # 3 - Liability Exposure
    for sent in sentences:
        for pattern, desc in LIABILITY_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                risks.append(_risk(
                    "liability_exposure", "Liability Exposure", "scales",
                    "HIGH", sent, m.group(), desc))

    # 4 - Unilateral Terms
    for sent in sentences:
        for pattern, desc in UNILATERAL_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                risks.append(_risk(
                    "unilateral_terms", "Unilateral Terms", "lock",
                    "HIGH", sent, m.group(), desc))

    # 5 - Auto-renewal / Perpetuity
    for sent in sentences:
        for pattern, desc in AUTO_RENEWAL_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                risks.append(_risk(
                    "auto_renewal", "Auto-Renewal / Perpetuity", "refresh",
                    "MEDIUM", sent, m.group(), desc))

    # 6 - Deadline / Timeline Risk
    date_pattern = re.compile(
        r"\b(?:january|february|march|april|may|june|july|august|september|"
        r"october|november|december)\s+\d{1,2}", re.IGNORECASE)
    numeric_date = re.compile(r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b")
    has_dates = bool(date_pattern.search(full_text)) or bool(numeric_date.search(full_text))
    if not has_dates:
        risks.append(_risk(
            "deadline_risk", "Deadline & Timeline Risk", "clock",
            "MEDIUM", "No specific dates found in document", "",
            "Documents without specific dates lack concrete timelines"))

    # 7 - Missing Signature / Execution
    sig_patterns = [r"\bsigned?\b", r"\bsignature\b", r"\bexecut", r"\bwitness\s+whereof\b"]
    has_sig = any(re.search(p, full_text, re.IGNORECASE) for p in sig_patterns)
    if not has_sig:
        risks.append(_risk(
            "missing_signature", "Missing Execution / Signature", "pen",
            "LOW", "No signature or execution clause detected", "",
            "Unsigned documents may not be legally binding"))

    # De-duplicate (same sentence + same category)
    seen = set()
    unique = []
    for r in risks:
        key = (r["category"], r["sentence"][:60])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort by severity
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    unique.sort(key=lambda r: order.get(r["severity"], 9))

    h = sum(1 for r in unique if r["severity"] == "HIGH")
    m = sum(1 for r in unique if r["severity"] == "MEDIUM")
    lo = sum(1 for r in unique if r["severity"] == "LOW")

    return {
        "risks": unique,
        "summary": {
            "total_risks": len(unique),
            "high": h, "medium": m, "low": lo,
            "risk_density": round(len(unique) / max(len(sentences), 1), 2),
        },
    }


# ── Icons (plain text for PDF safety) ────────────────────

_ICONS = {
    "diamond_with_a_dot": "[!]",
    "warning": "[!!]",
    "scales": "[=]",
    "lock": "[#]",
    "refresh": "[~]",
    "clock": "[T]",
    "pen": "[S]",
}


def _risk(cat, label, icon_key, severity, sentence, trigger, desc):
    return {
        "category": cat,
        "category_label": label,
        "icon": _ICONS.get(icon_key, "[!]"),
        "severity": severity,
        "sentence": sentence[:200],
        "trigger": trigger,
        "description": desc,
    }

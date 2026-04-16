"""
Risk Detection Engine v2.0
Single-pass architecture: iterates sentences once, checking all patterns.
All regex patterns compiled at module load for performance.
"""

import re
import logging

log = logging.getLogger("compliance.risk")

# ── Pattern registry (compiled once) ─────────────────────

_RULES = []


def _register(category, label, severity, patterns_with_desc):
    """Register a risk category with its compiled patterns."""
    for pattern_str, desc in patterns_with_desc:
        _RULES.append({
            "category": category,
            "label": label,
            "severity": severity,
            "pattern": re.compile(pattern_str, re.IGNORECASE),
            "description": desc,
        })


# Category 1: Vague Language (MEDIUM)
_register("vague_language", "Vague Language", "MEDIUM", [
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
    (r"\bto\s+be\s+determined\b", "Unresolved term"),
    (r"\bat\s+(?:its|their|our)\s+(?:sole\s+)?discretion\b", "One-sided discretionary power"),
    (r"\bendeavou?r\b", "Best-effort, not binding"),
])

# Category 2: Ambiguous Obligations (HIGH)
_register("ambiguous_obligation", "Ambiguous Obligation", "HIGH", [
    (r"\bsolely\s+responsible\b", "One-sided responsibility allocation"),
    (r"\bbear\s+(?:all|full)\s+responsibilit", "Unlimited responsibility burden"),
    (r"\bwithout\s+(?:any\s+)?limit", "Uncapped obligation or liability"),
    (r"\bat\s+(?:its|their|our)\s+own\s+(?:cost|expense|risk)\b", "Risk/cost shifting"),
    (r"\bfull\s+(?:and\s+complete\s+)?responsibilit", "Broad responsibility clause"),
])

# Category 3: Liability Exposure (HIGH)
_register("liability_exposure", "Liability Exposure", "HIGH", [
    (r"\bunlimited\s+liabilit", "Uncapped financial exposure"),
    (r"\bno\s+(?:limit|cap)\s+(?:on|to)\b", "Absence of liability cap"),
    (r"\bwholly\s+liable\b", "Total liability on one party"),
])

# Category 4: Unilateral Terms (HIGH)
_register("unilateral_terms", "Unilateral Terms", "HIGH", [
    (r"\breserves\s+the\s+right\b", "Unilateral power to act"),
    (r"\bmodify.*without\s+(?:prior\s+)?notice\b", "Changes without notification"),
    (r"\bsole\s+(?:and\s+absolute\s+)?discretion\b", "One-sided decision power"),
    (r"\bwithout\s+(?:prior\s+)?(?:written\s+)?consent\b", "No consent required"),
])

# Category 5: Auto-renewal (MEDIUM)
_register("auto_renewal", "Auto-Renewal / Perpetuity", "MEDIUM", [
    (r"\bauto[\s-]?renew", "Automatic contract extension"),
    (r"\bautomatically\s+(?:renew|extend)", "Silent renewal clause"),
    (r"\bindefinitely\b", "No defined end date"),
    (r"\bin\s+perpetuity\b", "Perpetual obligation"),
])


# ── Single-pass engine ───────────────────────────────────

def detect_risks(sentences: list, full_text: str) -> dict:
    """
    Single-pass risk scan: iterate sentences ONCE, test ALL patterns.
    O(sentences * total_patterns) but only one loop over sentences.
    """
    risks = []
    seen = set()

    # PASS 1: pattern-based risks (single loop)
    for sent in sentences:
        for rule in _RULES:
            m = rule["pattern"].search(sent)
            if m:
                key = (rule["category"], sent[:60])
                if key not in seen:
                    seen.add(key)
                    risks.append({
                        "category": rule["category"],
                        "category_label": rule["label"],
                        "severity": rule["severity"],
                        "sentence": sent[:200],
                        "trigger": m.group(),
                        "description": rule["description"],
                    })

    # PASS 2: structural checks (full text)
    _check_dates(full_text, risks)
    _check_signatures(full_text, risks)

    # Sort: HIGH → MEDIUM → LOW
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    risks.sort(key=lambda r: order.get(r["severity"], 9))

    h = sum(1 for r in risks if r["severity"] == "HIGH")
    m = sum(1 for r in risks if r["severity"] == "MEDIUM")
    lo = sum(1 for r in risks if r["severity"] == "LOW")

    log.info("Detected %d risks (H:%d M:%d L:%d)", len(risks), h, m, lo)

    return {
        "risks": risks,
        "summary": {
            "total_risks": len(risks),
            "high": h, "medium": m, "low": lo,
            "risk_density": round(len(risks) / max(len(sentences), 1), 2),
        },
    }


_DATE_PAT = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\s+\d{1,2}", re.IGNORECASE)
_NUM_DATE = re.compile(r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b")
_SIG_PATS = [re.compile(p, re.IGNORECASE) for p in
             [r"\bsigned?\b", r"\bsignature\b", r"\bexecut", r"\bwitness\s+whereof\b"]]


def _check_dates(text, risks):
    if not _DATE_PAT.search(text) and not _NUM_DATE.search(text):
        risks.append({
            "category": "deadline_risk", "category_label": "Deadline & Timeline Risk",
            "severity": "MEDIUM", "sentence": "No specific dates found",
            "trigger": "", "description": "Documents without dates lack concrete timelines",
        })


def _check_signatures(text, risks):
    if not any(p.search(text) for p in _SIG_PATS):
        risks.append({
            "category": "missing_signature", "category_label": "Missing Execution / Signature",
            "severity": "LOW", "sentence": "No signature clause detected",
            "trigger": "", "description": "Unsigned documents may not be legally binding",
        })

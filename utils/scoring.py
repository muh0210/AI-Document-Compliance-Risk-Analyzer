"""
Compliance Scoring Engine v2.0
Adaptive weights based on document type.
"""

import logging

log = logging.getLogger("compliance.scoring")

# ── Document-type weight profiles ────────────────────────

_WEIGHTS = {
    "contract":   {"clause": 45, "risk": 25, "structure": 15, "clarity": 15},
    "nda":        {"clause": 50, "risk": 25, "structure": 10, "clarity": 15},
    "sla":        {"clause": 35, "risk": 25, "structure": 25, "clarity": 15},
    "employment": {"clause": 40, "risk": 30, "structure": 15, "clarity": 15},
    "freelance":  {"clause": 45, "risk": 25, "structure": 15, "clarity": 15},
    "policy":     {"clause": 30, "risk": 20, "structure": 30, "clarity": 20},
    "general":    {"clause": 40, "risk": 30, "structure": 20, "clarity": 10},
}


def compliance_score(clauses: dict, risks: dict, cleaned: dict,
                     doc_type: str = "general") -> dict:
    """
    Calculate overall compliance score with adaptive weights.
    """
    w = _WEIGHTS.get(doc_type, _WEIGHTS["general"])

    # 1. Clause coverage
    cs = clauses["summary"]
    coverage_pct = cs["found_count"] / max(cs["total_clauses"], 1)
    clause_score = round(coverage_pct * w["clause"])
    clause_details = f'{cs["found_count"]}/{cs["total_clauses"]} clauses detected'

    # 2. Risk density (fewer risks = higher score)
    rs = risks["summary"]
    penalty = rs["high"] * 6 + rs["medium"] * 3 + rs["low"] * 1
    risk_score = max(0, w["risk"] - penalty)
    risk_details = f'{rs["high"]} high, {rs["medium"]} medium, {rs["low"]} low risks'

    # 3. Structure
    sents = len(cleaned.get("sentences", []))
    paras = len(cleaned.get("paragraphs", []))
    heads = len(cleaned.get("section_headers", []))
    struct_pts = 0
    if sents >= 5:  struct_pts += 5
    if paras >= 3:  struct_pts += 5
    if heads >= 2:  struct_pts += 5
    if sents >= 10 and paras >= 5: struct_pts += 5
    struct_score = min(w["structure"], struct_pts)
    struct_details = f'{sents} sentences, {paras} paragraphs, {heads} sections'

    # 4. Clarity
    vague = sum(1 for r in risks.get("risks", []) if r["category"] == "vague_language")
    clarity_score = max(0, w["clarity"] - vague)
    clarity_details = f'{vague} vague language instances'

    total = max(0, min(100, clause_score + risk_score + struct_score + clarity_score))
    grade, label, color = _grade(total)

    log.info("Score: %d (%s) [clause=%d/%d risk=%d/%d struct=%d/%d clarity=%d/%d] type=%s",
             total, grade, clause_score, w["clause"], risk_score, w["risk"],
             struct_score, w["structure"], clarity_score, w["clarity"], doc_type)

    return {
        "score": total,
        "grade": grade,
        "label": label,
        "color": color,
        "document_type": doc_type,
        "weights_used": w,
        "breakdown": {
            "clause_coverage": {"score": clause_score, "max": w["clause"], "details": clause_details},
            "risk_density":    {"score": risk_score,   "max": w["risk"],   "details": risk_details},
            "structure":       {"score": struct_score,  "max": w["structure"], "details": struct_details},
            "clarity":         {"score": clarity_score, "max": w["clarity"],   "details": clarity_details},
        },
    }


def _grade(score: int):
    if score >= 90: return "A+", "Excellent Compliance", "#00e676"
    if score >= 80: return "A",  "Strong Compliance", "#00e676"
    if score >= 70: return "B+", "Good Compliance", "#69f0ae"
    if score >= 60: return "B",  "Adequate Compliance", "#4fc3f7"
    if score >= 50: return "C",  "Needs Improvement", "#ffab40"
    if score >= 40: return "D",  "High Risk", "#ff9100"
    if score >= 30: return "D-", "Critical Deficiencies", "#ff5252"
    return "F", "Non-Compliant", "#d50000"

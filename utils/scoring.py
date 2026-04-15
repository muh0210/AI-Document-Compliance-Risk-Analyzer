"""
Compliance Scoring Engine
Calculates a weighted compliance score (0-100) based on:
  - Clause coverage     40%
  - Risk density         30%
  - Document structure   20%
  - Language clarity     10%
"""


def compliance_score(clauses: dict, risks: dict, cleaned: dict) -> dict:
    """
    Calculate overall compliance score.

    Returns dict with score, grade, label, color, and per-component breakdown.
    """
    # ── Component scores ──

    # 1. Clause coverage (0-40)
    cs = clauses["summary"]
    coverage_pct = cs["found_count"] / max(cs["total_clauses"], 1)
    clause_score = round(coverage_pct * 40)
    clause_details = f'{cs["found_count"]}/{cs["total_clauses"]} clauses detected'

    # 2. Risk density (0-30) — fewer risks = higher score
    rs = risks["summary"]
    penalty = rs["high"] * 6 + rs["medium"] * 3 + rs["low"] * 1
    risk_score = max(0, 30 - penalty)
    risk_details = f'{rs["high"]} high, {rs["medium"]} medium, {rs["low"]} low risks'

    # 3. Structure (0-20)
    sents = len(cleaned.get("sentences", []))
    paras = len(cleaned.get("paragraphs", []))
    heads = len(cleaned.get("section_headers", []))
    struct_pts = 0
    if sents >= 5:
        struct_pts += 5
    if paras >= 3:
        struct_pts += 5
    if heads >= 2:
        struct_pts += 5
    if sents >= 10 and paras >= 5:
        struct_pts += 5
    struct_score = min(20, struct_pts)
    struct_details = f'{sents} sentences, {paras} paragraphs, {heads} sections'

    # 4. Clarity (0-10)
    vague_count = sum(1 for r in risks.get("risks", []) if r["category"] == "vague_language")
    clarity_score = max(0, 10 - vague_count)
    clarity_details = f'{vague_count} vague language instances found'

    total = clause_score + risk_score + struct_score + clarity_score
    total = max(0, min(100, total))

    grade, label, color = _grade(total)

    return {
        "score": total,
        "grade": grade,
        "label": label,
        "color": color,
        "breakdown": {
            "clause_coverage": {"score": clause_score, "max": 40, "details": clause_details},
            "risk_density": {"score": risk_score, "max": 30, "details": risk_details},
            "structure": {"score": struct_score, "max": 20, "details": struct_details},
            "clarity": {"score": clarity_score, "max": 10, "details": clarity_details},
        },
    }


def _grade(score: int):
    """Map numeric score to letter grade, label, and colour."""
    if score >= 90:
        return "A+", "Excellent Compliance", "#00e676"
    if score >= 80:
        return "A", "Strong Compliance", "#00e676"
    if score >= 70:
        return "B+", "Good Compliance", "#69f0ae"
    if score >= 60:
        return "B", "Adequate Compliance", "#4fc3f7"
    if score >= 50:
        return "C", "Needs Improvement", "#ffab40"
    if score >= 40:
        return "D", "High Risk", "#ff9100"
    if score >= 30:
        return "D-", "Critical Deficiencies", "#ff5252"
    return "F", "Non-Compliant", "#d50000"

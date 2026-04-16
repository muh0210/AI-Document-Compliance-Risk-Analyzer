"""
AI Explanation Generator v2.0
Enhanced with "why score reduced" and "what happens if ignored" narratives.
"""

import logging

log = logging.getLogger("compliance.explain")

_MISSING_IMPACT = {
    "payment_terms":     {"impact": "Without clear payment terms, disputes over amounts and timing are likely.",
                          "if_ignored": "Financial disputes could arise, leading to delayed payments or legal action."},
    "termination":       {"impact": "No clear exit path -- parties may be trapped in unfavourable agreements.",
                          "if_ignored": "You may be unable to end the agreement even when it no longer serves your interests."},
    "liability":         {"impact": "Unlimited financial exposure from claims threatens business viability.",
                          "if_ignored": "A single claim could result in uncapped financial damages against your organisation."},
    "confidentiality":   {"impact": "Sensitive information may be shared without legal protection.",
                          "if_ignored": "Trade secrets and proprietary data could be disclosed to competitors."},
    "ip_rights":         {"impact": "Ownership of created work is unclear, risking future IP disputes.",
                          "if_ignored": "Work you paid for could legally belong to someone else."},
    "indemnification":   {"impact": "No protection against third-party claims or losses.",
                          "if_ignored": "Third-party lawsuits could fall entirely on your organisation."},
    "dispute_resolution":{"impact": "No defined mechanism for resolving disagreements.",
                          "if_ignored": "Conflicts default to expensive litigation instead of mediation/arbitration."},
    "governing_law":     {"impact": "Legal jurisdiction is undefined, complicating enforcement.",
                          "if_ignored": "You may be forced to litigate in an unfavourable jurisdiction."},
    "force_majeure":     {"impact": "No protection against extraordinary events.",
                          "if_ignored": "You remain obligated even during pandemics, disasters, or force majeure events."},
    "data_protection":   {"impact": "Personal data handling is unaddressed.",
                          "if_ignored": "Regulatory fines (GDPR/CCPA) and reputational damage from data breaches."},
    "warranty":          {"impact": "No quality assurance commitments are defined.",
                          "if_ignored": "Defective deliverables have no contractual remedy."},
    "non_compete":       {"impact": "No restrictions on competitive activities post-agreement.",
                          "if_ignored": "The other party could immediately compete against you using knowledge gained."},
}

_CRITICAL_IDS = {"payment_terms", "termination", "liability", "confidentiality"}


def generate_explanations(clauses: dict, risks: dict, score: dict) -> dict:
    overall = _overall(score)
    critical = _critical(clauses, risks)
    actions = _actions(clauses, risks)
    score_reasons = _score_reasons(score)

    return {
        "overall_assessment": overall,
        "critical_findings": critical,
        "action_items": actions,
        "score_reduction_reasons": score_reasons,
    }


def _overall(score: dict) -> dict:
    s = score["score"]
    g = score["grade"]
    dt = score.get("document_type", "document")
    dt_label = dt.replace("_", " ").title()

    if s >= 70:
        narrative = (
            f"This {dt_label} scores {s}/100 ({g}), indicating solid compliance. "
            "Most critical clauses are present and risks are manageable. "
            "Review the recommended actions to further strengthen the document."
        )
    elif s >= 50:
        narrative = (
            f"This {dt_label} scores {s}/100 ({g}). Several important areas need attention. "
            "Key clauses may be missing and risk indicators were detected. "
            "Address the action items below before signing."
        )
    else:
        narrative = (
            f"This {dt_label} scores {s}/100 ({g}), indicating significant compliance gaps. "
            "Multiple critical clauses are missing and high-risk language was detected. "
            "This document should not be signed without substantial revisions."
        )
    return {"narrative": narrative, "score_summary": f"{s}/100 ({g})"}


def _score_reasons(score: dict) -> list:
    """Explain WHY the score was reduced in each category."""
    reasons = []
    for key, bd in score.get("breakdown", {}).items():
        lost = bd["max"] - bd["score"]
        if lost > 0:
            reasons.append({
                "category": key,
                "points_lost": lost,
                "max_possible": bd["max"],
                "scored": bd["score"],
                "reason": f"Lost {lost} points: {bd['details']}",
            })
    return sorted(reasons, key=lambda r: r["points_lost"], reverse=True)


def _critical(clauses, risks):
    findings = []
    for cid, c in clauses["detected"].items():
        if not c["found"] and cid in _CRITICAL_IDS:
            info = _MISSING_IMPACT.get(cid, {"impact": "Missing.", "if_ignored": "Unknown consequences."})
            findings.append({
                "title": f"Missing: {c['label']}",
                "severity": "HIGH",
                "explanation": info["impact"],
                "if_ignored": info["if_ignored"],
                "evidence": c.get("evidence", ""),
            })
    for r in [r for r in risks["risks"] if r["severity"] == "HIGH"][:3]:
        findings.append({
            "title": r["category_label"],
            "severity": "HIGH",
            "explanation": r["description"],
            "if_ignored": "Continued exposure to this risk could result in legal or financial consequences.",
            "evidence": r["sentence"][:120],
        })
    return findings


def _actions(clauses, risks):
    items = []
    for cid in list(_CRITICAL_IDS) + [k for k in clauses["detected"] if k not in _CRITICAL_IDS]:
        c = clauses["detected"][cid]
        if not c["found"]:
            sev = "HIGH" if cid in _CRITICAL_IDS else "MEDIUM"
            info = _MISSING_IMPACT.get(cid, {"impact": c["description"], "if_ignored": ""})
            items.append({
                "action": f"{'Add' if sev=='HIGH' else 'Consider adding'} {c['label']}",
                "detail": info["impact"],
                "if_ignored": info.get("if_ignored", ""),
                "severity": sev,
            })
    seen = set()
    for r in risks["risks"]:
        if r["category"] not in seen and r["severity"] == "HIGH":
            seen.add(r["category"])
            items.append({
                "action": f"Review: {r['category_label']}",
                "detail": r["description"],
                "if_ignored": "This risk could lead to unfavourable legal outcomes.",
                "severity": "HIGH",
            })
    return items

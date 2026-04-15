"""
AI Explanation Generator
Produces human-readable narratives from analysis results:
  - Overall assessment
  - Critical findings with business-impact explanations
  - Prioritised action items
"""


def generate_explanations(clauses: dict, risks: dict, score: dict) -> dict:
    """
    Generate AI-driven explanations for the analysis results.

    Returns dict with overall_assessment, critical_findings, action_items.
    """
    overall = _overall(score)
    critical = _critical(clauses, risks)
    actions = _actions(clauses, risks)

    return {
        "overall_assessment": overall,
        "critical_findings": critical,
        "action_items": actions,
    }


# ── Helpers ──────────────────────────────────────────────

_MISSING_IMPACT = {
    "payment_terms": "Without clear payment terms, disputes over amounts and timing are likely.",
    "termination": "No clear exit path -- parties may be trapped in unfavourable agreements.",
    "liability": "Unlimited financial exposure from claims threatens business viability.",
    "confidentiality": "Sensitive information may be shared without legal protection.",
    "ip_rights": "Ownership of created work is unclear, risking future IP disputes.",
    "indemnification": "No protection against third-party claims or losses.",
    "dispute_resolution": "No defined mechanism for resolving disagreements.",
    "governing_law": "Legal jurisdiction is undefined, complicating enforcement.",
    "force_majeure": "No protection against extraordinary events (pandemic, disaster, etc.).",
    "data_protection": "Personal data handling is unaddressed, risking regulatory fines.",
    "warranty": "No quality assurance commitments are defined.",
    "non_compete": "No restrictions on competitive activities post-agreement.",
}

_CRITICAL_IDS = {"payment_terms", "termination", "liability", "confidentiality"}


def _overall(score: dict) -> dict:
    s = score["score"]
    g = score["grade"]
    if s >= 70:
        narrative = (
            f"This document scores {s}/100 ({g}), indicating solid compliance. "
            "Most critical clauses are present and risks are manageable. "
            "Review the recommended actions to further strengthen the document."
        )
    elif s >= 50:
        narrative = (
            f"This document scores {s}/100 ({g}). Several important areas need attention. "
            "Key clauses may be missing and some risk indicators were detected. "
            "Address the action items below before signing."
        )
    else:
        narrative = (
            f"This document scores {s}/100 ({g}), indicating significant compliance gaps. "
            "Multiple critical clauses are missing and high-risk language was detected. "
            "This document should not be signed without substantial revisions."
        )
    return {"narrative": narrative, "score_summary": f"{s}/100 ({g})"}


def _critical(clauses: dict, risks: dict) -> list:
    findings = []
    for cid, c in clauses["detected"].items():
        if not c["found"] and cid in _CRITICAL_IDS:
            findings.append({
                "title": f"Missing: {c['label']}",
                "icon": "[!]",
                "severity": "HIGH",
                "explanation": _MISSING_IMPACT.get(cid, "This clause is missing from the document."),
                "evidence": c.get("evidence", ""),
            })

    high_risks = [r for r in risks["risks"] if r["severity"] == "HIGH"]
    for r in high_risks[:3]:
        findings.append({
            "title": r["category_label"],
            "icon": "[!]",
            "severity": "HIGH",
            "explanation": r["description"],
            "evidence": r["sentence"][:120],
        })

    return findings


def _actions(clauses: dict, risks: dict) -> list:
    items = []

    # Missing-clause actions (critical first)
    for cid in list(_CRITICAL_IDS) + [k for k in clauses["detected"] if k not in _CRITICAL_IDS]:
        c = clauses["detected"][cid]
        if not c["found"]:
            sev = "HIGH" if cid in _CRITICAL_IDS else "MEDIUM"
            verb = "Add" if sev == "HIGH" else "Consider adding"
            items.append({
                "action": f"{verb} {c['label']}",
                "detail": _MISSING_IMPACT.get(cid, c["description"]),
                "severity": sev,
                "icon": "[!]" if sev == "HIGH" else "[+]",
            })

    # Risk-based actions
    seen_cats = set()
    for r in risks["risks"]:
        if r["category"] not in seen_cats:
            seen_cats.add(r["category"])
            if r["severity"] == "HIGH":
                items.append({
                    "action": f"Review: {r['category_label']}",
                    "detail": r["description"],
                    "severity": "HIGH",
                    "icon": "[!]",
                })

    return items

"""
AI Explanation Engine
Generates plain-English explanations linking risks to business impact.
"""


def generate_explanations(clause_result, risk_result, score_result):
    explanations = {
        'overall_assessment': _gen_overall(score_result),
        'critical_findings': _gen_critical(clause_result, risk_result),
        'clause_explanations': _gen_clauses(clause_result),
        'risk_explanations': _gen_risks(risk_result),
        'action_items': _gen_actions(clause_result, risk_result)
    }
    return explanations


def _gen_overall(score_result):
    s = score_result['score']
    g = score_result['grade']
    l = score_result['label']
    if s >= 80:
        t, a = "Strong compliance fundamentals.", "Minor refinements could improve it."
    elif s >= 60:
        t, a = "Moderate compliance with notable gaps.", "Several areas need attention."
    elif s >= 40:
        t, a = "Significant compliance deficiencies.", "Substantial revisions recommended."
    else:
        t, a = "Critical compliance issues presenting serious risk.", "Major restructuring and legal review strongly recommended."
    return {'summary': f"Grade: {g} ({s}/100) — {l}", 'narrative': f"{t} {a}", 'score': s, 'grade': g}


def _gen_critical(clause_result, risk_result):
    critical = []
    impacts = {
        "Payment Terms": "Without clear payment terms, disputes over amounts and timing are likely.",
        "Termination Clause": "No clear exit path — parties may be trapped in unfavorable agreements.",
        "Liability & Limitation": "Unlimited financial exposure from claims threatens business viability.",
        "Confidentiality / NDA": "Sensitive information and trade secrets have no contractual safeguards.",
    }
    for cl in clause_result['summary']['missing_critical']:
        critical.append({'type': 'missing_clause', 'severity': 'HIGH', 'icon': '❌',
                         'title': f"Missing: {cl}", 'explanation': impacts.get(cl, f"Missing {cl} reduces legal completeness.")})
    seen = set()
    for r in risk_result['risks']:
        if r['severity'] == 'HIGH' and r['category'] not in seen:
            seen.add(r['category'])
            critical.append({'type': 'high_risk', 'severity': 'HIGH', 'icon': '🔴',
                             'title': r['category_label'], 'explanation': r['description'], 'evidence': r['sentence'][:120]})
            if len(seen) >= 5:
                break
    return critical


def _gen_clauses(clause_result):
    explanations = []
    missing_text = {
        "payment": "No payment terms detected — missing compensation amounts, schedules, or invoicing procedures.",
        "termination": "No termination clause found — no specification for how/when the agreement can end.",
        "liability": "No liability limitation — parties may face unlimited financial risk.",
        "confidentiality": "No confidentiality provisions — shared information has no protection.",
        "indemnification": "No indemnification clause — no protection against third-party claims.",
        "force_majeure": "No force majeure clause — no provisions for extraordinary events.",
        "dispute_resolution": "No dispute resolution mechanism — conflicts default to costly litigation.",
        "governing_law": "No governing law specified — unclear which jurisdiction applies.",
        "warranty": "No warranty provisions — no quality guarantees for deliverables.",
        "intellectual_property": "No IP clause — ownership of created works undefined.",
        "non_compete": "No non-compete terms detected.",
        "data_protection": "No data protection provisions — no safeguards for personal data.",
    }
    for cid, c in clause_result['detected'].items():
        if c['found']:
            explanations.append({'clause': c['label'], 'icon': c['icon'], 'status': 'present', 'status_icon': '✅',
                                 'explanation': f"{c['label']} detected ({c['confidence']}% confidence).",
                                 'evidence': c['evidence'][:2], 'impact': 'positive'})
        else:
            explanations.append({'clause': c['label'], 'icon': c['icon'], 'status': 'missing', 'status_icon': '❌',
                                 'explanation': missing_text.get(cid, f"{c['label']} not detected. {c['description']}."),
                                 'evidence': [], 'impact': 'negative'})
    explanations.sort(key=lambda x: 0 if x['status'] == 'missing' else 1)
    return explanations


def _gen_risks(risk_result):
    impacts = {
        "vague_language": "Vague wording leads to different interpretations and disputes.",
        "ambiguous_obligations": "Unclear obligations cause disagreements on requirements.",
        "deadline_risk": "No specific deadlines makes enforcement impossible.",
        "liability_exposure": "High liability exposure can cause significant financial losses.",
        "automatic_renewal": "Auto-renewal may lock parties into outdated agreements.",
        "unilateral_changes": "One-sided modification rights alter agreements without consent.",
        "weak_enforcement": "Non-binding language reduces enforceability.",
        "structural": "Poor structure makes navigation and enforcement difficult.",
    }
    return [{'category': r['category_label'], 'severity': r['severity'], 'icon': r['icon'],
             'trigger': r.get('trigger', ''), 'sentence': r['sentence'][:150],
             'explanation': r['description'],
             'business_impact': impacts.get(r['category'], "May reduce document effectiveness.")}
            for r in risk_result['risks']]


def _gen_actions(clause_result, risk_result):
    actions = []
    p = 1
    clause_actions = {
        "Payment Terms": "Define amounts, schedules (Net 30), methods, late penalties, invoicing.",
        "Termination Clause": "Specify conditions, notice periods (30 days), post-termination obligations.",
        "Liability & Limitation": "Add caps (e.g., contract value), exclude consequential damages.",
        "Confidentiality / NDA": "Define confidential info, protection obligations, duration.",
    }
    for cl in clause_result['summary']['missing_critical']:
        actions.append({'priority': p, 'severity': 'HIGH', 'action': f"Add {cl}",
                        'detail': clause_actions.get(cl, f"Draft comprehensive {cl} section."), 'icon': '🔴'})
        p += 1
    for cid, c in clause_result['detected'].items():
        if not c['found'] and c['label'] not in clause_result['summary']['missing_critical']:
            actions.append({'priority': p, 'severity': 'MEDIUM', 'action': f"Consider adding {c['label']}",
                            'detail': f"{c['description']} — adds legal protection.", 'icon': '🔶'})
            p += 1
    seen = set()
    for r in risk_result['risks']:
        if r['severity'] == 'HIGH' and r['category'] not in seen:
            seen.add(r['category'])
            actions.append({'priority': p, 'severity': 'HIGH', 'action': f"Address {r['category_label']}",
                            'detail': r['description'], 'icon': '🔴'})
            p += 1
    sev = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    actions.sort(key=lambda x: (sev.get(x['severity'], 99), x['priority']))
    return actions

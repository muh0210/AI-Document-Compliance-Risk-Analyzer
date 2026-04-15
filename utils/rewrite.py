"""
Smart Rewrite Suggestion Engine
Suggests concrete replacements for vague or risky language.
"""

import re

# (regex_pattern, replacement_text, change_label)
_RULES = [
    (r"\bapproximately\b", "[specify exact amount]", "approximately -> exact amount"),
    (r"\breasonable\s+time(?:frame)?\b", "within [X] business days", "vague timeline -> specific days"),
    (r"\breasonable\b", "[define specific standard]", "reasonable -> defined standard"),
    (r"\bmight\s+be\s+paid\b", "shall be paid", "might be paid -> shall be paid"),
    (r"\bmight\b", "shall", "might -> shall"),
    (r"\bcould\b", "shall", "could -> shall"),
    (r"\bshould\b(?!\s+not)", "shall", "should -> shall"),
    (r"\bprobably\b", "[confirm or remove]", "probably -> confirmed"),
    (r"\bgenerally\b", "[specify exact scope]", "generally -> specific scope"),
    (r"\bmay\b(?!\s+not)", "shall", "may -> shall"),
    (r"\bendeavou?r\s+to\b", "shall", "endeavour to -> shall"),
    (r"\bwill\s+try\s+to\b", "shall", "will try to -> shall"),
    (r"\btry\s+(?:to|their|its|our)\s+best\b", "shall", "try best -> shall"),
    (r"\bas\s+needed\b", "as specified in Schedule [X]", "as needed -> scheduled"),
    (r"\bas\s+appropriate\b", "as defined in Section [X]", "as appropriate -> defined"),
    (r"\bto\s+be\s+determined\b", "[insert agreed value]", "TBD -> agreed value"),
    (r"\bfrom\s+time\s+to\s+time\b", "[specify frequency, e.g. quarterly]", "vague frequency -> specific"),
    (r"\bat\s+(?:its|their)\s+sole\s+discretion\b", "with mutual written agreement", "sole discretion -> mutual"),
    (r"\bat\s+some\s+point\b", "within [X] days of [event]", "at some point -> deadline"),
    (r"\bgive\s+or\s+take\b", "[specify tolerance range]", "give or take -> tolerance"),
    (r"\bwe'?ll\s+figure\s+(?:it\s+)?out\b", "[define resolution process]", "informal -> process"),
    (r"\bgood\s+faith\b", "in accordance with the dispute resolution process in Section [X]",
     "good faith -> formal process"),
    (r"\bif\s+and\s+when\b", "upon occurrence of [defined event]", "if and when -> defined trigger"),
    (r"\bgood\s+vibes\b", "[replace with formal legal language]", "informal -> formal"),
]


def suggest_rewrites(risk_list: list) -> list:
    """
    Generate rewrite suggestions for sentences flagged by the risk engine.

    Args:
        risk_list: List of risk dicts from detect_risks().

    Returns:
        List of dicts with original, rewritten, and changes.
    """
    results = []
    seen = set()

    for risk in risk_list:
        if risk.get("category") not in ("vague_language", "ambiguous_obligation",
                                         "unilateral_terms", "auto_renewal"):
            continue

        original = risk.get("sentence", "")
        if not original or original in seen:
            continue
        seen.add(original)

        rewritten = original
        changes = []
        for pattern, replacement, label in _RULES:
            if re.search(pattern, rewritten, re.IGNORECASE):
                rewritten = re.sub(pattern, replacement, rewritten, count=1, flags=re.IGNORECASE)
                changes.append(label)

        if changes:
            results.append({
                "original": original[:250],
                "rewritten": rewritten[:250],
                "changes": changes,
                "risk_category": risk["category"],
            })

    return results

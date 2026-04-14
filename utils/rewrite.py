"""
Smart Rewrite Engine
Suggests concrete rewrites for vague/risky sentences.
"""

import re

REPLACEMENTS = {
    "may": "shall", "might": "shall", "could": "will",
    "possibly": "definitively", "perhaps": "specifically",
    "approximately": "exactly", "roughly": "precisely",
    "around": "exactly", "about": "specifically",
    "reasonable": "defined", "adequate": "specified",
    "sufficient": "required minimum", "appropriate": "prescribed",
    "generally": "in all cases", "typically": "always",
    "usually": "consistently", "normally": "in every instance",
    "should": "shall", "ought to": "must",
    "is encouraged": "is required", "is expected": "is obligated",
    "endeavour": "commit to", "endeavor": "commit to",
    "strive": "ensure", "attempt": "guarantee", "seek to": "ensure",
    "best efforts": "commercially reasonable and documented efforts",
    "reasonable efforts": "defined and measurable efforts",
    "good faith": "documented and verifiable good faith",
    "as needed": "as specified in Schedule A",
    "as required": "as defined in Section X",
    "as appropriate": "as prescribed by the governing standards",
    "when necessary": "upon occurrence of the defined trigger events",
    "to be determined": "[SPECIFY EXACT TERMS]",
    "tbd": "[SPECIFY EXACT TERMS]",
    "tba": "[SPECIFY EXACT TERMS]",
    "timely": "within [X] business days",
    "promptly": "within [X] business days",
    "as soon as practicable": "within [X] calendar days",
    "without undue delay": "within [X] business days",
}


def suggest_rewrites(risks):
    """
    Generate rewrite suggestions for risky sentences.
    
    Args:
        risks: List of risk objects from risk_engine.detect_risks()
    
    Returns:
        list of {original, rewritten, changes, category}
    """
    suggestions = []
    seen = set()
    
    for risk in risks:
        sentence = risk['sentence'].strip()
        if sentence in seen or not sentence:
            continue
        seen.add(sentence)
        
        rewritten, changes = _rewrite_sentence(sentence, risk.get('trigger', ''))
        if rewritten != sentence:
            suggestions.append({
                'original': sentence[:200],
                'rewritten': rewritten[:200],
                'changes': changes,
                'category': risk.get('category_label', 'General'),
                'severity': risk.get('severity', 'MEDIUM')
            })
    
    return suggestions


def _rewrite_sentence(sentence, trigger):
    """Apply rule-based rewrites to a sentence."""
    rewritten = sentence
    changes = []
    
    for old, new in sorted(REPLACEMENTS.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(r'\b' + re.escape(old) + r'\b', re.IGNORECASE)
        if pattern.search(rewritten):
            def replace_match(m):
                orig = m.group(0)
                if orig[0].isupper():
                    return new.capitalize()
                return new
            rewritten = pattern.sub(replace_match, rewritten)
            changes.append(f'"{old}" → "{new}"')
    
    return rewritten, changes

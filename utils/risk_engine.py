"""
Risk Engine — Core System
Detects risky patterns, vague language, ambiguous obligations, 
missing structure, and classifies by severity.
"""

import re


# ═══════════════════════════════════════════════════════════════
# RISK PATTERN DEFINITIONS
# ═══════════════════════════════════════════════════════════════

RISK_CATEGORIES = {
    "vague_language": {
        "label": "Vague Language",
        "severity": "MEDIUM",
        "icon": "🔶",
        "patterns": [
            {"words": ["may", "might", "could", "possibly", "perhaps", "arguably"],
             "description": "Hedging language reduces enforceability"},
            {"words": ["approximately", "roughly", "around", "about", "estimated"],
             "description": "Imprecise quantities create ambiguity"},
            {"words": ["reasonable", "reasonably", "appropriate", "adequate", "sufficient"],
             "description": "Subjective terms lack clear definition"},
            {"words": ["generally", "typically", "usually", "normally", "often"],
             "description": "Non-absolute language weakens obligations"},
        ]
    },
    "ambiguous_obligations": {
        "label": "Ambiguous Obligations",
        "severity": "HIGH",
        "icon": "🔴",
        "patterns": [
            {"regex": r"\b(best\s+efforts?|reasonable\s+efforts?|good\s+faith)\b",
             "description": "Effort-based obligations are hard to enforce"},
            {"regex": r"\b(as\s+needed|as\s+required|as\s+appropriate|when\s+necessary)\b",
             "description": "Open-ended triggers create uncertainty"},
            {"regex": r"\b(to\s+be\s+determined|tbd|tba|to\s+be\s+agreed)\b",
             "description": "Undefined terms indicate incomplete agreement"},
            {"regex": r"\b(at\s+(its|their|our)\s+(sole\s+)?discretion)\b",
             "description": "Unilateral discretion creates imbalance"},
        ]
    },
    "deadline_risk": {
        "label": "Deadline & Timeline Risk",
        "severity": "MEDIUM",
        "icon": "⏰",
        "patterns": [
            {"regex": r"\b(timely|promptly|as\s+soon\s+as\s+practicable|without\s+undue\s+delay)\b",
             "description": "Vague timelines lack specific deadlines"},
            {"regex": r"\b(no\s+later\s+than|within\s+a\s+reasonable\s+time)\b",
             "description": "Undefined time periods create disputes"},
        ]
    },
    "liability_exposure": {
        "label": "Liability Exposure",
        "severity": "HIGH",
        "icon": "🔴",
        "patterns": [
            {"regex": r"\b(unlimited\s+liabilit|no\s+cap\s+on|without\s+limit)\b",
             "description": "Uncapped liability exposes to unlimited risk"},
            {"regex": r"\b(sole\s+responsibilit|full\s+responsibilit|entirely\s+responsible)\b",
             "description": "Full responsibility assignment is high risk"},
            {"regex": r"\b(waive|waiver\s+of|forfeit|surrender)\s+(any\s+)?(rights?|claims?)\b",
             "description": "Rights waivers reduce legal protections"},
        ]
    },
    "automatic_renewal": {
        "label": "Automatic Renewal Risk",
        "severity": "LOW",
        "icon": "🟡",
        "patterns": [
            {"regex": r"\b(auto\w*\s+renew|automatic\w*\s+renew|shall\s+renew)\b",
             "description": "Auto-renewal may lock in unfavorable terms"},
            {"regex": r"\b(evergreen|perpetual\s+term|indefinite\s+term)\b",
             "description": "Indefinite terms limit exit options"},
        ]
    },
    "unilateral_changes": {
        "label": "Unilateral Modification Risk",
        "severity": "HIGH",
        "icon": "🔴",
        "patterns": [
            {"regex": r"\b(right\s+to\s+(modify|change|amend|alter)\s+(at\s+any\s+time|without\s+notice))\b",
             "description": "Unilateral change rights create instability"},
            {"regex": r"\b(subject\s+to\s+change\s+without\s+notice)\b",
             "description": "Changes without notice are unfair"},
        ]
    },
    "weak_enforcement": {
        "label": "Weak Enforcement Language",
        "severity": "MEDIUM",
        "icon": "🔶",
        "patterns": [
            {"words": ["should", "ought to", "is encouraged", "is expected"],
             "description": "Non-binding language suggests optional compliance"},
            {"words": ["endeavour", "endeavor", "strive", "attempt", "seek to"],
             "description": "Aspirational language lacks commitment"},
        ]
    }
}

# Severity ordering for sorting
SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def detect_risks(sentences, text=None):
    """
    Analyze sentences for risk patterns.
    
    Args:
        sentences: List of sentence strings
        text: Optional full text for structural analysis
    
    Returns:
        dict: {
            'risks': list of risk objects,
            'summary': {
                'total_risks': int,
                'high': int,
                'medium': int,
                'low': int,
                'risk_density': float,
                'top_categories': list
            }
        }
    """
    risks = []
    category_counts = {}
    
    for sentence in sentences:
        sentence_risks = _analyze_sentence(sentence)
        risks.extend(sentence_risks)
        for r in sentence_risks:
            cat = r['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Add structural risks if full text provided
    if text:
        structural = _check_structural_risks(text)
        risks.extend(structural)
    
    # Sort by severity
    risks.sort(key=lambda r: SEVERITY_ORDER.get(r['severity'], 99))
    
    # Count by severity
    high = sum(1 for r in risks if r['severity'] == 'HIGH')
    medium = sum(1 for r in risks if r['severity'] == 'MEDIUM')
    low = sum(1 for r in risks if r['severity'] == 'LOW')
    
    # Risk density (risks per sentence)
    density = round(len(risks) / max(len(sentences), 1), 2)
    
    # Top risk categories
    top_categories = sorted(category_counts.items(), key=lambda x: -x[1])[:5]
    
    return {
        'risks': risks,
        'summary': {
            'total_risks': len(risks),
            'high': high,
            'medium': medium,
            'low': low,
            'risk_density': density,
            'top_categories': [{'category': c, 'count': n} for c, n in top_categories]
        }
    }


def _analyze_sentence(sentence):
    """Analyze a single sentence for all risk patterns."""
    found_risks = []
    sentence_lower = sentence.lower()
    
    for category_id, category in RISK_CATEGORIES.items():
        for pattern in category['patterns']:
            matched = False
            trigger_word = None
            
            if 'words' in pattern:
                for word in pattern['words']:
                    # Word boundary check
                    if re.search(r'\b' + re.escape(word) + r'\b', sentence_lower):
                        matched = True
                        trigger_word = word
                        break
            
            if 'regex' in pattern:
                match = re.search(pattern['regex'], sentence_lower)
                if match:
                    matched = True
                    trigger_word = match.group(0)
            
            if matched:
                found_risks.append({
                    'sentence': sentence.strip(),
                    'category': category_id,
                    'category_label': category['label'],
                    'severity': category['severity'],
                    'icon': category['icon'],
                    'trigger': trigger_word,
                    'description': pattern['description'],
                    'type': 'pattern'
                })
                break  # One risk per category per sentence
    
    return found_risks


def _check_structural_risks(text):
    """Check for document-level structural issues."""
    risks = []
    
    # Check for missing section structure
    lines = text.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    
    # Very short document
    word_count = len(text.split())
    if word_count < 200:
        risks.append({
            'sentence': f"Document contains only {word_count} words",
            'category': 'structural',
            'category_label': 'Structural Issue',
            'severity': 'MEDIUM',
            'icon': '🔶',
            'trigger': 'short document',
            'description': 'Document may be too brief to cover all necessary terms',
            'type': 'structural'
        })
    
    # No clear sections/headers
    has_headers = any(
        line.strip().isupper() and len(line.strip()) > 3
        or re.match(r'^\d+[\.\)]\s+', line.strip())
        or re.match(r'^(section|article|clause)\s+\d+', line.strip(), re.IGNORECASE)
        for line in non_empty_lines
    )
    
    if not has_headers and word_count > 300:
        risks.append({
            'sentence': "No clear section headers detected in document",
            'category': 'structural',
            'category_label': 'Structural Issue',
            'severity': 'LOW',
            'icon': '🟡',
            'trigger': 'missing headers',
            'description': 'Lack of structure makes the document harder to navigate and enforce',
            'type': 'structural'
        })
    
    # Check for missing date references
    has_dates = bool(re.search(
        r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})\b', text
    ))
    if not has_dates and word_count > 200:
        risks.append({
            'sentence': "No specific dates found in document",
            'category': 'deadline_risk',
            'category_label': 'Deadline & Timeline Risk',
            'severity': 'MEDIUM',
            'icon': '⏰',
            'trigger': 'no dates',
            'description': 'Documents without specific dates lack concrete timelines',
            'type': 'structural'
        })
    
    return risks

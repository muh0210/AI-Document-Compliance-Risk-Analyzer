"""
Clause Detection Engine
Detects the presence or absence of critical business/legal clauses in documents.
Uses keyword matching, phrase patterns, and contextual analysis.
"""

import re


# ═══════════════════════════════════════════════════════════════
# CLAUSE DEFINITIONS — Each clause has keywords, phrases, and weight
# ═══════════════════════════════════════════════════════════════

CLAUSE_DEFINITIONS = {
    "payment": {
        "label": "Payment Terms",
        "icon": "💰",
        "keywords": ["payment", "pay", "invoice", "billing", "fee", "cost", "price",
                      "compensation", "remuneration", "reimbursement", "dues"],
        "phrases": [
            r"payment\s+(shall|will|must|should)\s+be",
            r"(net\s+\d+|within\s+\d+\s+days)",
            r"(invoice|bill)\s+(will|shall)\s+be\s+(sent|issued)",
            r"total\s+(cost|price|amount|fee)",
        ],
        "weight": 15,
        "description": "Defines how and when payments are made"
    },
    "termination": {
        "label": "Termination Clause",
        "icon": "🚫",
        "keywords": ["terminat", "cancel", "end of agreement", "discontinue",
                      "expiration", "expire", "cease", "revoke"],
        "phrases": [
            r"(either\s+party|any\s+party)\s+(may|can|shall)\s+terminat",
            r"terminat\w*\s+(upon|with|without)\s+\d+",
            r"(right\s+to\s+terminat|grounds\s+for\s+terminat)",
            r"(notice\s+of\s+terminat|terminat\w*\s+notice)",
        ],
        "weight": 15,
        "description": "Conditions under which the agreement can be ended"
    },
    "liability": {
        "label": "Liability & Limitation",
        "icon": "⚖️",
        "keywords": ["liable", "liability", "responsible", "responsibility",
                      "limitation of liability", "damages", "negligence"],
        "phrases": [
            r"(shall\s+not\s+be|not\s+be)\s+(liable|responsible)",
            r"limit\w*\s+of\s+liabilit",
            r"(direct|indirect|consequential)\s+damages",
            r"aggregate\s+liabilit",
        ],
        "weight": 12,
        "description": "Limits on legal responsibility and damages"
    },
    "confidentiality": {
        "label": "Confidentiality / NDA",
        "icon": "🔒",
        "keywords": ["confidential", "non-disclosure", "proprietary", "trade secret",
                      "sensitive information", "private", "nda"],
        "phrases": [
            r"confidential\s+information",
            r"(shall|will|must)\s+(not\s+)?disclos",
            r"(non[\-\s]?disclosure|nda)",
            r"proprietary\s+(information|data|material)",
        ],
        "weight": 10,
        "description": "Protection of sensitive information"
    },
    "indemnification": {
        "label": "Indemnification",
        "icon": "🛡️",
        "keywords": ["indemnif", "hold harmless", "defend", "indemnity"],
        "phrases": [
            r"(shall|will|agrees?\s+to)\s+indemnif",
            r"hold\s+harmless",
            r"indemnif\w*\s+(against|from|for)",
            r"defend\s+and\s+indemnif",
        ],
        "weight": 10,
        "description": "Agreement to compensate for losses or damages"
    },
    "force_majeure": {
        "label": "Force Majeure",
        "icon": "🌪️",
        "keywords": ["force majeure", "act of god", "unforeseeable", "beyond control",
                      "natural disaster", "pandemic", "war", "earthquake"],
        "phrases": [
            r"force\s+majeure",
            r"(acts?\s+of\s+god|beyond\s+(reasonable\s+)?control)",
            r"(unforeseeable|extraordinary)\s+(circumstances|events)",
            r"(pandemic|epidemic|natural\s+disaster)",
        ],
        "weight": 8,
        "description": "Protection against extraordinary events"
    },
    "dispute_resolution": {
        "label": "Dispute Resolution",
        "icon": "🤝",
        "keywords": ["dispute", "arbitration", "mediation", "litigation",
                      "resolution", "settle", "court", "jurisdiction"],
        "phrases": [
            r"dispute\s+(resolution|settlement)",
            r"(submit\w*\s+to|refer\w*\s+to)\s+(arbitration|mediation)",
            r"(exclusive\s+)?jurisdiction",
            r"(binding\s+)?arbitration",
        ],
        "weight": 8,
        "description": "How conflicts between parties will be resolved"
    },
    "governing_law": {
        "label": "Governing Law",
        "icon": "📜",
        "keywords": ["governing law", "applicable law", "governed by", "subject to the laws"],
        "phrases": [
            r"govern\w*\s+(by|under)\s+the\s+laws",
            r"(applicable|governing)\s+law",
            r"laws\s+of\s+the\s+(state|country|province)",
            r"subject\s+to\s+the\s+(laws|jurisdiction)",
        ],
        "weight": 6,
        "description": "Which legal jurisdiction applies"
    },
    "warranty": {
        "label": "Warranty / Guarantee",
        "icon": "✅",
        "keywords": ["warranty", "guarantee", "warrant", "representation",
                      "as-is", "merchantability", "fitness"],
        "phrases": [
            r"warrant\w*\s+(that|and\s+represent)",
            r"(no\s+)?warrant\w*\s+(express|implied)",
            r"(as[\-\s]?is|without\s+warranty)",
            r"(merchantability|fitness\s+for\s+a\s+particular\s+purpose)",
        ],
        "weight": 8,
        "description": "Promises about product/service quality"
    },
    "intellectual_property": {
        "label": "Intellectual Property",
        "icon": "💡",
        "keywords": ["intellectual property", "copyright", "trademark", "patent",
                      "trade secret", "proprietary rights", "ip rights", "ownership"],
        "phrases": [
            r"intellectual\s+property",
            r"(copyright|trademark|patent)\s+(rights|ownership|protection)",
            r"(all\s+)?(ip|intellectual\s+property)\s+rights",
            r"(ownership|title)\s+(of|to|in)\s+(the\s+)?(work|deliverable|material)",
        ],
        "weight": 8,
        "description": "Ownership of created work and inventions"
    },
    "non_compete": {
        "label": "Non-Compete / Non-Solicitation",
        "icon": "🚧",
        "keywords": ["non-compete", "non-solicitation", "restrictive covenant",
                      "compete", "solicit", "competitive"],
        "phrases": [
            r"non[\-\s]?compet\w*",
            r"non[\-\s]?solicitat\w*",
            r"(shall|will|agree)\s+not\s+(to\s+)?(compet|solicit)",
            r"restrictive\s+covenant",
        ],
        "weight": 6,
        "description": "Restrictions on competitive activities"
    },
    "data_protection": {
        "label": "Data Protection / Privacy",
        "icon": "🔐",
        "keywords": ["data protection", "privacy", "gdpr", "personal data",
                      "data processing", "data controller", "data subject", "ccpa"],
        "phrases": [
            r"(data\s+protection|privacy\s+policy)",
            r"(gdpr|ccpa|data\s+protection\s+act)",
            r"personal\s+(data|information)",
            r"data\s+(processor|controller|subject)",
        ],
        "weight": 8,
        "description": "How personal and sensitive data is handled"
    },
}


def detect_clauses(text, sentences=None):
    """
    Detect which clauses are present or missing in the document.
    
    Args:
        text: Full document text
        sentences: Optional pre-split sentences list
    
    Returns:
        dict: {
            'detected': {clause_id: {label, icon, found, confidence, evidence, weight, description}},
            'summary': {
                'total_clauses': int,
                'found_count': int,
                'missing_count': int,
                'coverage_pct': float,
                'missing_critical': list[str]
            }
        }
    """
    text_lower = text.lower()
    detected = {}
    
    for clause_id, definition in CLAUSE_DEFINITIONS.items():
        result = _analyze_clause(text_lower, text, definition, sentences)
        detected[clause_id] = {
            'id': clause_id,
            'label': definition['label'],
            'icon': definition['icon'],
            'found': result['found'],
            'confidence': result['confidence'],
            'evidence': result['evidence'],
            'weight': definition['weight'],
            'description': definition['description']
        }
    
    # Build summary
    found = [k for k, v in detected.items() if v['found']]
    missing = [k for k, v in detected.items() if not v['found']]
    critical_clauses = ['payment', 'termination', 'liability', 'confidentiality']
    missing_critical = [detected[c]['label'] for c in critical_clauses if c in missing]
    
    total = len(CLAUSE_DEFINITIONS)
    return {
        'detected': detected,
        'summary': {
            'total_clauses': total,
            'found_count': len(found),
            'missing_count': len(missing),
            'coverage_pct': round((len(found) / total) * 100, 1),
            'missing_critical': missing_critical
        }
    }


def _analyze_clause(text_lower, original_text, definition, sentences=None):
    """Analyze a single clause for presence, confidence, and evidence."""
    keyword_hits = 0
    phrase_hits = 0
    evidence = []
    
    # Check keywords
    for keyword in definition['keywords']:
        if keyword.lower() in text_lower:
            keyword_hits += 1
    
    # Check phrase patterns
    for pattern in definition['phrases']:
        matches = re.findall(pattern, text_lower)
        if matches:
            phrase_hits += len(matches)
            # Extract evidence from original text
            for match in re.finditer(pattern, text_lower):
                start = max(0, match.start() - 40)
                end = min(len(original_text), match.end() + 40)
                snippet = original_text[start:end].strip()
                if snippet and len(evidence) < 3:
                    evidence.append(f"...{snippet}...")
    
    # Calculate confidence
    total_keywords = len(definition['keywords'])
    total_phrases = len(definition['phrases'])
    
    keyword_ratio = keyword_hits / total_keywords if total_keywords else 0
    phrase_ratio = phrase_hits / total_phrases if total_phrases else 0
    
    # Weighted confidence: phrases are stronger signals
    confidence = min(100, round((keyword_ratio * 40 + phrase_ratio * 60) * 100))
    
    # Determine if clause is found (threshold: at least 1 keyword + 1 phrase, or high keyword density)
    found = (keyword_hits >= 1 and phrase_hits >= 1) or keyword_hits >= 3
    
    return {
        'found': found,
        'confidence': confidence if found else 0,
        'evidence': evidence
    }

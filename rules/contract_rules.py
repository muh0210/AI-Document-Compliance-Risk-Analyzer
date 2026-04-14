"""
Contract Rules — Rule definitions for contract document analysis.
"""

CONTRACT_REQUIRED_CLAUSES = [
    "payment", "termination", "liability", "confidentiality",
    "indemnification", "dispute_resolution", "governing_law", "warranty"
]

CONTRACT_RISK_THRESHOLDS = {
    "max_vague_words_per_100_sentences": 15,
    "min_clause_coverage_pct": 60,
    "max_high_severity_risks": 3,
}

CONTRACT_PENALTIES = {
    "missing_payment": -20,
    "missing_termination": -20,
    "missing_liability": -15,
    "missing_confidentiality": -10,
    "vague_language_per_instance": -2,
    "high_risk_per_instance": -5,
    "medium_risk_per_instance": -2,
}

CONTRACT_DOCUMENT_TYPES = {
    "service_agreement": {
        "label": "Service Agreement",
        "required": ["payment", "termination", "liability", "warranty"],
        "recommended": ["confidentiality", "indemnification", "dispute_resolution"]
    },
    "nda": {
        "label": "Non-Disclosure Agreement",
        "required": ["confidentiality", "termination", "governing_law"],
        "recommended": ["dispute_resolution", "intellectual_property"]
    },
    "employment": {
        "label": "Employment Contract",
        "required": ["payment", "termination", "confidentiality", "non_compete"],
        "recommended": ["intellectual_property", "dispute_resolution", "data_protection"]
    },
    "partnership": {
        "label": "Partnership Agreement",
        "required": ["payment", "termination", "liability", "dispute_resolution"],
        "recommended": ["confidentiality", "intellectual_property", "force_majeure"]
    }
}

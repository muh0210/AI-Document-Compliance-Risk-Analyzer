"""
Policy Rules — Rule definitions for policy document analysis.
"""

POLICY_REQUIRED_CLAUSES = [
    "data_protection", "confidentiality", "liability",
    "termination", "governing_law"
]

POLICY_COMPLIANCE_KEYWORDS = {
    "gdpr": ["data protection", "personal data", "data subject", "data controller",
             "data processor", "consent", "right to erasure", "data portability"],
    "hipaa": ["protected health information", "phi", "covered entity",
              "business associate", "minimum necessary", "privacy officer"],
    "sox": ["internal controls", "financial reporting", "audit committee",
            "material weakness", "disclosure controls"],
    "pci_dss": ["cardholder data", "payment card", "encryption",
                "access control", "security assessment"],
}

POLICY_RISK_PATTERNS = {
    "missing_enforcement": {
        "description": "Policy lacks enforcement mechanisms",
        "keywords": ["penalty", "consequence", "disciplinary", "enforcement", "violation"],
        "severity": "HIGH"
    },
    "missing_scope": {
        "description": "Policy scope is undefined",
        "keywords": ["scope", "applicability", "applies to", "covered by"],
        "severity": "MEDIUM"
    },
    "missing_review": {
        "description": "No review/update schedule defined",
        "keywords": ["review", "update", "revision", "amendment", "periodic"],
        "severity": "LOW"
    }
}

POLICY_DOCUMENT_TYPES = {
    "privacy_policy": {
        "label": "Privacy Policy",
        "required": ["data_protection", "confidentiality"],
        "frameworks": ["gdpr"]
    },
    "security_policy": {
        "label": "Security Policy",
        "required": ["data_protection", "liability"],
        "frameworks": ["pci_dss"]
    },
    "hr_policy": {
        "label": "HR Policy",
        "required": ["termination", "confidentiality", "non_compete"],
        "frameworks": []
    }
}

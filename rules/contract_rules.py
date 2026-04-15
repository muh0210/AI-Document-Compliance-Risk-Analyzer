"""
Contract compliance rules.
Maps clause types to their legal requirements and severity.
"""

CONTRACT_RULES = {
    "payment_terms": {"required": True, "severity": "HIGH",
                      "message": "Payment terms must be clearly defined with amounts, due dates, and methods."},
    "termination": {"required": True, "severity": "HIGH",
                    "message": "Termination clause must specify notice period, conditions, and consequences."},
    "liability": {"required": True, "severity": "HIGH",
                  "message": "Liability limitations protect parties from unlimited financial exposure."},
    "confidentiality": {"required": True, "severity": "HIGH",
                        "message": "Confidentiality clause protects sensitive business information."},
    "ip_rights": {"required": True, "severity": "MEDIUM",
                  "message": "IP ownership must be clearly assigned to avoid future disputes."},
    "indemnification": {"required": True, "severity": "MEDIUM",
                        "message": "Indemnification protects against third-party claims."},
    "dispute_resolution": {"required": True, "severity": "MEDIUM",
                           "message": "A dispute resolution mechanism avoids costly litigation."},
    "governing_law": {"required": True, "severity": "MEDIUM",
                      "message": "Governing law clarifies which legal jurisdiction applies."},
    "force_majeure": {"required": False, "severity": "LOW",
                      "message": "Force majeure protects against extraordinary events."},
    "data_protection": {"required": False, "severity": "MEDIUM",
                        "message": "Data protection clause ensures regulatory compliance (GDPR/CCPA)."},
    "warranty": {"required": False, "severity": "LOW",
                 "message": "Warranty clause defines quality expectations."},
    "non_compete": {"required": False, "severity": "LOW",
                    "message": "Non-compete restricts competitive activities after agreement ends."},
}

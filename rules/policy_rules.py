"""
Policy document compliance rules.
Rules specific to internal policy and regulatory documents.
"""

POLICY_RULES = {
    "effective_date": {"required": True, "severity": "HIGH",
                       "message": "Every policy must have a clearly stated effective date."},
    "scope": {"required": True, "severity": "HIGH",
              "message": "Policy scope must define who and what it applies to."},
    "definitions": {"required": True, "severity": "MEDIUM",
                    "message": "Key terms should be defined to avoid ambiguity."},
    "compliance_requirements": {"required": True, "severity": "HIGH",
                                "message": "Specific compliance obligations must be stated."},
    "enforcement": {"required": True, "severity": "MEDIUM",
                    "message": "Enforcement mechanisms ensure the policy is followed."},
    "review_cycle": {"required": False, "severity": "LOW",
                     "message": "Policies should specify when they will be reviewed and updated."},
    "exceptions": {"required": False, "severity": "LOW",
                   "message": "Exception handling process should be documented."},
}

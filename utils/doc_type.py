"""
Document Type Auto-Detector
Classifies documents into: contract, nda, sla, employment, policy, freelance, or general.
Uses keyword frequency analysis on the full text + section headers.
"""

import re

_SIGNATURES = {
    "nda": {
        "label": "Non-Disclosure Agreement",
        "icon": "lock",
        "patterns": [
            r"\bnon[\s-]?disclosure\b", r"\bnda\b", r"\bconfidential\s+information\b",
            r"\breceiving\s+party\b", r"\bdisclosing\s+party\b",
        ],
    },
    "sla": {
        "label": "Service Level Agreement",
        "icon": "gauge",
        "patterns": [
            r"\bservice\s+level\b", r"\bsla\b", r"\buptime\b", r"\bavailability\b",
            r"\bresponse\s+time\b", r"\bresolution\s+time\b",
        ],
    },
    "employment": {
        "label": "Employment Contract",
        "icon": "briefcase",
        "patterns": [
            r"\bemploy(?:ee|er|ment)\b", r"\bsalary\b", r"\bprobation\b",
            r"\bbenefits\b", r"\bjob\s+(?:title|description|duties)\b",
            r"\bworking\s+hours\b", r"\bleave\b",
        ],
    },
    "freelance": {
        "label": "Freelance / Consulting Agreement",
        "icon": "pen-tool",
        "patterns": [
            r"\bfreelance\b", r"\bconsultant\b", r"\bindependent\s+contractor\b",
            r"\bscope\s+of\s+work\b", r"\bdeliverables?\b", r"\bproject\s+(?:fee|rate)\b",
        ],
    },
    "policy": {
        "label": "Policy Document",
        "icon": "file-text",
        "patterns": [
            r"\bpolicy\b", r"\bcompliance\b", r"\bregulat", r"\bprocedure[s]?\b",
            r"\bstandard[s]?\b", r"\bguideline[s]?\b", r"\beffective\s+date\b",
        ],
    },
    "contract": {
        "label": "Business Contract",
        "icon": "file-signature",
        "patterns": [
            r"\bcontract\b", r"\bagreement\b", r"\bparties?\b", r"\bterms\s+and\s+conditions\b",
            r"\bwhereof\b", r"\bexecute\b", r"\bhereby\b",
        ],
    },
}

# Compile all patterns once at module load
for sig in _SIGNATURES.values():
    sig["_compiled"] = [re.compile(p, re.IGNORECASE) for p in sig["patterns"]]


def detect_document_type(text: str, headers: list = None) -> dict:
    """
    Classify the document type based on keyword frequency.

    Returns dict with type, label, icon, confidence, and scores.
    """
    combined = text
    if headers:
        combined += " " + " ".join(headers)
    combined_lower = combined.lower()

    scores = {}
    for dtype, sig in _SIGNATURES.items():
        hits = 0
        for pat in sig["_compiled"]:
            hits += len(pat.findall(combined_lower))
        scores[dtype] = hits

    if not scores or max(scores.values()) == 0:
        return {"type": "general", "label": "General Document", "icon": "file",
                "confidence": 0, "scores": scores}

    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = min(100, int((scores[best] / total) * 100))

    return {
        "type": best,
        "label": _SIGNATURES[best]["label"],
        "icon": _SIGNATURES[best]["icon"],
        "confidence": confidence,
        "scores": scores,
    }

"""
Clause Detection Engine
Identifies 12 critical business/legal clause types via keyword + phrase pattern matching.
Each clause gets a confidence score and supporting evidence.
"""

import re

# ── Clause definitions ───────────────────────────────────

CLAUSES = {
    "payment_terms": {
        "label": "Payment Terms",
        "icon": "💰",
        "description": "Defines how and when payments are made",
        "keywords": [
            r"\bpayment\b", r"\bcompensation\b", r"\bfee[s]?\b", r"\binvoic",
            r"\bsalar[yi]", r"\bpayable\b", r"\bdue\s+within\b", r"\bnet\s+\d+",
            r"\bbilling\b", r"\bremuneration\b", r"\bstipend\b",
        ],
    },
    "termination": {
        "label": "Termination Clause",
        "icon": "🚫",
        "description": "Conditions under which the agreement can be ended",
        "keywords": [
            r"\bterminat", r"\bcancel", r"\bend\s+(?:of\s+)?(?:this|the)\s+agreement",
            r"\bexpir", r"\bdissolv", r"\brescind", r"\brevok",
            r"\bnotice\s+period\b", r"\bexit\s+clause\b",
        ],
    },
    "liability": {
        "label": "Liability & Limitation",
        "icon": "⚖️",
        "description": "Limits on legal responsibility and damages",
        "keywords": [
            r"\bliabilit", r"\blimitation\s+of\b", r"\bcap\s+on\b", r"\bliable\b",
            r"\bdamage[s]?\b", r"\bconsequential\b", r"\bexclusion\b",
            r"\bnot\s+(?:be\s+)?(?:held\s+)?(?:liable|responsible)\b",
        ],
    },
    "confidentiality": {
        "label": "Confidentiality / NDA",
        "icon": "🔒",
        "description": "Protection of sensitive information",
        "keywords": [
            r"\bconfidential", r"\bnon[\s-]?disclosure\b", r"\bnda\b",
            r"\bproprietary\b", r"\btrade\s+secret", r"\bsensitive\s+information\b",
            r"\bnot\s+disclose\b",
        ],
    },
    "ip_rights": {
        "label": "Intellectual Property",
        "icon": "💡",
        "description": "Ownership of created work and inventions",
        "keywords": [
            r"\bintellectual\s+propert", r"\bcopyright", r"\bpatent",
            r"\btrademark", r"\bownership\s+of\b", r"\bwork[\s-]?product\b",
            r"\binvention[s]?\b", r"\blicen[sc]", r"\broyalt",
        ],
    },
    "indemnification": {
        "label": "Indemnification",
        "icon": "🔵",
        "description": "Agreement to compensate for losses or damages",
        "keywords": [
            r"\bindemni", r"\bhold\s+harmless\b", r"\bdefend\b.*\bclaim",
            r"\bcompensate.*\bloss",
        ],
    },
    "dispute_resolution": {
        "label": "Dispute Resolution",
        "icon": "🤝",
        "description": "How conflicts between parties will be resolved",
        "keywords": [
            r"\bdispute\s+resol", r"\barbitrat", r"\bmediat",
            r"\bjurisdiction\b", r"\blitigation\b", r"\bcourt\b",
        ],
    },
    "governing_law": {
        "label": "Governing Law",
        "icon": "📜",
        "description": "Which legal jurisdiction applies",
        "keywords": [
            r"\bgoverning\s+law\b", r"\bjurisdiction\b", r"\blaws\s+of\s+the\s+state\b",
            r"\bapplicable\s+law\b", r"\bgoverned\s+by\b",
        ],
    },
    "force_majeure": {
        "label": "Force Majeure",
        "icon": "🌪️",
        "description": "Protection against extraordinary events",
        "keywords": [
            r"\bforce\s+majeure\b", r"\bact\s+of\s+god\b", r"\bunforeseeable\b",
            r"\bnatural\s+disaster\b", r"\bpandemic\b", r"\bbeyond.*control\b",
        ],
    },
    "data_protection": {
        "label": "Data Protection / Privacy",
        "icon": "🛡️",
        "description": "How personal and sensitive data is handled",
        "keywords": [
            r"\bdata\s+protect", r"\bprivacy\b", r"\bgdpr\b", r"\bccpa\b",
            r"\bpersonal\s+(?:data|information)\b", r"\bdata\s+process",
            r"\bdata\s+secur",
        ],
    },
    "warranty": {
        "label": "Warranty / Guarantee",
        "icon": "✅",
        "description": "Promises about product/service quality",
        "keywords": [
            r"\bwarrant", r"\bguarantee", r"\brepresentation[s]?\b",
            r"\bfit\s+for\s+purpose\b", r"\bworkmanlike\b", r"\bdefect",
        ],
    },
    "non_compete": {
        "label": "Non-Compete / Non-Solicitation",
        "icon": "🚷",
        "description": "Restrictions on competitive activities",
        "keywords": [
            r"\bnon[\s-]?compet", r"\bnon[\s-]?solicit", r"\brestrict.*compet",
            r"\bnot\s+(?:directly|indirectly)\s+compet",
        ],
    },
}


# ── Public API ───────────────────────────────────────────


def detect_clauses(text: str, sentences: list) -> dict:
    """
    Detect which of the 12 clause types are present.

    Args:
        text: Full cleaned document text.
        sentences: List of sentences from the cleaner.

    Returns:
        dict with 'detected' (clause results) and 'summary' (counts).
    """
    text_lower = text.lower()
    detected = {}
    found = 0

    for cid, cdef in CLAUSES.items():
        matches = 0
        evidence = []
        for kw in cdef["keywords"]:
            hits = re.findall(kw, text_lower)
            matches += len(hits)
            # Extract evidence sentence for the first hit
            if hits and not evidence:
                for s in sentences:
                    if re.search(kw, s.lower()):
                        evidence.append(s[:150])
                        break

        is_found = matches >= 2  # require at least 2 keyword hits
        confidence = min(100, matches * 20) if is_found else 0

        if is_found:
            found += 1

        detected[cid] = {
            "id": cid,
            "label": cdef["label"],
            "icon": cdef["icon"],
            "description": cdef["description"],
            "found": is_found,
            "confidence": confidence,
            "match_count": matches,
            "evidence": evidence[0] if evidence else "",
        }

    return {
        "detected": detected,
        "summary": {
            "total_clauses": len(CLAUSES),
            "found_count": found,
            "missing_count": len(CLAUSES) - found,
            "coverage_pct": round(found / len(CLAUSES) * 100),
        },
    }

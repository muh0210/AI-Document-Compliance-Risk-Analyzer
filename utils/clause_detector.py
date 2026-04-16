"""
Clause Detection Engine v2.0
All regex compiled at module load.
Context-aware: checks surrounding sentences for confidence boost.
"""

import re
import logging

log = logging.getLogger("compliance.clause")

# ── Clause definitions (compiled patterns) ───────────────

_CLAUSES = {}


def _def(key, label, desc, patterns):
    _CLAUSES[key] = {
        "label": label,
        "description": desc,
        "patterns": [re.compile(p, re.IGNORECASE) for p in patterns],
    }


_def("payment_terms", "Payment Terms",
     "Defines amounts, schedules, methods, late penalties",
     [r"\bpayment\b", r"\binvoice\b", r"\bfees?\b", r"\bcompensation\b",
      r"\b\d+\s*%", r"\bdue\s+(?:date|within)\b", r"\bnet\s*\d+\b",
      r"\bpayable\b", r"\blate\s+(?:fee|penalty)\b"])

_def("termination", "Termination Clause",
     "Specifies how and when the agreement can be ended",
     [r"\bterminate?\b", r"\bcancell?ation\b", r"\bnotice\s+period\b",
      r"\b(?:30|60|90)\s*(?:day|calendar)\b", r"\bread\s+notice\b",
      r"\bexit\s+clause\b"])

_def("liability", "Liability Limitation",
     "Caps financial exposure between parties",
     [r"\bliabilit(?:y|ies)\b", r"\blimit(?:ation|ed)\b",
      r"\bcap\b", r"\bdam(?:age|ages)\b", r"\bindirect\s+dam",
      r"\bconsequential\b"])

_def("confidentiality", "Confidentiality / NDA",
     "Protects sensitive and proprietary information",
     [r"\bconfidential", r"\bnon[\s-]?disclosure\b", r"\bproprietary\b",
      r"\btrade\s+secret", r"\bsensitive\s+information\b"])

_def("ip_rights", "Intellectual Property",
     "Assigns IP ownership of created work",
     [r"\bintellectual\s+property\b", r"\bcopyright\b", r"\bpatent\b",
      r"\btrademark\b", r"\blicen[sc]e\b", r"\bownership\b",
      r"\bwork[\s-]?for[\s-]?hire\b"])

_def("indemnification", "Indemnification",
     "Protection against third-party claims",
     [r"\bindemn", r"\bhold\s+harmless\b", r"\bdefend\b.*\bclaim",
      r"\bthird[\s-]?party\s+claim\b"])

_def("dispute_resolution", "Dispute Resolution",
     "Process for resolving disagreements",
     [r"\bdispute\b", r"\barbitrat", r"\bmediat", r"\bjurisdiction\b",
      r"\blitigation\b", r"\bcourt\b"])

_def("governing_law", "Governing Law",
     "Which legal jurisdiction applies",
     [r"\bgoverning\s+law\b", r"\bjurisdiction\b", r"\blaws?\s+of\b",
      r"\bapplicable\s+law\b", r"\bvenue\b"])

_def("force_majeure", "Force Majeure",
     "Protection against extraordinary events",
     [r"\bforce\s+majeure\b", r"\bact\s+of\s+god\b", r"\bunforeseen\b",
      r"\bextraordinary\b", r"\bbeyond.*control\b"])

_def("data_protection", "Data Protection",
     "Personal data handling and regulatory compliance",
     [r"\bdata\s+protect", r"\bgdpr\b", r"\bccpa\b", r"\bprivacy\b",
      r"\bpersonal\s+(?:data|information)\b", r"\bdata\s+breach\b"])

_def("warranty", "Warranty",
     "Quality assurance and fitness guarantees",
     [r"\bwarrant(?:y|ies)\b", r"\brepresentation", r"\bas[\s-]?is\b",
      r"\bfit(?:ness)?\s+for\b", r"\bmerchantab"])

_def("non_compete", "Non-Compete / Non-Solicitation",
     "Restrictions on competitive activity",
     [r"\bnon[\s-]?compete?\b", r"\bnon[\s-]?solicitat", r"\brestrictive\s+covenant\b",
      r"\bcompetit(?:ive|or)\b.*\brestrict"])


def detect_clauses(text: str, sentences: list) -> dict:
    """
    Detect all 12 clause types with context-aware confidence.

    Checks both full text AND surrounding sentence context.
    """
    detected = {}
    text_lower = text.lower()

    for cid, cdef in _CLAUSES.items():
        total_hits = 0
        evidence = []

        # Full-text pattern scan
        for pat in cdef["patterns"]:
            matches = pat.findall(text_lower)
            total_hits += len(matches)
            for m in matches[:2]:
                evidence.append(m)

        # Sentence-level context scan: find which sentences contain patterns
        matching_sents = []
        for sent in sentences:
            for pat in cdef["patterns"]:
                if pat.search(sent):
                    matching_sents.append(sent[:120])
                    break

        # Context boost: if multiple consecutive sentences match → stronger
        context_bonus = min(3, len(matching_sents)) * 5

        is_found = total_hits >= 2
        confidence = min(100, total_hits * 10 + context_bonus) if is_found else 0

        detected[cid] = {
            "label": cdef["label"],
            "description": cdef["description"],
            "found": is_found,
            "confidence": confidence,
            "match_count": total_hits,
            "evidence": matching_sents[:2] if matching_sents else evidence[:2],
        }

    found = sum(1 for d in detected.values() if d["found"])
    total = len(detected)
    log.info("Clauses: %d/%d found", found, total)

    return {
        "detected": detected,
        "summary": {
            "total_clauses": total,
            "found_count": found,
            "missing_count": total - found,
            "coverage_pct": round(found / total * 100) if total else 0,
        },
    }

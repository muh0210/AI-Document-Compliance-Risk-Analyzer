"""
Text Cleaning & NLP Segmentation Module
Cleans raw text and splits it into sentences, paragraphs, and headers.
spaCy model is loaded once and cached for the lifetime of the process.
"""

import re

# ── Module-level spaCy cache ─────────────────────────────
_nlp = None
_nlp_tried = False


def _get_nlp():
    global _nlp, _nlp_tried
    if not _nlp_tried:
        _nlp_tried = True
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = None
    return _nlp


# ── Public API ───────────────────────────────────────────


def clean_text(text: str) -> dict:
    """
    Clean and segment the input text.

    Returns dict with keys:
        original, cleaned, sentences, paragraphs, section_headers
    """
    if not text or not text.strip():
        return {"original": "", "cleaned": "", "sentences": [],
                "paragraphs": [], "section_headers": []}

    original = text.strip()
    cleaned = _remove_noise(original)
    cleaned = _normalise(cleaned)

    return {
        "original": original,
        "cleaned": cleaned,
        "sentences": _split_sentences(cleaned),
        "paragraphs": _split_paragraphs(cleaned),
        "section_headers": _detect_headers(original),
    }


# ── Cleaning helpers ─────────────────────────────────────


def _remove_noise(text: str) -> str:
    text = re.sub(r"[\u2022\u25cf\u25cb\u25a0\u25a1\u25ba\u25b8\u25b9\u25c6\u25c7]", "", text)
    text = re.sub(r"[Pp]age\s+\d+(\s*of\s*\d+)?", "", text)
    return text


def _normalise(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(ln.strip() for ln in text.split("\n"))


# ── Sentence splitting ───────────────────────────────────


def _split_sentences(text: str) -> list:
    nlp = _get_nlp()
    if nlp is None:
        return _regex_sentences(text)
    try:
        max_len = 100_000
        if len(text) > max_len:
            sents = []
            for i in range(0, len(text), max_len):
                doc = nlp(text[i : i + max_len])
                sents.extend(s.text.strip() for s in doc.sents if s.text.strip())
            return sents
        doc = nlp(text)
        return [s.text.strip() for s in doc.sents if s.text.strip()]
    except Exception:
        return _regex_sentences(text)


def _regex_sentences(text: str) -> list:
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [s.strip() for s in raw if s.strip() and len(s.strip()) > 5]


# ── Paragraph splitting ──────────────────────────────────


def _split_paragraphs(text: str) -> list:
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 10]


# ── Header detection ─────────────────────────────────────


def _detect_headers(text: str) -> list:
    headers = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if s.isupper() and 3 < len(s) < 100:
            headers.append(s)
        elif re.match(r"^(\d+[.)]\s+|[Ss]ection\s+\d+|[Aa]rticle\s+\d+|[Cc]lause\s+\d+)", s):
            headers.append(s[:80])
        elif len(s) < 60 and not s.endswith((".", ",", ";")) and i + 1 < len(lines) and not lines[i + 1].strip():
            headers.append(s)
    return headers

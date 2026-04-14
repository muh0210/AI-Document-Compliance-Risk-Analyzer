"""
Text Cleaning & Normalization Module
Prepares raw extracted text for NLP analysis.
"""

import re


def clean_text(text):
    """
    Clean and normalize text for analysis.
    Returns both the cleaned version (for analysis) and original (for display).
    
    Args:
        text: Raw extracted text string
    
    Returns:
        dict: {
            'original': str,
            'cleaned': str,
            'sentences': list[str],
            'paragraphs': list[str],
            'section_headers': list[str]
        }
    """
    original = text.strip()
    
    # Step 1: Remove special characters that aren't punctuation
    cleaned = _remove_noise(original)
    
    # Step 2: Normalize whitespace
    cleaned = _normalize_spacing(cleaned)
    
    # Step 3: Split into logical segments
    sentences = split_sentences(cleaned)
    paragraphs = split_paragraphs(cleaned)
    section_headers = detect_section_headers(original)
    
    return {
        'original': original,
        'cleaned': cleaned,
        'sentences': sentences,
        'paragraphs': paragraphs,
        'section_headers': section_headers
    }


def _remove_noise(text):
    """Remove non-informative characters while preserving meaning."""
    # Remove bullet point symbols
    text = re.sub(r'[•●○■□►▸▹◆◇]', '', text)
    # Remove excessive special characters
    text = re.sub(r'[^\w\s.,;:!?\'\"()\-/%$@#&+=\[\]{}]', '', text)
    # Remove page numbers like "Page 1 of 10"
    text = re.sub(r'[Pp]age\s+\d+\s*(of\s*\d+)?', '', text)
    return text


def _normalize_spacing(text):
    """Normalize whitespace for consistent processing."""
    # Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespace on each line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines)


def split_sentences(text):
    """
    Split text into sentences using spaCy if available, 
    fallback to regex-based splitting.
    """
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return _regex_sentence_split(text)
        
        # Process in chunks to handle large documents
        max_length = 100000
        if len(text) > max_length:
            chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            sentences = []
            for chunk in chunks:
                doc = nlp(chunk)
                sentences.extend([sent.text.strip() for sent in doc.sents if sent.text.strip()])
            return sentences
        
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except ImportError:
        return _regex_sentence_split(text)


def _regex_sentence_split(text):
    """Fallback regex-based sentence splitting."""
    # Split on sentence-ending punctuation followed by space and capital letter
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in raw if s.strip() and len(s.strip()) > 5]


def split_paragraphs(text):
    """Split text into paragraphs based on double newlines."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 10]


def detect_section_headers(text):
    """Detect potential section headers in the document."""
    headers = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        # Pattern: ALL CAPS line (likely a header)
        if stripped.isupper() and len(stripped) > 3 and len(stripped) < 100:
            headers.append(stripped)
            continue
        
        # Pattern: Numbered section like "1. Introduction" or "Section 1:"
        if re.match(r'^(\d+[\.\)]\s+|[Ss]ection\s+\d+|[Aa]rticle\s+\d+|[Cc]lause\s+\d+)', stripped):
            headers.append(stripped[:80])
            continue
        
        # Pattern: Short line followed by empty line (potential header)
        if len(stripped) < 60 and not stripped.endswith(('.', ',', ';')):
            if i + 1 < len(lines) and not lines[i + 1].strip():
                headers.append(stripped)
    
    return headers

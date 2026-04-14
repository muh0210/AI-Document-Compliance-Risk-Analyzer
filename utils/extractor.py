"""
Document Text Extraction Module
Handles PDF, DOCX, and TXT file ingestion with robust error handling.
"""

import os
import io


def extract_text(file_storage):
    """
    Extract text from an uploaded file (Flask FileStorage object).
    Supports PDF, DOCX, and TXT formats.
    
    Args:
        file_storage: Flask FileStorage object from request.files
    
    Returns:
        dict: {
            'text': str,
            'filename': str,
            'file_type': str,
            'page_count': int or None,
            'word_count': int,
            'char_count': int
        }
    """
    filename = file_storage.filename
    ext = os.path.splitext(filename)[1].lower()
    
    extractors = {
        '.pdf': _extract_pdf,
        '.docx': _extract_docx,
        '.doc': _extract_docx,
        '.txt': _extract_txt,
    }
    
    extractor = extractors.get(ext)
    if not extractor:
        raise ValueError(f"Unsupported file format: {ext}. Supported: PDF, DOCX, TXT")
    
    file_bytes = file_storage.read()
    text, page_count = extractor(file_bytes)
    
    # Clean up excessive whitespace
    text = _normalize_whitespace(text)
    
    words = text.split()
    return {
        'text': text,
        'filename': filename,
        'file_type': ext.replace('.', '').upper(),
        'page_count': page_count,
        'word_count': len(words),
        'char_count': len(text)
    }


def _extract_pdf(file_bytes):
    """Extract text from PDF bytes."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text.strip())
        return '\n\n'.join(pages), len(reader.pages)
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {str(e)}")


def _extract_docx(file_bytes):
    """Extract text from DOCX bytes."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return '\n\n'.join(paragraphs), None
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX text: {str(e)}")


def _extract_txt(file_bytes):
    """Extract text from TXT bytes."""
    try:
        # Try UTF-8 first, then fallback encodings
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                text = file_bytes.decode(encoding)
                return text.strip(), None
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode text file with any supported encoding")
    except Exception as e:
        raise ValueError(f"Failed to extract TXT text: {str(e)}")


def _normalize_whitespace(text):
    """Normalize excessive whitespace while preserving paragraph breaks."""
    import re
    # Replace 3+ newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Clean up lines
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines)

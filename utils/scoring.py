"""
Compliance Scoring Engine
Produces a weighted compliance score based on clause coverage,
risk density, structure quality, and language clarity.
"""


def compliance_score(clause_result, risk_result, cleaned_data):
    """
    Calculate comprehensive compliance score.
    
    Scoring weights:
      - Clause Coverage: 40%
      - Risk Density: 30%
      - Document Structure: 20%
      - Language Clarity: 10%
    
    Args:
        clause_result: Output from clause_detector.detect_clauses()
        risk_result: Output from risk_engine.detect_risks()
        cleaned_data: Output from cleaner.clean_text()
    
    Returns:
        dict: {
            'score': int (0-100),
            'grade': str (A+ to F),
            'label': str,
            'color': str (hex),
            'breakdown': {
                'clause_coverage': {'score': int, 'max': 40, 'details': str},
                'risk_density': {'score': int, 'max': 30, 'details': str},
                'structure': {'score': int, 'max': 20, 'details': str},
                'clarity': {'score': int, 'max': 10, 'details': str},
            },
            'recommendations_count': int
        }
    """
    breakdown = {}
    
    # ── 1. Clause Coverage (40 points max) ──
    clause_coverage = _score_clause_coverage(clause_result)
    breakdown['clause_coverage'] = clause_coverage
    
    # ── 2. Risk Density (30 points max) ──
    risk_density = _score_risk_density(risk_result)
    breakdown['risk_density'] = risk_density
    
    # ── 3. Document Structure (20 points max) ──
    structure = _score_structure(cleaned_data)
    breakdown['structure'] = structure
    
    # ── 4. Language Clarity (10 points max) ──
    clarity = _score_clarity(risk_result)
    breakdown['clarity'] = clarity
    
    # ── Total Score ──
    total = (clause_coverage['score'] + risk_density['score'] + 
             structure['score'] + clarity['score'])
    total = max(0, min(100, total))
    
    grade, label, color = _get_grade(total)
    
    return {
        'score': total,
        'grade': grade,
        'label': label,
        'color': color,
        'breakdown': breakdown,
        'recommendations_count': (
            clause_result['summary']['missing_count'] + 
            risk_result['summary']['total_risks']
        )
    }


def _score_clause_coverage(clause_result):
    """Score based on presence of important clauses (40 points max)."""
    detected = clause_result['detected']
    total_weight = sum(c['weight'] for c in detected.values())
    found_weight = sum(c['weight'] for c in detected.values() if c['found'])
    
    if total_weight == 0:
        ratio = 0
    else:
        ratio = found_weight / total_weight
    
    score = round(ratio * 40)
    
    coverage_pct = clause_result['summary']['coverage_pct']
    found = clause_result['summary']['found_count']
    total = clause_result['summary']['total_clauses']
    
    return {
        'score': score,
        'max': 40,
        'details': f"{found}/{total} clauses detected ({coverage_pct}% coverage)"
    }


def _score_risk_density(risk_result):
    """Score based on risk count and severity (30 points max, inverted)."""
    summary = risk_result['summary']
    
    # Start with full points, subtract for risks
    score = 30
    score -= summary['high'] * 5      # -5 per HIGH risk
    score -= summary['medium'] * 2    # -2 per MEDIUM risk
    score -= summary['low'] * 1       # -1 per LOW risk
    
    score = max(0, score)
    
    total = summary['total_risks']
    density = summary['risk_density']
    details = f"{total} risks found (density: {density} per sentence)"
    if summary['high'] > 0:
        details += f" — {summary['high']} HIGH severity"
    
    return {
        'score': score,
        'max': 30,
        'details': details
    }


def _score_structure(cleaned_data):
    """Score document structure quality (20 points max)."""
    score = 0
    details_parts = []
    
    # Has section headers
    headers = cleaned_data.get('section_headers', [])
    if len(headers) >= 3:
        score += 8
        details_parts.append(f"{len(headers)} section headers")
    elif len(headers) >= 1:
        score += 4
        details_parts.append(f"Only {len(headers)} section header(s)")
    else:
        details_parts.append("No section headers detected")
    
    # Has multiple paragraphs (well-organized)
    paragraphs = cleaned_data.get('paragraphs', [])
    if len(paragraphs) >= 5:
        score += 6
        details_parts.append(f"{len(paragraphs)} paragraphs")
    elif len(paragraphs) >= 2:
        score += 3
        details_parts.append(f"Only {len(paragraphs)} paragraph(s)")
    else:
        details_parts.append("Minimal paragraph structure")
    
    # Adequate length
    sentences = cleaned_data.get('sentences', [])
    if len(sentences) >= 20:
        score += 6
        details_parts.append("Adequate document length")
    elif len(sentences) >= 10:
        score += 3
        details_parts.append("Short document")
    else:
        details_parts.append("Very short document")
    
    return {
        'score': min(20, score),
        'max': 20,
        'details': ' | '.join(details_parts)
    }


def _score_clarity(risk_result):
    """Score language clarity (10 points max)."""
    vague_count = sum(
        1 for r in risk_result['risks']
        if r['category'] in ('vague_language', 'weak_enforcement')
    )
    
    score = 10
    score -= vague_count * 1  # -1 per vague/weak language instance
    score = max(0, score)
    
    if vague_count == 0:
        details = "Clear, precise language throughout"
    elif vague_count <= 3:
        details = f"{vague_count} instances of unclear language"
    else:
        details = f"{vague_count} instances of vague/weak language detected"
    
    return {
        'score': score,
        'max': 10,
        'details': details
    }


def _get_grade(score):
    """Convert numeric score to letter grade, label, and color."""
    if score >= 95:
        return 'A+', 'Excellent Compliance', '#00E676'
    elif score >= 90:
        return 'A', 'Strong Compliance', '#00E676'
    elif score >= 85:
        return 'A-', 'Very Good Compliance', '#69F0AE'
    elif score >= 80:
        return 'B+', 'Good Compliance', '#B2FF59'
    elif score >= 75:
        return 'B', 'Above Average', '#EEFF41'
    elif score >= 70:
        return 'B-', 'Satisfactory', '#FFFF00'
    elif score >= 65:
        return 'C+', 'Needs Improvement', '#FFD740'
    elif score >= 60:
        return 'C', 'Below Average', '#FFAB40'
    elif score >= 55:
        return 'C-', 'Poor Compliance', '#FF9100'
    elif score >= 50:
        return 'D+', 'Significant Issues', '#FF6E40'
    elif score >= 40:
        return 'D', 'Major Deficiencies', '#FF5252'
    elif score >= 30:
        return 'D-', 'Critical Deficiencies', '#FF1744'
    else:
        return 'F', 'Non-Compliant', '#D50000'

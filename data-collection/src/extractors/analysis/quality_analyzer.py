"""
Quality analysis for Legal RAG Extraction System (Phase 3)
Multi-dimensional quality scoring and validation
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

from ..base_extractor import SimpleExtractor
from ..schemas import QualityAnalysisResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


# Quality thresholds
QUALITY_THRESHOLDS = {
    'excellent': 0.90,
    'good': 0.75,
    'acceptable': 0.60,
    'poor': 0.40,
    'unacceptable': 0.0
}

# Validation status thresholds
VALIDATION_THRESHOLDS = {
    'valid': 0.75,
    'needs_review': 0.50,
    'invalid': 0.0
}


class QualityAnalyzer(SimpleExtractor):
    """
    Multi-dimensional quality analyzer for legal document extractions.

    Quality Dimensions:
    1. Completeness (0-1): Presence of key metadata fields
    2. Citation Quality (0-1): Quality of extracted citations
    3. Text Quality (0-1): Quality of text extraction
    4. Metadata Quality (0-1): Validation of extracted metadata
    5. Consistency (0-1): Logical consistency of data

    Overall Score: Weighted average of dimensions
    """

    def __init__(self):
        super().__init__(name="QualityAnalyzer")

        # Dimension weights (must sum to 1.0)
        self.weights = {
            'completeness': 0.25,
            'citation_quality': 0.20,
            'text_quality': 0.20,
            'metadata_quality': 0.20,
            'consistency': 0.15
        }

    def _extract_impl(self, extraction_result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze quality of extraction result.

        Args:
            extraction_result: Complete extraction result with all components
            **kwargs: Additional parameters
                - strict: Use strict scoring (default False)
                - custom_weights: Override dimension weights

        Returns:
            QualityAnalysisResult dict
        """
        strict = kwargs.get('strict', False)
        custom_weights = kwargs.get('custom_weights', None)

        if custom_weights:
            self.weights = custom_weights

        # Calculate dimension scores
        dimension_scores = {
            'completeness': self._score_completeness(extraction_result),
            'citation_quality': self._score_citation_quality(extraction_result),
            'text_quality': self._score_text_quality(extraction_result),
            'metadata_quality': self._score_metadata_quality(extraction_result),
            'consistency': self._score_consistency(extraction_result)
        }

        # Calculate overall score
        overall_score = sum(
            score * self.weights[dimension]
            for dimension, score in dimension_scores.items()
        )

        # Determine validation status
        validation_status = self._determine_validation_status(overall_score, strict)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            dimension_scores,
            extraction_result
        )

        # Determine if manual review needed
        needs_manual_review = self._needs_manual_review(
            overall_score,
            dimension_scores,
            extraction_result
        )

        # Quality grade
        quality_grade = self._get_quality_grade(overall_score)

        return {
            'status': 'success',
            'data': {
                'overall_score': round(overall_score, 4),
                'quality_grade': quality_grade,
                'validation_status': validation_status,
                'needs_manual_review': needs_manual_review,
                'dimension_scores': {
                    k: round(v, 4) for k, v in dimension_scores.items()
                },
                'recommendations': recommendations,
                'weights_used': self.weights
            }
        }

    # ==================== Dimension 1: Completeness ====================

    def _score_completeness(self, result: Dict[str, Any]) -> float:
        """
        Score completeness of extracted metadata.

        Checks for:
        - Title
        - Citations (at least 1)
        - Parties (petitioner and respondent)
        - Judges (at least 1)
        - Dates (judgment date minimum)
        - Sections cited
        - Keywords
        - Subject classification

        Args:
            result: Extraction result

        Returns:
            Completeness score (0-1)
        """
        score = 0.0
        max_score = 8.0  # 8 components

        # Title
        if result.get('title'):
            score += 1.0

        # Citations
        citations = result.get('citations', [])
        if citations:
            score += 1.0

        # Parties
        parties = result.get('parties', {})
        if parties.get('petitioner') and parties.get('respondent'):
            score += 1.0
        elif parties.get('petitioner') or parties.get('respondent'):
            score += 0.5

        # Judges
        judges = result.get('judges', [])
        if judges:
            score += 1.0

        # Dates
        dates = result.get('dates', {})
        if dates.get('judgment_date'):
            score += 1.0
        elif dates.get('filing_date') or dates.get('hearing_date'):
            score += 0.5

        # Sections
        sections = result.get('sections_cited', [])
        if sections:
            score += 1.0

        # Keywords
        keywords = result.get('keywords', [])
        if keywords and len(keywords) >= 5:
            score += 1.0
        elif keywords:
            score += 0.5

        # Subject
        subject = result.get('subject_classification', {})
        if subject.get('primary_subject'):
            score += 1.0

        return score / max_score

    # ==================== Dimension 2: Citation Quality ====================

    def _score_citation_quality(self, result: Dict[str, Any]) -> float:
        """
        Score quality of extracted citations.

        Checks:
        - Average confidence score
        - Primary citation present
        - Citation encoding valid
        - Reporter recognized

        Args:
            result: Extraction result

        Returns:
            Citation quality score (0-1)
        """
        citations = result.get('citations', [])

        if not citations:
            return 0.0

        score = 0.0
        max_score = 4.0

        # 1. Average confidence
        confidences = [c.get('confidence', 0.0) for c in citations]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        score += avg_confidence

        # 2. Primary citation
        has_primary = any(c.get('is_primary', False) for c in citations)
        if has_primary:
            score += 1.0

        # 3. Citation encoding
        encoded_citations = [c for c in citations if c.get('citation_encoded')]
        if len(encoded_citations) == len(citations):
            score += 1.0
        elif encoded_citations:
            score += 0.5

        # 4. Reporter recognized
        recognized_reporters = [c for c in citations if c.get('reporter')]
        if len(recognized_reporters) == len(citations):
            score += 1.0
        elif recognized_reporters:
            score += 0.5

        return score / max_score

    # ==================== Dimension 3: Text Quality ====================

    def _score_text_quality(self, result: Dict[str, Any]) -> float:
        """
        Score quality of extracted text.

        Checks:
        - Text length (not too short)
        - OCR confidence (if applicable)
        - Text structure (paragraphs, sentences)
        - Special characters ratio

        Args:
            result: Extraction result

        Returns:
            Text quality score (0-1)
        """
        text = result.get('full_text', '')

        if not text:
            return 0.0

        score = 0.0
        max_score = 4.0

        # 1. Text length
        if len(text) >= 5000:
            score += 1.0
        elif len(text) >= 1000:
            score += 0.7
        elif len(text) >= 500:
            score += 0.4
        else:
            score += 0.2

        # 2. OCR confidence
        ocr_confidence = result.get('ocr_confidence', None)
        if ocr_confidence is not None:
            score += ocr_confidence
        else:
            score += 1.0  # Assume good if not OCR

        # 3. Text structure
        paragraphs = text.split('\n\n')
        sentences = re.split(r'[.!?]+', text)

        if len(paragraphs) >= 10 and len(sentences) >= 50:
            score += 1.0
        elif len(paragraphs) >= 5 and len(sentences) >= 20:
            score += 0.7
        else:
            score += 0.4

        # 4. Special characters ratio
        special_chars = len(re.findall(r'[^\w\s.,;:!?()-]', text))
        special_ratio = special_chars / len(text) if text else 1.0

        if special_ratio < 0.05:
            score += 1.0
        elif special_ratio < 0.10:
            score += 0.7
        else:
            score += 0.4

        return score / max_score

    # ==================== Dimension 4: Metadata Quality ====================

    def _score_metadata_quality(self, result: Dict[str, Any]) -> float:
        """
        Score quality of metadata validation.

        Checks:
        - Date formats valid
        - Year in valid range
        - Party names not empty
        - Judge names not empty
        - Section references valid

        Args:
            result: Extraction result

        Returns:
            Metadata quality score (0-1)
        """
        score = 0.0
        max_score = 5.0

        # 1. Date formats
        dates = result.get('dates', {})
        valid_dates = 0
        total_dates = 0

        for date_type in ['judgment_date', 'filing_date', 'hearing_date']:
            date_str = dates.get(date_type)
            if date_str:
                total_dates += 1
                if self._is_valid_date_format(date_str):
                    valid_dates += 1

        if total_dates > 0:
            score += (valid_dates / total_dates)
        else:
            score += 0.5  # Neutral if no dates

        # 2. Year validation
        year = result.get('year')
        if year and 1800 <= year <= datetime.now().year:
            score += 1.0
        elif year:
            score += 0.3
        else:
            score += 0.5  # Neutral if missing

        # 3. Party names
        parties = result.get('parties', {})
        petitioner = parties.get('petitioner', [])
        respondent = parties.get('respondent', [])

        if petitioner and respondent:
            # Check not just empty strings
            valid_petitioner = any(len(p.strip()) > 2 for p in petitioner)
            valid_respondent = any(len(r.strip()) > 2 for r in respondent)

            if valid_petitioner and valid_respondent:
                score += 1.0
            elif valid_petitioner or valid_respondent:
                score += 0.5
        else:
            score += 0.3

        # 4. Judge names
        judges = result.get('judges', [])
        if judges:
            valid_judges = [j for j in judges if j.get('name') and len(j['name']) > 2]
            if len(valid_judges) == len(judges):
                score += 1.0
            elif valid_judges:
                score += 0.6
        else:
            score += 0.5  # Neutral if missing

        # 5. Section references
        sections = result.get('sections_cited', [])
        if sections:
            valid_sections = [
                s for s in sections
                if s.get('section_number') and s.get('act_name')
            ]
            if len(valid_sections) == len(sections):
                score += 1.0
            elif valid_sections:
                score += 0.6
        else:
            score += 0.5  # Neutral if missing

        return score / max_score

    # ==================== Dimension 5: Consistency ====================

    def _score_consistency(self, result: Dict[str, Any]) -> float:
        """
        Score logical consistency of extracted data.

        Checks:
        - Date ordering (filing < hearing < judgment)
        - Year consistency across dates
        - Citation year matches document year
        - Title matches parties
        - Court consistency

        Args:
            result: Extraction result

        Returns:
            Consistency score (0-1)
        """
        score = 0.0
        max_score = 5.0

        # 1. Date ordering
        dates = result.get('dates', {})
        if self._check_date_ordering(dates):
            score += 1.0
        else:
            score += 0.5  # Partial if not all dates present

        # 2. Year consistency
        if self._check_year_consistency(result):
            score += 1.0
        else:
            score += 0.3

        # 3. Citation year matches
        if self._check_citation_year_match(result):
            score += 1.0
        else:
            score += 0.5

        # 4. Title-parties match
        if self._check_title_parties_match(result):
            score += 1.0
        else:
            score += 0.5

        # 5. Court consistency
        if self._check_court_consistency(result):
            score += 1.0
        else:
            score += 0.5

        return score / max_score

    # ==================== Validation Helpers ====================

    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date is in ISO format (YYYY-MM-DD)."""
        try:
            datetime.fromisoformat(date_str)
            return True
        except (ValueError, TypeError):
            return False

    def _check_date_ordering(self, dates: Dict[str, str]) -> bool:
        """Check if dates are in logical order."""
        filing = dates.get('filing_date')
        hearing = dates.get('hearing_date')
        judgment = dates.get('judgment_date')

        # If all three present, check order
        if filing and hearing and judgment:
            try:
                filing_dt = datetime.fromisoformat(filing)
                hearing_dt = datetime.fromisoformat(hearing)
                judgment_dt = datetime.fromisoformat(judgment)

                return filing_dt <= hearing_dt <= judgment_dt
            except ValueError:
                return False

        # If not all present, consider it consistent
        return True

    def _check_year_consistency(self, result: Dict[str, Any]) -> bool:
        """Check if years are consistent across dates."""
        year = result.get('year')
        dates = result.get('dates', {})

        if not year:
            return True  # Can't check

        for date_str in dates.values():
            if date_str:
                try:
                    date_year = datetime.fromisoformat(date_str).year
                    if abs(date_year - year) > 1:  # Allow 1 year difference
                        return False
                except ValueError:
                    continue

        return True

    def _check_citation_year_match(self, result: Dict[str, Any]) -> bool:
        """Check if primary citation year matches document year."""
        year = result.get('year')
        citations = result.get('citations', [])

        if not year or not citations:
            return True  # Can't check

        primary_citations = [c for c in citations if c.get('is_primary')]

        if primary_citations:
            citation = primary_citations[0]
            citation_year = citation.get('year')

            if citation_year:
                return abs(citation_year - year) <= 1

        return True

    def _check_title_parties_match(self, result: Dict[str, Any]) -> bool:
        """Check if title contains party names."""
        title = result.get('title', '')
        parties = result.get('parties', {})

        if not title or not parties:
            return True  # Can't check

        petitioner = parties.get('petitioner', [])
        respondent = parties.get('respondent', [])

        # Check if at least one party appears in title
        all_parties = petitioner + respondent

        for party in all_parties:
            if party and party.lower() in title.lower():
                return True

        return False

    def _check_court_consistency(self, result: Dict[str, Any]) -> bool:
        """Check if court is consistent across citations."""
        citations = result.get('citations', [])

        if len(citations) <= 1:
            return True

        courts = [c.get('court') for c in citations if c.get('court')]

        if not courts:
            return True

        # All courts should be the same
        return len(set(courts)) == 1

    # ==================== Status Determination ====================

    def _determine_validation_status(self, overall_score: float, strict: bool) -> str:
        """
        Determine validation status based on score.

        Args:
            overall_score: Overall quality score
            strict: Use strict thresholds

        Returns:
            'valid', 'needs_review', or 'invalid'
        """
        if strict:
            valid_threshold = 0.85
            review_threshold = 0.70
        else:
            valid_threshold = VALIDATION_THRESHOLDS['valid']
            review_threshold = VALIDATION_THRESHOLDS['needs_review']

        if overall_score >= valid_threshold:
            return 'valid'
        elif overall_score >= review_threshold:
            return 'needs_review'
        else:
            return 'invalid'

    def _get_quality_grade(self, overall_score: float) -> str:
        """Get quality grade label."""
        if overall_score >= QUALITY_THRESHOLDS['excellent']:
            return 'excellent'
        elif overall_score >= QUALITY_THRESHOLDS['good']:
            return 'good'
        elif overall_score >= QUALITY_THRESHOLDS['acceptable']:
            return 'acceptable'
        elif overall_score >= QUALITY_THRESHOLDS['poor']:
            return 'poor'
        else:
            return 'unacceptable'

    # ==================== Recommendations ====================

    def _generate_recommendations(
        self,
        dimension_scores: Dict[str, float],
        result: Dict[str, Any]
    ) -> List[str]:
        """
        Generate automated recommendations for improvement.

        Args:
            dimension_scores: Scores for each dimension
            result: Extraction result

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Completeness recommendations
        if dimension_scores['completeness'] < 0.7:
            missing = []
            if not result.get('title'):
                missing.append('title')
            if not result.get('citations'):
                missing.append('citations')
            if not result.get('parties', {}).get('petitioner'):
                missing.append('petitioner')
            if not result.get('parties', {}).get('respondent'):
                missing.append('respondent')
            if not result.get('dates', {}).get('judgment_date'):
                missing.append('judgment date')

            if missing:
                recommendations.append(
                    f"Missing critical fields: {', '.join(missing)}"
                )

        # Citation quality recommendations
        if dimension_scores['citation_quality'] < 0.7:
            citations = result.get('citations', [])
            if citations:
                low_confidence = [
                    c for c in citations
                    if c.get('confidence', 0) < 0.8
                ]
                if low_confidence:
                    recommendations.append(
                        f"Review {len(low_confidence)} low-confidence citations"
                    )

        # Text quality recommendations
        if dimension_scores['text_quality'] < 0.7:
            text = result.get('full_text', '')
            if len(text) < 1000:
                recommendations.append(
                    "Text may be incomplete - verify PDF extraction"
                )
            if result.get('ocr_confidence', 1.0) < 0.8:
                recommendations.append(
                    "Low OCR confidence - consider manual verification"
                )

        # Metadata quality recommendations
        if dimension_scores['metadata_quality'] < 0.7:
            recommendations.append(
                "Review and validate extracted metadata fields"
            )

        # Consistency recommendations
        if dimension_scores['consistency'] < 0.7:
            recommendations.append(
                "Check for logical inconsistencies in dates and references"
            )

        return recommendations

    def _needs_manual_review(
        self,
        overall_score: float,
        dimension_scores: Dict[str, float],
        result: Dict[str, Any]
    ) -> bool:
        """
        Determine if manual review is needed.

        Criteria:
        - Overall score < 0.70
        - Any dimension < 0.50
        - OCR confidence < 0.80
        - Missing critical fields

        Args:
            overall_score: Overall quality score
            dimension_scores: Individual dimension scores
            result: Extraction result

        Returns:
            True if manual review needed
        """
        # Check overall score
        if overall_score < 0.70:
            return True

        # Check any dimension very low
        if any(score < 0.50 for score in dimension_scores.values()):
            return True

        # Check OCR confidence
        if result.get('ocr_confidence', 1.0) < 0.80:
            return True

        # Check critical fields
        if not result.get('title'):
            return True

        if not result.get('dates', {}).get('judgment_date'):
            return True

        return False


# ==================== Convenience Functions ====================

def analyze_quality(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick quality analysis (convenience function).

    Args:
        extraction_result: Complete extraction result

    Returns:
        Quality analysis data
    """
    analyzer = QualityAnalyzer()
    result = analyzer.extract(extraction_result)
    return result.get('data', {})


def get_quality_score(extraction_result: Dict[str, Any]) -> float:
    """
    Get overall quality score only.

    Args:
        extraction_result: Complete extraction result

    Returns:
        Quality score (0-1)
    """
    analysis = analyze_quality(extraction_result)
    return analysis.get('overall_score', 0.0)


def is_valid_extraction(
    extraction_result: Dict[str, Any],
    strict: bool = False
) -> bool:
    """
    Check if extraction is valid.

    Args:
        extraction_result: Complete extraction result
        strict: Use strict validation

    Returns:
        True if valid
    """
    analyzer = QualityAnalyzer()
    result = analyzer.extract(extraction_result, strict=strict)
    status = result.get('data', {}).get('validation_status')

    return status == 'valid'


def get_quality_report(extraction_result: Dict[str, Any]) -> str:
    """
    Get human-readable quality report.

    Args:
        extraction_result: Complete extraction result

    Returns:
        Quality report string
    """
    analysis = analyze_quality(extraction_result)

    report = f"""
Quality Analysis Report
=======================

Overall Score: {analysis['overall_score']:.2%}
Quality Grade: {analysis['quality_grade'].upper()}
Validation Status: {analysis['validation_status'].upper()}
Manual Review Needed: {'YES' if analysis['needs_manual_review'] else 'NO'}

Dimension Scores:
- Completeness: {analysis['dimension_scores']['completeness']:.2%}
- Citation Quality: {analysis['dimension_scores']['citation_quality']:.2%}
- Text Quality: {analysis['dimension_scores']['text_quality']:.2%}
- Metadata Quality: {analysis['dimension_scores']['metadata_quality']:.2%}
- Consistency: {analysis['dimension_scores']['consistency']:.2%}

Recommendations:
"""

    for i, rec in enumerate(analysis['recommendations'], 1):
        report += f"{i}. {rec}\n"

    if not analysis['recommendations']:
        report += "None - extraction quality is satisfactory.\n"

    return report.strip()

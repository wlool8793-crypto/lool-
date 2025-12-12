"""
Citation extraction for Legal RAG Extraction System (Phase 3)
Multi-pattern citation extraction with Phase 1 integration
"""

from typing import Dict, Any, List, Optional, Tuple
import re

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import CitationSchema, CitationExtractionResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class CitationExtractor(SimpleExtractor):
    """
    Citation extractor for legal documents.

    Extracts citations from:
    - Bangladesh (DLR, BLD, BLC, BCR, MLR)
    - India (AIR, SCC, SCR)
    - Pakistan (PLD, SCMR, CLC)

    Integrates with Phase 1 CitationEncoder for encoding.
    """

    def __init__(self):
        super().__init__(name="CitationExtractor")
        self.cache = get_pattern_cache()

        # Load citation patterns
        self.patterns = self.cache.load_pattern('citations.yaml')
        self.bangladesh_patterns = self.patterns.get('bangladesh', {})
        self.india_patterns = self.patterns.get('india', {})
        self.pakistan_patterns = self.patterns.get('pakistan', {})
        self.court_codes = self.patterns.get('court_codes', {})

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract all citations from text.

        Args:
            text: Document text
            **kwargs: Additional parameters

        Returns:
            CitationExtractionResult dict
        """
        all_citations = []

        # Extract from each region
        all_citations.extend(self._extract_bangladesh_citations(text))
        all_citations.extend(self._extract_india_citations(text))
        all_citations.extend(self._extract_pakistan_citations(text))

        # Sort by position in text and confidence
        all_citations.sort(key=lambda c: (-c['confidence'], text.find(c['citation_text'])))

        # Determine primary citation (first one, highest confidence)
        primary_citation = None
        if all_citations:
            all_citations[0]['is_primary'] = True
            primary_citation = all_citations[0]

        return {
            'status': 'success' if all_citations else 'partial',
            'data': {
                'citations': all_citations,
                'primary_citation': primary_citation,
                'total_citations': len(all_citations)
            }
        }

    # ==================== Bangladesh Citations ====================

    def _extract_bangladesh_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract Bangladesh citations (DLR, BLD, BLC, BCR, MLR)"""
        citations = []

        for reporter_code, reporter_info in self.bangladesh_patterns.items():
            pattern = reporter_info['pattern']
            full_name = reporter_info['full_name']

            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    citation = self._parse_bangladesh_citation(
                        match,
                        reporter_code,
                        reporter_info
                    )
                    if citation:
                        citations.append(citation)

                except Exception as e:
                    logger.warning(f"Failed to parse {reporter_code} citation: {e}")

        return citations

    def _parse_bangladesh_citation(
        self,
        match: re.Match,
        reporter_code: str,
        reporter_info: Dict
    ) -> Optional[Dict[str, Any]]:
        """Parse Bangladesh citation from regex match"""

        # Extract groups based on reporter
        if reporter_code == 'MLR':
            # MLR format: volume MLR (year) page
            volume = int(match.group(1))
            year = int(match.group(2))
            page = int(match.group(3))
            court = 'HCD'  # MLR is High Court Division
        else:
            # Standard format: volume (year) REPORTER (COURT) page
            volume = int(match.group(1))
            year = int(match.group(2))
            court = match.group(3)
            page = int(match.group(4))

        # Validate
        if not self._validate_year(year):
            return None

        # Encode citation (Phase 1 integration)
        citation_encoded = self._encode_citation(
            volume, year, reporter_code, court, page
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            volume, year, reporter_code, court, page
        )

        return {
            'citation_text': match.group(0),
            'citation_encoded': citation_encoded,
            'volume': volume,
            'year': year,
            'reporter': reporter_code,
            'court': court,
            'page': page,
            'is_primary': False,
            'confidence': confidence,
            'country': 'BD',
            'reporter_full_name': reporter_info['full_name']
        }

    # ==================== India Citations ====================

    def _extract_india_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract India citations (AIR, SCC, SCR)"""
        citations = []

        for reporter_code, reporter_info in self.india_patterns.items():
            pattern = reporter_info['pattern']

            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    citation = self._parse_india_citation(
                        match,
                        reporter_code,
                        reporter_info
                    )
                    if citation:
                        citations.append(citation)

                except Exception as e:
                    logger.warning(f"Failed to parse {reporter_code} citation: {e}")

        return citations

    def _parse_india_citation(
        self,
        match: re.Match,
        reporter_code: str,
        reporter_info: Dict
    ) -> Optional[Dict[str, Any]]:
        """Parse India citation from regex match"""

        if reporter_code == 'AIR':
            # AIR format: AIR year COURT page
            year = int(match.group(1))
            court = match.group(2)
            page = int(match.group(3))
            volume = None
        else:
            # SCC/SCR format: (year) volume REPORTER page
            year = int(match.group(1))
            volume = int(match.group(2))
            page = int(match.group(3))
            court = 'SC'  # Supreme Court

        # Validate
        if not self._validate_year(year):
            return None

        # Encode citation
        citation_encoded = self._encode_citation(
            volume, year, reporter_code, court, page
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            volume, year, reporter_code, court, page
        )

        return {
            'citation_text': match.group(0),
            'citation_encoded': citation_encoded,
            'volume': volume,
            'year': year,
            'reporter': reporter_code,
            'court': court,
            'page': page,
            'is_primary': False,
            'confidence': confidence,
            'country': 'IN',
            'reporter_full_name': reporter_info['full_name']
        }

    # ==================== Pakistan Citations ====================

    def _extract_pakistan_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract Pakistan citations (PLD, SCMR, CLC)"""
        citations = []

        for reporter_code, reporter_info in self.pakistan_patterns.items():
            pattern = reporter_info['pattern']

            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    citation = self._parse_pakistan_citation(
                        match,
                        reporter_code,
                        reporter_info
                    )
                    if citation:
                        citations.append(citation)

                except Exception as e:
                    logger.warning(f"Failed to parse {reporter_code} citation: {e}")

        return citations

    def _parse_pakistan_citation(
        self,
        match: re.Match,
        reporter_code: str,
        reporter_info: Dict
    ) -> Optional[Dict[str, Any]]:
        """Parse Pakistan citation from regex match"""

        if reporter_code == 'PLD':
            # PLD format: PLD year COURT page
            year = int(match.group(1))
            court = match.group(2)
            page = int(match.group(3))
            volume = None
        else:
            # SCMR/CLC format: year REPORTER page
            year = int(match.group(1))
            page = int(match.group(2))
            court = 'SC'
            volume = None

        # Validate
        if not self._validate_year(year):
            return None

        # Encode citation
        citation_encoded = self._encode_citation(
            volume, year, reporter_code, court, page
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            volume, year, reporter_code, court, page
        )

        return {
            'citation_text': match.group(0),
            'citation_encoded': citation_encoded,
            'volume': volume,
            'year': year,
            'reporter': reporter_code,
            'court': court,
            'page': page,
            'is_primary': False,
            'confidence': confidence,
            'country': 'PK',
            'reporter_full_name': reporter_info['full_name']
        }

    # ==================== Helper Methods ====================

    def _encode_citation(
        self,
        volume: Optional[int],
        year: int,
        reporter: str,
        court: str,
        page: int
    ) -> str:
        """
        Encode citation (Phase 1 compatible).

        Format: {volume}{reporter}{year_short}{court_code}{page}
        Example: "22 (1998) DLR (HCD) 205" → "22DLR98H205"
        """
        # Year short (last 2 digits)
        year_short = str(year)[-2:]

        # Court code (first letter or abbreviation)
        court_code = self._get_court_code(court)

        # Build encoded citation
        if volume:
            encoded = f"{volume}{reporter}{year_short}{court_code}{page}"
        else:
            # No volume (AIR, PLD formats)
            encoded = f"{reporter}{year_short}{court_code}{page}"

        return encoded

    def _get_court_code(self, court: str) -> str:
        """Get court code for encoding"""
        # First letter for simple codes
        if len(court) <= 3:
            return court[0].upper()

        # Special handling
        court_map = {
            'HCD': 'H',
            'AD': 'A',
            'SC': 'S',
            'FSC': 'F',
        }

        return court_map.get(court, court[0].upper())

    def _validate_year(self, year: int) -> bool:
        """Validate year is in reasonable range"""
        return 1800 <= year <= 2100

    def _calculate_confidence(
        self,
        volume: Optional[int],
        year: int,
        reporter: str,
        court: str,
        page: int
    ) -> float:
        """
        Calculate confidence score based on validation.

        Scoring:
        - Year valid: +0.30
        - Page valid: +0.20
        - Volume valid: +0.20
        - Court recognized: +0.20
        - Reporter known: +0.10
        """
        score = 0.0

        # Year validation
        if self._validate_year(year):
            score += 0.30

        # Page validation
        if page > 0 and page < 10000:
            score += 0.20

        # Volume validation
        if volume is None or (volume > 0 and volume < 1000):
            score += 0.20

        # Court recognized
        if court in self.court_codes:
            score += 0.20
        else:
            score += 0.10  # Partial credit

        # Reporter known
        all_reporters = list(self.bangladesh_patterns.keys()) + \
                       list(self.india_patterns.keys()) + \
                       list(self.pakistan_patterns.keys())

        if reporter in all_reporters:
            score += 0.10

        return min(score, 1.0)

    # ==================== Fuzzy Matching ====================

    def extract_with_fuzzy_matching(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract citations with fuzzy matching for OCR errors.

        Args:
            text: Document text (possibly with OCR errors)

        Returns:
            List of citations
        """
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)

        # Extract normally
        result = self.extract(text)

        return result.get('data', {}).get('citations', [])

    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in citations"""
        # l (lowercase L) → 1 in years/volumes
        text = re.sub(r'\bl99(\d)\b', r'199\1', text)
        text = re.sub(r'\bl00(\d)\b', r'200\1', text)

        # O (capital O) → 0 in years
        text = re.sub(r'\b2OO(\d)\b', r'200\1', text)

        # Fix reporter OCR errors
        text = re.sub(r'\bDl_R\b', 'DLR', text)
        text = re.sub(r'\bAlR\b', 'AIR', text)

        return text


# ==================== Convenience Functions ====================

def extract_citations(text: str) -> List[Dict[str, Any]]:
    """
    Quick extract citations (convenience function).

    Args:
        text: Document text

    Returns:
        List of citation dictionaries
    """
    extractor = CitationExtractor()
    result = extractor.extract(text)
    return result.get('data', {}).get('citations', [])


def get_primary_citation(text: str) -> Optional[Dict[str, Any]]:
    """
    Get primary citation from document.

    Args:
        text: Document text

    Returns:
        Primary citation dict or None
    """
    extractor = CitationExtractor()
    result = extractor.extract(text)
    return result.get('data', {}).get('primary_citation')

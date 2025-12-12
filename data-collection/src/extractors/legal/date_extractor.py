"""
Date extraction for Legal RAG Extraction System (Phase 3)
Multi-format date extraction with python-dateutil
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime, date
from dateutil import parser as dateutil_parser

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import DateExtractionResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class DateExtractor(SimpleExtractor):
    """
    Date extractor for legal documents.

    Extracts:
    - Judgment date
    - Filing date
    - Hearing date
    - Order date

    Uses python-dateutil for robust parsing of various formats.
    """

    def __init__(self):
        super().__init__(name="DateExtractor")
        self.cache = get_pattern_cache()

        # Load date patterns
        self.patterns = self.cache.load_pattern('dates.yaml')
        self.date_labels = self.patterns.get('date_labels', {})
        self.date_formats = self.patterns.get('date_formats', [])
        self.validation = self.patterns.get('validation', {})

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract all dates from text.

        Args:
            text: Document text
            **kwargs: Additional parameters

        Returns:
            DateExtractionResult dict
        """
        dates = {}

        # Extract judgment date
        judgment_date = self._extract_date_by_type(text, 'judgment')
        if judgment_date:
            dates['date_judgment'] = judgment_date

        # Extract filing date
        filing_date = self._extract_date_by_type(text, 'filing')
        if filing_date:
            dates['date_filing'] = filing_date

        # Extract hearing date
        hearing_date = self._extract_date_by_type(text, 'hearing')
        if hearing_date:
            dates['date_hearing'] = hearing_date

        # Validate date ordering
        validation_errors = self._validate_date_order(dates)

        return {
            'status': 'success' if dates else 'partial',
            'data': {
                **dates,
                'validation_errors': validation_errors
            }
        }

    # ==================== Labeled Date Extraction ====================

    def _extract_date_by_type(self, text: str, date_type: str) -> Optional[str]:
        """
        Extract date for specific type using labels.

        Args:
            text: Document text
            date_type: 'judgment', 'filing', or 'hearing'

        Returns:
            ISO date string (YYYY-MM-DD) or None
        """
        labels = self.date_labels.get(date_type, [])

        # Search in first 3000 characters (dates usually mentioned early)
        search_text = text[:3000]

        for label in labels:
            # Pattern: Label: date
            pattern = rf'{label}\s*:?\s*(.{{0,100}}?)(?:\n|$|\.)'
            match = re.search(pattern, search_text, re.IGNORECASE)

            if match:
                date_text = match.group(1).strip()

                # Try to parse date
                parsed_date = self._parse_date(date_text)

                if parsed_date:
                    logger.debug(f"Found {date_type} date: {parsed_date}")
                    return parsed_date

        return None

    # ==================== Date Parsing ====================

    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date from text using multiple strategies.

        Args:
            date_text: Text containing date

        Returns:
            ISO date string (YYYY-MM-DD) or None
        """
        # Normalize date text
        date_text = self._normalize_date_text(date_text)

        # Strategy 1: Try pattern-based extraction
        for format_info in self.date_formats:
            pattern = format_info['pattern']
            match = re.search(pattern, date_text, re.IGNORECASE)

            if match:
                try:
                    # Extract date components
                    date_str = match.group(0)

                    # Parse with dateutil
                    parsed = dateutil_parser.parse(date_str, dayfirst=True)

                    # Validate year
                    if not self._validate_year(parsed.year):
                        continue

                    # Return ISO format
                    return parsed.date().isoformat()

                except Exception as e:
                    logger.debug(f"Failed to parse date '{date_str}': {e}")
                    continue

        # Strategy 2: Try dateutil directly (very flexible)
        try:
            parsed = dateutil_parser.parse(date_text, dayfirst=True, fuzzy=True)

            if self._validate_year(parsed.year):
                return parsed.date().isoformat()

        except Exception as e:
            logger.debug(f"Dateutil failed to parse '{date_text}': {e}")

        return None

    def _normalize_date_text(self, date_text: str) -> str:
        """
        Normalize date text for easier parsing.

        Args:
            date_text: Raw date text

        Returns:
            Normalized text
        """
        # Remove ordinal suffixes (1st, 2nd, 3rd, 4th)
        date_text = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', date_text, flags=re.IGNORECASE)

        # Normalize "Sept" to "Sep"
        date_text = re.sub(r'\bSept\b', 'Sep', date_text, flags=re.IGNORECASE)

        # Remove extra whitespace
        date_text = re.sub(r'\s+', ' ', date_text).strip()

        return date_text

    # ==================== Validation ====================

    def _validate_year(self, year: int) -> bool:
        """
        Validate year is in reasonable range.

        Args:
            year: Year to validate

        Returns:
            True if valid
        """
        min_year = self.validation.get('min_year', 1800)
        max_year = self.validation.get('max_year', 2100)

        return min_year <= year <= max_year

    def _validate_date_order(self, dates: Dict[str, str]) -> List[str]:
        """
        Validate logical date ordering.

        Args:
            dates: Dictionary of extracted dates

        Returns:
            List of validation errors
        """
        errors = []

        filing = dates.get('date_filing')
        hearing = dates.get('date_hearing')
        judgment = dates.get('date_judgment')

        # Convert to date objects for comparison
        try:
            if filing:
                filing_date = datetime.fromisoformat(filing).date()
            if hearing:
                hearing_date = datetime.fromisoformat(hearing).date()
            if judgment:
                judgment_date = datetime.fromisoformat(judgment).date()

            # Check: filing before hearing
            if filing and hearing:
                if filing_date > hearing_date:
                    errors.append("Filing date after hearing date")

            # Check: hearing before judgment
            if hearing and judgment:
                if hearing_date > judgment_date:
                    errors.append("Hearing date after judgment date")

            # Check: filing before judgment
            if filing and judgment:
                if filing_date > judgment_date:
                    errors.append("Filing date after judgment date")

        except Exception as e:
            logger.warning(f"Date validation error: {e}")

        return errors

    # ==================== Bulk Extraction ====================

    def extract_all_dates(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract all dates from text (not just labeled ones).

        Args:
            text: Document text

        Returns:
            List of (date_string, iso_date) tuples
        """
        all_dates = []

        # Try each date format pattern
        for format_info in self.date_formats:
            pattern = format_info['pattern']
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                date_str = match.group(0)
                parsed = self._parse_date(date_str)

                if parsed:
                    all_dates.append((date_str, parsed))

        # Deduplicate
        seen = set()
        unique_dates = []
        for date_str, iso_date in all_dates:
            if iso_date not in seen:
                seen.add(iso_date)
                unique_dates.append((date_str, iso_date))

        return unique_dates

    # ==================== Year Extraction ====================

    def extract_year(self, text: str) -> Optional[int]:
        """
        Extract year from text (when full date not available).

        Args:
            text: Document text

        Returns:
            Year as integer or None
        """
        year_patterns = self.patterns.get('year_patterns', [])

        # Search in first 1000 characters
        search_text = text[:1000]

        for pattern_info in year_patterns:
            pattern = pattern_info['pattern']
            match = re.search(pattern, search_text)

            if match:
                year = int(match.group(1))
                if self._validate_year(year):
                    return year

        return None


# ==================== Convenience Functions ====================

def extract_dates(text: str) -> Dict[str, Optional[str]]:
    """
    Quick extract dates (convenience function).

    Args:
        text: Document text

    Returns:
        Dictionary with judgment, filing, hearing dates
    """
    extractor = DateExtractor()
    result = extractor.extract(text)
    data = result.get('data', {})

    return {
        'date_judgment': data.get('date_judgment'),
        'date_filing': data.get('date_filing'),
        'date_hearing': data.get('date_hearing')
    }


def get_judgment_date(text: str) -> Optional[str]:
    """
    Get judgment date only.

    Args:
        text: Document text

    Returns:
        ISO date string or None
    """
    dates = extract_dates(text)
    return dates.get('date_judgment')

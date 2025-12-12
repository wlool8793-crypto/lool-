"""
Text normalization for Legal RAG Extraction System (Phase 3)
Advanced text cleaning and normalization for legal documents
"""

from typing import Optional
import re
import unicodedata

from ..base_extractor import SimpleExtractor
from ..utils import normalize_text
from ..logging_config import get_logger

logger = get_logger(__name__)


class TextNormalizer(SimpleExtractor):
    """
    Text normalizer for legal documents.

    Applies comprehensive text cleaning:
    - Unicode normalization (NFKC)
    - Ligature expansion
    - Smart quote conversion
    - Whitespace cleanup
    - Legal-specific cleaning
    - OCR error correction
    """

    def __init__(self):
        super().__init__(name="TextNormalizer")

    def _extract_impl(self, text: str, **kwargs) -> dict:
        """
        Normalize text with all cleaning operations.

        Args:
            text: Raw text to normalize
            **kwargs: Optional cleaning parameters

        Returns:
            Dictionary with normalized text
        """
        if not text:
            return {
                'status': 'success',
                'normalized_text': '',
                'original_length': 0,
                'normalized_length': 0,
                'changes_applied': []
            }

        original_length = len(text)
        changes = []

        # Apply normalization steps
        text = self._normalize_unicode(text, changes)
        text = self._expand_ligatures(text, changes)
        text = self._normalize_quotes(text, changes)
        text = self._clean_whitespace(text, changes)
        text = self._fix_line_breaks(text, changes)
        text = self._remove_control_chars(text, changes)
        text = self._fix_ocr_errors(text, changes)
        text = self._clean_legal_artifacts(text, changes)

        normalized_length = len(text)

        return {
            'status': 'success',
            'data': {
                'normalized_text': text,
                'original_length': original_length,
                'normalized_length': normalized_length,
                'changes_applied': changes,
                'reduction_ratio': 1.0 - (normalized_length / original_length) if original_length > 0 else 0.0
            }
        }

    # ==================== Normalization Methods ====================

    def _normalize_unicode(self, text: str, changes: list) -> str:
        """
        Apply Unicode NFKC normalization.

        NFKC = Compatibility Decomposition + Canonical Composition
        Converts compatibility characters to their canonical equivalents.
        """
        original = text
        text = unicodedata.normalize('NFKC', text)

        if text != original:
            changes.append('unicode_normalization')
            logger.debug("Applied Unicode normalization")

        return text

    def _expand_ligatures(self, text: str, changes: list) -> str:
        """
        Expand typographic ligatures.

        Common in legal PDFs: ﬁ, ﬂ, ﬀ, ﬃ, ﬄ, ﬆ
        """
        ligature_map = {
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬀ': 'ff',
            'ﬃ': 'ffi',
            'ﬄ': 'ffl',
            'ﬆ': 'st',
            'æ': 'ae',
            'Æ': 'AE',
            'œ': 'oe',
            'Œ': 'OE',
        }

        original = text
        for ligature, replacement in ligature_map.items():
            text = text.replace(ligature, replacement)

        if text != original:
            changes.append('ligature_expansion')
            logger.debug("Expanded ligatures")

        return text

    def _normalize_quotes(self, text: str, changes: list) -> str:
        """
        Convert smart quotes to ASCII quotes.

        Important for citation parsing and search.
        """
        quote_map = {
            # Single quotes
            ''': "'",
            ''': "'",
            '‚': "'",
            '‛': "'",
            # Double quotes
            '"': '"',
            '"': '"',
            '„': '"',
            '‟': '"',
            # Angle quotes
            '‹': '<',
            '›': '>',
            '«': '<<',
            '»': '>>',
            # Primes (sometimes used as quotes)
            '′': "'",
            '″': '"',
        }

        original = text
        for smart, ascii_char in quote_map.items():
            text = text.replace(smart, ascii_char)

        if text != original:
            changes.append('quote_normalization')
            logger.debug("Normalized quotes")

        return text

    def _clean_whitespace(self, text: str, changes: list) -> str:
        """
        Clean up whitespace:
        - Remove multiple spaces
        - Remove trailing/leading whitespace
        - Normalize line breaks
        """
        original = text

        # Replace tabs with spaces
        text = text.replace('\t', '    ')

        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)

        # Remove spaces at line breaks
        text = re.sub(r' *\n *', '\n', text)

        # Remove multiple blank lines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        if text != original:
            changes.append('whitespace_cleanup')
            logger.debug("Cleaned whitespace")

        return text

    def _fix_line_breaks(self, text: str, changes: list) -> str:
        """
        Fix common line break issues in PDFs.

        PDFs often have:
        - Broken words across lines (hyphenation)
        - Broken sentences across lines
        """
        original = text

        # Fix hyphenated words across lines
        # "con-\ntract" -> "contract"
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # Fix broken sentences (lowercase after newline within sentence)
        # "The court held that\nthe defendant" -> "The court held that the defendant"
        text = re.sub(r'(\w)\n([a-z])', r'\1 \2', text)

        if text != original:
            changes.append('line_break_fixes')
            logger.debug("Fixed line breaks")

        return text

    def _remove_control_chars(self, text: str, changes: list) -> str:
        """
        Remove control characters except common ones.

        Keep: newline (\n), carriage return (\r), tab (\t)
        Remove: null bytes, form feed, vertical tab, etc.
        """
        original = text

        # Remove null bytes
        text = text.replace('\x00', '')

        # Remove other control characters except \n, \r, \t
        text = re.sub(r'[\x01-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)

        if text != original:
            changes.append('control_char_removal')
            logger.debug("Removed control characters")

        return text

    def _fix_ocr_errors(self, text: str, changes: list) -> str:
        """
        Fix common OCR errors in legal documents.

        Common OCR mistakes:
        - l (lowercase L) ↔ I (capital i) ↔ 1 (one)
        - O (capital o) ↔ 0 (zero)
        - S (capital s) ↔ 5 (five)
        - rn (r+n) ↔ m
        """
        original = text

        # Fix common legal term OCR errors
        ocr_fixes = {
            # Common legal words
            r'\bAppel1ant\b': 'Appellant',
            r'\bAppellant5\b': 'Appellants',
            r'\bPetiti0ner\b': 'Petitioner',
            r'\bResp0ndent\b': 'Respondent',
            r'\bC0urt\b': 'Court',
            r'\bJudgrnent\b': 'Judgment',
            r'\bGovemment\b': 'Government',
            r'\bConstituti0n\b': 'Constitution',
            r'\bSecti0n\b': 'Section',

            # Fix standalone characters in legal context
            r'\b([A-Z][a-z]+) l ([A-Z][a-z]+)\b': r'\1 I \2',  # "John l Smith" -> "John I Smith"
            r'\bvs\.\s+l\b': 'vs. I',  # Citation context
            r'\bAIR\s+l99': 'AIR 199',  # AIR 1998 mistaken as AIR l998
        }

        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        if text != original:
            changes.append('ocr_error_fixes')
            logger.debug("Fixed OCR errors")

        return text

    def _clean_legal_artifacts(self, text: str, changes: list) -> str:
        """
        Remove common legal document artifacts.

        Artifacts:
        - Page numbers
        - Headers/footers
        - Watermarks
        - Common separator patterns
        """
        original = text

        # Remove page numbers
        patterns_to_remove = [
            r'Page \d+ of \d+',
            r'^\d+\s*$',  # Standalone page numbers
            r'^-+\s*$',  # Dash separators
            r'^\*+\s*$',  # Star separators
            r'^=+\s*$',  # Equal sign separators
            r'^_{5,}\s*$',  # Underscore separators
            r'^\[Page \d+\]',  # [Page 1]
            r'^\d+\s*\n\s*$',  # Page number on own line
        ]

        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)

        # Remove common headers (repeated text)
        # If same line appears 3+ times, it's likely a header
        lines = text.split('\n')
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) > 10:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

        # Remove lines that appear 3+ times
        headers = {line for line, count in line_counts.items() if count >= 3}
        if headers:
            lines = [line for line in lines if line.strip() not in headers]
            text = '\n'.join(lines)
            changes.append('header_removal')

        if text != original:
            changes.append('artifact_removal')
            logger.debug("Removed legal artifacts")

        return text

    # ==================== Specialized Cleaning ====================

    def normalize_for_citation_parsing(self, text: str) -> str:
        """
        Specialized normalization for citation parsing.

        Args:
            text: Raw text

        Returns:
            Text optimized for citation extraction
        """
        # Apply basic normalization
        result = self.extract(text)
        normalized = result['data']['normalized_text']

        # Additional citation-specific cleaning
        # Ensure spaces around parentheses for year parsing
        normalized = re.sub(r'(\d)\(', r'\1 (', normalized)
        normalized = re.sub(r'\)(\d)', r') \1', normalized)

        # Normalize reporter abbreviations spacing
        normalized = re.sub(r'(\d+)\s*([A-Z]{2,})\s*(\d+)', r'\1 \2 \3', normalized)

        return normalized

    def normalize_for_party_parsing(self, text: str) -> str:
        """
        Specialized normalization for party name parsing.

        Args:
            text: Raw text

        Returns:
            Text optimized for party extraction
        """
        result = self.extract(text)
        normalized = result['data']['normalized_text']

        # Normalize "v.", "vs.", "versus"
        normalized = re.sub(r'\bvs?\.\s+', 'v. ', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\bversus\s+', 'v. ', normalized, flags=re.IGNORECASE)

        # Fix common party name issues
        normalized = re.sub(r'\bMd\.\s+', 'Md. ', normalized)  # Ensure space after "Md."
        normalized = re.sub(r'\bSmt\.\s+', 'Smt. ', normalized)  # Ensure space after "Smt."

        return normalized

    def normalize_for_date_parsing(self, text: str) -> str:
        """
        Specialized normalization for date parsing.

        Args:
            text: Raw text

        Returns:
            Text optimized for date extraction
        """
        result = self.extract(text)
        normalized = result['data']['normalized_text']

        # Remove ordinal suffixes for easier parsing
        normalized = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', normalized)

        # Normalize date separators
        normalized = re.sub(r'(\d+)[./](\d+)[./](\d+)', r'\1-\2-\3', normalized)

        return normalized

    def clean_extracted_text(self, text: str) -> str:
        """
        Quick cleaning for already-extracted text.

        Lighter than full normalization, used for post-processing.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove common noise
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\"\'\/]', '', text)

        return text


# ==================== Convenience Functions ====================

def normalize_legal_text(text: str) -> str:
    """
    Quick normalize legal text (convenience function).

    Args:
        text: Raw text

    Returns:
        Normalized text
    """
    normalizer = TextNormalizer()
    result = normalizer.extract(text)
    return result['data']['normalized_text']


def quick_clean(text: str) -> str:
    """
    Quick text cleaning without full normalization.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    normalizer = TextNormalizer()
    return normalizer.clean_extracted_text(text)

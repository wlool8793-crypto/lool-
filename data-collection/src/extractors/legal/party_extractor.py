"""
Party name extraction for Legal RAG Extraction System (Phase 3)
Extract party names with Phase 1 abbreviation integration
"""

from typing import Dict, Any, List, Optional, Tuple
import re

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import PartySchema, PartyExtractionResult, PartyType, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class PartyExtractor(SimpleExtractor):
    """
    Party name extractor for legal documents.

    Extracts:
    - Petitioner/Appellant/Plaintiff
    - Respondent/Defendant
    - Multiple parties per side
    - Government entities
    - Organizations

    Integrates with Phase 1 PartyAbbreviator for name abbreviation.
    """

    def __init__(self):
        super().__init__(name="PartyExtractor")
        self.cache = get_pattern_cache()

        # Load party patterns
        self.patterns = self.cache.load_pattern('parties.yaml')
        self.versus_patterns = self.patterns.get('versus_patterns', [])
        self.party_labels = self.patterns.get('party_labels', {})
        self.special_parties = self.patterns.get('special_parties', {})
        self.titles_to_remove = self.patterns.get('titles_to_remove', [])

    def _extract_impl(self, text: str, title: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Extract party names from text.

        Args:
            text: Document text
            title: Document title (prioritized for extraction)
            **kwargs: Additional parameters

        Returns:
            PartyExtractionResult dict
        """
        parties = []

        # Strategy 1: Extract from title (highest priority)
        if title:
            title_parties = self._extract_from_title(title)
            if title_parties:
                parties.extend(title_parties)

        # Strategy 2: Extract from versus patterns in text
        if not parties:
            versus_parties = self._extract_from_versus_pattern(text)
            if versus_parties:
                parties.extend(versus_parties)

        # Strategy 3: Extract from party labels
        if not parties:
            label_parties = self._extract_from_labels(text)
            if label_parties:
                parties.extend(label_parties)

        # Deduplicate parties
        parties = self._deduplicate_parties(parties)

        # Assign party order
        parties = self._assign_party_order(parties)

        return {
            'status': 'success' if parties else 'partial',
            'data': {
                'parties': parties,
                'total_parties': len(parties)
            }
        }

    # ==================== Strategy 1: Title Extraction ====================

    def _extract_from_title(self, title: str) -> List[Dict[str, Any]]:
        """
        Extract parties from title/case name.

        Most reliable method as titles follow standard format.
        """
        parties = []

        # Try each versus pattern
        for pattern_info in self.versus_patterns:
            pattern = pattern_info['pattern']
            confidence_base = pattern_info['confidence']

            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                petitioner_text = match.group(1).strip()
                respondent_text = match.group(2).strip()

                # Parse petitioner(s)
                petitioners = self._parse_party_names(
                    petitioner_text,
                    PartyType.PETITIONER,
                    confidence_base
                )
                parties.extend(petitioners)

                # Parse respondent(s)
                respondents = self._parse_party_names(
                    respondent_text,
                    PartyType.RESPONDENT,
                    confidence_base
                )
                parties.extend(respondents)

                logger.debug(f"Extracted {len(parties)} parties from title")
                break

        return parties

    # ==================== Strategy 2: Versus Pattern ====================

    def _extract_from_versus_pattern(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract parties from versus pattern in text.

        Searches for "A v. B" patterns in document body.
        """
        parties = []

        # Look in first 2000 characters (parties usually mentioned early)
        search_text = text[:2000]

        for pattern_info in self.versus_patterns:
            pattern = pattern_info['pattern']
            confidence_base = pattern_info['confidence'] * 0.9  # Lower confidence than title

            matches = re.finditer(pattern, search_text, re.IGNORECASE)

            for match in matches:
                petitioner_text = match.group(1).strip()
                respondent_text = match.group(2).strip()

                # Skip if too long (likely not a party name)
                if len(petitioner_text) > 100 or len(respondent_text) > 100:
                    continue

                # Parse parties
                petitioners = self._parse_party_names(
                    petitioner_text,
                    PartyType.PETITIONER,
                    confidence_base
                )
                respondents = self._parse_party_names(
                    respondent_text,
                    PartyType.RESPONDENT,
                    confidence_base
                )

                if petitioners and respondents:
                    parties.extend(petitioners)
                    parties.extend(respondents)
                    logger.debug(f"Extracted parties from versus pattern")
                    break

            if parties:
                break

        return parties

    # ==================== Strategy 3: Label-Based Extraction ====================

    def _extract_from_labels(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract parties using labels like "Petitioner:", "Respondent:".

        Fallback method when versus pattern not found.
        """
        parties = []

        # Search in first 3000 characters
        search_text = text[:3000]

        # Extract petitioners
        for label in self.party_labels.get('petitioner', []):
            pattern = rf'{label}\s*:?\s*(.+?)(?:\n|Respondent|Defendant|$)'
            match = re.search(pattern, search_text, re.IGNORECASE | re.DOTALL)

            if match:
                party_text = match.group(1).strip()
                petitioners = self._parse_party_names(
                    party_text,
                    PartyType.PETITIONER,
                    0.85
                )
                parties.extend(petitioners)
                break

        # Extract respondents
        for label in self.party_labels.get('respondent', []):
            pattern = rf'{label}\s*:?\s*(.+?)(?:\n|$)'
            match = re.search(pattern, search_text, re.IGNORECASE | re.DOTALL)

            if match:
                party_text = match.group(1).strip()
                respondents = self._parse_party_names(
                    party_text,
                    PartyType.RESPONDENT,
                    0.85
                )
                parties.extend(respondents)
                break

        if parties:
            logger.debug(f"Extracted parties from labels")

        return parties

    # ==================== Party Parsing ====================

    def _parse_party_names(
        self,
        party_text: str,
        party_type: PartyType,
        confidence: float
    ) -> List[Dict[str, Any]]:
        """
        Parse party names from text (may contain multiple parties).

        Args:
            party_text: Text containing party name(s)
            party_type: Type of party
            confidence: Base confidence score

        Returns:
            List of party dictionaries
        """
        parties = []

        # Check for multiple parties
        party_names = self._split_multiple_parties(party_text)

        for party_name in party_names:
            # Clean party name
            cleaned_name = self._clean_party_name(party_name)

            if not cleaned_name or len(cleaned_name) < 2:
                continue

            # Abbreviate (Phase 1 integration)
            abbreviated_name = self._abbreviate_party_name(cleaned_name)

            # Create party dict
            party = {
                'party_type': party_type.value,
                'party_name': cleaned_name,
                'party_name_abbr': abbreviated_name,
                'party_order': 0,  # Will be assigned later
                'confidence': confidence
            }

            parties.append(party)

        return parties

    def _split_multiple_parties(self, party_text: str) -> List[str]:
        """
        Split text into individual party names.

        Handles: "A & B", "A and B", "A and Others"
        """
        separators = self.patterns.get('multiple_parties', {}).get('separator_patterns', [])

        # Build pattern: split on "&", "and", "Ors.", etc.
        separator_pattern = '|'.join(re.escape(sep) for sep in separators)

        # Split
        parties = re.split(separator_pattern, party_text, flags=re.IGNORECASE)

        # Clean and filter
        parties = [p.strip() for p in parties if p.strip()]

        # Limit to max parties
        max_parties = self.patterns.get('multiple_parties', {}).get('max_parties', 5)
        parties = parties[:max_parties]

        return parties

    def _clean_party_name(self, party_name: str) -> str:
        """
        Clean party name by removing titles and formatting.

        Args:
            party_name: Raw party name

        Returns:
            Cleaned party name
        """
        # Remove titles
        for title in self.titles_to_remove:
            party_name = re.sub(rf'\b{title}\b', '', party_name, flags=re.IGNORECASE)

        # Remove extra whitespace
        party_name = re.sub(r'\s+', ' ', party_name).strip()

        # Remove leading/trailing punctuation
        party_name = party_name.strip('.,;:')

        return party_name

    def _abbreviate_party_name(self, party_name: str) -> str:
        """
        Abbreviate party name (Phase 1 compatible).

        Rules:
        - Individual: Last name only
        - Government: Special abbreviations (StateBD, UOI, etc.)
        - Company: Remove suffixes, abbreviate
        """
        # Check for special parties (government entities)
        for region in self.special_parties.values():
            for special_party in region:
                pattern = special_party['pattern']
                if re.search(pattern, party_name, re.IGNORECASE):
                    return special_party['abbr']

        # Check for company/organization
        if re.search(r'\b(Ltd|Limited|Pvt|Private|Inc|Corp|Co|Company)\b', party_name, re.IGNORECASE):
            # Remove suffixes
            abbr = re.sub(r'\s+(Ltd|Limited|Pvt|Private|Inc|Corp|Co|Company)\.?', '', party_name, flags=re.IGNORECASE)
            # Take first word or first 10 chars
            abbr = abbr.split()[0] if abbr.split() else abbr[:10]
            return abbr

        # Individual name: take last word (surname)
        words = party_name.split()
        if words:
            return words[-1]

        return party_name[:10]  # Fallback: first 10 chars

    # ==================== Post-Processing ====================

    def _deduplicate_parties(self, parties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate parties based on name"""
        seen_names = set()
        unique_parties = []

        for party in parties:
            name = party['party_name'].lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_parties.append(party)

        return unique_parties

    def _assign_party_order(self, parties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign party_order within each party type.

        First petitioner = order 1, second = order 2, etc.
        """
        # Group by type
        by_type = {}
        for party in parties:
            ptype = party['party_type']
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(party)

        # Assign order within each type
        for ptype, plist in by_type.items():
            for i, party in enumerate(plist, 1):
                party['party_order'] = i

        return parties


# ==================== Convenience Functions ====================

def extract_parties(text: str, title: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Quick extract parties (convenience function).

    Args:
        text: Document text
        title: Document title

    Returns:
        List of party dictionaries
    """
    extractor = PartyExtractor()
    result = extractor.extract(text, title=title)
    return result.get('data', {}).get('parties', [])


def get_party_names(text: str, title: Optional[str] = None) -> Tuple[List[str], List[str]]:
    """
    Get simple party name lists.

    Args:
        text: Document text
        title: Document title

    Returns:
        Tuple of (petitioners, respondents)
    """
    parties = extract_parties(text, title)

    petitioners = [p['party_name'] for p in parties if p['party_type'] == 'petitioner']
    respondents = [p['party_name'] for p in parties if p['party_type'] == 'respondent']

    return petitioners, respondents

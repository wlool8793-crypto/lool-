"""
Phase 1 Integration for Legal RAG Extraction System (Phase 3)
Integrates with Phase 1 Naming Convention System
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..logging_config import get_logger
from ..utils import hash_content

logger = get_logger(__name__)


class Phase1Integrator:
    """
    Integrates Phase 3 extractors with Phase 1 naming conventions.

    Phase 1 Components:
    - CitationEncoder: Encode citations to standardized format
    - PartyAbbreviator: Abbreviate party names
    - ContentHasher: Generate content hashes
    - FileNamer: Generate standardized filenames

    Integration Points:
    1. Citation encoding (already done in CitationExtractor)
    2. Party abbreviation (already done in PartyExtractor)
    3. Content hashing (used for document IDs)
    4. Filename generation for downloaded PDFs
    """

    def __init__(self):
        """Initialize Phase 1 integrator."""
        # In production, these would import from Phase 1 modules
        # For now, we use the Phase 3 implementations which follow Phase 1 spec
        pass

    def generate_filename(
        self,
        extraction_result: Dict[str, Any],
        extension: str = 'pdf'
    ) -> str:
        """
        Generate standardized filename from extraction result.

        Format: {CitationEncoded}_{PartyAbbrev}_{ContentHash}.{ext}
        Example: 22DLR98H205_Rahman_A3F5D8E2.pdf

        Args:
            extraction_result: Complete extraction result
            extension: File extension (default: pdf)

        Returns:
            Standardized filename
        """
        # Get primary citation
        citations = extraction_result.get('citations', [])
        primary_citation = None

        for citation in citations:
            if citation.get('is_primary'):
                primary_citation = citation
                break

        # Fallback to first citation
        if not primary_citation and citations:
            primary_citation = citations[0]

        # Citation component
        if primary_citation:
            citation_encoded = primary_citation.get('citation_encoded', 'UNKNOWN')
        else:
            # Use year + subject if no citation
            year = extraction_result.get('year', '0000')
            subject = extraction_result.get('subject_classification', {}).get('primary_subject', 'GEN')
            citation_encoded = f"{year}{subject}"

        # Party component
        parties = extraction_result.get('parties', {})
        petitioners = parties.get('petitioner', [])

        if petitioners:
            # Use abbreviated form (Phase 1 compatible)
            party_abbrev = self._abbreviate_party(petitioners[0])
        else:
            party_abbrev = 'NoParty'

        # Content hash component
        full_text = extraction_result.get('full_text', '')
        content_hash = extraction_result.get('text_hash') or hash_content(full_text, length=8)

        # Combine components
        filename = f"{citation_encoded}_{party_abbrev}_{content_hash}.{extension}"

        # Sanitize filename
        filename = self._sanitize_filename(filename)

        return filename

    def _abbreviate_party(self, party_name: str) -> str:
        """
        Abbreviate party name (Phase 1 compatible).

        Examples:
        - "Md. Rahman" -> "Rahman"
        - "State of Bangladesh" -> "StateBD"
        - "ABC Corporation Ltd." -> "ABC"

        Args:
            party_name: Full party name

        Returns:
            Abbreviated party name
        """
        if not party_name:
            return "Unknown"

        # Remove common prefixes
        prefixes = ['Md.', 'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.']
        for prefix in prefixes:
            if party_name.startswith(prefix):
                party_name = party_name[len(prefix):].strip()

        # Handle "State of X" pattern
        if party_name.lower().startswith('state of'):
            country = party_name[8:].strip()
            if 'bangladesh' in country.lower():
                return 'StateBD'
            elif 'india' in country.lower():
                return 'StateIN'
            else:
                return 'State'

        # Handle corporations
        corp_suffixes = ['Ltd.', 'Limited', 'Corporation', 'Corp.', 'Inc.']
        for suffix in corp_suffixes:
            if suffix.lower() in party_name.lower():
                # Take first word
                words = party_name.split()
                if words:
                    return words[0]

        # Take last word (surname)
        words = party_name.split()
        if words:
            # Remove punctuation
            last_word = words[-1].rstrip('.,;:')
            return last_word

        return party_name[:20]  # Truncate if too long

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename
        """
        # Replace invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if len(name) > 200:
            name = name[:200]

        return f"{name}.{ext}" if ext else name

    def apply_naming_conventions(
        self,
        extraction_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply Phase 1 naming conventions to extraction result.

        Ensures all fields use Phase 1 format:
        - Citations are encoded
        - Parties are abbreviated
        - Content hash is generated

        Args:
            extraction_result: Extraction result

        Returns:
            Updated extraction result with Phase 1 conventions applied
        """
        # Verify citation encoding
        citations = extraction_result.get('citations', [])
        for citation in citations:
            if not citation.get('citation_encoded'):
                logger.warning(f"Citation missing encoding: {citation}")

        # Verify party abbreviation
        parties = extraction_result.get('parties', {})
        for party_list in [parties.get('petitioner', []), parties.get('respondent', [])]:
            for party in party_list:
                if len(party) > 50:
                    logger.warning(f"Party name not abbreviated: {party}")

        # Ensure content hash exists
        if not extraction_result.get('text_hash'):
            full_text = extraction_result.get('full_text', '')
            extraction_result['text_hash'] = hash_content(full_text)

        # Add suggested filename
        extraction_result['suggested_filename'] = self.generate_filename(extraction_result)

        return extraction_result

    def generate_batch_filenames(
        self,
        extraction_results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate filenames for batch of extraction results.

        Args:
            extraction_results: List of extraction results

        Returns:
            List of filenames
        """
        filenames = []

        for result in extraction_results:
            filename = self.generate_filename(result)
            filenames.append(filename)

        return filenames

    def validate_phase1_compliance(
        self,
        extraction_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that extraction result complies with Phase 1 format.

        Args:
            extraction_result: Extraction result

        Returns:
            Validation report
        """
        issues = []

        # Check citations
        citations = extraction_result.get('citations', [])
        if citations:
            for i, citation in enumerate(citations):
                if not citation.get('citation_encoded'):
                    issues.append(f"Citation {i} missing encoded format")

        # Check parties
        parties = extraction_result.get('parties', {})
        if not parties.get('petitioner'):
            issues.append("Missing petitioner")
        if not parties.get('respondent'):
            issues.append("Missing respondent")

        # Check content hash
        if not extraction_result.get('text_hash'):
            issues.append("Missing content hash")

        # Check filename can be generated
        try:
            filename = self.generate_filename(extraction_result)
            if len(filename) > 255:
                issues.append(f"Generated filename too long: {len(filename)} chars")
        except Exception as e:
            issues.append(f"Cannot generate filename: {e}")

        return {
            'is_compliant': len(issues) == 0,
            'issues': issues,
            'total_issues': len(issues)
        }


# ==================== Convenience Functions ====================

def apply_naming_conventions(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply Phase 1 naming conventions (convenience function).

    Args:
        extraction_result: Extraction result

    Returns:
        Updated extraction result
    """
    integrator = Phase1Integrator()
    return integrator.apply_naming_conventions(extraction_result)


def generate_filename(
    extraction_result: Dict[str, Any],
    extension: str = 'pdf'
) -> str:
    """
    Generate standardized filename (convenience function).

    Args:
        extraction_result: Extraction result
        extension: File extension

    Returns:
        Standardized filename
    """
    integrator = Phase1Integrator()
    return integrator.generate_filename(extraction_result, extension)


def validate_compliance(extraction_result: Dict[str, Any]) -> bool:
    """
    Check Phase 1 compliance (convenience function).

    Args:
        extraction_result: Extraction result

    Returns:
        True if compliant
    """
    integrator = Phase1Integrator()
    report = integrator.validate_phase1_compliance(extraction_result)
    return report['is_compliant']


# ==================== Example Usage ====================

def example_integration():
    """
    Example of Phase 1 integration.

    This shows how to use Phase 3 extraction results with Phase 1 naming.
    """
    from ..pipeline.extraction_pipeline import extract_document

    # Extract document
    result = extract_document('/path/to/case.pdf')

    # Apply Phase 1 conventions
    result = apply_naming_conventions(result)

    # Get standardized filename
    filename = generate_filename(result)

    print(f"Suggested filename: {filename}")

    # Validate compliance
    if validate_compliance(result):
        print("✓ Phase 1 compliant")
    else:
        integrator = Phase1Integrator()
        report = integrator.validate_phase1_compliance(result)
        print(f"✗ Issues found: {report['issues']}")

    return result, filename

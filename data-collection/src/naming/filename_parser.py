"""
Filename Parser for Universal Legal Document Naming System
Parses filenames back to structured metadata components
"""

import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .constants import (
    COUNTRY_CODES, DOC_TYPE_NAMES, COURT_CODES, SUBJECT_NAMES, STATUS_NAMES,
    LANGUAGE_CODES, HASH_LENGTH
)
from .citation_encoder import CitationEncoder, CitationComponents
from .enhanced_namer import FilenameComponents


class FilenameParser:
    """
    Parse legal document filenames back to structured metadata.

    Expected format:
    {GLOBALID}_{CC}_{TYPE}_{SUBTYPE}_{YEAR}_{DOCNUM}_{IDENTIFIER}_{SUBJ}_{STATUS}_{VER}_{LANG}_{HASH16}.pdf

    Example:
    BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf
    """

    # Pattern for complete filename
    FILENAME_PATTERN = re.compile(
        r'^(?P<global_id>[A-Z]{2}\d{8})_'  # GLOBALID
        r'(?P<country>[A-Z]{2})_'           # Country code
        r'(?P<type>[A-Z]{3})_'              # Document type
        r'(?P<subtype>[A-Z]{2,4})_'         # Subtype/Court
        r'(?P<year>\d{4})_'                 # Year
        r'(?P<docnum>[A-Za-z0-9]+)_'        # DOCNUM
        r'(?P<identifier>[A-Za-z0-9]+)_'    # Identifier
        r'(?P<subject>[A-Z]{2,3})_'         # Subject
        r'(?P<status>[A-Z]{3})_'            # Status
        r'(?P<version>V\d{2})_'             # Version
        r'(?P<language>[a-z]{2})_'          # Language
        r'(?P<hash>[A-Fa-f0-9]{16})'        # Hash
        r'\.(?P<ext>pdf|PDF)$'              # Extension
    )

    # Relaxed pattern for partial matches
    RELAXED_PATTERN = re.compile(
        r'^(?P<global_id>[A-Z]{2}\d+)?_?'
        r'(?P<country>[A-Z]{2})?_?'
        r'(?P<type>[A-Z]{3})?_?'
        r'(?P<subtype>[A-Z0-9]+)?_?'
        r'(?P<year>\d{4})?_?'
        r'(?P<docnum>[A-Za-z0-9]+)?_?'
        r'(?P<identifier>[A-Za-z0-9]+)?_?'
        r'(?P<subject>[A-Z]+)?_?'
        r'(?P<status>[A-Z]+)?_?'
        r'(?P<version>V?\d+)?_?'
        r'(?P<language>[a-z]{2})?_?'
        r'(?P<hash>[A-Fa-f0-9]+)?'
        r'\.?(?P<ext>pdf|PDF)?$'
    )

    @classmethod
    def parse(cls, filename: str) -> Optional[FilenameComponents]:
        """
        Parse filename into structured components.

        Args:
            filename: Filename to parse

        Returns:
            FilenameComponents object or None if parsing fails

        Example:
            >>> result = FilenameParser.parse(
            ...     "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf"
            ... )
            >>> result.country_code
            'BD'
            >>> result.year
            1998
        """
        if not filename:
            return None

        # Try strict pattern first
        match = cls.FILENAME_PATTERN.match(filename)
        if match:
            return cls._extract_components(match, filename)

        # Try relaxed pattern
        match = cls.RELAXED_PATTERN.match(filename)
        if match:
            return cls._extract_components(match, filename)

        return None

    @classmethod
    def parse_to_dict(cls, filename: str) -> Dict[str, Any]:
        """
        Parse filename into dictionary format.

        Args:
            filename: Filename to parse

        Returns:
            Dictionary with parsed components

        Example:
            >>> FilenameParser.parse_to_dict("BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf")
            {'global_id': 'BD00000001', 'country_code': 'BD', ...}
        """
        components = cls.parse(filename)
        if components:
            return components.to_dict()
        return {}

    @classmethod
    def _extract_components(cls, match: re.Match, filename: str) -> FilenameComponents:
        """Extract components from regex match."""
        groups = match.groupdict()

        # Parse version number
        version_str = groups.get('version', 'V01')
        version = int(re.sub(r'[^0-9]', '', version_str or '1')) or 1

        # Parse year
        year_str = groups.get('year', '')
        year = int(year_str) if year_str and year_str.isdigit() else 0

        return FilenameComponents(
            global_id=groups.get('global_id', ''),
            country_code=groups.get('country', ''),
            doc_type=groups.get('type', ''),
            subtype=groups.get('subtype', ''),
            year=year,
            docnum=groups.get('docnum', ''),
            identifier=groups.get('identifier', ''),
            subject=groups.get('subject', ''),
            status=groups.get('status', ''),
            version=version,
            language=groups.get('language', ''),
            content_hash=groups.get('hash', ''),
            extension=groups.get('ext', 'pdf'),
            filename=filename
        )

    @classmethod
    def extract_citation(cls, filename: str) -> Optional[CitationComponents]:
        """
        Extract and decode citation from filename.

        Args:
            filename: Filename containing encoded citation

        Returns:
            CitationComponents or None

        Example:
            >>> cit = FilenameParser.extract_citation("BD00000001_BD_CAS_HCD_1998_22DLR98H205_...")
            >>> cit.reporter
            'DLR'
            >>> cit.volume
            22
        """
        components = cls.parse(filename)
        if not components or not components.docnum:
            return None

        return CitationEncoder.decode(components.docnum)

    @classmethod
    def extract_metadata(cls, filename: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from filename.

        Args:
            filename: Filename to extract from

        Returns:
            Dictionary with full metadata including decoded citation

        Example:
            >>> meta = FilenameParser.extract_metadata("BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf")
            >>> meta['doc_type_name']
            'Case/Judgment'
        """
        components = cls.parse(filename)
        if not components:
            return {}

        # Base metadata
        metadata = components.to_dict()

        # Add descriptive names
        metadata['country_name'] = COUNTRY_CODES.get(components.country_code, 'Unknown')
        metadata['doc_type_name'] = DOC_TYPE_NAMES.get(components.doc_type, 'Unknown')
        metadata['subject_name'] = SUBJECT_NAMES.get(components.subject, 'Unknown')
        metadata['status_name'] = STATUS_NAMES.get(components.status, 'Unknown')
        metadata['language_name'] = LANGUAGE_CODES.get(components.language, 'Unknown')

        # Court name (if applicable)
        country_courts = COURT_CODES.get(components.country_code, {})
        metadata['court_name'] = country_courts.get(components.subtype, components.subtype)

        # Decode citation if case document
        if components.doc_type == 'CAS':
            citation = CitationEncoder.decode(components.docnum)
            if citation:
                metadata['citation'] = {
                    'volume': citation.volume,
                    'year': citation.year,
                    'reporter': citation.reporter,
                    'court': citation.court,
                    'page': citation.page,
                    'display': CitationEncoder.format_display(components.docnum)
                }

        # Parse identifier (party names)
        if components.identifier and 'v' in components.identifier.lower():
            parts = re.split(r'v(?=[A-Z])', components.identifier, maxsplit=1)
            if len(parts) == 2:
                metadata['petitioner_abbr'] = parts[0]
                metadata['respondent_abbr'] = parts[1]

        return metadata

    @classmethod
    def get_country(cls, filename: str) -> str:
        """Quick extraction of country code."""
        components = cls.parse(filename)
        return components.country_code if components else ""

    @classmethod
    def get_doc_type(cls, filename: str) -> str:
        """Quick extraction of document type."""
        components = cls.parse(filename)
        return components.doc_type if components else ""

    @classmethod
    def get_year(cls, filename: str) -> int:
        """Quick extraction of year."""
        components = cls.parse(filename)
        return components.year if components else 0

    @classmethod
    def get_hash(cls, filename: str) -> str:
        """Quick extraction of content hash."""
        components = cls.parse(filename)
        return components.content_hash if components else ""

    @classmethod
    def split_filename(cls, filename: str) -> Tuple[list, str]:
        """
        Split filename into components list and extension.

        Args:
            filename: Filename to split

        Returns:
            Tuple of (components list, extension)

        Example:
            >>> parts, ext = FilenameParser.split_filename("BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf")
            >>> len(parts)
            12
            >>> ext
            'pdf'
        """
        # Split extension
        if '.' in filename:
            base, ext = filename.rsplit('.', 1)
        else:
            base, ext = filename, 'pdf'

        # Split by underscore
        parts = base.split('_')

        return parts, ext

    @classmethod
    def validate_and_parse(cls, filename: str) -> Tuple[bool, Optional[FilenameComponents], list]:
        """
        Validate filename and return parsed components with errors.

        Args:
            filename: Filename to validate

        Returns:
            Tuple of (is_valid, components, errors)

        Example:
            >>> valid, comp, errors = FilenameParser.validate_and_parse("invalid_filename.pdf")
            >>> valid
            False
            >>> len(errors) > 0
            True
        """
        errors = []

        # Check extension
        if not filename.lower().endswith('.pdf'):
            errors.append("Filename must end with .pdf")

        # Parse components
        components = cls.parse(filename)
        if not components:
            errors.append("Filename does not match expected format")
            return False, None, errors

        # Validate each component
        if len(components.global_id) != 10:
            errors.append(f"Global ID must be 10 characters: {components.global_id}")

        if components.country_code not in COUNTRY_CODES:
            errors.append(f"Invalid country code: {components.country_code}")

        if components.doc_type not in DOC_TYPE_NAMES:
            errors.append(f"Invalid document type: {components.doc_type}")

        if components.year < 1800 or components.year > 2100:
            errors.append(f"Year out of range: {components.year}")

        if components.subject and components.subject not in SUBJECT_NAMES:
            errors.append(f"Invalid subject code: {components.subject}")

        if components.status and components.status not in STATUS_NAMES:
            errors.append(f"Invalid status code: {components.status}")

        if components.language and components.language not in LANGUAGE_CODES:
            errors.append(f"Invalid language code: {components.language}")

        if len(components.content_hash) != HASH_LENGTH:
            errors.append(f"Hash must be {HASH_LENGTH} characters: {components.content_hash}")

        return len(errors) == 0, components, errors

    @classmethod
    def compare_filenames(cls, filename1: str, filename2: str) -> Dict[str, Any]:
        """
        Compare two filenames and identify differences.

        Args:
            filename1: First filename
            filename2: Second filename

        Returns:
            Dictionary with comparison results
        """
        comp1 = cls.parse(filename1)
        comp2 = cls.parse(filename2)

        if not comp1 or not comp2:
            return {"error": "Could not parse one or both filenames"}

        differences = {}
        fields = ['global_id', 'country_code', 'doc_type', 'subtype', 'year',
                  'docnum', 'identifier', 'subject', 'status', 'version',
                  'language', 'content_hash']

        for field in fields:
            val1 = getattr(comp1, field)
            val2 = getattr(comp2, field)
            if val1 != val2:
                differences[field] = {'file1': val1, 'file2': val2}

        return {
            "same_document": comp1.global_id == comp2.global_id,
            "same_content": comp1.content_hash == comp2.content_hash,
            "version_change": comp1.version != comp2.version,
            "differences": differences,
            "difference_count": len(differences)
        }


# Convenience functions
def parse_filename(filename: str) -> Optional[FilenameComponents]:
    """Parse filename to components."""
    return FilenameParser.parse(filename)


def extract_metadata(filename: str) -> Dict[str, Any]:
    """Extract full metadata from filename."""
    return FilenameParser.extract_metadata(filename)


if __name__ == "__main__":
    # Test filename parser
    print("Testing Filename Parser...\n")

    test_filenames = [
        "BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf",
        "BD00000002_BD_ACT_CTR_1860_XLV_PenalCode_CRM_AMD_V01_en_B4E5C6D7F8A9E0F1.pdf",
        "IN00000001_IN_CAS_SC_1973_AIR73SC1461_KesavanandavState_CON_ACT_V01_en_C5D6E7F8A9B0C1D2.pdf",
    ]

    for filename in test_filenames:
        print(f"=== Parsing: {filename} ===")

        # Parse to components
        components = FilenameParser.parse(filename)
        if components:
            print(f"Global ID: {components.global_id}")
            print(f"Country: {components.country_code}")
            print(f"Doc Type: {components.doc_type}")
            print(f"Subtype: {components.subtype}")
            print(f"Year: {components.year}")
            print(f"DOCNUM: {components.docnum}")
            print(f"Identifier: {components.identifier}")
            print(f"Subject: {components.subject}")
            print(f"Status: {components.status}")
            print(f"Version: {components.version}")
            print(f"Language: {components.language}")
            print(f"Hash: {components.content_hash}")
        else:
            print("Failed to parse")
        print()

        # Extract full metadata
        metadata = FilenameParser.extract_metadata(filename)
        if metadata.get('citation'):
            print(f"Citation Display: {metadata['citation']['display']}")
        print(f"Document Type: {metadata.get('doc_type_name')}")
        print(f"Subject Area: {metadata.get('subject_name')}")
        print()

    # Test validation
    print("=== Validation Test ===")
    valid, comp, errors = FilenameParser.validate_and_parse(test_filenames[0])
    print(f"Valid: {valid}")
    if errors:
        print(f"Errors: {errors}")
    print()

    # Test comparison
    print("=== Comparison Test ===")
    comparison = FilenameParser.compare_filenames(test_filenames[0], test_filenames[1])
    print(f"Same document: {comparison['same_document']}")
    print(f"Differences: {comparison['difference_count']}")

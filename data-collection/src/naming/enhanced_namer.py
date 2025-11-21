"""
Enhanced Universal Legal Document Namer
World-Class Legal RAG System - File Naming Convention

Generates filenames in format:
{GLOBALID}_{CC}_{TYPE}_{SUBTYPE}_{YEAR}_{DOCNUM}_{IDENTIFIER}_{SUBJ}_{STATUS}_{VER}_{LANG}_{HASH16}.pdf

Example:
BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvState_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf
"""

import re
import uuid
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .constants import (
    COUNTRY_CODES, DOC_TYPE_NAMES, COURT_CODES, SUBJECT_NAMES, STATUS_NAMES,
    LANGUAGE_CODES, SUBJECT_KEYWORDS, MAX_FILENAME_LENGTH, MAX_IDENTIFIER_LENGTH,
    MAX_DOCNUM_LENGTH, HASH_LENGTH, GLOBAL_ID_LENGTH, VALID_FILENAME_CHARS,
    DocType, SubjectCode, LegalStatus
)
from .citation_encoder import CitationEncoder
from .party_abbreviator import PartyAbbreviator
from .docnum_generator import DocnumGenerator
from .hash_generator import HashGenerator


@dataclass
class DocumentMetadata:
    """Complete metadata for a legal document."""
    # Required fields
    country_code: str = "BD"
    doc_type: str = "CAS"
    year: Optional[int] = None

    # Court/Subtype
    subtype: str = ""  # Court code for cases, CTR/STA for acts

    # Document identification
    citation: Optional[str] = None
    act_number: Optional[str] = None
    rule_number: Optional[str] = None
    order_number: Optional[str] = None
    ordinance_number: Optional[str] = None
    treaty_number: Optional[str] = None
    amendment_number: Optional[int] = None
    doc_number: Optional[str] = None
    case_number: Optional[str] = None
    case_type: Optional[str] = None  # WP, CA, CRL, etc.

    # Party information (for cases)
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    case_title: Optional[str] = None

    # Document title (for acts, rules, etc.)
    title: Optional[str] = None

    # Classification
    subject: str = "GEN"  # Subject code
    status: str = "ACT"  # Legal status
    version: int = 1
    language: str = "en"

    # Content for hashing
    content: Optional[str] = None
    pdf_path: Optional[str] = None

    # Source tracking
    source_url: Optional[str] = None
    source_id: Optional[str] = None

    # Dates
    date_judgment: Optional[str] = None
    date_enacted: Optional[str] = None
    date_effective: Optional[str] = None

    # Auto-generated
    global_id: Optional[str] = None
    content_hash: Optional[str] = None


@dataclass
class FilenameComponents:
    """Parsed components of a legal document filename."""
    global_id: str = ""
    country_code: str = ""
    doc_type: str = ""
    subtype: str = ""
    year: int = 0
    docnum: str = ""
    identifier: str = ""
    subject: str = ""
    status: str = ""
    version: int = 1
    language: str = ""
    content_hash: str = ""
    extension: str = "pdf"

    # Full filename
    filename: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "global_id": self.global_id,
            "country_code": self.country_code,
            "doc_type": self.doc_type,
            "subtype": self.subtype,
            "year": self.year,
            "docnum": self.docnum,
            "identifier": self.identifier,
            "subject": self.subject,
            "status": self.status,
            "version": self.version,
            "language": self.language,
            "content_hash": self.content_hash,
            "extension": self.extension,
            "filename": self.filename,
        }


class EnhancedNamer:
    """
    Universal Legal Document Naming System.

    Generates standardized filenames for legal documents across jurisdictions.

    Format: {GLOBALID}_{CC}_{TYPE}_{SUBTYPE}_{YEAR}_{DOCNUM}_{IDENTIFIER}_{SUBJ}_{STATUS}_{VER}_{LANG}_{HASH16}.pdf

    Components:
    - GLOBALID: Unique 10-char identifier (CC + 8 digits)
    - CC: Country code (BD, IN, PK)
    - TYPE: Document type (CAS, ACT, RUL, ORD, etc.)
    - SUBTYPE: Court/jurisdiction (HCD, AD, SC, CTR, STA)
    - YEAR: 4-digit year
    - DOCNUM: Document number/citation (max 15 chars)
    - IDENTIFIER: Party names or title abbreviation (max 30 chars)
    - SUBJ: Subject area code (CRM, CIV, CON, etc.)
    - STATUS: Legal status (ACT, REP, AMD, etc.)
    - VER: Version (V01, V02, etc.)
    - LANG: Language code (en, bn, hi, ur)
    - HASH16: 16-char content hash
    """

    # ID sequence counter (in production, use database sequence)
    _sequence_counter = 0

    @classmethod
    def generate_filename(cls, metadata: DocumentMetadata, content: Optional[str] = None) -> str:
        """
        Generate a complete filename from document metadata.

        Args:
            metadata: DocumentMetadata object with all document info
            content: Optional content for hash generation

        Returns:
            Complete filename with extension

        Example:
            >>> meta = DocumentMetadata(
            ...     country_code="BD",
            ...     doc_type="CAS",
            ...     subtype="HCD",
            ...     year=1998,
            ...     citation="22 DLR 1998 HCD 205",
            ...     petitioner="Md. Rahman",
            ...     respondent="State of Bangladesh",
            ...     subject="CRM",
            ...     status="ACT"
            ... )
            >>> EnhancedNamer.generate_filename(meta)
            'BD00000001_BD_CAS_HCD_1998_22DLR98H205_RahmanvStateBD_CRM_ACT_V01_en_A3F4B2C1D5E6F7G8.pdf'
        """
        # Generate each component
        global_id = cls._generate_global_id(metadata)
        country_code = cls._validate_country(metadata.country_code)
        doc_type = cls._validate_doc_type(metadata.doc_type)
        subtype = cls._generate_subtype(metadata)
        year = cls._extract_year(metadata)
        docnum = cls._generate_docnum(metadata)
        identifier = cls._generate_identifier(metadata)
        subject = cls._classify_subject(metadata)
        status = cls._validate_status(metadata.status)
        version = cls._format_version(metadata.version)
        language = cls._validate_language(metadata.language)
        content_hash = cls._generate_hash(metadata, content)

        # Assemble filename
        components = [
            global_id,
            country_code,
            doc_type,
            subtype,
            str(year),
            docnum,
            identifier,
            subject,
            status,
            version,
            language,
            content_hash
        ]

        filename = "_".join(components) + ".pdf"

        # Validate length
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = cls._truncate_filename(components)

        return filename

    @classmethod
    def generate_from_dict(cls, data: Dict[str, Any], content: Optional[str] = None) -> str:
        """
        Generate filename from dictionary data.

        Args:
            data: Dictionary with document metadata
            content: Optional content for hash

        Returns:
            Complete filename
        """
        metadata = DocumentMetadata(
            country_code=data.get("country_code", "BD"),
            doc_type=data.get("doc_type", data.get("type", "CAS")),
            year=data.get("year"),
            subtype=data.get("subtype", data.get("court_code", "")),
            citation=data.get("citation"),
            act_number=data.get("act_number"),
            rule_number=data.get("rule_number"),
            order_number=data.get("order_number"),
            ordinance_number=data.get("ordinance_number"),
            treaty_number=data.get("treaty_number"),
            amendment_number=data.get("amendment_number"),
            doc_number=data.get("doc_number"),
            case_number=data.get("case_number"),
            case_type=data.get("case_type"),
            petitioner=data.get("petitioner"),
            respondent=data.get("respondent"),
            case_title=data.get("case_title", data.get("title", "")),
            title=data.get("title"),
            subject=data.get("subject", "GEN"),
            status=data.get("status", "ACT"),
            version=data.get("version", 1),
            language=data.get("language", "en"),
            content=data.get("content", content),
            pdf_path=data.get("pdf_path"),
            source_url=data.get("source_url", data.get("url", "")),
            source_id=data.get("source_id", data.get("id", "")),
            date_judgment=data.get("date_judgment", data.get("date", "")),
            date_enacted=data.get("date_enacted"),
            date_effective=data.get("date_effective"),
            global_id=data.get("global_id"),
            content_hash=data.get("content_hash"),
        )

        return cls.generate_filename(metadata, content)

    @classmethod
    def _generate_global_id(cls, metadata: DocumentMetadata) -> str:
        """Generate unique global identifier (CC + 8 digits)."""
        if metadata.global_id:
            return metadata.global_id[:GLOBAL_ID_LENGTH]

        # Use country code + 8-digit sequence
        country = metadata.country_code.upper()[:2]
        cls._sequence_counter += 1
        sequence = str(cls._sequence_counter).zfill(8)

        return f"{country}{sequence}"

    @classmethod
    def generate_global_id(cls, country_code: str, sequence: int) -> str:
        """
        Generate a global ID from country code and sequence.

        Args:
            country_code: 2-letter country code
            sequence: Sequence number

        Returns:
            10-character global ID (e.g., "BD00000001")
        """
        country = country_code.upper()[:2]
        return f"{country}{str(sequence).zfill(8)}"

    @classmethod
    def _validate_country(cls, country_code: str) -> str:
        """Validate and normalize country code."""
        code = country_code.upper()[:2] if country_code else "BD"
        return code if code in COUNTRY_CODES else "BD"

    @classmethod
    def _validate_doc_type(cls, doc_type: str) -> str:
        """Validate and normalize document type."""
        dtype = doc_type.upper()[:3] if doc_type else "CAS"
        return dtype if dtype in DOC_TYPE_NAMES else "CAS"

    @classmethod
    def _generate_subtype(cls, metadata: DocumentMetadata) -> str:
        """Generate subtype/court code."""
        if metadata.subtype:
            return metadata.subtype.upper()[:4]

        country = metadata.country_code.upper()

        # Default subtypes by document type
        if metadata.doc_type.upper() == "CAS":
            # Default to High Court
            return COURT_CODES.get(country, {}).get("HCD", "HCD")[:4] if country == "BD" else "HC"
        elif metadata.doc_type.upper() in ("ACT", "RUL", "ORD", "ORN", "REG"):
            return "CTR"  # Central
        elif metadata.doc_type.upper() == "CON":
            return "FED"  # Federal
        elif metadata.doc_type.upper() == "TRE":
            return "INTL"  # International

        return "GEN"

    @classmethod
    def _extract_year(cls, metadata: DocumentMetadata) -> int:
        """Extract year from metadata."""
        if metadata.year:
            return metadata.year

        # Try to extract from dates
        for date_field in [metadata.date_judgment, metadata.date_enacted, metadata.date_effective]:
            if date_field:
                match = re.search(r'(\d{4})', str(date_field))
                if match:
                    return int(match.group(1))

        # Try to extract from citation
        if metadata.citation:
            match = re.search(r'\((\d{4})\)|(\d{4})', metadata.citation)
            if match:
                return int(match.group(1) or match.group(2))

        # Default to current year
        return datetime.now().year

    @classmethod
    def _generate_docnum(cls, metadata: DocumentMetadata) -> str:
        """Generate DOCNUM component."""
        doc_data = {
            "citation": metadata.citation,
            "citation_primary": metadata.citation,
            "country_code": metadata.country_code,
            "court_code": metadata.subtype,
            "year": metadata.year or cls._extract_year(metadata),
            "case_type": metadata.case_type,
            "case_number": metadata.case_number,
            "act_number": metadata.act_number,
            "rule_number": metadata.rule_number,
            "order_number": metadata.order_number,
            "ordinance_number": metadata.ordinance_number,
            "treaty_number": metadata.treaty_number,
            "amendment_number": metadata.amendment_number,
            "doc_number": metadata.doc_number,
            "title": metadata.title,
            "sequence": metadata.case_number or 0,
        }

        return DocnumGenerator.generate(metadata.doc_type, doc_data)

    @classmethod
    def _generate_identifier(cls, metadata: DocumentMetadata) -> str:
        """Generate IDENTIFIER (party names or title abbreviation)."""
        if metadata.doc_type.upper() == "CAS":
            # Case: use party names
            if metadata.petitioner and metadata.respondent:
                return PartyAbbreviator.abbreviate(metadata.petitioner, metadata.respondent)
            elif metadata.case_title:
                return PartyAbbreviator.abbreviate_from_title(metadata.case_title)
            elif metadata.title:
                return PartyAbbreviator.abbreviate_from_title(metadata.title)
        else:
            # Non-case: use title abbreviation
            if metadata.title:
                return PartyAbbreviator.abbreviate_title(metadata.title)

        return "DOC"

    @classmethod
    def _classify_subject(cls, metadata: DocumentMetadata) -> str:
        """Auto-classify subject based on content/title."""
        if metadata.subject and metadata.subject.upper() in SUBJECT_NAMES:
            return metadata.subject.upper()

        # Try to auto-classify from title or content
        text_to_analyze = " ".join(filter(None, [
            metadata.title,
            metadata.case_title,
            metadata.content[:500] if metadata.content else None
        ])).lower()

        if not text_to_analyze:
            return "GEN"

        # Score each subject
        scores = {}
        for subject_code, keywords in SUBJECT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_to_analyze)
            if score > 0:
                scores[subject_code] = score

        # Return highest scoring subject
        if scores:
            return max(scores, key=scores.get)

        return "GEN"

    @classmethod
    def _validate_status(cls, status: str) -> str:
        """Validate and normalize legal status."""
        stat = status.upper()[:3] if status else "ACT"
        return stat if stat in STATUS_NAMES else "ACT"

    @classmethod
    def _format_version(cls, version: int) -> str:
        """Format version number (V01, V02, etc.)."""
        ver = version if version and version > 0 else 1
        return f"V{str(ver).zfill(2)}"

    @classmethod
    def _validate_language(cls, language: str) -> str:
        """Validate and normalize language code."""
        lang = language.lower()[:2] if language else "en"
        return lang if lang in LANGUAGE_CODES else "en"

    @classmethod
    def _generate_hash(cls, metadata: DocumentMetadata, content: Optional[str] = None) -> str:
        """Generate 16-character content hash."""
        if metadata.content_hash:
            return metadata.content_hash[:HASH_LENGTH]

        # Determine content to hash
        hash_content = content or metadata.content

        if hash_content:
            return HashGenerator.generate_hash(hash_content)
        elif metadata.pdf_path:
            file_hash = HashGenerator.generate_file_hash(metadata.pdf_path)
            if file_hash:
                return file_hash

        # Fallback: hash metadata
        fallback_content = f"{metadata.country_code}{metadata.doc_type}{metadata.year}{metadata.title or ''}{metadata.citation or ''}"
        return HashGenerator.generate_hash(fallback_content)

    @classmethod
    def _truncate_filename(cls, components: list) -> str:
        """Truncate filename while preserving structure."""
        # Components that can be truncated
        # Index 5 = docnum, Index 6 = identifier

        # Calculate current length
        filename = "_".join(components) + ".pdf"
        excess = len(filename) - MAX_FILENAME_LENGTH

        if excess <= 0:
            return filename

        # Truncate identifier first (index 6)
        identifier = components[6]
        max_id_len = len(identifier) - excess - 5  # Keep some buffer
        if max_id_len > 5:
            components[6] = identifier[:max_id_len]
            filename = "_".join(components) + ".pdf"
            if len(filename) <= MAX_FILENAME_LENGTH:
                return filename

        # Then truncate docnum (index 5)
        docnum = components[5]
        max_docnum_len = len(docnum) - (len(filename) - MAX_FILENAME_LENGTH) - 2
        if max_docnum_len > 3:
            components[5] = docnum[:max_docnum_len]

        return "_".join(components) + ".pdf"

    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, list]:
        """
        Validate a filename against the naming convention.

        Args:
            filename: Filename to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check extension
        if not filename.endswith(".pdf"):
            errors.append("Filename must end with .pdf")

        # Remove extension for parsing
        base = filename.rsplit(".", 1)[0]

        # Check component count
        parts = base.split("_")
        if len(parts) != 12:
            errors.append(f"Expected 12 components, got {len(parts)}")
            return False, errors

        # Validate each component
        global_id, country, doc_type, subtype, year, docnum, identifier, subject, status, version, lang, hash_str = parts

        # Global ID: 10 chars
        if len(global_id) != 10:
            errors.append(f"Global ID must be 10 chars, got {len(global_id)}")

        # Country code: 2 chars
        if country not in COUNTRY_CODES:
            errors.append(f"Invalid country code: {country}")

        # Document type: 3 chars
        if doc_type not in DOC_TYPE_NAMES:
            errors.append(f"Invalid document type: {doc_type}")

        # Year: 4 digits
        if not year.isdigit() or len(year) != 4:
            errors.append(f"Year must be 4 digits: {year}")

        # DOCNUM: max 15 chars
        if len(docnum) > MAX_DOCNUM_LENGTH:
            errors.append(f"DOCNUM too long: {len(docnum)} > {MAX_DOCNUM_LENGTH}")

        # Identifier: max 30 chars
        if len(identifier) > MAX_IDENTIFIER_LENGTH:
            errors.append(f"Identifier too long: {len(identifier)} > {MAX_IDENTIFIER_LENGTH}")

        # Subject: 3 chars, valid code
        if subject not in SUBJECT_NAMES:
            errors.append(f"Invalid subject code: {subject}")

        # Status: 3 chars, valid code
        if status not in STATUS_NAMES:
            errors.append(f"Invalid status code: {status}")

        # Version: V + 2 digits
        if not re.match(r'^V\d{2}$', version):
            errors.append(f"Invalid version format: {version}")

        # Language: 2 chars
        if lang not in LANGUAGE_CODES:
            errors.append(f"Invalid language code: {lang}")

        # Hash: 16 hex chars
        if not HashGenerator.validate_hash(hash_str):
            errors.append(f"Invalid hash: {hash_str}")

        # Total length
        if len(filename) > MAX_FILENAME_LENGTH:
            errors.append(f"Filename too long: {len(filename)} > {MAX_FILENAME_LENGTH}")

        return len(errors) == 0, errors

    @classmethod
    def get_component_descriptions(cls) -> Dict[str, str]:
        """Get descriptions of all filename components."""
        return {
            "GLOBALID": "Unique 10-character identifier (CC + 8-digit sequence)",
            "CC": "2-letter country code (BD, IN, PK, US, UK, etc.)",
            "TYPE": "3-letter document type (CAS, ACT, RUL, ORD, etc.)",
            "SUBTYPE": "3-4 letter court/jurisdiction (HCD, AD, SC, CTR, etc.)",
            "YEAR": "4-digit year of document",
            "DOCNUM": "Document number/citation encoding (max 15 chars)",
            "IDENTIFIER": "Party names or title abbreviation (max 30 chars)",
            "SUBJ": "3-letter subject area code (CRM, CIV, CON, etc.)",
            "STATUS": "3-letter legal status (ACT, REP, AMD, etc.)",
            "VER": "Version number (V01, V02, etc.)",
            "LANG": "2-letter language code (en, bn, hi, ur)",
            "HASH16": "16-character content hash for integrity",
        }


# Convenience functions
def generate_filename(data: Dict[str, Any], content: Optional[str] = None) -> str:
    """Convenience function to generate filename from dictionary."""
    return EnhancedNamer.generate_from_dict(data, content)


def validate_filename(filename: str) -> Tuple[bool, list]:
    """Convenience function to validate filename."""
    return EnhancedNamer.validate_filename(filename)


def generate_global_id(country_code: str, sequence: int) -> str:
    """Convenience function to generate global ID."""
    return EnhancedNamer.generate_global_id(country_code, sequence)


if __name__ == "__main__":
    # Test enhanced namer
    print("Testing Enhanced Namer...\n")

    # Test case document
    print("=== Case Document ===")
    case_meta = DocumentMetadata(
        country_code="BD",
        doc_type="CAS",
        subtype="HCD",
        year=1998,
        citation="22 (1998) DLR (HCD) 205",
        petitioner="Md. Rahman",
        respondent="State of Bangladesh",
        subject="CRM",
        status="ACT",
        language="en",
        content="This is the judgment content..."
    )
    filename = EnhancedNamer.generate_filename(case_meta)
    print(f"Filename: {filename}")
    print(f"Length: {len(filename)}")
    is_valid, errors = EnhancedNamer.validate_filename(filename)
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    print()

    # Test Act document
    print("=== Act Document ===")
    act_data = {
        "country_code": "BD",
        "doc_type": "ACT",
        "subtype": "CTR",
        "year": 1860,
        "act_number": "XLV",
        "title": "The Penal Code, 1860",
        "subject": "CRM",
        "status": "AMD",
        "language": "en",
    }
    filename = EnhancedNamer.generate_from_dict(act_data)
    print(f"Filename: {filename}")
    print(f"Length: {len(filename)}")
    is_valid, errors = EnhancedNamer.validate_filename(filename)
    print(f"Valid: {is_valid}")
    print()

    # Test unreported case
    print("=== Unreported Case ===")
    unreported_data = {
        "country_code": "BD",
        "doc_type": "CAS",
        "subtype": "HCD",
        "year": 2020,
        "case_type": "WP",
        "case_number": "4567",
        "petitioner": "ABC Corporation Ltd",
        "respondent": "National Board of Revenue",
        "subject": "TAX",
    }
    filename = EnhancedNamer.generate_from_dict(unreported_data)
    print(f"Filename: {filename}")
    print(f"Length: {len(filename)}")
    print()

    # Test Constitution
    print("=== Constitution ===")
    const_data = {
        "country_code": "BD",
        "doc_type": "CON",
        "subtype": "FED",
        "year": 1972,
        "amendment_number": 17,
        "title": "Constitution of Bangladesh",
        "subject": "CON",
    }
    filename = EnhancedNamer.generate_from_dict(const_data)
    print(f"Filename: {filename}")
    print()

    # Show component descriptions
    print("=== Component Descriptions ===")
    for comp, desc in EnhancedNamer.get_component_descriptions().items():
        print(f"{comp}: {desc}")

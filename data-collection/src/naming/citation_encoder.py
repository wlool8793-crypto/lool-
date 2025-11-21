"""
Citation Encoder/Decoder for Legal Document Naming System
Handles encoding citations like "22 DLR (1998) HCD 205" to "22DLR98H205"
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from .constants import REPORTER_CODES


@dataclass
class CitationComponents:
    """Parsed citation components."""
    volume: Optional[int] = None
    year: Optional[int] = None
    reporter: Optional[str] = None
    court: Optional[str] = None
    page: Optional[int] = None
    series: Optional[str] = None
    raw: Optional[str] = None


class CitationEncoder:
    """
    Encode and decode legal citations for filename use.

    Supported formats:
    - Bangladesh: DLR, BLD, BLC, BCR
    - India: AIR, SCC, SCR, SCALE
    - Pakistan: PLD, PCRLJ, CLC, SCMR
    """

    # Citation patterns for parsing
    PATTERNS = {
        # Bangladesh DLR: "22 (1998) DLR (HCD) 205" or "22 DLR (1998) HCD 205"
        "BD_DLR": [
            r'(\d+)\s*\((\d{4})\)\s*DLR\s*\(?(AD|HCD|HC|SC)?\)?\s*(\d+)',
            r'(\d+)\s*DLR\s*\((\d{4})\)\s*(AD|HCD|HC|SC)?\s*(\d+)',
        ],
        # Bangladesh BLD: "8 BLD (AD) 212"
        "BD_BLD": [
            r'(\d+)\s*BLD\s*\(?(AD|HCD|HC|SC)?\)?\s*(\d+)',
        ],
        # Bangladesh BLC: "15 BLC (AD) 123"
        "BD_BLC": [
            r'(\d+)\s*BLC\s*\(?(AD|HCD|HC|SC)?\)?\s*(\d+)',
        ],
        # India AIR: "AIR 1973 SC 1461"
        "IN_AIR": [
            r'AIR\s*(\d{4})\s*(SC|Del|Bom|Mad|Cal|Kar|All|Guj|P&H|Pat|Raj|Ker|AP|Ori|HP|J&K)\s*(\d+)',
        ],
        # India SCC: "(1973) 4 SCC 225"
        "IN_SCC": [
            r'\((\d{4})\)\s*(\d+)\s*SCC\s*(\d+)',
        ],
        # India SCR: "(2009) 9 SCR 611"
        "IN_SCR": [
            r'\((\d{4})\)\s*(\d+)\s*SCR\s*(\d+)',
        ],
        # Pakistan PLD: "1989 PLD SC 1" or "PLD 1989 SC 1"
        "PK_PLD": [
            r'(\d{4})\s*PLD\s*(SC|Kar|Lah|Pesh|Quetta|FSC)\s*(\d+)',
            r'PLD\s*(\d{4})\s*(SC|Kar|Lah|Pesh|Quetta|FSC)\s*(\d+)',
        ],
        # Pakistan SCMR: "2005 SCMR 1234"
        "PK_SCMR": [
            r'(\d{4})\s*SCMR\s*(\d+)',
        ],
    }

    # Court code mappings for encoding
    COURT_ENCODE = {
        # Bangladesh
        "HCD": "H", "AD": "A", "HC": "H", "SC": "S",
        # India
        "Del": "D", "Bom": "B", "Mad": "M", "Cal": "C",
        "Kar": "K", "All": "A", "Guj": "G", "P&H": "P",
        # Pakistan
        "Kar": "K", "Lah": "L", "Pesh": "P", "Quetta": "Q", "FSC": "F",
    }

    COURT_DECODE = {v: k for k, v in COURT_ENCODE.items()}

    @classmethod
    def encode(cls, citation: str, country: str = "BD") -> str:
        """
        Encode a citation string for filename use.

        Args:
            citation: Full citation string
            country: Country code (BD, IN, PK)

        Returns:
            Encoded citation (e.g., "22DLR98H205")

        Examples:
            >>> CitationEncoder.encode("22 (1998) DLR (HCD) 205", "BD")
            '22DLR98H205'
            >>> CitationEncoder.encode("AIR 1973 SC 1461", "IN")
            'AIR73SC1461'
            >>> CitationEncoder.encode("(1973) 4 SCC 225", "IN")
            '4SCC73P225'
        """
        if not citation:
            return ""

        citation = citation.strip()
        country = country.upper()

        # Try Bangladesh patterns
        if country == "BD":
            result = cls._encode_bangladesh(citation)
            if result:
                return result

        # Try India patterns
        elif country == "IN":
            result = cls._encode_india(citation)
            if result:
                return result

        # Try Pakistan patterns
        elif country == "PK":
            result = cls._encode_pakistan(citation)
            if result:
                return result

        # Auto-detect based on content
        result = cls._encode_auto(citation)
        if result:
            return result

        # Fallback: clean and truncate
        return cls._fallback_encode(citation)

    @classmethod
    def _encode_bangladesh(cls, citation: str) -> Optional[str]:
        """Encode Bangladesh citations (DLR, BLD, BLC)."""

        # Try DLR pattern
        for pattern in cls.PATTERNS["BD_DLR"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                groups = match.groups()
                volume = groups[0]
                year = groups[1][-2:]  # Last 2 digits
                court = cls.COURT_ENCODE.get(groups[2], "H") if len(groups) > 2 and groups[2] else "H"
                page = groups[3] if len(groups) > 3 else groups[2]
                return f"{volume}DLR{year}{court}{page}"

        # Try BLD pattern
        for pattern in cls.PATTERNS["BD_BLD"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                volume = match.group(1)
                court = cls.COURT_ENCODE.get(match.group(2), "H") if match.group(2) else "H"
                page = match.group(3)
                return f"{volume}BLD{court}{page}"

        # Try BLC pattern
        for pattern in cls.PATTERNS["BD_BLC"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                volume = match.group(1)
                court = cls.COURT_ENCODE.get(match.group(2), "H") if match.group(2) else "H"
                page = match.group(3)
                return f"{volume}BLC{court}{page}"

        return None

    @classmethod
    def _encode_india(cls, citation: str) -> Optional[str]:
        """Encode India citations (AIR, SCC, SCR)."""

        # Try AIR pattern
        for pattern in cls.PATTERNS["IN_AIR"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                year = match.group(1)[-2:]  # Last 2 digits
                court = match.group(2).upper()
                page = match.group(3)
                return f"AIR{year}{court}{page}"

        # Try SCC pattern
        for pattern in cls.PATTERNS["IN_SCC"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                year = match.group(1)[-2:]
                volume = match.group(2)
                page = match.group(3)
                return f"{volume}SCC{year}P{page}"

        # Try SCR pattern
        for pattern in cls.PATTERNS["IN_SCR"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                year = match.group(1)[-2:]
                volume = match.group(2)
                page = match.group(3)
                return f"{volume}SCR{year}P{page}"

        return None

    @classmethod
    def _encode_pakistan(cls, citation: str) -> Optional[str]:
        """Encode Pakistan citations (PLD, SCMR)."""

        # Try PLD pattern
        for pattern in cls.PATTERNS["PK_PLD"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                year = match.group(1)[-2:]
                court = match.group(2).upper()
                page = match.group(3)
                return f"PLD{year}{court}{page}"

        # Try SCMR pattern
        for pattern in cls.PATTERNS["PK_SCMR"]:
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                year = match.group(1)[-2:]
                page = match.group(2)
                return f"SCMR{year}P{page}"

        return None

    @classmethod
    def _encode_auto(cls, citation: str) -> Optional[str]:
        """Auto-detect and encode citation."""
        citation_upper = citation.upper()

        if "DLR" in citation_upper:
            return cls._encode_bangladesh(citation)
        elif "BLD" in citation_upper or "BLC" in citation_upper:
            return cls._encode_bangladesh(citation)
        elif "AIR" in citation_upper:
            return cls._encode_india(citation)
        elif "SCC" in citation_upper or "SCR" in citation_upper:
            return cls._encode_india(citation)
        elif "PLD" in citation_upper:
            return cls._encode_pakistan(citation)
        elif "SCMR" in citation_upper:
            return cls._encode_pakistan(citation)

        return None

    @classmethod
    def _fallback_encode(cls, citation: str) -> str:
        """Fallback encoding when patterns don't match."""
        # Remove special characters, keep alphanumeric
        cleaned = re.sub(r'[^A-Za-z0-9]', '', citation)
        # Truncate to 15 characters
        return cleaned[:15].upper()

    @classmethod
    def decode(cls, encoded: str) -> Optional[CitationComponents]:
        """
        Decode an encoded citation back to components.

        Args:
            encoded: Encoded citation (e.g., "22DLR98H205")

        Returns:
            CitationComponents dataclass or None

        Example:
            >>> components = CitationEncoder.decode("22DLR98H205")
            >>> components.volume
            22
            >>> components.reporter
            'DLR'
        """
        if not encoded:
            return None

        # DLR pattern: 22DLR98H205
        match = re.match(r'^(\d+)(DLR|BLD|BLC)(\d{2})([A-Z])(\d+)$', encoded)
        if match:
            return CitationComponents(
                volume=int(match.group(1)),
                reporter=match.group(2),
                year=1900 + int(match.group(3)) if int(match.group(3)) > 50 else 2000 + int(match.group(3)),
                court=cls.COURT_DECODE.get(match.group(4), match.group(4)),
                page=int(match.group(5)),
                raw=encoded
            )

        # AIR pattern: AIR73SC1461
        match = re.match(r'^AIR(\d{2})([A-Z]+)(\d+)$', encoded)
        if match:
            return CitationComponents(
                reporter="AIR",
                year=1900 + int(match.group(1)) if int(match.group(1)) > 50 else 2000 + int(match.group(1)),
                court=match.group(2),
                page=int(match.group(3)),
                raw=encoded
            )

        # SCC/SCR pattern: 4SCC73P225
        match = re.match(r'^(\d+)(SCC|SCR)(\d{2})P(\d+)$', encoded)
        if match:
            return CitationComponents(
                volume=int(match.group(1)),
                reporter=match.group(2),
                year=1900 + int(match.group(3)) if int(match.group(3)) > 50 else 2000 + int(match.group(3)),
                page=int(match.group(4)),
                raw=encoded
            )

        # PLD pattern: PLD89SC1
        match = re.match(r'^PLD(\d{2})([A-Z]+)(\d+)$', encoded)
        if match:
            return CitationComponents(
                reporter="PLD",
                year=1900 + int(match.group(1)) if int(match.group(1)) > 50 else 2000 + int(match.group(1)),
                court=match.group(2),
                page=int(match.group(3)),
                raw=encoded
            )

        return None

    @classmethod
    def format_display(cls, encoded: str) -> str:
        """
        Format encoded citation for display.

        Args:
            encoded: Encoded citation

        Returns:
            Human-readable citation string

        Example:
            >>> CitationEncoder.format_display("22DLR98H205")
            '22 (1998) DLR (HCD) 205'
        """
        components = cls.decode(encoded)
        if not components:
            return encoded

        if components.reporter == "DLR":
            court_name = {"H": "HCD", "A": "AD", "S": "SC"}.get(
                cls.COURT_ENCODE.get(components.court, "H"), components.court
            )
            return f"{components.volume} ({components.year}) DLR ({court_name}) {components.page}"

        elif components.reporter in ("BLD", "BLC"):
            court_name = {"H": "HCD", "A": "AD"}.get(
                cls.COURT_ENCODE.get(components.court, "H"), components.court
            )
            return f"{components.volume} {components.reporter} ({court_name}) {components.page}"

        elif components.reporter == "AIR":
            return f"AIR {components.year} {components.court} {components.page}"

        elif components.reporter in ("SCC", "SCR"):
            return f"({components.year}) {components.volume} {components.reporter} {components.page}"

        elif components.reporter == "PLD":
            return f"{components.year} PLD {components.court} {components.page}"

        return encoded

    @classmethod
    def encode_unreported(cls, court: str, year: int, case_type: str, sequence: int) -> str:
        """
        Generate DOCNUM for unreported cases.

        Args:
            court: Court code (HCD, AD, SC)
            year: Year
            case_type: Case type (WP, CA, CRL, etc.)
            sequence: Sequence number

        Returns:
            Encoded docnum (e.g., "HCD98WP0123")

        Example:
            >>> CitationEncoder.encode_unreported("HCD", 1998, "WP", 123)
            'HCD98WP0123'
        """
        year_short = str(year)[-2:]
        seq_padded = str(sequence).zfill(4)
        return f"{court.upper()}{year_short}{case_type.upper()}{seq_padded}"


if __name__ == "__main__":
    # Test citation encoder
    print("Testing Citation Encoder...\n")

    # Bangladesh tests
    print("=== Bangladesh Citations ===")
    bd_citations = [
        "22 (1998) DLR (HCD) 205",
        "44 DLR (1992) AD 111",
        "8 BLD (AD) 212",
        "15 BLC (HCD) 123",
    ]
    for cit in bd_citations:
        encoded = CitationEncoder.encode(cit, "BD")
        decoded = CitationEncoder.format_display(encoded)
        print(f"Original: {cit}")
        print(f"Encoded:  {encoded}")
        print(f"Decoded:  {decoded}")
        print()

    # India tests
    print("=== India Citations ===")
    in_citations = [
        "AIR 1973 SC 1461",
        "(1973) 4 SCC 225",
        "(2009) 9 SCR 611",
    ]
    for cit in in_citations:
        encoded = CitationEncoder.encode(cit, "IN")
        decoded = CitationEncoder.format_display(encoded)
        print(f"Original: {cit}")
        print(f"Encoded:  {encoded}")
        print(f"Decoded:  {decoded}")
        print()

    # Pakistan tests
    print("=== Pakistan Citations ===")
    pk_citations = [
        "1989 PLD SC 1",
        "2005 SCMR 1234",
    ]
    for cit in pk_citations:
        encoded = CitationEncoder.encode(cit, "PK")
        decoded = CitationEncoder.format_display(encoded)
        print(f"Original: {cit}")
        print(f"Encoded:  {encoded}")
        print(f"Decoded:  {decoded}")
        print()

    # Unreported case
    print("=== Unreported Case ===")
    unreported = CitationEncoder.encode_unreported("HCD", 1998, "WP", 123)
    print(f"Unreported: {unreported}")

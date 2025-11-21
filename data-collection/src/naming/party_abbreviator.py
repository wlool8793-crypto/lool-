"""
Party Name Abbreviator for Legal Document Naming System
Abbreviates party names like "Secretary Ministry of Law v. State" to "SecyMinLawvState"
"""

import re
from typing import Tuple, Optional

from .constants import PARTY_ABBREVIATIONS, PARTY_REMOVE_WORDS, MAX_IDENTIFIER_LENGTH


class PartyAbbreviator:
    """
    Abbreviate party names for filename use.

    Handles:
    - Government entities: Secretary Ministry of Law → SecyMinLaw
    - Corporate names: ABC Corporation Ltd → ABCCorpLtd
    - Individual names: Md. Abdul Rahman → MdAbdulRahman
    - Multiple parties: A, B, C v. X, Y, Z → AorsvXors
    """

    # Separator pattern for "versus"
    VS_PATTERNS = [
        r'\s+v\.?\s+',
        r'\s+vs\.?\s+',
        r'\s+versus\s+',
        r'\s+-v-\s+',
        r'\s+against\s+',
    ]

    MAX_PARTY_LENGTH = 25  # Max length for each party
    MAX_TOTAL_LENGTH = MAX_IDENTIFIER_LENGTH  # 30 chars total

    @classmethod
    def abbreviate(cls, petitioner: str, respondent: str) -> str:
        """
        Create abbreviated party identifier.

        Args:
            petitioner: Petitioner/Appellant name
            respondent: Respondent name

        Returns:
            Abbreviated identifier (e.g., "RahmanvState")

        Example:
            >>> PartyAbbreviator.abbreviate("Md. Rahman", "State of Bangladesh")
            'RahmanvStateBD'
        """
        pet_abbr = cls._abbreviate_single(petitioner)
        resp_abbr = cls._abbreviate_single(respondent)

        # Balance lengths
        pet_abbr, resp_abbr = cls._balance_lengths(pet_abbr, resp_abbr)

        return f"{pet_abbr}v{resp_abbr}"

    @classmethod
    def abbreviate_from_title(cls, case_title: str) -> str:
        """
        Extract and abbreviate parties from case title.

        Args:
            case_title: Full case title (e.g., "Rahman v. State")

        Returns:
            Abbreviated identifier

        Example:
            >>> PartyAbbreviator.abbreviate_from_title("Md. Rahman v. State of Bangladesh")
            'RahmanvStateBD'
        """
        petitioner, respondent = cls.extract_parties(case_title)

        if petitioner and respondent:
            return cls.abbreviate(petitioner, respondent)
        elif petitioner:
            return cls._abbreviate_single(petitioner)[:cls.MAX_TOTAL_LENGTH]
        else:
            return cls._clean_title(case_title)[:cls.MAX_TOTAL_LENGTH]

    @classmethod
    def extract_parties(cls, case_title: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract petitioner and respondent from case title.

        Args:
            case_title: Full case title

        Returns:
            Tuple of (petitioner, respondent)

        Example:
            >>> PartyAbbreviator.extract_parties("Rahman v. State")
            ('Rahman', 'State')
        """
        if not case_title:
            return None, None

        # Try each vs pattern
        for pattern in cls.VS_PATTERNS:
            match = re.split(pattern, case_title, maxsplit=1, flags=re.IGNORECASE)
            if len(match) == 2:
                return match[0].strip(), match[1].strip()

        # No "v." found - might be single party or different format
        return case_title.strip(), None

    @classmethod
    def _abbreviate_single(cls, name: str) -> str:
        """Abbreviate a single party name."""
        if not name:
            return ""

        # Clean the name
        name = cls._clean_name(name)

        # Apply abbreviations
        name = cls._apply_abbreviations(name)

        # Remove small words
        name = cls._remove_small_words(name)

        # Handle multiple parties (A, B, C)
        name = cls._handle_multiple_parties(name)

        # Camel case and remove spaces
        name = cls._to_camel_case(name)

        # Truncate if needed
        if len(name) > cls.MAX_PARTY_LENGTH:
            name = cls._smart_truncate(name, cls.MAX_PARTY_LENGTH)

        return name

    @classmethod
    def _clean_name(cls, name: str) -> str:
        """Clean party name of special characters."""
        # Remove honorifics and prefixes
        name = re.sub(r'^(M/s\.?|Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Shri|Smt\.?|Sri|Kumari)\s*', '', name, flags=re.IGNORECASE)

        # Remove content in parentheses (often redundant info)
        name = re.sub(r'\([^)]*\)', '', name)

        # Remove quotes
        name = re.sub(r'["\']', '', name)

        # Remove special characters but keep spaces and basic punctuation
        name = re.sub(r'[^\w\s&,.-]', '', name)

        # Normalize spaces
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    @classmethod
    def _apply_abbreviations(cls, name: str) -> str:
        """Apply known abbreviations."""
        for full, abbr in PARTY_ABBREVIATIONS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(full), re.IGNORECASE)
            name = pattern.sub(abbr, name)
        return name

    @classmethod
    def _remove_small_words(cls, name: str) -> str:
        """Remove small connector words."""
        words = name.split()
        filtered = [w for w in words if w.lower() not in PARTY_REMOVE_WORDS]
        return ' '.join(filtered) if filtered else name

    @classmethod
    def _handle_multiple_parties(cls, name: str) -> str:
        """Handle multiple parties (A, B, C → Aors)."""
        # Check for comma or "and" separated parties
        if ',' in name or ' and ' in name.lower() or ' & ' in name:
            # Split by comma or "and"
            parts = re.split(r',|\s+and\s+|\s*&\s*', name, flags=re.IGNORECASE)
            parts = [p.strip() for p in parts if p.strip()]

            if len(parts) > 1:
                # Take first party and add "ors" (others)
                first_party = parts[0]
                # Get just the surname/main identifier
                first_words = first_party.split()
                if first_words:
                    return first_words[-1] + "ors"  # Last word + "ors"

        return name

    @classmethod
    def _to_camel_case(cls, name: str) -> str:
        """Convert to CamelCase without spaces."""
        words = name.split()
        result = []
        for word in words:
            if word:
                # Capitalize first letter, keep rest as is
                result.append(word[0].upper() + word[1:] if len(word) > 1 else word.upper())
        return ''.join(result)

    @classmethod
    def _smart_truncate(cls, name: str, max_length: int) -> str:
        """Truncate intelligently at word boundaries if possible."""
        if len(name) <= max_length:
            return name

        # Try to find a good break point
        truncated = name[:max_length]

        # Look for uppercase letters (word boundaries in CamelCase)
        for i in range(max_length - 1, max_length // 2, -1):
            if truncated[i].isupper():
                return truncated[:i]

        return truncated

    @classmethod
    def _balance_lengths(cls, pet: str, resp: str) -> Tuple[str, str]:
        """Balance lengths between petitioner and respondent."""
        total_available = cls.MAX_TOTAL_LENGTH - 1  # -1 for 'v'

        if len(pet) + len(resp) <= total_available:
            return pet, resp

        # Allocate space proportionally
        half = total_available // 2

        if len(pet) > half and len(resp) > half:
            # Both too long - truncate both
            pet = cls._smart_truncate(pet, half)
            resp = cls._smart_truncate(resp, half)
        elif len(pet) > half:
            # Only petitioner too long
            pet = cls._smart_truncate(pet, total_available - len(resp))
        else:
            # Only respondent too long
            resp = cls._smart_truncate(resp, total_available - len(pet))

        return pet, resp

    @classmethod
    def _clean_title(cls, title: str) -> str:
        """Clean a title for use as identifier (for non-case documents)."""
        # Remove special characters
        title = re.sub(r'[^\w\s]', '', title)
        # Convert to CamelCase
        return cls._to_camel_case(title)

    @classmethod
    def abbreviate_title(cls, title: str) -> str:
        """
        Abbreviate a document title (for Acts, Rules, etc.).

        Args:
            title: Document title (e.g., "The Penal Code, 1860")

        Returns:
            Abbreviated title (e.g., "PenalCode")

        Example:
            >>> PartyAbbreviator.abbreviate_title("The Penal Code, 1860")
            'PenalCode'
        """
        if not title:
            return ""

        # Remove year
        title = re.sub(r',?\s*\d{4}\s*$', '', title)

        # Remove "The" at start
        title = re.sub(r'^The\s+', '', title, flags=re.IGNORECASE)

        # Remove "Act", "Rules", "Ordinance" etc. at end (optional)
        # Keep them for uniqueness, just clean

        # Clean and abbreviate
        title = cls._clean_name(title)
        title = cls._apply_abbreviations(title)
        title = cls._remove_small_words(title)
        title = cls._to_camel_case(title)

        # Truncate if needed
        if len(title) > cls.MAX_TOTAL_LENGTH:
            title = cls._smart_truncate(title, cls.MAX_TOTAL_LENGTH)

        return title


if __name__ == "__main__":
    # Test party abbreviator
    print("Testing Party Abbreviator...\n")

    # Case titles
    print("=== Case Titles ===")
    cases = [
        "Md. Rahman v. State of Bangladesh",
        "Secretary Ministry of Law v. Bangladesh Legal Aid Services Trust",
        "Kesavananda Bharati Sripadagalvaru v. State of Kerala",
        "A, B, C v. X, Y, Z",
        "M/s ABC Corporation Pvt. Ltd. v. Union of India",
        "The State v. Unknown Accused",
    ]
    for case in cases:
        result = PartyAbbreviator.abbreviate_from_title(case)
        print(f"Original: {case}")
        print(f"Abbreviated: {result}")
        print(f"Length: {len(result)}")
        print()

    # Document titles
    print("=== Document Titles ===")
    titles = [
        "The Penal Code, 1860",
        "Bangladesh Constitution, 1972",
        "Income Tax Act, 1961",
        "Civil Procedure Rules, 2012",
        "Companies Act, 2013",
    ]
    for title in titles:
        result = PartyAbbreviator.abbreviate_title(title)
        print(f"Original: {title}")
        print(f"Abbreviated: {result}")
        print(f"Length: {len(result)}")
        print()

    # Extract parties
    print("=== Extract Parties ===")
    pet, resp = PartyAbbreviator.extract_parties("Rahman v. State")
    print(f"Petitioner: {pet}")
    print(f"Respondent: {resp}")

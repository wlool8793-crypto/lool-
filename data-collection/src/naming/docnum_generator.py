"""
Document Number Generator for Legal Document Naming System
Generates DOCNUM component for different document types
"""

import re
from typing import Optional, Dict, Any

from .constants import ROMAN_NUMERALS, NUMBERS_TO_ROMAN, MAX_DOCNUM_LENGTH
from .citation_encoder import CitationEncoder


class DocnumGenerator:
    """
    Generate DOCNUM component for legal document filenames.

    DOCNUM varies by document type:
    - Cases (reported): Encoded citation (22DLR98H205)
    - Cases (unreported): Court+Year+Type+Seq (HCD98WP0123)
    - Acts: Act number (XLV, 045)
    - Rules: R + number (R015)
    - Orders: O + number (O0023)
    - Constitution: CONST
    - Treaties: T + year (T2015)
    """

    @classmethod
    def generate(cls, doc_type: str, doc_data: Dict[str, Any]) -> str:
        """
        Generate DOCNUM based on document type.

        Args:
            doc_type: Document type (CAS, ACT, RUL, ORD, etc.)
            doc_data: Document metadata dictionary

        Returns:
            DOCNUM string (max 15 chars)

        Examples:
            >>> DocnumGenerator.generate("CAS", {"citation": "22 DLR 1998"})
            '22DLR98H205'
            >>> DocnumGenerator.generate("ACT", {"act_number": "XLV"})
            'XLV'
        """
        doc_type = doc_type.upper()

        if doc_type == "CAS":
            return cls._generate_case_docnum(doc_data)
        elif doc_type == "ACT":
            return cls._generate_act_docnum(doc_data)
        elif doc_type == "RUL":
            return cls._generate_rule_docnum(doc_data)
        elif doc_type == "ORD":
            return cls._generate_order_docnum(doc_data)
        elif doc_type == "ORN":
            return cls._generate_ordinance_docnum(doc_data)
        elif doc_type == "CON":
            return cls._generate_constitution_docnum(doc_data)
        elif doc_type == "TRE":
            return cls._generate_treaty_docnum(doc_data)
        elif doc_type in ("NOT", "CIR", "GAZ"):
            return cls._generate_notification_docnum(doc_data)
        else:
            return cls._generate_generic_docnum(doc_data)

    @classmethod
    def _generate_case_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for case documents."""
        # Check if case has citation (reported)
        citation = doc_data.get("citation") or doc_data.get("citation_primary")

        if citation:
            # Encode the citation
            country = doc_data.get("country_code", "BD")
            encoded = CitationEncoder.encode(citation, country)
            if encoded:
                return encoded[:MAX_DOCNUM_LENGTH]

        # Unreported case - use court + year + type + sequence
        court = doc_data.get("court_code", "")
        year = doc_data.get("year", doc_data.get("date_judgment", ""))
        if isinstance(year, str) and len(year) >= 4:
            year = year[:4]

        case_type = doc_data.get("case_type", "MISC")
        sequence = doc_data.get("case_number", doc_data.get("sequence", 0))

        # Extract just the number from case_number if it contains text
        if isinstance(sequence, str):
            match = re.search(r'(\d+)', sequence)
            sequence = int(match.group(1)) if match else 0

        return CitationEncoder.encode_unreported(
            court=court,
            year=int(year) if year else 0,
            case_type=case_type[:2] if case_type else "MS",
            sequence=int(sequence) if sequence else 0
        )

    @classmethod
    def _generate_act_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Act documents."""
        act_number = doc_data.get("act_number") or doc_data.get("doc_number", "")

        if not act_number:
            # Try to extract from title
            title = doc_data.get("title", "")
            match = re.search(r'Act\s+(?:No\.?\s*)?([IVXLCDM]+|\d+)', title, re.IGNORECASE)
            if match:
                act_number = match.group(1)

        if not act_number:
            return "ACT"

        # Check if Roman numeral
        act_number_upper = str(act_number).upper().strip()
        if act_number_upper in ROMAN_NUMERALS:
            return act_number_upper

        # If numeric, pad to 3 digits
        if str(act_number).isdigit():
            return str(act_number).zfill(3)

        # Clean and return
        return re.sub(r'[^A-Za-z0-9]', '', str(act_number))[:MAX_DOCNUM_LENGTH]

    @classmethod
    def _generate_rule_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Rule documents."""
        rule_number = doc_data.get("rule_number") or doc_data.get("doc_number", "")

        if not rule_number:
            return "R000"

        # If numeric
        if str(rule_number).isdigit():
            return f"R{str(rule_number).zfill(3)}"

        return f"R{re.sub(r'[^A-Za-z0-9]', '', str(rule_number))}"[:MAX_DOCNUM_LENGTH]

    @classmethod
    def _generate_order_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Order documents."""
        order_number = doc_data.get("order_number") or doc_data.get("doc_number", "")

        if not order_number:
            year = doc_data.get("year", "")
            if year:
                return f"O{str(year)[-2:]}000"
            return "O0000"

        # If numeric
        if str(order_number).isdigit():
            return f"O{str(order_number).zfill(4)}"

        return f"O{re.sub(r'[^A-Za-z0-9]', '', str(order_number))}"[:MAX_DOCNUM_LENGTH]

    @classmethod
    def _generate_ordinance_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Ordinance documents."""
        ord_number = doc_data.get("ordinance_number") or doc_data.get("doc_number", "")

        if not ord_number:
            return "ORD"

        # Check if Roman numeral
        ord_upper = str(ord_number).upper().strip()
        if ord_upper in ROMAN_NUMERALS:
            return ord_upper

        # If numeric
        if str(ord_number).isdigit():
            return str(ord_number).zfill(3)

        return re.sub(r'[^A-Za-z0-9]', '', str(ord_number))[:MAX_DOCNUM_LENGTH]

    @classmethod
    def _generate_constitution_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Constitution documents."""
        amendment = doc_data.get("amendment_number")

        if amendment:
            # Constitutional amendment
            if isinstance(amendment, int) or str(amendment).isdigit():
                return f"CONST{str(amendment).zfill(2)}"
            return f"CONST{amendment}"

        return "CONST"

    @classmethod
    def _generate_treaty_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Treaty documents."""
        year = doc_data.get("year", "")
        treaty_number = doc_data.get("treaty_number") or doc_data.get("doc_number", "")

        if treaty_number:
            return f"T{re.sub(r'[^A-Za-z0-9]', '', str(treaty_number))}"[:MAX_DOCNUM_LENGTH]

        if year:
            return f"T{year}"

        return "TREATY"

    @classmethod
    def _generate_notification_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate DOCNUM for Notification/Circular/Gazette documents."""
        doc_number = doc_data.get("doc_number") or doc_data.get("notification_number", "")
        year = doc_data.get("year", "")

        if doc_number:
            if str(doc_number).isdigit():
                if year:
                    return f"N{str(year)[-2:]}{str(doc_number).zfill(4)}"
                return f"N{str(doc_number).zfill(6)}"
            return f"N{re.sub(r'[^A-Za-z0-9]', '', str(doc_number))}"[:MAX_DOCNUM_LENGTH]

        if year:
            return f"N{year}"

        return "N000000"

    @classmethod
    def _generate_generic_docnum(cls, doc_data: Dict[str, Any]) -> str:
        """Generate generic DOCNUM when type is unknown."""
        doc_number = doc_data.get("doc_number", "")
        year = doc_data.get("year", "")

        if doc_number:
            return re.sub(r'[^A-Za-z0-9]', '', str(doc_number))[:MAX_DOCNUM_LENGTH]

        if year:
            return f"DOC{year}"

        return "DOC0000"

    @classmethod
    def to_roman(cls, number: int) -> str:
        """
        Convert number to Roman numeral.

        Args:
            number: Integer (1-60)

        Returns:
            Roman numeral string

        Example:
            >>> DocnumGenerator.to_roman(45)
            'XLV'
        """
        if number in NUMBERS_TO_ROMAN:
            return NUMBERS_TO_ROMAN[number]

        # Handle numbers > 60 with basic algorithm
        result = ""
        values = [
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
        ]
        for val, numeral in values:
            while number >= val:
                result += numeral
                number -= val
        return result

    @classmethod
    def from_roman(cls, roman: str) -> int:
        """
        Convert Roman numeral to number.

        Args:
            roman: Roman numeral string

        Returns:
            Integer value

        Example:
            >>> DocnumGenerator.from_roman("XLV")
            45
        """
        roman = roman.upper().strip()

        if roman in ROMAN_NUMERALS:
            return ROMAN_NUMERALS[roman]

        # Parse complex numerals
        values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        result = 0
        prev = 0

        for char in reversed(roman):
            curr = values.get(char, 0)
            if curr < prev:
                result -= curr
            else:
                result += curr
            prev = curr

        return result

    @classmethod
    def validate_docnum(cls, docnum: str) -> bool:
        """
        Validate DOCNUM format.

        Args:
            docnum: DOCNUM string to validate

        Returns:
            True if valid format
        """
        if not docnum:
            return False

        if len(docnum) > MAX_DOCNUM_LENGTH:
            return False

        # Check for valid characters (alphanumeric only)
        if not re.match(r'^[A-Za-z0-9]+$', docnum):
            return False

        return True


if __name__ == "__main__":
    # Test docnum generator
    print("Testing Document Number Generator...\n")

    # Test case (reported)
    print("=== Reported Case ===")
    case_data = {
        "citation": "22 (1998) DLR (HCD) 205",
        "country_code": "BD"
    }
    docnum = DocnumGenerator.generate("CAS", case_data)
    print(f"Citation: {case_data['citation']}")
    print(f"DOCNUM: {docnum}\n")

    # Test case (unreported)
    print("=== Unreported Case ===")
    unreported_data = {
        "court_code": "HCD",
        "year": 2020,
        "case_type": "WP",
        "case_number": "4567"
    }
    docnum = DocnumGenerator.generate("CAS", unreported_data)
    print(f"Court: {unreported_data['court_code']}, Year: {unreported_data['year']}")
    print(f"DOCNUM: {docnum}\n")

    # Test Act
    print("=== Act ===")
    act_data = {"act_number": "XLV"}
    docnum = DocnumGenerator.generate("ACT", act_data)
    print(f"Act Number: {act_data['act_number']}")
    print(f"DOCNUM: {docnum}\n")

    act_data2 = {"act_number": "45"}
    docnum2 = DocnumGenerator.generate("ACT", act_data2)
    print(f"Act Number: {act_data2['act_number']}")
    print(f"DOCNUM: {docnum2}\n")

    # Test Rule
    print("=== Rule ===")
    rule_data = {"rule_number": "15"}
    docnum = DocnumGenerator.generate("RUL", rule_data)
    print(f"Rule Number: {rule_data['rule_number']}")
    print(f"DOCNUM: {docnum}\n")

    # Test Constitution
    print("=== Constitution ===")
    const_data = {}
    docnum = DocnumGenerator.generate("CON", const_data)
    print(f"Constitution DOCNUM: {docnum}")

    const_amend = {"amendment_number": 17}
    docnum2 = DocnumGenerator.generate("CON", const_amend)
    print(f"17th Amendment DOCNUM: {docnum2}\n")

    # Test Roman numeral conversion
    print("=== Roman Numerals ===")
    for num in [1, 5, 10, 45, 50, 99]:
        roman = DocnumGenerator.to_roman(num)
        back = DocnumGenerator.from_roman(roman)
        print(f"{num} → {roman} → {back}")

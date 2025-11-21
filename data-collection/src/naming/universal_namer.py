"""
Universal Filename Generator for Legal Documents
Generates standardized filenames following the universal naming convention
"""

import re
from typing import Dict, Any, Optional
from pathlib import Path
import json


class UniversalNamer:
    """
    Generates universal filenames for legal documents.

    Filename Format:
    {CC}_{CAT}_{SUBCAT}_{YEAR}_{NUM}_{SEQ}_{YRSEQ}_{SHORT_TITLE}_{SUBJ}_{SUBJSUB}_{DATE}_{STATUS}_{GLOBALID}.pdf

    Example:
    BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045.pdf
    """

    def __init__(self, taxonomy_path: str = None, country_codes_path: str = None):
        """
        Initialize namer with taxonomy and country data.

        Args:
            taxonomy_path: Path to taxonomy.json
            country_codes_path: Path to country_codes.json
        """
        # Default paths
        if taxonomy_path is None:
            taxonomy_path = 'Legal_Database/_SYSTEM/taxonomy.json'
        if country_codes_path is None:
            country_codes_path = 'Legal_Database/_SYSTEM/country_codes.json'

        self.taxonomy = self._load_json(taxonomy_path)
        self.country_codes = self._load_json(country_codes_path)

    def _load_json(self, filepath: str) -> dict:
        """Load JSON file, return empty dict if not found"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def generate_filename(self, doc_data: Dict[str, Any]) -> str:
        """
        Generate universal filename for a document.

        Args:
            doc_data: Dictionary containing document metadata

        Returns:
            Standardized filename (without extension)
        """
        # Extract required fields
        country_code = doc_data.get('country_code', 'XX').upper()
        doc_category = doc_data.get('doc_category', 'MISC').upper()

        # Route to appropriate formatter
        if doc_category == 'CASE':
            return self._format_case_filename(doc_data)
        elif doc_category in ['ACT', 'ORDINANCE']:
            return self._format_act_filename(doc_data)
        elif doc_category == 'RULE':
            return self._format_rule_filename(doc_data)
        elif doc_category == 'ORDER':
            return self._format_order_filename(doc_data)
        else:
            return self._format_generic_filename(doc_data)

    def _format_case_filename(self, doc_data: Dict[str, Any]) -> str:
        """
        Format filename for CASE documents.

        Example: IN_CASE_SC_2023_0123_0001_0234_Kesavananda_CONSTITUTIONAL_FUN_20230515_ACTIVE_0000020234
        """
        parts = []

        # Country code
        parts.append(doc_data.get('country_code', 'XX').upper())

        # Category
        parts.append('CASE')

        # Subcategory (court level)
        court_code = doc_data.get('court_code', 'MISC')
        parts.append(court_code.upper())

        # Year
        year = doc_data.get('doc_year', 0)
        parts.append(str(year) if year else '0000')

        # Case number (padded to 4 digits)
        case_num = doc_data.get('doc_number', '0')
        case_num_str = self._format_number(case_num, 4)
        parts.append(case_num_str)

        # Sequence (padded to 4 digits)
        seq = doc_data.get('sequence', 1)
        parts.append(f"{seq:04d}")

        # Yearly sequence
        yearly_seq = doc_data.get('yearly_sequence', 1)
        parts.append(f"{yearly_seq:04d}")

        # Short title (sanitized)
        title = doc_data.get('title_short') or doc_data.get('title_full', 'Untitled')
        short_title = self._sanitize_title(title, max_length=30)
        parts.append(short_title)

        # Subject
        subject = doc_data.get('subject_code', 'GEN')
        parts.append(subject.upper())

        # Subject subcategory
        subject_sub = doc_data.get('subject_subcategory', 'MIS')
        parts.append(subject_sub.upper())

        # Date (YYYYMMDD or YYYY)
        date = doc_data.get('date_enacted') or doc_data.get('doc_year', '')
        date_str = self._format_date(date)
        parts.append(date_str)

        # Status
        status = doc_data.get('legal_status', 'ACTIVE').upper()
        parts.append(status)

        # Global ID (10 digits)
        global_id = doc_data.get('global_id_numeric', 0)
        parts.append(f"{global_id:010d}")

        return '_'.join(parts)

    def _format_act_filename(self, doc_data: Dict[str, Any]) -> str:
        """
        Format filename for ACT/ORDINANCE documents.

        Example: BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045
        """
        parts = []

        # Country code
        parts.append(doc_data.get('country_code', 'XX').upper())

        # Category
        parts.append('ACT')

        # Subcategory (jurisdiction level)
        jurisdiction = doc_data.get('jurisdiction_level', 'CENTRAL')
        parts.append(jurisdiction.upper())

        # Year
        year = doc_data.get('doc_year', 0)
        parts.append(str(year) if year else '0000')

        # Act number (Roman or Arabic)
        act_num = doc_data.get('doc_number', '0')
        act_num_str = self._format_act_number(act_num)
        parts.append(act_num_str)

        # Sequence (padded to 4 digits)
        seq = doc_data.get('sequence', 1)
        parts.append(f"{seq:04d}")

        # Yearly sequence
        yearly_seq = doc_data.get('yearly_sequence', 1)
        parts.append(f"{yearly_seq:04d}")

        # Short title (sanitized)
        title = doc_data.get('title_short') or doc_data.get('title_full', 'Untitled')
        short_title = self._sanitize_title(title, max_length=40)
        parts.append(short_title)

        # Subject
        subject = doc_data.get('subject_code', 'GEN')
        parts.append(subject.upper())

        # Subject subcategory
        subject_sub = doc_data.get('subject_subcategory', 'MIS')
        parts.append(subject_sub.upper())

        # Date (usually just year for acts)
        date = str(year) if year else '0000'
        parts.append(date)

        # Status
        status = doc_data.get('legal_status', 'ACTIVE').upper()
        parts.append(status)

        # Global ID (10 digits)
        global_id = doc_data.get('global_id_numeric', 0)
        parts.append(f"{global_id:010d}")

        return '_'.join(parts)

    def _format_rule_filename(self, doc_data: Dict[str, Any]) -> str:
        """Format filename for RULE documents"""
        # Similar to ACT but with RULE category
        parts = []

        parts.append(doc_data.get('country_code', 'XX').upper())
        parts.append('RULE')
        parts.append(doc_data.get('jurisdiction_level', 'CENTRAL').upper())

        year = doc_data.get('doc_year', 0)
        parts.append(str(year) if year else '0000')

        rule_num = doc_data.get('doc_number', '0')
        parts.append(self._format_number(rule_num, 4))

        seq = doc_data.get('sequence', 1)
        parts.append(f"{seq:04d}")

        yearly_seq = doc_data.get('yearly_sequence', 1)
        parts.append(f"{yearly_seq:04d}")

        title = doc_data.get('title_short') or doc_data.get('title_full', 'Untitled')
        parts.append(self._sanitize_title(title, max_length=40))

        parts.append(doc_data.get('subject_code', 'GEN').upper())
        parts.append(doc_data.get('subject_subcategory', 'MIS').upper())

        parts.append(str(year) if year else '0000')
        parts.append(doc_data.get('legal_status', 'ACTIVE').upper())

        global_id = doc_data.get('global_id_numeric', 0)
        parts.append(f"{global_id:010d}")

        return '_'.join(parts)

    def _format_order_filename(self, doc_data: Dict[str, Any]) -> str:
        """Format filename for ORDER documents"""
        parts = []

        parts.append(doc_data.get('country_code', 'XX').upper())
        parts.append('ORDER')
        parts.append(doc_data.get('jurisdiction_level', 'CENTRAL').upper())

        year = doc_data.get('doc_year', 0)
        parts.append(str(year) if year else '0000')

        order_num = doc_data.get('doc_number', '0')
        parts.append(self._format_number(order_num, 4))

        seq = doc_data.get('sequence', 1)
        parts.append(f"{seq:04d}")

        yearly_seq = doc_data.get('yearly_sequence', 1)
        parts.append(f"{yearly_seq:04d}")

        title = doc_data.get('title_short') or doc_data.get('title_full', 'Untitled')
        parts.append(self._sanitize_title(title, max_length=40))

        parts.append(doc_data.get('subject_code', 'GEN').upper())
        parts.append(doc_data.get('subject_subcategory', 'MIS').upper())

        parts.append(str(year) if year else '0000')
        parts.append(doc_data.get('legal_status', 'ACTIVE').upper())

        global_id = doc_data.get('global_id_numeric', 0)
        parts.append(f"{global_id:010d}")

        return '_'.join(parts)

    def _format_generic_filename(self, doc_data: Dict[str, Any]) -> str:
        """Format filename for other document types"""
        parts = []

        parts.append(doc_data.get('country_code', 'XX').upper())
        parts.append(doc_data.get('doc_category', 'MISC').upper())
        parts.append('MISC')

        year = doc_data.get('doc_year', 0)
        parts.append(str(year) if year else '0000')

        parts.append('0000')  # No specific number
        parts.append('0001')  # Sequence
        parts.append('0001')  # Yearly sequence

        title = doc_data.get('title_short') or doc_data.get('title_full', 'Untitled')
        parts.append(self._sanitize_title(title, max_length=40))

        parts.append('GEN')  # Subject
        parts.append('MIS')  # Subject sub

        parts.append(str(year) if year else '0000')
        parts.append('ACTIVE')

        global_id = doc_data.get('global_id_numeric', 0)
        parts.append(f"{global_id:010d}")

        return '_'.join(parts)

    def _sanitize_title(self, title: str, max_length: int = 40) -> str:
        """
        Sanitize title for use in filename.

        Args:
            title: Original title
            max_length: Maximum length

        Returns:
            Sanitized title (snake_case, alphanumeric)
        """
        # Remove special characters
        title = re.sub(r'[^\w\s-]', '', title)

        # Replace whitespace and hyphens with underscores
        title = re.sub(r'[-\s]+', '_', title)

        # Remove leading/trailing underscores
        title = title.strip('_')

        # Truncate to max length
        if len(title) > max_length:
            title = title[:max_length]

        # Remove trailing underscore if truncated mid-word
        title = title.rstrip('_')

        # Ensure not empty
        if not title:
            title = 'Untitled'

        return title

    def _format_number(self, number: Any, width: int = 4) -> str:
        """
        Format a number (Roman or Arabic) to fixed width.

        Args:
            number: Number (can be int, str, Roman numeral)
            width: Padding width

        Returns:
            Formatted number string
        """
        if isinstance(number, int):
            return f"{number:0{width}d}"
        elif isinstance(number, str):
            # If already numeric, pad it
            if number.isdigit():
                return f"{int(number):0{width}d}"
            # If Roman numeral or other, return as-is (uppercase)
            return number.upper()
        else:
            return '0' * width

    def _format_act_number(self, act_num: Any) -> str:
        """
        Format act number (can be Roman or Arabic).

        Args:
            act_num: Act number

        Returns:
            Formatted act number
        """
        if isinstance(act_num, int):
            # Pad Arabic numerals
            return f"{act_num:03d}"
        elif isinstance(act_num, str):
            # Check if it's a Roman numeral
            if self._is_roman_numeral(act_num):
                return act_num.upper()
            # Check if it's numeric
            elif act_num.isdigit():
                return f"{int(act_num):03d}"
            else:
                return act_num.upper()
        else:
            return '000'

    def _is_roman_numeral(self, s: str) -> bool:
        """Check if string is a Roman numeral"""
        return bool(re.match(r'^[IVXLCDM]+$', s.upper()))

    def _format_date(self, date: Any) -> str:
        """
        Format date for filename.

        Args:
            date: Date (can be YYYY-MM-DD, YYYYMMDD, or just YYYY)

        Returns:
            Formatted date (YYYYMMDD or YYYY)
        """
        if not date:
            return '0000'

        date_str = str(date)

        # If already YYYYMMDD (8 digits)
        if re.match(r'^\d{8}$', date_str):
            return date_str

        # If YYYY-MM-DD
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', date_str)
        if match:
            return f"{match.group(1)}{match.group(2)}{match.group(3)}"

        # If just YYYY
        if re.match(r'^\d{4}$', date_str):
            return date_str

        return '0000'

    def generate_folder_path(self, doc_data: Dict[str, Any]) -> str:
        """
        Generate folder path for document.

        Args:
            doc_data: Document metadata

        Returns:
            Relative path from Legal_Database/
            e.g., 'BD/ACT/1851-1900' or 'IN/CASE/SC'
        """
        country_code = doc_data.get('country_code', 'XX').upper()
        doc_category = doc_data.get('doc_category', 'MISC').upper()

        # Base path
        path_parts = [country_code, doc_category]

        # Add subcategory based on document type
        if doc_category == 'CASE':
            # For cases: use court level
            court_code = doc_data.get('court_code', 'MISC')
            path_parts.append(court_code.upper())

        elif doc_category in ['ACT', 'ORDINANCE']:
            # For acts: use jurisdiction or time period
            year = doc_data.get('doc_year', 0)

            # Bangladesh uses time periods
            if country_code == 'BD' and year:
                if year <= 1850:
                    path_parts.append('1799-1850')
                elif year <= 1900:
                    path_parts.append('1851-1900')
                elif year <= 1950:
                    path_parts.append('1901-1950')
                elif year <= 2000:
                    path_parts.append('1951-2000')
                else:
                    path_parts.append('2001-2025')
            else:
                # Other countries: use jurisdiction
                jurisdiction = doc_data.get('jurisdiction_level', 'CENTRAL')
                path_parts.append(jurisdiction.upper())

        elif doc_category == 'RULE':
            jurisdiction = doc_data.get('jurisdiction_level', 'CENTRAL')
            path_parts.append(jurisdiction.upper())

        return '/'.join(path_parts)

    def parse_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse universal filename back to metadata dictionary.
        Reverse operation of generate_filename().

        Args:
            filename: Universal filename (with or without .pdf extension)

        Returns:
            Dictionary of metadata or None if invalid

        Examples:
            >>> metadata = namer.parse_filename('BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045.pdf')
            >>> metadata['country_code']
            'BD'
            >>> metadata['doc_year']
            1860
        """
        # Remove .pdf extension if present
        if filename.endswith('.pdf'):
            filename = filename[:-4]

        # Split by underscore
        parts = filename.split('_')

        # Minimum number of parts required
        if len(parts) < 13:
            return None

        metadata = {}

        try:
            # Part 0: Country code (2 chars)
            metadata['country_code'] = parts[0]

            # Part 1: Document category
            metadata['doc_category'] = parts[1]

            # Part 2: Subcategory (jurisdiction or court)
            metadata['jurisdiction_level'] = parts[2]
            metadata['court_code'] = parts[2]  # Alias for cases

            # Part 3: Year
            metadata['doc_year'] = int(parts[3]) if parts[3].isdigit() else 0

            # Part 4: Document number (Roman or Arabic)
            metadata['doc_number'] = parts[4]

            # Part 5: Sequence
            metadata['sequence'] = int(parts[5]) if parts[5].isdigit() else 0

            # Part 6: Yearly sequence
            metadata['yearly_sequence'] = int(parts[6]) if parts[6].isdigit() else 0

            # Part 7: Short title (may contain underscores, need to find where it ends)
            # Title ends before the subject codes (3-letter codes)
            # Find the subject code (last 3-letter code before date/status/globalid)
            title_parts = []
            i = 7
            while i < len(parts) - 5:  # Leave room for SUBJ, SUBJSUB, DATE, STATUS, GLOBALID
                # Check if this looks like a 3-letter subject code
                if len(parts[i]) == 3 and parts[i].isupper():
                    break
                title_parts.append(parts[i])
                i += 1

            metadata['title_short'] = '_'.join(title_parts) if title_parts else 'Untitled'

            # Remaining parts from where title ended
            remaining = parts[i:]

            if len(remaining) >= 5:
                metadata['subject_code'] = remaining[0]
                metadata['subject_subcategory'] = remaining[1]
                metadata['date_enacted'] = remaining[2]  # YYYYMMDD or YYYY
                metadata['legal_status'] = remaining[3]
                metadata['global_id_numeric'] = int(remaining[4]) if remaining[4].isdigit() else 0
            else:
                # Not enough parts
                return None

            return metadata

        except (ValueError, IndexError) as e:
            # Parsing failed
            return None

    def validate_filename(self, filename: str) -> bool:
        """
        Validate if filename follows universal naming convention.

        Args:
            filename: Filename to validate

        Returns:
            True if valid, False otherwise

        Examples:
            >>> namer.validate_filename('BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRIMINAL_PEN_1860_ACTIVE_0000010045.pdf')
            True
            >>> namer.validate_filename('invalid_filename.pdf')
            False
        """
        # Try to parse it
        metadata = self.parse_filename(filename)

        if metadata is None:
            return False

        # Additional validation rules
        # Check country code is valid (2 uppercase letters)
        if not re.match(r'^[A-Z]{2}$', metadata.get('country_code', '')):
            return False

        # Check doc_category is valid
        valid_categories = ['CASE', 'ACT', 'RULE', 'ORDER', 'ORDINANCE', 'MISC']
        if metadata.get('doc_category', '') not in valid_categories:
            return False

        # Check year is reasonable (1000-2999)
        year = metadata.get('doc_year', 0)
        if year < 1000 or year > 2999:
            return False

        # Check global ID is valid (10 digits)
        global_id = metadata.get('global_id_numeric', 0)
        if global_id < 0 or global_id > 9999999999:
            return False

        return True

    def get_court_code(self, court_name: str, country: str = '') -> str:
        """
        Map court name to standard court code.

        Args:
            court_name: Full court name
            country: Country code (optional, for country-specific mapping)

        Returns:
            Standard court code

        Examples:
            >>> namer.get_court_code('Supreme Court of India')
            'SC'
            >>> namer.get_court_code('Delhi High Court')
            'DHC'
            >>> namer.get_court_code('Bombay High Court')
            'BHC'
        """
        court_name = court_name.lower().strip()

        # Supreme Court variations
        if 'supreme' in court_name:
            return 'SC'

        # High Court variations
        if 'high court' in court_name or 'high-court' in court_name:
            # Try to extract state/location name
            if 'delhi' in court_name:
                return 'DHC'
            elif 'bombay' in court_name or 'mumbai' in court_name:
                return 'BHC'
            elif 'calcutta' in court_name or 'kolkata' in court_name:
                return 'CHC'
            elif 'madras' in court_name or 'chennai' in court_name:
                return 'MHC'
            elif 'karnataka' in court_name or 'bangalore' in court_name:
                return 'KHC'
            elif 'allahabad' in court_name:
                return 'AHC'
            elif 'gujarat' in court_name or 'ahmedabad' in court_name:
                return 'GHC'
            else:
                return 'HC'

        # District Court
        if 'district' in court_name:
            return 'DISTRICT'

        # Tribunal
        if 'tribunal' in court_name:
            if 'income tax' in court_name or 'itat' in court_name:
                return 'ITAT'
            elif 'company' in court_name or 'nclt' in court_name:
                return 'NCLT'
            elif 'armed forces' in court_name or 'aft' in court_name:
                return 'AFT'
            else:
                return 'TRIBUNAL'

        # Bangladesh specific
        if country.upper() == 'BD':
            if 'appellate division' in court_name:
                return 'AD'
            elif 'high court division' in court_name:
                return 'HCD'

        return 'MISC'

    def get_law_code(self, act_name: str, year: Optional[int] = None) -> str:
        """
        Generate standard law reference code from act name.

        Args:
            act_name: Full act name
            year: Year of enactment (optional)

        Returns:
            Law code (e.g., 'IPC_1860', 'ITA_1961')

        Examples:
            >>> namer.get_law_code('Indian Penal Code', 1860)
            'IPC_1860'
            >>> namer.get_law_code('Income Tax Act', 1961)
            'ITA_1961'
            >>> namer.get_law_code('Companies Act', 2013)
            'CA_2013'
        """
        act_name = act_name.upper().strip()

        # Common law codes (predefined)
        law_codes = {
            'INDIAN PENAL CODE': 'IPC',
            'PENAL CODE': 'PEN',
            'INCOME TAX ACT': 'ITA',
            'COMPANIES ACT': 'CA',
            'EVIDENCE ACT': 'EVA',
            'CIVIL PROCEDURE CODE': 'CPC',
            'CRIMINAL PROCEDURE CODE': 'CRPC',
            'CONSTITUTION': 'CONST',
            'CONTRACT ACT': 'CA',
            'NEGOTIABLE INSTRUMENTS ACT': 'NIA',
            'TRANSFER OF PROPERTY ACT': 'TPA',
            'ARBITRATION': 'ARB',
            'LIMITATION': 'LIM',
            'SPECIFIC RELIEF': 'SRA',
            'GOODS AND SERVICES TAX': 'GST',
            'CUSTOMS': 'CUST',
            'FOREIGN EXCHANGE': 'FEMA'
        }

        # Check for known acts
        for key, code in law_codes.items():
            if key in act_name:
                if year:
                    return f'{code}_{year}'
                return code

        # Generate code from initials
        # Remove common words
        words = act_name.replace(',', '').split()
        filtered_words = [w for w in words if w not in ['THE', 'OF', 'AND', 'OR', 'ACT', 'CODE']]

        if filtered_words:
            # Take first letter of each significant word
            code = ''.join([w[0] for w in filtered_words[:4]])  # Max 4 letters

            if year:
                return f'{code}_{year}'
            return code

        if year:
            return f'ACT_{year}'
        return 'ACT'


if __name__ == "__main__":
    # Test universal namer
    print("Testing Universal Namer...")

    namer = UniversalNamer()

    # Test Bangladesh Act
    print("\n1. Bangladesh Penal Code:")
    bd_act = {
        'country_code': 'BD',
        'doc_category': 'ACT',
        'jurisdiction_level': 'CENTRAL',
        'doc_year': 1860,
        'doc_number': 'XLV',
        'sequence': 45,
        'yearly_sequence': 45,
        'title_full': 'The Penal Code, 1860',
        'title_short': 'Penal Code',
        'subject_code': 'CRM',
        'subject_subcategory': 'PEN',
        'legal_status': 'ACTIVE',
        'global_id_numeric': 10045
    }
    filename = namer.generate_filename(bd_act)
    folder = namer.generate_folder_path(bd_act)
    print(f"  Filename: {filename}.pdf")
    print(f"  Folder: Legal_Database/{folder}/")

    # Test India Supreme Court Case
    print("\n2. India Supreme Court Case:")
    in_case = {
        'country_code': 'IN',
        'doc_category': 'CASE',
        'court_code': 'SC',
        'doc_year': 2023,
        'doc_number': '123',
        'sequence': 1,
        'yearly_sequence': 234,
        'title_full': 'Kesavananda Bharati v. State of Kerala',
        'title_short': 'Kesavananda Bharati',
        'subject_code': 'CON',
        'subject_subcategory': 'FUN',
        'date_enacted': '2023-05-15',
        'legal_status': 'ACTIVE',
        'global_id_numeric': 20234
    }
    filename = namer.generate_filename(in_case)
    folder = namer.generate_folder_path(in_case)
    print(f"  Filename: {filename}.pdf")
    print(f"  Folder: Legal_Database/{folder}/")

    print("\n3. Bangladesh Act (1875):")
    bd_old_act = {
        'country_code': 'BD',
        'doc_category': 'ACT',
        'doc_year': 1875,
        'doc_number': 'IX',
        'sequence': 9,
        'yearly_sequence': 9,
        'title_short': 'Evidence Act',
        'subject_code': 'CRM',
        'subject_subcategory': 'EVD',
        'legal_status': 'ACTIVE',
        'global_id_numeric': 10009
    }
    filename = namer.generate_filename(bd_old_act)
    folder = namer.generate_folder_path(bd_old_act)
    print(f"  Filename: {filename}.pdf")
    print(f"  Folder: Legal_Database/{folder}/")

    # Test NEW METHODS
    print("\n" + "="*60)
    print("TESTING NEW ENHANCEMENT METHODS")
    print("="*60)

    # Test parse_filename
    print("\n4. Testing parse_filename():")
    test_filename = 'BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRM_PEN_1860_ACTIVE_0000010045.pdf'
    print(f"  Input: {test_filename}")
    parsed = namer.parse_filename(test_filename)
    if parsed:
        print(f"  Parsed successfully:")
        print(f"    Country: {parsed['country_code']}")
        print(f"    Category: {parsed['doc_category']}")
        print(f"    Year: {parsed['doc_year']}")
        print(f"    Title: {parsed['title_short']}")
        print(f"    Subject: {parsed['subject_code']}")
        print(f"    Global ID: {parsed['global_id_numeric']}")
    else:
        print("  Failed to parse!")

    # Test validate_filename
    print("\n5. Testing validate_filename():")
    valid_test = 'BD_ACT_CENTRAL_1860_XLV_0045_0045_Penal_Code_CRM_PEN_1860_ACTIVE_0000010045.pdf'
    invalid_test = 'invalid_filename.pdf'
    print(f"  Valid filename: {namer.validate_filename(valid_test)}")
    print(f"  Invalid filename: {namer.validate_filename(invalid_test)}")

    # Test get_court_code
    print("\n6. Testing get_court_code():")
    courts = [
        'Supreme Court of India',
        'Delhi High Court',
        'Bombay High Court',
        'Appellate Division',
        'Income Tax Appellate Tribunal'
    ]
    for court in courts:
        code = namer.get_court_code(court)
        print(f"  '{court}' → '{code}'")

    # Test get_law_code
    print("\n7. Testing get_law_code():")
    acts = [
        ('Indian Penal Code', 1860),
        ('Income Tax Act', 1961),
        ('Companies Act', 2013),
        ('Evidence Act', 1872),
        ('Custom Duty and Tax Act', 2020)
    ]
    for act_name, year in acts:
        code = namer.get_law_code(act_name, year)
        print(f"  '{act_name}' ({year}) → '{code}'")

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

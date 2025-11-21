"""
Utility Functions for Universal Legal Document System
Provides common helper functions for parsing, validation, and data processing
"""

import re
import hashlib
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path
import unicodedata


# Roman numeral conversion
ROMAN_NUMERALS = {
    'I': 1, 'V': 5, 'X': 10, 'L': 50,
    'C': 100, 'D': 500, 'M': 1000
}

DECIMAL_TO_ROMAN = [
    (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
]


def parse_roman_numeral(roman: str) -> Optional[int]:
    """
    Convert Roman numeral to integer.

    Args:
        roman: Roman numeral string (e.g., 'XLV', 'MCMXC')

    Returns:
        Integer value or None if invalid

    Examples:
        >>> parse_roman_numeral('XLV')
        45
        >>> parse_roman_numeral('MCMXC')
        1990
    """
    if not roman:
        return None

    roman = roman.upper().strip()
    result = 0
    prev_value = 0

    for char in reversed(roman):
        if char not in ROMAN_NUMERALS:
            return None

        value = ROMAN_NUMERALS[char]

        if value < prev_value:
            result -= value
        else:
            result += value

        prev_value = value

    return result


def int_to_roman(num: int) -> str:
    """
    Convert integer to Roman numeral.

    Args:
        num: Integer to convert (1-3999)

    Returns:
        Roman numeral string

    Examples:
        >>> int_to_roman(45)
        'XLV'
        >>> int_to_roman(1990)
        'MCMXC'
    """
    if not 1 <= num <= 3999:
        raise ValueError("Number must be between 1 and 3999")

    result = []
    for value, numeral in DECIMAL_TO_ROMAN:
        count = num // value
        if count:
            result.append(numeral * count)
            num -= value * count

    return ''.join(result)


def parse_date(date_str: Union[str, datetime, None], formats: Optional[list] = None) -> Optional[datetime]:
    """
    Parse date string into datetime object.

    Args:
        date_str: Date string in various formats
        formats: List of date format strings to try

    Returns:
        datetime object or None

    Examples:
        >>> parse_date('2023-05-15')
        datetime.datetime(2023, 5, 15, 0, 0)
        >>> parse_date('15-05-2023')
        datetime.datetime(2023, 5, 15, 0, 0)
    """
    if isinstance(date_str, datetime):
        return date_str

    if not date_str:
        return None

    # Default formats to try
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%Y%m%d',
            '%d.%m.%Y',
            '%Y.%m.%d',
            '%B %d, %Y',
            '%d %B %Y',
            '%b %d, %Y',
            '%d %b %Y'
        ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except (ValueError, TypeError):
            continue

    return None


def format_date(date_obj: Union[datetime, str, None], format_str: str = '%Y-%m-%d') -> str:
    """
    Format datetime object or string to specific format.

    Args:
        date_obj: datetime object or date string
        format_str: Output format string

    Returns:
        Formatted date string

    Examples:
        >>> format_date(datetime(2023, 5, 15), '%Y%m%d')
        '20230515'
    """
    if not date_obj:
        return ''

    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
        if not date_obj:
            return ''

    return date_obj.strftime(format_str)


def sanitize_filename(text: str, max_length: int = 50, replacement: str = '_') -> str:
    """
    Sanitize text for use in filenames.

    Args:
        text: Text to sanitize
        max_length: Maximum length of result
        replacement: Character to replace invalid characters

    Returns:
        Sanitized filename-safe string

    Examples:
        >>> sanitize_filename('Hello: World / Test')
        'Hello_World_Test'
        >>> sanitize_filename('Vodafone vs. Union of India')
        'Vodafone_vs_Union_of_India'
    """
    if not text:
        return 'Untitled'

    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Replace invalid filename characters
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, text)

    # Replace common legal separators
    text = re.sub(r'\s+vs\.?\s+', '_vs_', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+v\.?\s+', '_v_', text, flags=re.IGNORECASE)

    # Replace multiple spaces/underscores with single
    text = re.sub(r'[\s_]+', replacement, text)

    # Remove leading/trailing separators
    text = text.strip(replacement + ' .')

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rstrip(replacement + ' .')

    return text or 'Untitled'


def clean_text(text: str, remove_extra_whitespace: bool = True) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Text to clean
        remove_extra_whitespace: Remove extra whitespace

    Returns:
        Cleaned text
    """
    if not text:
        return ''

    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)

    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char == '\n' or char == '\t' or not unicodedata.category(char).startswith('C'))

    if remove_extra_whitespace:
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing whitespace from lines
        text = '\n'.join(line.rstrip() for line in text.split('\n'))

    return text.strip()


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> Optional[str]:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5, sha1)

    Returns:
        Hex digest of hash or None if file doesn't exist

    Examples:
        >>> calculate_file_hash('document.pdf')
        'a1b2c3d4e5f6...'
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    try:
        hash_obj = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    except (IOError, ValueError) as e:
        return None


def calculate_string_hash(text: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a string.

    Args:
        text: Text to hash
        algorithm: Hash algorithm

    Returns:
        Hex digest of hash
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def extract_year_from_string(text: str) -> Optional[int]:
    """
    Extract 4-digit year from string.

    Args:
        text: Text containing year

    Returns:
        Year as integer or None

    Examples:
        >>> extract_year_from_string('The Penal Code, 1860')
        1860
        >>> extract_year_from_string('Act XLV of 1860')
        1860
    """
    # Find 4-digit year (1000-2999)
    match = re.search(r'\b([12]\d{3})\b', text)
    if match:
        return int(match.group(1))
    return None


def extract_numbers_from_string(text: str) -> list:
    """
    Extract all numbers from string.

    Args:
        text: Text containing numbers

    Returns:
        List of numbers as integers

    Examples:
        >>> extract_numbers_from_string('Section 302 and 304 IPC')
        [302, 304]
    """
    return [int(num) for num in re.findall(r'\d+', text)]


def normalize_court_name(court_name: str) -> str:
    """
    Normalize court name to standard format.

    Args:
        court_name: Court name in any format

    Returns:
        Normalized court name

    Examples:
        >>> normalize_court_name('supreme court of india')
        'Supreme Court of India'
        >>> normalize_court_name('delhi high court')
        'Delhi High Court'
    """
    if not court_name:
        return ''

    # Title case
    court_name = court_name.strip().title()

    # Fix common abbreviations
    replacements = {
        'Sc ': 'SC ',
        'Hc ': 'HC ',
        ' Of ': ' of ',
        ' And ': ' and ',
        ' The ': ' the ',
        ' For ': ' for ',
        ' In ': ' in ',
        ' At ': ' at '
    }

    for old, new in replacements.items():
        court_name = court_name.replace(old, new)

    return court_name


def get_file_size(file_path: Union[str, Path]) -> Optional[int]:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes or None
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    return file_path.stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Examples:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].rstrip() + suffix


def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain name or None

    Examples:
        >>> extract_domain_from_url('https://indiankanoon.org/doc/123')
        'indiankanoon.org'
    """
    match = re.search(r'https?://([^/]+)', url)
    if match:
        return match.group(1)
    return None


def create_directory_if_not_exists(path: Union[str, Path]) -> Path:
    """
    Create directory if it doesn't exist.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_country_name(country_code: str) -> str:
    """
    Get country name from ISO code.

    Args:
        country_code: 2-letter ISO code

    Returns:
        Country name
    """
    country_map = {
        'BD': 'Bangladesh',
        'IN': 'India',
        'PK': 'Pakistan',
        'US': 'United States',
        'UK': 'United Kingdom',
        'GB': 'United Kingdom',
        'AU': 'Australia',
        'CA': 'Canada',
        'NZ': 'New Zealand',
        'ZA': 'South Africa'
    }

    return country_map.get(country_code.upper(), country_code)


def validate_country_code(country_code: str) -> bool:
    """
    Validate country code format.

    Args:
        country_code: Country code to validate

    Returns:
        True if valid
    """
    return bool(re.match(r'^[A-Z]{2}$', country_code.upper()))


if __name__ == '__main__':
    # Quick tests
    print("Testing Roman Numerals:")
    print(f"XLV = {parse_roman_numeral('XLV')}")  # 45
    print(f"45 = {int_to_roman(45)}")  # XLV

    print("\nTesting Date Parsing:")
    print(f"2023-05-15 = {parse_date('2023-05-15')}")

    print("\nTesting Filename Sanitization:")
    print(f"'Hello: World' = '{sanitize_filename('Hello: World')}'")
    print(f"'Vodafone vs. UOI' = '{sanitize_filename('Vodafone vs. Union of India')}'")

    print("\nTesting Year Extraction:")
    print(f"'The Penal Code, 1860' = {extract_year_from_string('The Penal Code, 1860')}")

    print("\nAll tests completed!")

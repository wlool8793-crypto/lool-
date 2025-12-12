"""
Common utilities for Legal RAG Extraction System (Phase 3)
Shared helper functions used across all extractors
"""

import hashlib
import re
import unicodedata
from typing import Optional, Dict, Any, List
from pathlib import Path
import time
from functools import wraps

from .logging_config import get_logger

logger = get_logger(__name__)


# ==================== Hashing Functions ====================

def hash_content(content: str, length: int = 16) -> str:
    """
    Generate content hash (Phase 1 compatible).

    Args:
        content: Text content to hash
        length: Hash length (16 for Phase 1 compatibility)

    Returns:
        Hex hash string of specified length
    """
    if not content:
        return "0" * length

    # SHA-256 hash
    full_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Return first N characters (uppercase for Phase 1 compatibility)
    return full_hash[:length].upper()


def hash_file(file_path: str) -> str:
    """
    Generate SHA-256 hash of entire file.

    Args:
        file_path: Path to file

    Returns:
        64-character hex hash
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read in chunks for memory efficiency
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


# ==================== Text Normalization ====================

def normalize_text(
    text: str,
    *,
    normalize_unicode: bool = True,
    expand_ligatures: bool = True,
    normalize_quotes: bool = True,
    remove_extra_spaces: bool = True,
    remove_null_bytes: bool = True
) -> str:
    """
    Normalize text for consistent processing.

    Args:
        text: Input text
        normalize_unicode: Apply Unicode NFKC normalization
        expand_ligatures: Expand ligatures (ﬁ → fi)
        normalize_quotes: Convert smart quotes to ASCII
        remove_extra_spaces: Remove extra whitespace
        remove_null_bytes: Remove null bytes

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Remove null bytes
    if remove_null_bytes:
        text = text.replace('\x00', '')

    # Unicode normalization (NFKC - Compatibility Decomposition + Canonical Composition)
    if normalize_unicode:
        text = unicodedata.normalize('NFKC', text)

    # Expand ligatures
    if expand_ligatures:
        ligature_map = {
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬀ': 'ff',
            'ﬃ': 'ffi',
            'ﬄ': 'ffl',
            'ﬆ': 'st',
            'æ': 'ae',
            'œ': 'oe',
        }
        for ligature, replacement in ligature_map.items():
            text = text.replace(ligature, replacement)

    # Normalize quotes
    if normalize_quotes:
        quote_map = {
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            '‚': ',',
            '„': '"',
            '‹': '<',
            '›': '>',
            '«': '<<',
            '»': '>>',
        }
        for smart, ascii_char in quote_map.items():
            text = text.replace(smart, ascii_char)

    # Remove extra spaces
    if remove_extra_spaces:
        # Replace multiple spaces with single space
        text = re.sub(r'  +', ' ', text)
        # Remove spaces at line breaks
        text = re.sub(r' *\n *', '\n', text)
        # Remove multiple newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        # Strip leading/trailing whitespace
        text = text.strip()

    return text


def clean_legal_text(text: str) -> str:
    """
    Clean legal document text with specific rules.

    Args:
        text: Input legal text

    Returns:
        Cleaned text
    """
    # Apply basic normalization
    text = normalize_text(text)

    # Remove page numbers (common pattern: "Page 1 of 10")
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)

    # Remove common headers/footers
    text = re.sub(r'^-+\s*$', '', text, flags=re.MULTILINE)  # Dash separators
    text = re.sub(r'^\*+\s*$', '', text, flags=re.MULTILINE)  # Star separators

    # Fix common OCR errors in legal text
    ocr_fixes = {
        r'\bl\b': 'I',  # Lowercase L → capital I in legal references
        r'\bO\b': '0',  # Capital O → zero in numbers
    }
    for pattern, replacement in ocr_fixes.items():
        text = re.sub(pattern, replacement, text)

    return text


# ==================== Safe Extraction ====================

def safe_extract(func):
    """
    Decorator for safe extraction with error handling.

    Catches exceptions and returns a standardized error result.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Extraction error in {func.__name__}: {e}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'error_type': type(e).__name__
            }
    return wrapper


def timed_execution(func):
    """
    Decorator to measure execution time.

    Adds execution_time_ms to result dict.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_ms = int((end_time - start_time) * 1000)

        if isinstance(result, dict):
            result['execution_time_ms'] = execution_ms

        logger.debug(f"{func.__name__} completed in {execution_ms}ms")

        return result
    return wrapper


# ==================== Text Extraction Helpers ====================

def extract_between(
    text: str,
    start_pattern: str,
    end_pattern: str,
    *,
    include_markers: bool = False,
    first_only: bool = True
) -> Optional[str]:
    """
    Extract text between two patterns.

    Args:
        text: Source text
        start_pattern: Start marker (regex)
        end_pattern: End marker (regex)
        include_markers: Whether to include the markers
        first_only: Return only first match

    Returns:
        Extracted text or None
    """
    if include_markers:
        pattern = f'({start_pattern}.*?{end_pattern})'
    else:
        pattern = f'{start_pattern}(.*?){end_pattern}'

    flags = re.DOTALL | re.IGNORECASE

    if first_only:
        match = re.search(pattern, text, flags=flags)
        return match.group(1) if match else None
    else:
        matches = re.findall(pattern, text, flags=flags)
        return matches if matches else None


def extract_after(text: str, pattern: str, max_chars: int = 500) -> Optional[str]:
    """
    Extract text after a pattern.

    Args:
        text: Source text
        pattern: Pattern to find (regex)
        max_chars: Maximum characters to extract

    Returns:
        Extracted text or None
    """
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        start_pos = match.end()
        return text[start_pos:start_pos + max_chars]
    return None


# ==================== Date Helpers ====================

def normalize_date_string(date_str: str) -> str:
    """
    Normalize date string for parsing.

    Args:
        date_str: Date string

    Returns:
        Normalized date string
    """
    # Remove ordinal suffixes (1st, 2nd, 3rd, 4th)
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    # Normalize month names
    month_map = {
        'jan': 'january',
        'feb': 'february',
        'mar': 'march',
        'apr': 'april',
        'jun': 'june',
        'jul': 'july',
        'aug': 'august',
        'sep': 'september',
        'sept': 'september',
        'oct': 'october',
        'nov': 'november',
        'dec': 'december',
    }

    for abbrev, full in month_map.items():
        date_str = re.sub(rf'\b{abbrev}\b', full, date_str, flags=re.IGNORECASE)

    return date_str


# ==================== Name Helpers ====================

def clean_name(name: str) -> str:
    """
    Clean person/entity name.

    Args:
        name: Raw name

    Returns:
        Cleaned name
    """
    # Remove common titles
    titles = [
        r'\bMr\.?', r'\bMrs\.?', r'\bMs\.?', r'\bDr\.?', r'\bProf\.?',
        r'\bHon\.?', r'\bHonourable', r'\bJustice', r'\bJ\.', r'\bChief',
        r'\bSr\.?', r'\bJr\.?', r'\bMd\.?',
    ]

    for title in titles:
        name = re.sub(title, '', name, flags=re.IGNORECASE)

    # Clean up extra spaces
    name = re.sub(r'\s+', ' ', name).strip()

    return name


# ==================== File Helpers ====================

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024)


def ensure_dir(dir_path: str) -> Path:
    """
    Ensure directory exists, create if not.

    Args:
        dir_path: Directory path

    Returns:
        Path object
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# ==================== Scoring Helpers ====================

def calculate_confidence(
    matches: int,
    total: int,
    *,
    threshold: float = 0.5,
    max_score: float = 1.0
) -> float:
    """
    Calculate confidence score based on matches.

    Args:
        matches: Number of matches
        total: Total possible matches
        threshold: Minimum threshold
        max_score: Maximum score

    Returns:
        Confidence score (0.0-1.0)
    """
    if total == 0:
        return 0.0

    score = matches / total

    # Apply threshold
    if score < threshold:
        score = score * 0.5  # Penalize below threshold

    return min(score, max_score)


def weighted_average(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Calculate weighted average of scores.

    Args:
        scores: Dictionary of score_name → score
        weights: Dictionary of score_name → weight

    Returns:
        Weighted average (0.0-1.0)
    """
    if not scores or not weights:
        return 0.0

    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(scores.get(name, 0.0) * weight for name, weight in weights.items())

    return weighted_sum / total_weight


# ==================== List Helpers ====================

def deduplicate_list(items: List[Any], key: Optional[str] = None) -> List[Any]:
    """
    Deduplicate list while preserving order.

    Args:
        items: List of items
        key: Key to use for dictionaries

    Returns:
        Deduplicated list
    """
    seen = set()
    result = []

    for item in items:
        # Get comparable value
        if key and isinstance(item, dict):
            value = item.get(key)
        else:
            value = item

        # Skip if seen
        if value in seen:
            continue

        seen.add(value)
        result.append(item)

    return result

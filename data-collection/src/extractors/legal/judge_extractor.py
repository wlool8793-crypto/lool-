"""
Judge extraction for Legal RAG Extraction System (Phase 3)
Extract judge names, bench composition, and opinion types
"""

from typing import Dict, Any, List, Optional
import re

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import JudgeSchema, JudgeExtractionResult, OpinionType, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class JudgeExtractor(SimpleExtractor):
    """
    Judge name extractor for legal documents.

    Extracts:
    - Bench composition (all judges)
    - Presiding judge
    - Judgment author(s)
    - Opinion type (majority/dissenting/concurring)
    - Judge order in bench
    """

    def __init__(self):
        super().__init__(name="JudgeExtractor")
        self.cache = get_pattern_cache()

        # Load judge patterns
        self.patterns = self.cache.load_pattern('judges.yaml')
        self.bench_labels = self.patterns.get('bench_labels', [])
        self.judge_titles = self.patterns.get('judge_titles', [])
        self.judge_patterns = self.patterns.get('judge_name_patterns', {})
        self.author_indicators = self.patterns.get('author_indicators', [])
        self.opinion_types = self.patterns.get('opinion_types', {})

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract judge information from text.

        Args:
            text: Document text
            **kwargs: Additional parameters

        Returns:
            JudgeExtractionResult dict
        """
        judges = []

        # Extract bench composition
        bench_judges = self._extract_bench_composition(text)
        if bench_judges:
            judges.extend(bench_judges)

        # Identify presiding judge
        judges = self._identify_presiding_judge(judges)

        # Identify judgment author(s)
        judges = self._identify_authors(judges, text)

        # Determine opinion types
        judges = self._determine_opinion_types(judges, text)

        # Assign judge order
        judges = self._assign_judge_order(judges)

        bench_size = len(judges)

        return {
            'status': 'success' if judges else 'partial',
            'data': {
                'judges': judges,
                'bench_size': bench_size
            }
        }

    # ==================== Bench Composition Extraction ====================

    def _extract_bench_composition(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all judges from bench composition section.

        Looks for sections starting with BEFORE:, CORAM:, etc.
        """
        judges = []

        # Search in first 2000 characters (bench info is usually early)
        search_text = text[:2000]

        # Try to find bench section
        for label in self.bench_labels:
            # Pattern: BEFORE: ... (until next section or double newline)
            pattern = rf'{label}\s*(.+?)(?:\n\n|JUDGMENT|FACTS|$)'
            match = re.search(pattern, search_text, re.IGNORECASE | re.DOTALL)

            if match:
                bench_text = match.group(1)
                judges = self._parse_judge_names(bench_text, confidence=0.90)

                if judges:
                    logger.debug(f"Found {len(judges)} judges under '{label}' label")
                    break

        return judges

    def _parse_judge_names(self, bench_text: str, confidence: float) -> List[Dict[str, Any]]:
        """
        Parse individual judge names from bench text.

        Args:
            bench_text: Text from bench section
            confidence: Base confidence score

        Returns:
            List of judge dictionaries
        """
        judges = []

        # Split by line (each judge usually on separate line)
        lines = bench_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Try each judge name pattern
            judge_name = None

            # Pattern 1: Full format (Hon'ble Justice Name, J.)
            pattern_info = self.judge_patterns.get('full_format', {})
            if pattern_info:
                pattern = pattern_info['pattern']
                match = re.search(pattern, line)
                if match:
                    judge_name = match.group(3) if len(match.groups()) >= 3 else match.group(0)

            # Pattern 2: Simple format (Justice Name)
            if not judge_name:
                pattern_info = self.judge_patterns.get('simple_format', {})
                if pattern_info:
                    pattern = pattern_info['pattern']
                    match = re.search(pattern, line)
                    if match:
                        judge_name = match.group(2) if len(match.groups()) >= 2 else match.group(0)

            # Pattern 3: Name only (when following label)
            if not judge_name:
                pattern_info = self.judge_patterns.get('name_only', {})
                if pattern_info:
                    pattern = pattern_info['pattern']
                    match = re.search(pattern, line)
                    if match:
                        judge_name = match.group(1)

            if judge_name:
                # Clean judge name
                cleaned_name = self._clean_judge_name(judge_name)

                # Check if Chief Justice (presiding)
                is_presiding = self._is_chief_justice(line)

                judge = {
                    'judge_name': cleaned_name,
                    'is_presiding': is_presiding,
                    'is_author': False,  # Will be determined later
                    'opinion_type': OpinionType.MAJORITY.value,
                    'judge_order': 0  # Will be assigned later
                }

                judges.append(judge)

        return judges

    def _clean_judge_name(self, judge_name: str) -> str:
        """
        Clean judge name by removing titles.

        Args:
            judge_name: Raw judge name

        Returns:
            Cleaned name
        """
        # Add "Justice" prefix if not present
        if 'Justice' not in judge_name:
            judge_name = f"Justice {judge_name}"

        # Remove titles
        titles = self.patterns.get('titles_to_remove', [])
        for title in titles:
            judge_name = re.sub(rf'\b{title}\b', '', judge_name, flags=re.IGNORECASE)

        # Remove J. suffix
        judge_name = re.sub(r',?\s*J\.?\s*$', '', judge_name)

        # Clean whitespace
        judge_name = re.sub(r'\s+', ' ', judge_name).strip()

        return judge_name

    def _is_chief_justice(self, line: str) -> bool:
        """Check if line indicates Chief Justice"""
        return bool(re.search(r'\bChief\s+Justice\b|\bCJ\b', line, re.IGNORECASE))

    # ==================== Presiding Judge Identification ====================

    def _identify_presiding_judge(self, judges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify presiding judge.

        Rules:
        1. If Chief Justice in bench, they preside
        2. Otherwise, first listed judge presides
        """
        if not judges:
            return judges

        # Check if any already marked as presiding (Chief Justice)
        has_presiding = any(j['is_presiding'] for j in judges)

        # If no presiding judge, first judge presides
        if not has_presiding and judges:
            judges[0]['is_presiding'] = True

        return judges

    # ==================== Author Identification ====================

    def _identify_authors(self, judges: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """
        Identify judgment author(s).

        Looks for patterns like:
        - "JUDGMENT" followed by judge name
        - "Per Justice Name"
        - "Justice Name, J. (Majority Opinion)"
        """
        # Search in first 5000 characters
        search_text = text[:5000]

        for judge in judges:
            judge_name_part = judge['judge_name'].split()[-1]  # Last name

            # Check for author indicators
            for indicator in self.author_indicators:
                # Pattern: JUDGMENT\n Justice Name
                pattern = rf'{indicator}\s*:?\s*.*?{judge_name_part}'
                if re.search(pattern, search_text, re.IGNORECASE | re.DOTALL):
                    judge['is_author'] = True
                    logger.debug(f"Identified author: {judge['judge_name']}")
                    break

        # If no author found, presiding judge is likely the author
        if not any(j['is_author'] for j in judges):
            for judge in judges:
                if judge['is_presiding']:
                    judge['is_author'] = True
                    break

        return judges

    # ==================== Opinion Type Determination ====================

    def _determine_opinion_types(self, judges: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """
        Determine opinion type for each judge.

        Types: majority, dissenting, concurring
        """
        search_text = text[:8000]

        for judge in judges:
            judge_name_part = judge['judge_name'].split()[-1]

            # Check for dissenting
            for indicator in self.opinion_types.get('dissenting', []):
                pattern = rf'{judge_name_part}.*?{indicator}|{indicator}.*?{judge_name_part}'
                if re.search(pattern, search_text, re.IGNORECASE):
                    judge['opinion_type'] = OpinionType.DISSENTING.value
                    break

            # Check for concurring (if not dissenting)
            if judge['opinion_type'] == OpinionType.MAJORITY.value:
                for indicator in self.opinion_types.get('concurring', []):
                    pattern = rf'{judge_name_part}.*?{indicator}|{indicator}.*?{judge_name_part}'
                    if re.search(pattern, search_text, re.IGNORECASE):
                        judge['opinion_type'] = OpinionType.CONCURRING.value
                        break

        return judges

    # ==================== Post-Processing ====================

    def _assign_judge_order(self, judges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assign judge order (1, 2, 3, ...)"""
        for i, judge in enumerate(judges, 1):
            judge['judge_order'] = i

        return judges


# ==================== Convenience Functions ====================

def extract_judges(text: str) -> List[Dict[str, Any]]:
    """
    Quick extract judges (convenience function).

    Args:
        text: Document text

    Returns:
        List of judge dictionaries
    """
    extractor = JudgeExtractor()
    result = extractor.extract(text)
    return result.get('data', {}).get('judges', [])


def get_presiding_judge(text: str) -> Optional[str]:
    """
    Get presiding judge name.

    Args:
        text: Document text

    Returns:
        Presiding judge name or None
    """
    judges = extract_judges(text)

    for judge in judges:
        if judge.get('is_presiding'):
            return judge['judge_name']

    return None

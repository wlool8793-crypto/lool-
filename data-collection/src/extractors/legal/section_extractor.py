"""
Section/statute extraction for Legal RAG Extraction System (Phase 3)
Extract statutory references with context and frequency tracking
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from collections import Counter

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import SectionSchema, SectionExtractionResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class SectionExtractor(SimpleExtractor):
    """
    Section/statute reference extractor for legal documents.

    Extracts:
    - Section references with act names
    - Article references (Constitution)
    - Rule references
    - Context around references
    - Mention frequency
    """

    def __init__(self):
        super().__init__(name="SectionExtractor")
        self.cache = get_pattern_cache()

        # Load section patterns
        self.patterns = self.cache.load_pattern('sections.yaml')
        self.section_patterns = self.patterns.get('section_patterns', [])
        self.common_acts = self.patterns.get('common_acts', {})
        self.context_config = self.patterns.get('context', {})

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract all section references from text.

        Args:
            text: Document text
            **kwargs: Additional parameters

        Returns:
            SectionExtractionResult dict
        """
        all_sections = []

        # Extract using each pattern
        for pattern_info in self.section_patterns:
            pattern = pattern_info['pattern']
            section_type = pattern_info['type']

            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                section = self._parse_section_reference(
                    match,
                    section_type,
                    text
                )
                if section:
                    all_sections.append(section)

        # Merge duplicates and count frequency
        merged_sections = self._merge_and_count(all_sections)

        # Sort by mention count (most cited first)
        merged_sections.sort(key=lambda s: s['mention_count'], reverse=True)

        return {
            'status': 'success' if merged_sections else 'partial',
            'data': {
                'sections_cited': merged_sections,
                'total_sections': len(merged_sections),
                'total_mentions': sum(s['mention_count'] for s in merged_sections)
            }
        }

    # ==================== Section Parsing ====================

    def _parse_section_reference(
        self,
        match: re.Match,
        section_type: str,
        full_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse section reference from regex match.

        Args:
            match: Regex match object
            section_type: Type of section reference
            full_text: Full document text (for context)

        Returns:
            Section dictionary or None
        """
        try:
            # Extract components based on section type
            if section_type == 'section':
                section_num = match.group(1)
                act_name = match.group(2).strip()

            elif section_type == 'sections':
                # Multiple sections
                sections_str = match.group(1)
                act_name = match.group(2).strip()
                # Split and return first (for now)
                section_num = sections_str.split(',')[0].strip()

            elif section_type == 'article':
                section_num = match.group(1)
                act_name = match.group(2).strip()

            elif section_type == 'rule':
                section_num = match.group(1)
                act_name = match.group(2).strip()

            elif section_type == 'order_rule':
                order_num = match.group(1)
                rule_num = match.group(2)
                act_name = match.group(3).strip()
                section_num = f"{order_num} Rule {rule_num}"

            elif section_type in ['section_short', 'article_short']:
                section_num = match.group(1)
                # Try to infer act from context
                act_name = self._infer_act_name(full_text, match.start())

            else:
                return None

            # Clean act name
            act_name = self._clean_act_name(act_name)

            # Extract context
            context = self._extract_context(full_text, match.start(), match.end())

            return {
                'act_name': act_name,
                'section_number': section_num,
                'section_type': section_type,
                'context': context,
                'mention_count': 1,  # Will be updated in merge
                'position': match.start()
            }

        except Exception as e:
            logger.warning(f"Failed to parse section reference: {e}")
            return None

    # ==================== Act Name Processing ====================

    def _clean_act_name(self, act_name: str) -> str:
        """
        Clean and standardize act name.

        Args:
            act_name: Raw act name

        Returns:
            Cleaned act name
        """
        # Remove leading/trailing punctuation
        act_name = act_name.strip('.,;:')

        # Remove "the" prefix
        act_name = re.sub(r'^the\s+', '', act_name, flags=re.IGNORECASE)

        # Normalize spacing
        act_name = re.sub(r'\s+', ' ', act_name).strip()

        # Capitalize properly
        # Keep "of" lowercase, capitalize others
        words = act_name.split()
        cleaned_words = []
        for word in words:
            if word.lower() in ['of', 'the', 'and']:
                cleaned_words.append(word.lower())
            elif word.isdigit() or ',' in word:
                cleaned_words.append(word)
            else:
                cleaned_words.append(word.capitalize())

        return ' '.join(cleaned_words)

    def _infer_act_name(self, text: str, position: int) -> str:
        """
        Infer act name from context when not explicitly mentioned.

        Args:
            text: Full document text
            position: Position of section reference

        Returns:
            Inferred act name or "Unknown Act"
        """
        # Look backwards up to 500 characters
        search_start = max(0, position - 500)
        context = text[search_start:position]

        # Look for act mentions
        for region in self.common_acts.values():
            for act in region:
                if act in context:
                    return act

        # Check for common keywords
        if 'penal' in context.lower() or 'murder' in context.lower():
            return "Penal Code, 1860"

        if 'constitution' in context.lower():
            return "Constitution"

        if 'criminal' in context.lower():
            return "Code of Criminal Procedure"

        if 'civil' in context.lower():
            return "Code of Civil Procedure"

        return "Unknown Act"

    # ==================== Context Extraction ====================

    def _extract_context(self, text: str, start_pos: int, end_pos: int) -> str:
        """
        Extract surrounding context for section reference.

        Args:
            text: Full text
            start_pos: Start position of match
            end_pos: End position of match

        Returns:
            Context string
        """
        chars_before = self.context_config.get('chars_before', 50)
        chars_after = self.context_config.get('chars_after', 100)

        # Extract before
        context_start = max(0, start_pos - chars_before)
        before = text[context_start:start_pos]

        # Extract after
        context_end = min(len(text), end_pos + chars_after)
        after = text[end_pos:context_end]

        # Combine
        context = before + text[start_pos:end_pos] + after

        # Clean up
        context = re.sub(r'\s+', ' ', context).strip()

        # Limit to reasonable length
        if len(context) > 200:
            context = context[:200] + '...'

        return context

    # ==================== Deduplication & Frequency ====================

    def _merge_and_count(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge duplicate sections and count frequency.

        Args:
            sections: List of section dictionaries

        Returns:
            Merged list with mention counts
        """
        # Group by (act_name, section_number)
        grouped = {}

        for section in sections:
            key = (section['act_name'], section['section_number'])

            if key not in grouped:
                grouped[key] = section.copy()
                grouped[key]['mention_count'] = 1
            else:
                # Increment count
                grouped[key]['mention_count'] += 1

                # Keep context from first mention
                # (or could concatenate all contexts)

        return list(grouped.values())

    # ==================== Bulk Operations ====================

    def get_most_cited_sections(
        self,
        text: str,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get most frequently cited sections.

        Args:
            text: Document text
            top_n: Number of top sections to return

        Returns:
            List of top sections
        """
        result = self.extract(text)
        sections = result.get('data', {}).get('sections_cited', [])

        # Already sorted by mention_count
        return sections[:top_n]

    def get_sections_by_act(
        self,
        text: str,
        act_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all sections from a specific act.

        Args:
            text: Document text
            act_name: Act name to filter by

        Returns:
            List of sections from that act
        """
        result = self.extract(text)
        sections = result.get('data', {}).get('sections_cited', [])

        # Filter by act name (case-insensitive partial match)
        filtered = [
            s for s in sections
            if act_name.lower() in s['act_name'].lower()
        ]

        return filtered

    # ==================== Statistics ====================

    def get_citation_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about section citations.

        Args:
            text: Document text

        Returns:
            Statistics dictionary
        """
        result = self.extract(text)
        data = result.get('data', {})
        sections = data.get('sections_cited', [])

        # Count by act
        acts_count = Counter(s['act_name'] for s in sections)

        # Count by section type
        types_count = Counter(s.get('section_type', 'unknown') for s in sections)

        return {
            'total_sections': data.get('total_sections', 0),
            'total_mentions': data.get('total_mentions', 0),
            'acts_cited': dict(acts_count),
            'section_types': dict(types_count),
            'most_cited': sections[0] if sections else None
        }


# ==================== Convenience Functions ====================

def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Quick extract sections (convenience function).

    Args:
        text: Document text

    Returns:
        List of section dictionaries
    """
    extractor = SectionExtractor()
    result = extractor.extract(text)
    return result.get('data', {}).get('sections_cited', [])


def get_section_summary(text: str) -> str:
    """
    Get human-readable summary of cited sections.

    Args:
        text: Document text

    Returns:
        Summary string
    """
    sections = extract_sections(text)

    if not sections:
        return "No sections cited."

    summary_parts = []
    for section in sections[:5]:  # Top 5
        act = section['act_name']
        num = section['section_number']
        count = section['mention_count']

        summary_parts.append(f"Section {num} of {act} ({count}x)")

    summary = ", ".join(summary_parts)

    if len(sections) > 5:
        summary += f" and {len(sections) - 5} more"

    return summary

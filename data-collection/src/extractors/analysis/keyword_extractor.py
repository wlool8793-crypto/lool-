"""
Keyword extraction for Legal RAG Extraction System (Phase 3)
TF-IDF based keyword extraction with legal term weighting
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import KeywordSchema, KeywordExtractionResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


class KeywordExtractor(SimpleExtractor):
    """
    TF-IDF keyword extractor for legal documents.

    Features:
    - Scikit-learn TF-IDF extraction
    - Legal term weighting (boost by multiplier)
    - Keyword type classification
    - Top N keyword selection
    - Stopword filtering
    - N-gram support (unigrams, bigrams, trigrams)
    """

    def __init__(self):
        super().__init__(name="KeywordExtractor")
        self.cache = get_pattern_cache()

        # Load legal terms dictionary
        self.legal_terms = self.cache.load_pattern('legal_terms.yaml')
        self.categories = self.legal_terms.get('categories', {})
        self.phrases = self.legal_terms.get('phrases', [])
        self.legal_stopwords = set(self.legal_terms.get('legal_stopwords', []))

        # Extraction config
        self.config = self.legal_terms.get('extraction_config', {})
        self.max_keywords = self.config.get('max_keywords', 20)
        self.min_frequency = self.config.get('min_frequency', 2)
        self.min_word_length = self.config.get('min_word_length', 3)

        # TF-IDF config
        tfidf_config = self.config.get('tfidf', {})
        self.max_features = tfidf_config.get('max_features', 100)
        self.ngram_range = tuple(tfidf_config.get('ngram_range', [1, 3]))
        self.min_df = tfidf_config.get('min_df', 1)
        self.max_df = tfidf_config.get('max_df', 0.8)

        # Weighting config
        self.boost_legal_terms = self.config.get('boost_legal_terms', True)
        self.legal_term_multiplier = self.config.get('legal_term_multiplier', 1.5)

        # Build legal term sets
        self._build_legal_term_sets()

        # Initialize TF-IDF vectorizer
        self._initialize_vectorizer()

    def _build_legal_term_sets(self):
        """Build sets of legal terms for fast lookup."""
        self.all_legal_terms = set()
        self.legal_term_weights = {}

        # Extract terms from categories
        for category_name, category_data in self.categories.items():
            weight = category_data.get('weight', 1.0)
            terms = category_data.get('terms', [])

            for term in terms:
                term_lower = term.lower()
                self.all_legal_terms.add(term_lower)
                self.legal_term_weights[term_lower] = weight

        # Add phrases
        for phrase in self.phrases:
            phrase_lower = phrase.lower()
            self.all_legal_terms.add(phrase_lower)
            self.legal_term_weights[phrase_lower] = 1.4  # Default phrase weight

    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer with custom config."""
        # Combine general and legal stopwords
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stop_words = set(ENGLISH_STOP_WORDS) | self.legal_stopwords

        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            stop_words=list(stop_words),
            lowercase=True,
            token_pattern=r'\b[a-zA-Z]{' + str(self.min_word_length) + r',}\b'
        )

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract keywords from text using TF-IDF.

        Args:
            text: Document text
            **kwargs: Additional parameters
                - max_keywords: Override max keywords
                - boost_legal: Override legal term boosting

        Returns:
            KeywordExtractionResult dict
        """
        max_keywords = kwargs.get('max_keywords', self.max_keywords)
        boost_legal = kwargs.get('boost_legal', self.boost_legal_terms)

        # Ensure text is not empty
        if not text or len(text.strip()) < 50:
            return {
                'status': 'failed',
                'data': {
                    'keywords': [],
                    'total_keywords': 0,
                    'legal_term_count': 0,
                    'phrase_count': 0
                },
                'error': 'Text too short for keyword extraction'
            }

        # Extract keywords using TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]

        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return {
                'status': 'failed',
                'data': {
                    'keywords': [],
                    'total_keywords': 0,
                    'legal_term_count': 0,
                    'phrase_count': 0
                },
                'error': str(e)
            }

        # Build keyword list
        keywords = []
        for i, feature in enumerate(feature_names):
            score = float(tfidf_scores[i])

            if score > 0:
                keyword_data = self._create_keyword_entry(
                    feature,
                    score,
                    boost_legal
                )
                keywords.append(keyword_data)

        # Sort by final score (descending)
        keywords.sort(key=lambda k: k['final_score'], reverse=True)

        # Take top N
        top_keywords = keywords[:max_keywords]

        # Calculate statistics
        stats = self._calculate_statistics(top_keywords)

        return {
            'status': 'success' if top_keywords else 'partial',
            'data': {
                'keywords': top_keywords,
                'total_keywords': len(top_keywords),
                'legal_term_count': stats['legal_term_count'],
                'phrase_count': stats['phrase_count'],
                'entity_count': stats['entity_count'],
                'average_score': stats['average_score']
            }
        }

    # ==================== Keyword Processing ====================

    def _create_keyword_entry(
        self,
        keyword: str,
        tfidf_score: float,
        boost_legal: bool
    ) -> Dict[str, Any]:
        """
        Create keyword entry with classification and weighting.

        Args:
            keyword: Keyword text
            tfidf_score: Base TF-IDF score
            boost_legal: Whether to boost legal terms

        Returns:
            Keyword dictionary
        """
        keyword_lower = keyword.lower()

        # Classify keyword type
        keyword_type = self._classify_keyword_type(keyword_lower)

        # Get weight
        base_weight = self.legal_term_weights.get(keyword_lower, 1.0)

        # Apply boosting
        if boost_legal and keyword_type == 'legal_term':
            final_weight = base_weight * self.legal_term_multiplier
        else:
            final_weight = base_weight

        # Calculate final score
        final_score = tfidf_score * final_weight

        return {
            'keyword': keyword,
            'keyword_type': keyword_type,
            'tfidf_score': round(tfidf_score, 4),
            'weight': round(final_weight, 2),
            'final_score': round(final_score, 4),
            'is_legal_term': keyword_type == 'legal_term',
            'is_phrase': ' ' in keyword
        }

    def _classify_keyword_type(self, keyword: str) -> str:
        """
        Classify keyword type.

        Types:
        - legal_term: Known legal vocabulary
        - entity: Proper nouns (capitalized)
        - concept: General concepts

        Args:
            keyword: Keyword to classify

        Returns:
            Keyword type
        """
        # Check if legal term
        if keyword in self.all_legal_terms:
            return 'legal_term'

        # Check if phrase with legal terms
        if ' ' in keyword:
            words = keyword.split()
            if any(w in self.all_legal_terms for w in words):
                return 'legal_term'

        # Check if entity (proper noun - capitalized in original)
        # Note: This is simplified since we lowercase everything
        # A more robust approach would check the original text
        if keyword[0].isupper():
            return 'entity'

        # Default: concept
        return 'concept'

    # ==================== Statistics ====================

    def _calculate_statistics(self, keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate keyword statistics.

        Args:
            keywords: List of keyword dictionaries

        Returns:
            Statistics dictionary
        """
        if not keywords:
            return {
                'legal_term_count': 0,
                'phrase_count': 0,
                'entity_count': 0,
                'average_score': 0.0
            }

        legal_term_count = sum(1 for k in keywords if k['is_legal_term'])
        phrase_count = sum(1 for k in keywords if k['is_phrase'])
        entity_count = sum(1 for k in keywords if k['keyword_type'] == 'entity')
        average_score = sum(k['final_score'] for k in keywords) / len(keywords)

        return {
            'legal_term_count': legal_term_count,
            'phrase_count': phrase_count,
            'entity_count': entity_count,
            'average_score': round(average_score, 4)
        }

    # ==================== Bulk Operations ====================

    def extract_top_keywords(
        self,
        text: str,
        n: int = 10,
        keyword_type: Optional[str] = None
    ) -> List[str]:
        """
        Get top N keywords as simple list.

        Args:
            text: Document text
            n: Number of keywords
            keyword_type: Filter by type (legal_term, entity, concept)

        Returns:
            List of keyword strings
        """
        result = self.extract(text, max_keywords=n * 2)  # Extract more to filter
        keywords = result.get('data', {}).get('keywords', [])

        # Filter by type if specified
        if keyword_type:
            keywords = [k for k in keywords if k['keyword_type'] == keyword_type]

        # Return top N
        return [k['keyword'] for k in keywords[:n]]

    def extract_legal_terms_only(self, text: str, n: int = 10) -> List[Dict[str, Any]]:
        """
        Extract only legal terms.

        Args:
            text: Document text
            n: Number of terms

        Returns:
            List of legal term keyword dictionaries
        """
        result = self.extract(text, max_keywords=n * 3)  # Extract more to filter
        keywords = result.get('data', {}).get('keywords', [])

        # Filter to legal terms only
        legal_terms = [k for k in keywords if k['is_legal_term']]

        return legal_terms[:n]

    def get_keyword_summary(self, text: str, max_keywords: int = 5) -> str:
        """
        Get human-readable keyword summary.

        Args:
            text: Document text
            max_keywords: Max keywords in summary

        Returns:
            Summary string
        """
        result = self.extract(text, max_keywords=max_keywords)
        keywords = result.get('data', {}).get('keywords', [])

        if not keywords:
            return "No keywords extracted."

        keyword_strings = [k['keyword'] for k in keywords]
        return ", ".join(keyword_strings)

    # ==================== Advanced Analysis ====================

    def analyze_keyword_distribution(self, text: str) -> Dict[str, Any]:
        """
        Analyze keyword type distribution.

        Args:
            text: Document text

        Returns:
            Distribution analysis
        """
        result = self.extract(text)
        keywords = result.get('data', {}).get('keywords', [])

        # Count by type
        type_counts = defaultdict(int)
        type_scores = defaultdict(list)

        for keyword in keywords:
            ktype = keyword['keyword_type']
            type_counts[ktype] += 1
            type_scores[ktype].append(keyword['final_score'])

        # Calculate averages
        type_averages = {
            ktype: sum(scores) / len(scores)
            for ktype, scores in type_scores.items()
        }

        return {
            'total_keywords': len(keywords),
            'type_counts': dict(type_counts),
            'type_averages': {k: round(v, 4) for k, v in type_averages.items()},
            'top_keyword': keywords[0]['keyword'] if keywords else None
        }

    def get_category_matches(self, text: str) -> Dict[str, List[str]]:
        """
        Get which legal category terms appear in text.

        Args:
            text: Document text

        Returns:
            Dictionary of category -> matching terms
        """
        text_lower = text.lower()
        category_matches = {}

        for category_name, category_data in self.categories.items():
            terms = category_data.get('terms', [])
            matches = [
                term for term in terms
                if term.lower() in text_lower
            ]

            if matches:
                category_matches[category_name] = matches

        return category_matches


# ==================== Convenience Functions ====================

def extract_keywords(text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
    """
    Quick keyword extraction (convenience function).

    Args:
        text: Document text
        max_keywords: Maximum keywords to extract

    Returns:
        List of keyword dictionaries
    """
    extractor = KeywordExtractor()
    result = extractor.extract(text, max_keywords=max_keywords)
    return result.get('data', {}).get('keywords', [])


def get_keyword_list(text: str, n: int = 10) -> List[str]:
    """
    Get simple list of top N keywords.

    Args:
        text: Document text
        n: Number of keywords

    Returns:
        List of keyword strings
    """
    extractor = KeywordExtractor()
    return extractor.extract_top_keywords(text, n=n)


def get_legal_terms(text: str, n: int = 10) -> List[str]:
    """
    Get only legal terms from text.

    Args:
        text: Document text
        n: Number of terms

    Returns:
        List of legal term strings
    """
    extractor = KeywordExtractor()
    legal_terms = extractor.extract_legal_terms_only(text, n=n)
    return [term['keyword'] for term in legal_terms]

"""
Subject classification for Legal RAG Extraction System (Phase 3)
Multi-method classification: rule-based + ML-based with ensemble voting
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from collections import Counter, defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
import numpy as np

from ..base_extractor import SimpleExtractor
from ..cache_manager import get_pattern_cache
from ..schemas import SubjectClassificationResult, ExtractionStatus
from ..logging_config import get_logger

logger = get_logger(__name__)


# Subject code mappings
SUBJECT_CODES = {
    'CRM': 'Criminal Law',
    'CIV': 'Civil Law',
    'CON': 'Constitutional Law',
    'FAM': 'Family Law',
    'LAB': 'Labour Law',
    'TAX': 'Taxation',
    'COM': 'Commercial Law',
    'PRO': 'Property Law',
    'BAN': 'Banking & Finance',
    'CNS': 'Consumer Protection',  # Changed from CON to avoid duplicate
    'ENV': 'Environment',
    'HUM': 'Human Rights',
    'ADM': 'Administrative Law',
    'ELE': 'Election Law',
    'INT': 'International Law',
    'GEN': 'General'
}


class SubjectClassifier(SimpleExtractor):
    """
    Multi-method subject classifier for legal documents.

    Methods:
    1. Rule-based: Keyword matching with scoring
    2. ML-based: Naive Bayes classification (when trained)
    3. Ensemble: Combine both methods with voting

    Outputs:
    - Primary subject (highest score)
    - Secondary subjects (above threshold)
    - Confidence scores per subject
    """

    def __init__(self, use_ml: bool = True):
        super().__init__(name="SubjectClassifier")
        self.cache = get_pattern_cache()
        self.use_ml = use_ml

        # Load subject keywords
        self.legal_terms = self.cache.load_pattern('legal_terms.yaml')
        self.subject_keywords = self.legal_terms.get('subject_keywords', {})

        # ML components (initialized on first use)
        self.ml_trained = False
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None

        # Classification thresholds
        self.primary_threshold = 0.30  # Minimum score for primary
        self.secondary_threshold = 0.20  # Minimum score for secondary
        self.max_secondary = 2  # Maximum secondary subjects

    def _extract_impl(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Classify document subject using ensemble method.

        Args:
            text: Document text
            **kwargs: Additional parameters
                - method: 'rule', 'ml', or 'ensemble' (default)
                - max_secondary: Override max secondary subjects

        Returns:
            SubjectClassificationResult dict
        """
        method = kwargs.get('method', 'ensemble')
        max_secondary = kwargs.get('max_secondary', self.max_secondary)

        if not text or len(text.strip()) < 100:
            return {
                'status': 'failed',
                'data': {
                    'primary_subject': 'GEN',
                    'primary_subject_name': 'General',
                    'primary_confidence': 1.0,
                    'secondary_subjects': [],
                    'all_scores': {'GEN': 1.0},
                    'classification_method': 'default'
                },
                'error': 'Text too short for classification'
            }

        # Get scores from different methods
        rule_scores = self._rule_based_classification(text)

        if self.use_ml and self.ml_trained:
            ml_scores = self._ml_based_classification(text)
        else:
            ml_scores = {}

        # Combine scores based on method
        if method == 'rule':
            final_scores = rule_scores
        elif method == 'ml' and ml_scores:
            final_scores = ml_scores
        elif method == 'ensemble' and ml_scores:
            final_scores = self._ensemble_voting(rule_scores, ml_scores)
        else:
            final_scores = rule_scores

        # Normalize scores
        final_scores = self._normalize_scores(final_scores)

        # Determine primary and secondary subjects
        primary, secondary = self._select_subjects(
            final_scores,
            max_secondary
        )

        if not primary:
            # Fallback to GEN
            primary = ('GEN', 0.5)
            secondary = []

        return {
            'status': 'success',
            'data': {
                'primary_subject': primary[0],
                'primary_subject_name': SUBJECT_CODES.get(primary[0], 'Unknown'),
                'primary_confidence': round(primary[1], 4),
                'secondary_subjects': [
                    {
                        'subject_code': code,
                        'subject_name': SUBJECT_CODES.get(code, 'Unknown'),
                        'confidence': round(score, 4)
                    }
                    for code, score in secondary
                ],
                'all_scores': {k: round(v, 4) for k, v in final_scores.items()},
                'classification_method': method
            }
        }

    # ==================== Rule-Based Classification ====================

    def _rule_based_classification(self, text: str) -> Dict[str, float]:
        """
        Rule-based classification using keyword matching.

        Args:
            text: Document text

        Returns:
            Dictionary of subject_code -> score
        """
        text_lower = text.lower()
        scores = defaultdict(float)

        # Match keywords for each subject
        for subject_code, keywords in self.subject_keywords.items():
            score = 0.0

            for keyword in keywords:
                keyword_lower = keyword.lower()

                # Count occurrences
                count = text_lower.count(keyword_lower)

                if count > 0:
                    # Weight by keyword length (longer = more specific)
                    keyword_weight = len(keyword_lower.split())

                    # Weight by position (earlier = more important)
                    first_pos = text_lower.find(keyword_lower)
                    position_weight = 1.0 if first_pos < 500 else 0.7

                    # Calculate keyword score
                    keyword_score = count * keyword_weight * position_weight

                    score += keyword_score

            scores[subject_code] = score

        return dict(scores)

    # ==================== ML-Based Classification ====================

    def _ml_based_classification(self, text: str) -> Dict[str, float]:
        """
        ML-based classification using trained classifier.

        Args:
            text: Document text

        Returns:
            Dictionary of subject_code -> probability
        """
        if not self.ml_trained:
            return {}

        try:
            # Transform text to TF-IDF features
            features = self.vectorizer.transform([text])

            # Get probabilities
            probabilities = self.classifier.predict_proba(features)[0]

            # Map to subject codes
            scores = {}
            for i, prob in enumerate(probabilities):
                subject_code = self.label_encoder.inverse_transform([i])[0]
                scores[subject_code] = float(prob)

            return scores

        except Exception as e:
            logger.warning(f"ML classification failed: {e}")
            return {}

    # ==================== Ensemble Voting ====================

    def _ensemble_voting(
        self,
        rule_scores: Dict[str, float],
        ml_scores: Dict[str, float],
        rule_weight: float = 0.6,
        ml_weight: float = 0.4
    ) -> Dict[str, float]:
        """
        Combine rule-based and ML-based scores.

        Args:
            rule_scores: Scores from rule-based method
            ml_scores: Scores from ML method
            rule_weight: Weight for rule-based (default 0.6)
            ml_weight: Weight for ML-based (default 0.4)

        Returns:
            Combined scores
        """
        # Normalize both score sets
        rule_scores = self._normalize_scores(rule_scores)
        ml_scores = self._normalize_scores(ml_scores)

        # Get all subject codes
        all_codes = set(rule_scores.keys()) | set(ml_scores.keys())

        # Combine scores
        combined = {}
        for code in all_codes:
            rule_score = rule_scores.get(code, 0.0)
            ml_score = ml_scores.get(code, 0.0)

            combined[code] = (rule_score * rule_weight) + (ml_score * ml_weight)

        return combined

    # ==================== Score Processing ====================

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize scores to sum to 1.0.

        Args:
            scores: Raw scores

        Returns:
            Normalized scores
        """
        if not scores:
            return {}

        total = sum(scores.values())

        if total == 0:
            return scores

        return {k: v / total for k, v in scores.items()}

    def _select_subjects(
        self,
        scores: Dict[str, float],
        max_secondary: int
    ) -> Tuple[Optional[Tuple[str, float]], List[Tuple[str, float]]]:
        """
        Select primary and secondary subjects from scores.

        Args:
            scores: Normalized scores
            max_secondary: Maximum secondary subjects

        Returns:
            (primary, secondary_list)
            - primary: (subject_code, confidence)
            - secondary: [(subject_code, confidence), ...]
        """
        # Sort by score (descending)
        sorted_subjects = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Primary subject
        if not sorted_subjects or sorted_subjects[0][1] < self.primary_threshold:
            return None, []

        primary = sorted_subjects[0]

        # Secondary subjects
        secondary = [
            (code, score)
            for code, score in sorted_subjects[1:]
            if score >= self.secondary_threshold
        ][:max_secondary]

        return primary, secondary

    # ==================== ML Training ====================

    def train_classifier(
        self,
        training_texts: List[str],
        training_labels: List[str]
    ):
        """
        Train ML classifier on labeled data.

        Args:
            training_texts: List of document texts
            training_labels: List of subject codes
        """
        if len(training_texts) != len(training_labels):
            raise ValueError("Texts and labels must have same length")

        if len(training_texts) < 10:
            logger.warning("Too few training samples for ML classifier")
            return

        try:
            # Initialize components
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8,
                stop_words='english'
            )

            self.label_encoder = LabelEncoder()

            # Transform data
            X = self.vectorizer.fit_transform(training_texts)
            y = self.label_encoder.fit_transform(training_labels)

            # Train classifier
            self.classifier = MultinomialNB(alpha=0.1)
            self.classifier.fit(X, y)

            self.ml_trained = True

            logger.info(f"ML classifier trained on {len(training_texts)} samples")

        except Exception as e:
            logger.error(f"Failed to train ML classifier: {e}")
            self.ml_trained = False

    # ==================== Bulk Operations ====================

    def classify_multiple(
        self,
        texts: List[str],
        method: str = 'ensemble'
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple documents.

        Args:
            texts: List of document texts
            method: Classification method

        Returns:
            List of classification results
        """
        results = []

        for text in texts:
            result = self.extract(text, method=method)
            results.append(result.get('data', {}))

        return results

    def get_subject_distribution(
        self,
        texts: List[str]
    ) -> Dict[str, int]:
        """
        Get distribution of primary subjects across documents.

        Args:
            texts: List of document texts

        Returns:
            Dictionary of subject_code -> count
        """
        results = self.classify_multiple(texts)

        distribution = Counter(
            r.get('primary_subject', 'GEN')
            for r in results
        )

        return dict(distribution)

    # ==================== Analysis ====================

    def analyze_subject_overlap(self, text: str) -> Dict[str, Any]:
        """
        Analyze how many subjects are present in text.

        Args:
            text: Document text

        Returns:
            Overlap analysis
        """
        result = self.extract(text)
        data = result.get('data', {})

        all_scores = data.get('all_scores', {})

        # Count subjects above threshold
        above_threshold = {
            code: score
            for code, score in all_scores.items()
            if score >= self.secondary_threshold
        }

        return {
            'total_subjects_detected': len(above_threshold),
            'primary_subject': data.get('primary_subject'),
            'is_multi_subject': len(above_threshold) > 1,
            'subject_scores': above_threshold,
            'dominant_ratio': data.get('primary_confidence', 0)
        }

    def get_keyword_matches(
        self,
        text: str,
        subject_code: str
    ) -> List[str]:
        """
        Get which keywords matched for a specific subject.

        Args:
            text: Document text
            subject_code: Subject to check

        Returns:
            List of matched keywords
        """
        if subject_code not in self.subject_keywords:
            return []

        text_lower = text.lower()
        keywords = self.subject_keywords[subject_code]

        matches = [
            keyword
            for keyword in keywords
            if keyword.lower() in text_lower
        ]

        return matches

    # ==================== Confidence Analysis ====================

    def is_confident_classification(
        self,
        text: str,
        min_confidence: float = 0.50
    ) -> bool:
        """
        Check if classification is confident enough.

        Args:
            text: Document text
            min_confidence: Minimum confidence threshold

        Returns:
            True if confident
        """
        result = self.extract(text)
        confidence = result.get('data', {}).get('primary_confidence', 0.0)

        return confidence >= min_confidence

    def get_classification_strength(self, text: str) -> str:
        """
        Get classification strength label.

        Args:
            text: Document text

        Returns:
            'strong', 'moderate', or 'weak'
        """
        result = self.extract(text)
        confidence = result.get('data', {}).get('primary_confidence', 0.0)

        if confidence >= 0.60:
            return 'strong'
        elif confidence >= 0.40:
            return 'moderate'
        else:
            return 'weak'


# ==================== Convenience Functions ====================

def classify_subject(text: str, method: str = 'ensemble') -> str:
    """
    Quick subject classification (convenience function).

    Args:
        text: Document text
        method: Classification method

    Returns:
        Primary subject code
    """
    classifier = SubjectClassifier()
    result = classifier.extract(text, method=method)
    return result.get('data', {}).get('primary_subject', 'GEN')


def get_subject_with_confidence(
    text: str,
    method: str = 'ensemble'
) -> Tuple[str, float]:
    """
    Get subject code and confidence.

    Args:
        text: Document text
        method: Classification method

    Returns:
        (subject_code, confidence)
    """
    classifier = SubjectClassifier()
    result = classifier.extract(text, method=method)
    data = result.get('data', {})

    return (
        data.get('primary_subject', 'GEN'),
        data.get('primary_confidence', 0.0)
    )


def get_all_subjects(text: str, min_score: float = 0.15) -> List[str]:
    """
    Get all subjects above threshold.

    Args:
        text: Document text
        min_score: Minimum score threshold

    Returns:
        List of subject codes
    """
    classifier = SubjectClassifier()
    result = classifier.extract(text)
    data = result.get('data', {})

    all_scores = data.get('all_scores', {})

    return [
        code for code, score in all_scores.items()
        if score >= min_score
    ]


def classify_by_keywords(text: str) -> str:
    """
    Classify using rule-based method only.

    Args:
        text: Document text

    Returns:
        Primary subject code
    """
    classifier = SubjectClassifier(use_ml=False)
    result = classifier.extract(text, method='rule')
    return result.get('data', {}).get('primary_subject', 'GEN')

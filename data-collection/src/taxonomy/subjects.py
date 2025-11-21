"""
Subject Classification System
Automatically classifies legal documents into subject categories
"""

import json
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class SubjectClassifier:
    """
    Classifies legal documents into hierarchical subject taxonomy.

    Uses keyword matching and pattern recognition to infer subjects from:
    - Document title
    - Content
    - Document type
    - Citations
    """

    def __init__(self, taxonomy_path: str = None):
        """
        Initialize classifier with taxonomy.

        Args:
            taxonomy_path: Path to taxonomy.json file
        """
        if taxonomy_path is None:
            taxonomy_path = 'Legal_Database/_SYSTEM/taxonomy.json'

        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.subjects = self.taxonomy.get('subjects', {})

    def _load_taxonomy(self, filepath: str) -> dict:
        """Load taxonomy from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return minimal default taxonomy
            return {
                'subjects': {
                    'GENERAL': {
                        'code': 'GEN',
                        'name': 'General',
                        'subcategories': {
                            'MIS': {'name': 'Miscellaneous', 'keywords': []}
                        }
                    }
                }
            }

    def classify(
        self,
        title: str,
        content: str = None,
        doc_type: str = None,
        country_code: str = None
    ) -> Tuple[str, str, str]:
        """
        Classify document into subject taxonomy.

        Args:
            title: Document title
            content: Document content (optional)
            doc_type: Document type (optional)
            country_code: Country code for country-specific mappings

        Returns:
            Tuple of (primary_subject, subcategory, subject_code)
            e.g., ('CRIMINAL', 'PEN', 'CRM')
        """
        # Combine text for analysis
        text_to_analyze = title.lower()
        if content:
            # Use first 1000 chars of content
            text_to_analyze += ' ' + content[:1000].lower()

        # Try country-specific mappings first
        if country_code:
            result = self._try_country_mapping(title, country_code)
            if result:
                return result

        # Try title-based classification
        scores = {}
        for subject_key, subject_data in self.subjects.items():
            score = self._calculate_subject_score(
                text_to_analyze,
                subject_data,
                title
            )
            if score > 0:
                scores[subject_key] = score

        if scores:
            # Get subject with highest score
            best_subject = max(scores.items(), key=lambda x: x[1])[0]
            subject_data = self.subjects[best_subject]

            # Find best subcategory
            subcategory = self._find_best_subcategory(
                text_to_analyze,
                subject_data.get('subcategories', {})
            )

            return (
                best_subject,
                subcategory,
                subject_data.get('code', 'GEN')
            )

        # Default to GENERAL
        return ('GENERAL', 'MIS', 'GEN')

    def _try_country_mapping(
        self,
        title: str,
        country_code: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Try country-specific act mappings.

        Args:
            title: Document title
            country_code: Country code

        Returns:
            Tuple or None
        """
        mappings = self.taxonomy.get('country_specific_mappings', {})
        country_data = mappings.get(country_code, {})
        common_acts = country_data.get('common_acts', {})

        title_lower = title.lower()

        for act_name, subject_path in common_acts.items():
            if act_name.lower() in title_lower:
                # Parse subject path (e.g., "CRIMINAL.PEN")
                parts = subject_path.split('.')
                if len(parts) >= 2:
                    primary = parts[0]
                    subcategory = parts[1]
                    subject_data = self.subjects.get(primary, {})
                    code = subject_data.get('code', 'GEN')
                    return (primary, subcategory, code)

        return None

    def _calculate_subject_score(
        self,
        text: str,
        subject_data: dict,
        title: str
    ) -> float:
        """
        Calculate relevance score for a subject.

        Args:
            text: Text to analyze
            subject_data: Subject configuration
            title: Document title (weighted higher)

        Returns:
            Score (higher = more relevant)
        """
        score = 0.0

        # Check main subject name
        subject_name = subject_data.get('name', '').lower()
        if subject_name in text:
            score += 5.0
            if subject_name in title.lower():
                score += 10.0  # Title match worth more

        # Check subcategory keywords
        subcategories = subject_data.get('subcategories', {})
        for subcat_key, subcat_data in subcategories.items():
            keywords = subcat_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1.0
                    if keyword.lower() in title.lower():
                        score += 2.0  # Title match worth more

        return score

    def _find_best_subcategory(
        self,
        text: str,
        subcategories: dict
    ) -> str:
        """
        Find best matching subcategory.

        Args:
            text: Text to analyze
            subcategories: Subcategory definitions

        Returns:
            Subcategory code (e.g., 'PEN', 'CPC')
        """
        scores = {}

        for subcat_key, subcat_data in subcategories.items():
            score = 0.0

            # Check subcategory name
            name = subcat_data.get('name', '').lower()
            if name in text:
                score += 5.0

            # Check keywords
            keywords = subcat_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1.0

            if score > 0:
                scores[subcat_key] = score

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        # Default to first subcategory or MIS
        if subcategories:
            return list(subcategories.keys())[0]
        return 'MIS'

    def get_subject_info(self, subject_code: str) -> Dict[str, Any]:
        """
        Get information about a subject.

        Args:
            subject_code: Subject code (e.g., 'CRM', 'CIV')

        Returns:
            Subject information dictionary
        """
        for subject_key, subject_data in self.subjects.items():
            if subject_data.get('code') == subject_code:
                return {
                    'key': subject_key,
                    'code': subject_code,
                    'name': subject_data.get('name'),
                    'description': subject_data.get('description'),
                    'subcategories': subject_data.get('subcategories', {})
                }

        return {}

    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """
        Get all subjects in taxonomy.

        Returns:
            List of subject dictionaries
        """
        subjects_list = []

        for subject_key, subject_data in self.subjects.items():
            subjects_list.append({
                'key': subject_key,
                'code': subject_data.get('code'),
                'name': subject_data.get('name'),
                'description': subject_data.get('description'),
                'subcategory_count': len(subject_data.get('subcategories', {}))
            })

        return subjects_list

    def classify_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, str]]:
        """
        Classify multiple documents.

        Args:
            documents: List of document dictionaries

        Returns:
            List of (primary, subcategory, code) tuples
        """
        results = []

        for doc in documents:
            title = doc.get('title', '')
            content = doc.get('content', '')
            doc_type = doc.get('doc_type', '')
            country = doc.get('country_code', '')

            result = self.classify(title, content, doc_type, country)
            results.append(result)

        return results

    def suggest_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """
        Suggest relevant tags based on content.

        Args:
            text: Document text
            max_tags: Maximum number of tags to return

        Returns:
            List of suggested tags
        """
        tags = set()
        text_lower = text.lower()

        # Collect keywords from all subjects
        for subject_key, subject_data in self.subjects.items():
            subcategories = subject_data.get('subcategories', {})
            for subcat_data in subcategories.values():
                keywords = subcat_data.get('keywords', [])
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        tags.add(keyword.lower())

        # Return top N most relevant
        return sorted(list(tags))[:max_tags]


if __name__ == "__main__":
    # Test subject classifier
    print("Testing Subject Classifier...")

    classifier = SubjectClassifier()

    # Test cases
    test_docs = [
        {
            'title': 'The Penal Code, 1860',
            'content': 'Act relating to offenses and punishments',
            'country': 'BD'
        },
        {
            'title': 'Code of Criminal Procedure',
            'content': 'Procedure for arrest, investigation and trial',
            'country': 'BD'
        },
        {
            'title': 'Contract Act, 1872',
            'content': 'Law relating to contracts and agreements',
            'country': 'IN'
        },
        {
            'title': 'Income Tax Act, 1961',
            'content': 'Tax on income, assessment, deduction',
            'country': 'IN'
        },
        {
            'title': 'Environmental Protection Act',
            'content': 'Protection of environment, pollution control',
            'country': 'IN'
        }
    ]

    print("\nClassifying documents:")
    for doc in test_docs:
        primary, subcat, code = classifier.classify(
            doc['title'],
            doc['content'],
            country_code=doc['country']
        )
        print(f"\n  Title: {doc['title']}")
        print(f"  Subject: {primary} ({code})")
        print(f"  Subcategory: {subcat}")

        # Suggest tags
        tags = classifier.suggest_tags(doc['title'] + ' ' + doc['content'])
        if tags:
            print(f"  Tags: {', '.join(tags)}")

    # Show all subjects
    print("\n\nAll Subjects:")
    for subject in classifier.get_all_subjects():
        print(f"  {subject['code']}: {subject['name']} ({subject['subcategory_count']} subcategories)")

"""
Phase 2 Integration for Legal RAG Extraction System (Phase 3)
Integrates with Phase 2 PostgreSQL Database System
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..logging_config import get_logger

logger = get_logger(__name__)


class Phase2Integrator:
    """
    Integrates Phase 3 extractors with Phase 2 PostgreSQL database.

    Phase 2 Tables:
    - legal_cases: Main case information
    - citations: Citation references
    - parties: Party information
    - judges: Judge information
    - sections: Statutory sections cited
    - keywords: Extracted keywords
    - metadata: Additional metadata

    Integration Functions:
    1. Save complete extraction result to database
    2. Update existing case with new metadata
    3. Batch insert extraction results
    4. Query and retrieve cases
    """

    def __init__(self, db_connection=None):
        """
        Initialize Phase 2 integrator.

        Args:
            db_connection: SQLAlchemy database connection (optional)
                          If None, will use Phase 2 database module when available
        """
        self.db = db_connection

        # In production, import Phase 2 database models
        # from src.database.models import LegalCase, Citation, Party, etc.

    def save_extraction_result(
        self,
        extraction_result: Dict[str, Any],
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        Save complete extraction result to database.

        Args:
            extraction_result: Complete extraction result from pipeline
            commit: Whether to commit transaction (default True)

        Returns:
            Database save result with IDs
        """
        try:
            # Extract core fields
            document_id = extraction_result.get('document_id')

            # 1. Save main case record
            case_id = self._save_legal_case(extraction_result)

            # 2. Save citations
            citation_ids = self._save_citations(case_id, extraction_result)

            # 3. Save parties
            party_ids = self._save_parties(case_id, extraction_result)

            # 4. Save judges
            judge_ids = self._save_judges(case_id, extraction_result)

            # 5. Save sections
            section_ids = self._save_sections(case_id, extraction_result)

            # 6. Save keywords
            keyword_ids = self._save_keywords(case_id, extraction_result)

            # 7. Save quality analysis
            quality_id = self._save_quality_analysis(case_id, extraction_result)

            if commit and self.db:
                self.db.commit()

            logger.info(f"Saved extraction result to database: {document_id}")

            return {
                'success': True,
                'case_id': case_id,
                'citation_ids': citation_ids,
                'party_ids': party_ids,
                'judge_ids': judge_ids,
                'section_ids': section_ids,
                'keyword_ids': keyword_ids,
                'quality_id': quality_id
            }

        except Exception as e:
            logger.error(f"Failed to save extraction result: {e}", exc_info=True)

            if self.db:
                self.db.rollback()

            return {
                'success': False,
                'error': str(e)
            }

    def _save_legal_case(self, result: Dict[str, Any]) -> int:
        """
        Save main legal case record.

        Maps to legal_cases table:
        - document_id
        - title
        - full_text
        - year
        - judgment_date
        - court
        - subject_code
        - quality_score
        - validation_status
        """
        case_data = {
            'document_id': result.get('document_id'),
            'title': result.get('title'),
            'full_text': result.get('full_text'),
            'text_hash': result.get('text_hash'),
            'year': result.get('year'),

            # Dates
            'judgment_date': result.get('dates', {}).get('judgment_date'),
            'filing_date': result.get('dates', {}).get('filing_date'),
            'hearing_date': result.get('dates', {}).get('hearing_date'),

            # Classification
            'subject_code': result.get('subject_classification', {}).get('primary_subject'),
            'subject_confidence': result.get('subject_classification', {}).get('primary_confidence'),

            # Quality
            'quality_score': result.get('quality_analysis', {}).get('overall_score'),
            'validation_status': result.get('quality_analysis', {}).get('validation_status'),
            'needs_manual_review': result.get('quality_analysis', {}).get('needs_manual_review'),

            # Metadata
            'source_type': result.get('source_type'),
            'url': result.get('url'),
            'bench_size': result.get('bench_size'),

            # Timestamps
            'extraction_timestamp': result.get('extraction_metadata', {}).get('extraction_timestamp'),
            'created_at': datetime.utcnow()
        }

        # In production, use SQLAlchemy model:
        # case = LegalCase(**case_data)
        # self.db.add(case)
        # self.db.flush()
        # return case.id

        # For now, return mock ID
        logger.info(f"Would save legal case: {case_data['document_id']}")
        return 1  # Mock case_id

    def _save_citations(self, case_id: int, result: Dict[str, Any]) -> List[int]:
        """
        Save citations to database.

        Maps to citations table:
        - case_id (FK)
        - citation_text
        - citation_encoded
        - volume, year, reporter, court, page
        - is_primary
        - confidence
        """
        citations = result.get('citations', [])
        citation_ids = []

        for citation in citations:
            citation_data = {
                'case_id': case_id,
                'citation_text': citation.get('citation_text'),
                'citation_encoded': citation.get('citation_encoded'),
                'volume': citation.get('volume'),
                'year': citation.get('year'),
                'reporter': citation.get('reporter'),
                'court': citation.get('court'),
                'page': citation.get('page'),
                'is_primary': citation.get('is_primary', False),
                'confidence': citation.get('confidence', 0.0)
            }

            # In production: citation_obj = Citation(**citation_data)
            # citation_ids.append(citation_obj.id)

            logger.debug(f"Would save citation: {citation_data['citation_encoded']}")
            citation_ids.append(len(citation_ids) + 1)  # Mock ID

        return citation_ids

    def _save_parties(self, case_id: int, result: Dict[str, Any]) -> List[int]:
        """
        Save parties to database.

        Maps to parties table:
        - case_id (FK)
        - party_name
        - party_type (petitioner/respondent)
        - party_abbrev
        """
        parties = result.get('parties', {})
        party_ids = []

        # Petitioners
        for party_name in parties.get('petitioner', []):
            party_data = {
                'case_id': case_id,
                'party_name': party_name,
                'party_type': 'petitioner'
            }

            logger.debug(f"Would save party: {party_name}")
            party_ids.append(len(party_ids) + 1)  # Mock ID

        # Respondents
        for party_name in parties.get('respondent', []):
            party_data = {
                'case_id': case_id,
                'party_name': party_name,
                'party_type': 'respondent'
            }

            logger.debug(f"Would save party: {party_name}")
            party_ids.append(len(party_ids) + 1)  # Mock ID

        return party_ids

    def _save_judges(self, case_id: int, result: Dict[str, Any]) -> List[int]:
        """
        Save judges to database.

        Maps to judges table:
        - case_id (FK)
        - judge_name
        - is_presiding
        - is_author
        - opinion_type
        """
        judges = result.get('judges', [])
        judge_ids = []

        for judge in judges:
            judge_data = {
                'case_id': case_id,
                'judge_name': judge.get('name'),
                'is_presiding': judge.get('is_presiding', False),
                'is_author': judge.get('is_author', False),
                'opinion_type': judge.get('opinion_type')
            }

            logger.debug(f"Would save judge: {judge_data['judge_name']}")
            judge_ids.append(len(judge_ids) + 1)  # Mock ID

        return judge_ids

    def _save_sections(self, case_id: int, result: Dict[str, Any]) -> List[int]:
        """
        Save statutory sections to database.

        Maps to sections table:
        - case_id (FK)
        - section_number
        - act_name
        - context
        - frequency
        """
        sections = result.get('sections_cited', [])
        section_ids = []

        for section in sections:
            section_data = {
                'case_id': case_id,
                'section_number': section.get('section_number'),
                'act_name': section.get('act_name'),
                'context': section.get('context'),
                'frequency': section.get('frequency', 1)
            }

            logger.debug(f"Would save section: {section_data['section_number']}")
            section_ids.append(len(section_ids) + 1)  # Mock ID

        return section_ids

    def _save_keywords(self, case_id: int, result: Dict[str, Any]) -> List[int]:
        """
        Save keywords to database.

        Maps to keywords table:
        - case_id (FK)
        - keyword
        - keyword_type
        - score
        """
        keywords = result.get('keywords', [])
        keyword_ids = []

        for keyword in keywords:
            if isinstance(keyword, dict):
                keyword_data = {
                    'case_id': case_id,
                    'keyword': keyword.get('keyword'),
                    'keyword_type': keyword.get('keyword_type'),
                    'score': keyword.get('final_score', 0.0),
                    'is_legal_term': keyword.get('is_legal_term', False)
                }
            else:
                # String keyword
                keyword_data = {
                    'case_id': case_id,
                    'keyword': str(keyword),
                    'keyword_type': 'concept',
                    'score': 0.0,
                    'is_legal_term': False
                }

            logger.debug(f"Would save keyword: {keyword_data['keyword']}")
            keyword_ids.append(len(keyword_ids) + 1)  # Mock ID

        return keyword_ids

    def _save_quality_analysis(self, case_id: int, result: Dict[str, Any]) -> Optional[int]:
        """
        Save quality analysis to database.

        Maps to quality_analysis table:
        - case_id (FK)
        - overall_score
        - dimension_scores (JSON)
        - quality_grade
        - validation_status
        - needs_manual_review
        - recommendations (JSON)
        """
        quality_analysis = result.get('quality_analysis', {})

        if not quality_analysis:
            return None

        quality_data = {
            'case_id': case_id,
            'overall_score': quality_analysis.get('overall_score'),
            'dimension_scores': json.dumps(quality_analysis.get('dimension_scores', {})),
            'quality_grade': quality_analysis.get('quality_grade'),
            'validation_status': quality_analysis.get('validation_status'),
            'needs_manual_review': quality_analysis.get('needs_manual_review'),
            'recommendations': json.dumps(quality_analysis.get('recommendations', []))
        }

        logger.debug(f"Would save quality analysis for case {case_id}")
        return 1  # Mock ID

    # ==================== Batch Operations ====================

    def save_batch(
        self,
        extraction_results: List[Dict[str, Any]],
        commit_per_batch: int = 100
    ) -> Dict[str, Any]:
        """
        Save multiple extraction results to database.

        Args:
            extraction_results: List of extraction results
            commit_per_batch: Commit every N records

        Returns:
            Batch save result
        """
        results = {
            'total': len(extraction_results),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for i, result in enumerate(extraction_results, 1):
            try:
                # Save without committing
                save_result = self.save_extraction_result(result, commit=False)

                if save_result.get('success'):
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'document_id': result.get('document_id'),
                        'error': save_result.get('error')
                    })

                # Commit periodically
                if i % commit_per_batch == 0 and self.db:
                    self.db.commit()
                    logger.info(f"Committed batch at {i}/{len(extraction_results)}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'document_id': result.get('document_id'),
                    'error': str(e)
                })

                logger.error(f"Failed to save result {i}: {e}")

        # Final commit
        if self.db:
            self.db.commit()

        logger.info(
            f"Batch save complete: {results['successful']}/{results['total']} successful"
        )

        return results

    # ==================== Query Operations ====================

    def get_case_by_id(self, case_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve case by ID.

        Args:
            case_id: Database case ID

        Returns:
            Complete case data or None
        """
        # In production, query database and join related tables
        logger.info(f"Would retrieve case {case_id}")
        return None

    def search_cases(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search cases with filters.

        Args:
            query: Search query
            filters: Optional filters (year, subject, court, etc.)
            limit: Maximum results

        Returns:
            List of matching cases
        """
        # In production, build and execute database query
        logger.info(f"Would search cases: {query}")
        return []


# ==================== Convenience Functions ====================

def save_to_database(
    extraction_result: Dict[str, Any],
    db_connection=None
) -> Dict[str, Any]:
    """
    Save extraction result to database (convenience function).

    Args:
        extraction_result: Extraction result
        db_connection: Database connection (optional)

    Returns:
        Save result
    """
    integrator = Phase2Integrator(db_connection)
    return integrator.save_extraction_result(extraction_result)


def save_batch_to_database(
    extraction_results: List[Dict[str, Any]],
    db_connection=None
) -> Dict[str, Any]:
    """
    Save batch of results to database (convenience function).

    Args:
        extraction_results: List of extraction results
        db_connection: Database connection (optional)

    Returns:
        Batch save result
    """
    integrator = Phase2Integrator(db_connection)
    return integrator.save_batch(extraction_results)


# ==================== Example Usage ====================

def example_integration():
    """
    Example of Phase 2 integration.

    This shows how to save Phase 3 extraction results to Phase 2 database.
    """
    from ..pipeline.extraction_pipeline import extract_document

    # In production, get database connection from Phase 2:
    # from src.database.connection import get_db_session
    # db = get_db_session()

    db = None  # Mock for now

    # Extract document
    result = extract_document('/path/to/case.pdf')

    # Save to database
    save_result = save_to_database(result, db_connection=db)

    if save_result.get('success'):
        print(f"✓ Saved to database: case_id={save_result['case_id']}")
    else:
        print(f"✗ Save failed: {save_result.get('error')}")

    return save_result

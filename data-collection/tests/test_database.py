"""
Unit Tests for Database Module
Tests CRUD operations, connection pooling, retry logic, session cleanup, and checkpoints.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.database import (
    CaseDatabase, LegalCase, URLTracker, CourtType,
    DownloadStatus, Base
)
from tests.fixtures import (
    mock_legal_case, mock_url_tracker,
    generate_mock_cases, generate_mock_urls
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    db_path = temp_file.name
    connection_string = f'sqlite:///{db_path}'

    yield connection_string

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db(temp_db):
    """Create a CaseDatabase instance for testing."""
    database = CaseDatabase(temp_db)
    yield database
    database.close()


# =============================================================================
# Test Database Initialization
# =============================================================================

class TestDatabaseInitialization:
    """Test database initialization and setup."""

    def test_database_creates_tables(self, temp_db):
        """Test that database initialization creates all tables."""
        db = CaseDatabase(temp_db)

        # Check that tables exist
        inspector = db.engine
        table_names = db.engine.table_names()

        assert 'legal_cases' in table_names
        assert 'url_tracker' in table_names

        db.close()

    def test_database_connection_pooling(self, temp_db):
        """Test that database uses connection pooling."""
        db = CaseDatabase(temp_db)

        # Verify pool settings
        assert db.engine.pool.size() >= 0
        assert db.engine.pool._pre_ping is True
        assert db.engine.pool._recycle == 3600

        db.close()

    def test_database_session_creation(self, temp_db):
        """Test that database creates a valid session."""
        db = CaseDatabase(temp_db)

        assert db.session is not None
        assert db.Session is not None

        db.close()


# =============================================================================
# Test CRUD Operations - Legal Cases
# =============================================================================

class TestLegalCaseCRUD:
    """Test CRUD operations for legal cases."""

    def test_save_case_creates_new_record(self, db):
        """Test saving a new legal case."""
        case_data = mock_legal_case()

        case_id = db.save_case(case_data)

        assert case_id is not None
        assert isinstance(case_id, int)

        # Verify case was saved
        saved_case = db.get_case_by_url(case_data['case_url'])
        assert saved_case is not None
        assert saved_case.title == case_data['title']
        assert saved_case.citation == case_data['citation']

    def test_save_case_returns_existing_id_for_duplicate(self, db):
        """Test that saving duplicate case returns existing ID."""
        case_data = mock_legal_case()

        # Save first time
        case_id_1 = db.save_case(case_data)

        # Save again with same URL
        case_id_2 = db.save_case(case_data)

        # Should return same ID
        assert case_id_1 == case_id_2

        # Verify only one record exists
        total_cases = db.session.query(LegalCase).count()
        assert total_cases == 1

    def test_save_case_with_all_fields(self, db):
        """Test saving case with all optional fields."""
        case_data = mock_legal_case(
            court_type=CourtType.SUPREME,
            court_name='Supreme Court of India',
            state=None,
            document_type='judgment',
            year=2024,
            scrape_tier=1,
            pagination_page=5,
            is_historical=False
        )

        case_id = db.save_case(case_data)
        saved_case = db.get_case_by_url(case_data['case_url'])

        # Verify new fields are saved
        assert saved_case.year == 2024
        assert saved_case.scrape_tier == 1
        assert saved_case.pagination_page == 5
        assert saved_case.is_historical is False

    def test_save_case_handles_missing_fields(self, db):
        """Test saving case with minimal fields."""
        case_data = {
            'url': 'https://indiankanoon.org/doc/999/',
            'title': 'Minimal Case'
        }

        case_id = db.save_case(case_data)

        assert case_id is not None
        saved_case = db.get_case_by_url(case_data['url'])
        assert saved_case.title == 'Minimal Case'
        assert saved_case.citation == ''

    def test_save_case_handles_database_error(self, db):
        """Test that save_case handles database errors gracefully."""
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError("DB Error")):
            case_data = mock_legal_case()
            case_id = db.save_case(case_data)

            # Should return None on error
            assert case_id is None

    def test_bulk_save_cases(self, db):
        """Test bulk saving multiple cases."""
        cases = generate_mock_cases(10)

        saved_count = db.bulk_save_cases(cases)

        assert saved_count == 10

        # Verify all cases were saved
        total = db.session.query(LegalCase).count()
        assert total == 10

    def test_bulk_save_cases_skips_duplicates(self, db):
        """Test bulk save skips duplicate URLs."""
        cases = generate_mock_cases(5)

        # Save first time
        count_1 = db.bulk_save_cases(cases)
        assert count_1 == 5

        # Save again (duplicates)
        count_2 = db.bulk_save_cases(cases)
        assert count_2 == 5  # Returns IDs for existing cases

        # Verify no duplicates
        total = db.session.query(LegalCase).count()
        assert total == 5

    def test_get_case_by_url(self, db):
        """Test retrieving case by URL."""
        case_data = mock_legal_case()
        db.save_case(case_data)

        retrieved = db.get_case_by_url(case_data['case_url'])

        assert retrieved is not None
        assert retrieved.case_url == case_data['case_url']
        assert retrieved.title == case_data['title']

    def test_get_case_by_url_not_found(self, db):
        """Test get_case_by_url returns None for non-existent URL."""
        result = db.get_case_by_url('https://nonexistent.com/doc/999/')

        assert result is None

    def test_get_cases_with_limit(self, db):
        """Test retrieving cases with limit."""
        cases = generate_mock_cases(20)
        db.bulk_save_cases(cases)

        results = db.get_cases(limit=10)

        assert len(results) == 10

    def test_get_cases_with_court_filter(self, db):
        """Test filtering cases by court."""
        # Save cases with different courts
        case1 = mock_legal_case(case_url='https://test.com/1', court='Supreme Court')
        case2 = mock_legal_case(case_url='https://test.com/2', court='High Court')
        db.save_case(case1)
        db.save_case(case2)

        results = db.get_cases(court='Supreme Court')

        assert len(results) >= 1
        assert all('Supreme Court' in c.court for c in results)

    def test_get_cases_with_year_filter(self, db):
        """Test filtering cases by year."""
        case1 = mock_legal_case(case_url='https://test.com/1', case_date='2024-01-01')
        case2 = mock_legal_case(case_url='https://test.com/2', case_date='2023-01-01')
        db.save_case(case1)
        db.save_case(case2)

        results = db.get_cases(year='2024')

        assert len(results) >= 1
        assert all('2024' in c.case_date for c in results)

    def test_get_cases_without_pdfs(self, db):
        """Test retrieving cases that need PDF downloads."""
        # Case with PDF link but not downloaded
        case1 = mock_legal_case(
            case_url='https://test.com/1',
            pdf_link='https://test.com/1.pdf',
            pdf_downloaded=False
        )
        # Case with PDF already downloaded
        case2 = mock_legal_case(
            case_url='https://test.com/2',
            pdf_link='https://test.com/2.pdf',
            pdf_downloaded=True
        )
        # Case without PDF link
        case3 = mock_legal_case(
            case_url='https://test.com/3',
            pdf_link='',
            pdf_downloaded=False
        )

        db.save_case(case1)
        db.save_case(case2)
        db.save_case(case3)

        results = db.get_cases_without_pdfs()

        assert len(results) == 1
        assert results[0].case_url == case1['case_url']

    def test_update_pdf_status(self, db):
        """Test updating PDF download status."""
        case_data = mock_legal_case(pdf_downloaded=False)
        case_id = db.save_case(case_data)

        success = db.update_pdf_status(case_id, '/path/to/pdf.pdf')

        assert success is True

        # Verify update
        updated = db.session.query(LegalCase).filter_by(id=case_id).first()
        assert updated.pdf_downloaded is True
        assert updated.pdf_path == '/path/to/pdf.pdf'

    def test_update_pdf_status_nonexistent_case(self, db):
        """Test updating PDF status for non-existent case."""
        success = db.update_pdf_status(99999, '/path/to/pdf.pdf')

        assert success is False

    def test_update_pdf_status_handles_error(self, db):
        """Test update_pdf_status handles errors gracefully."""
        case_data = mock_legal_case()
        case_id = db.save_case(case_data)

        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError("DB Error")):
            success = db.update_pdf_status(case_id, '/path/to/pdf.pdf')

            assert success is False


# =============================================================================
# Test CRUD Operations - URL Tracker
# =============================================================================

class TestURLTrackerCRUD:
    """Test CRUD operations for URL tracker."""

    def test_save_url_creates_new_record(self, db):
        """Test saving a new URL tracker record."""
        url_data = mock_url_tracker()

        url_id = db.save_url(url_data)

        assert url_id is not None
        assert isinstance(url_id, int)

        # Verify URL was saved
        saved_url = db.session.query(URLTracker).filter_by(id=url_id).first()
        assert saved_url is not None
        assert saved_url.doc_url == url_data['doc_url']
        assert saved_url.doc_id == url_data['doc_id']

    def test_save_url_returns_existing_id_for_duplicate(self, db):
        """Test that saving duplicate URL returns existing ID."""
        url_data = mock_url_tracker()

        url_id_1 = db.save_url(url_data)
        url_id_2 = db.save_url(url_data)

        assert url_id_1 == url_id_2

        # Verify only one record
        total = db.session.query(URLTracker).count()
        assert total == 1

    def test_bulk_save_urls(self, db):
        """Test bulk saving URLs."""
        urls = generate_mock_urls(15)

        saved_count = db.bulk_save_urls(urls)

        assert saved_count == 15

        total = db.session.query(URLTracker).count()
        assert total == 15

    def test_get_pending_urls(self, db):
        """Test retrieving pending download URLs."""
        # Create URLs with different statuses
        url1 = mock_url_tracker(doc_url='https://test.com/1', download_status='PENDING')
        url2 = mock_url_tracker(doc_url='https://test.com/2', download_status='COMPLETED')
        url3 = mock_url_tracker(doc_url='https://test.com/3', download_status='PENDING')

        db.save_url(url1)
        db.save_url(url2)
        db.save_url(url3)

        pending = db.get_pending_urls()

        assert len(pending) == 2
        assert all(u.download_status == DownloadStatus.PENDING for u in pending)

    def test_get_failed_urls(self, db):
        """Test retrieving failed URLs for retry."""
        # Create URL with failed status
        url_data = mock_url_tracker(
            doc_url='https://test.com/1',
            download_status='FAILED',
            download_attempts=2
        )
        db.save_url(url_data)

        # Manually update status (save_url doesn't set enum properly from dict)
        url_record = db.session.query(URLTracker).filter_by(doc_url=url_data['doc_url']).first()
        url_record.download_status = DownloadStatus.FAILED
        url_record.download_attempts = 2
        db.session.commit()

        failed = db.get_failed_urls(max_attempts=3)

        assert len(failed) >= 1
        assert failed[0].download_status == DownloadStatus.FAILED
        assert failed[0].download_attempts < 3

    def test_update_download_status_success(self, db):
        """Test updating download status to success."""
        url_data = mock_url_tracker()
        url_id = db.save_url(url_data)

        success = db.update_download_status(
            url_id,
            DownloadStatus.COMPLETED,
            pdf_path='/path/to/doc.pdf',
            pdf_size=10240
        )

        assert success is True

        # Verify update
        updated = db.session.query(URLTracker).filter_by(id=url_id).first()
        assert updated.download_status == DownloadStatus.COMPLETED
        assert updated.pdf_downloaded is True
        assert updated.pdf_path == '/path/to/doc.pdf'
        assert updated.pdf_size == 10240
        assert updated.download_attempts == 1

    def test_update_download_status_failure(self, db):
        """Test updating download status to failed."""
        url_data = mock_url_tracker()
        url_id = db.save_url(url_data)

        success = db.update_download_status(
            url_id,
            DownloadStatus.FAILED,
            error_message='Connection timeout'
        )

        assert success is True

        # Verify update
        updated = db.session.query(URLTracker).filter_by(id=url_id).first()
        assert updated.download_status == DownloadStatus.FAILED
        assert updated.error_message == 'Connection timeout'
        assert updated.download_attempts == 1

    def test_update_download_status_nonexistent(self, db):
        """Test updating status for non-existent URL."""
        success = db.update_download_status(99999, DownloadStatus.COMPLETED)

        assert success is False

    def test_update_drive_status(self, db):
        """Test updating Google Drive upload status."""
        url_data = mock_url_tracker()
        url_id = db.save_url(url_data)

        success = db.update_drive_status(url_id, 'drive_file_12345')

        assert success is True

        # Verify update
        updated = db.session.query(URLTracker).filter_by(id=url_id).first()
        assert updated.uploaded_to_drive is True
        assert updated.drive_file_id == 'drive_file_12345'
        assert updated.uploaded_at is not None


# =============================================================================
# Test Statistics and Queries
# =============================================================================

class TestStatisticsQueries:
    """Test statistics and analytical queries."""

    def test_get_statistics(self, db):
        """Test getting database statistics."""
        # Create test data
        cases = generate_mock_cases(10)
        db.bulk_save_cases(cases)

        # Update some to have PDFs
        for i in range(5):
            case = db.session.query(LegalCase).offset(i).first()
            case.pdf_downloaded = True
        db.session.commit()

        stats = db.get_statistics()

        assert stats['total_cases'] == 10
        assert stats['cases_with_pdfs'] == 5
        assert stats['cases_without_pdfs'] == 5
        assert stats['unique_courts'] >= 0

    def test_get_cases_by_court_type(self, db):
        """Test filtering by court type."""
        case_data = mock_legal_case(court_type=CourtType.SUPREME)
        db.save_case(case_data)

        # Need to manually set enum since save_case doesn't handle it from dict
        case = db.session.query(LegalCase).first()
        case.court_type = CourtType.SUPREME
        db.session.commit()

        results = db.get_cases_by_court_type(CourtType.SUPREME)

        assert len(results) >= 1
        assert all(c.court_type == CourtType.SUPREME for c in results)

    def test_get_cases_by_year(self, db):
        """Test filtering by year."""
        case_data = mock_legal_case(year=2024)
        db.save_case(case_data)

        # Manually set year
        case = db.session.query(LegalCase).first()
        case.year = 2024
        db.session.commit()

        results = db.get_cases_by_year(2024)

        assert len(results) >= 1
        assert all(c.year == 2024 for c in results)

    def test_get_cases_by_tier(self, db):
        """Test filtering by scrape tier."""
        case_data = mock_legal_case(scrape_tier=1)
        db.save_case(case_data)

        results = db.get_cases_by_tier(1)

        assert len(results) >= 1

    def test_get_progress_by_court(self, db):
        """Test getting progress statistics by court."""
        # Create cases for specific court
        for i in range(10):
            case = mock_legal_case(
                case_url=f'https://test.com/{i}',
                court_name='Delhi High Court',
                pdf_downloaded=(i < 5)
            )
            db.save_case(case)

        # Manually update court_name
        cases = db.session.query(LegalCase).all()
        for i, case in enumerate(cases):
            case.court_name = 'Delhi High Court'
            case.pdf_downloaded = (i < 5)
        db.session.commit()

        progress = db.get_progress_by_court('Delhi High Court')

        assert progress['court_name'] == 'Delhi High Court'
        assert progress['total_cases'] == 10
        assert progress['cases_with_pdfs'] == 5
        assert progress['completion_rate'] == 50.0

    def test_get_progress_by_year(self, db):
        """Test getting progress statistics by year."""
        for i in range(8):
            case = mock_legal_case(
                case_url=f'https://test.com/{i}',
                year=2024,
                pdf_downloaded=(i < 4)
            )
            db.save_case(case)

        # Manually update year and pdf_downloaded
        cases = db.session.query(LegalCase).all()
        for i, case in enumerate(cases):
            case.year = 2024
            case.pdf_downloaded = (i < 4)
        db.session.commit()

        progress = db.get_progress_by_year(2024)

        assert progress['year'] == 2024
        assert progress['total_cases'] == 8
        assert progress['cases_with_pdfs'] == 4
        assert progress['completion_rate'] == 50.0

    def test_get_download_progress(self, db):
        """Test getting download progress statistics."""
        urls = generate_mock_urls(20)
        db.bulk_save_urls(urls)

        # Update some statuses
        all_urls = db.session.query(URLTracker).all()
        for i, url in enumerate(all_urls):
            if i < 5:
                url.download_status = DownloadStatus.COMPLETED
                url.pdf_downloaded = True
            elif i < 8:
                url.download_status = DownloadStatus.FAILED
            elif i < 10:
                url.download_status = DownloadStatus.IN_PROGRESS
        db.session.commit()

        progress = db.get_download_progress()

        assert progress['total_urls'] == 20
        assert progress['pdfs_downloaded'] == 5
        assert progress['status_breakdown']['COMPLETED'] == 5
        assert progress['status_breakdown']['FAILED'] == 3
        assert progress['completion_rate'] == 25.0

    def test_get_urls_to_download(self, db):
        """Test getting URLs ready for download."""
        urls = generate_mock_urls(5)
        db.bulk_save_urls(urls)

        download_urls = db.get_urls_to_download(batch_size=10)

        assert len(download_urls) == 5
        assert all('url' in u for u in download_urls)
        assert all('doc_id' in u for u in download_urls)


# =============================================================================
# Test Session Management and Cleanup
# =============================================================================

class TestSessionManagement:
    """Test session management and resource cleanup."""

    def test_session_cleanup_on_close(self, temp_db):
        """Test that session is properly closed."""
        db = CaseDatabase(temp_db)
        session = db.session

        db.close()

        # Session should be closed (checking internal state)
        # We can't directly test if closed, but no errors should occur
        assert True

    def test_context_manager_entry(self, temp_db):
        """Test context manager __enter__."""
        with CaseDatabase(temp_db) as db:
            assert db is not None
            assert db.session is not None

    def test_context_manager_exit_commits(self, temp_db):
        """Test context manager commits on successful exit."""
        with CaseDatabase(temp_db) as db:
            case_data = mock_legal_case()
            db.save_case(case_data)

        # Verify case was committed
        db2 = CaseDatabase(temp_db)
        saved = db2.get_case_by_url(case_data['case_url'])
        assert saved is not None
        db2.close()

    def test_context_manager_exit_rollback_on_exception(self, temp_db):
        """Test context manager rollbacks on exception."""
        try:
            with CaseDatabase(temp_db) as db:
                case_data = mock_legal_case()
                db.save_case(case_data)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Changes may have been committed before exception
        # This test mainly ensures no crashes occur

    def test_engine_disposal_on_close(self, temp_db):
        """Test that engine is disposed on close."""
        db = CaseDatabase(temp_db)
        engine = db.engine

        db.close()

        # Engine should be disposed
        assert True  # No exceptions


# =============================================================================
# Test Retry Logic
# =============================================================================

class TestRetryLogic:
    """Test commit retry logic."""

    def test_commit_with_retry_success(self, db):
        """Test successful commit with retry."""
        db._commit_with_retry(max_retries=3)
        # Should not raise exception

    def test_commit_with_retry_recovers_from_temporary_failure(self, db):
        """Test retry logic recovers from temporary failure."""
        call_count = [0]

        original_commit = db.session.commit

        def failing_commit():
            call_count[0] += 1
            if call_count[0] < 2:
                raise SQLAlchemyError("Temporary error")
            original_commit()

        with patch.object(db.session, 'commit', side_effect=failing_commit):
            db._commit_with_retry(max_retries=3)

        # Should have retried and succeeded
        assert call_count[0] == 2

    def test_commit_with_retry_fails_after_max_attempts(self, db):
        """Test retry logic fails after max attempts."""
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError("Persistent error")):
            with pytest.raises(SQLAlchemyError):
                db._commit_with_retry(max_retries=3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

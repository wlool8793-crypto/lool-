"""
Database Module for IndianKanoon Data
Handles storage and retrieval of scraped legal cases.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Enum, Index, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import logging
import enum
import time
from functools import wraps

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# SLOW QUERY LOGGING
# ============================================================================

def log_slow_queries(threshold_seconds=1.0):
    """
    Decorator to log slow database queries.

    Args:
        threshold_seconds: Queries taking longer than this will be logged
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                if elapsed > threshold_seconds:
                    logger.warning(
                        f"SLOW QUERY: {func.__name__} took {elapsed:.2f}s "
                        f"(threshold: {threshold_seconds}s)"
                    )
                else:
                    logger.debug(f"Query {func.__name__} completed in {elapsed:.3f}s")

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Query {func.__name__} failed after {elapsed:.2f}s: {e}")
                raise
        return wrapper
    return decorator


class CourtType(enum.Enum):
    """Enum for different court types"""
    SUPREME = "SUPREME"
    HIGH = "HIGH"
    TRIBUNAL = "TRIBUNAL"
    DISTRICT = "DISTRICT"
    APPELLATE = "APPELLATE"
    SESSIONS = "SESSIONS"
    MAGISTRATE = "MAGISTRATE"


class DownloadStatus(enum.Enum):
    """Enum for download status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class CheckpointStatus(enum.Enum):
    """Enum for checkpoint status"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"


class Checkpoint(Base):
    """Model for tracking download checkpoint and resume functionality."""
    __tablename__ = 'checkpoints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_name = Column(String(100), nullable=False, index=True)  # e.g., 'bulk_download'
    last_case_id = Column(Integer, nullable=False)  # Last successfully processed case ID
    last_offset = Column(Integer, nullable=False, default=0)  # Last offset position
    total_processed = Column(Integer, default=0)  # Total cases processed in this session
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(Enum(CheckpointStatus), default=CheckpointStatus.ACTIVE, index=True)

    # Statistics for this checkpoint session
    pdfs_downloaded = Column(Integer, default=0)
    details_fetched = Column(Integer, default=0)
    failures = Column(Integer, default=0)

    # Metadata for additional information
    metadata_json = Column(Text)  # Additional checkpoint metadata as JSON
    error_message = Column(Text)  # Error message if checkpoint failed

    # Add composite index for querying active checkpoints by process
    __table_args__ = (
        Index('idx_process_status', 'process_name', 'status'),
    )

    def __repr__(self):
        return f"<Checkpoint(id={self.id}, process={self.process_name}, last_case_id={self.last_case_id}, offset={self.last_offset}, status={self.status.value})>"


class URLTracker(Base):
    """Model for tracking URL collection and download progress."""
    __tablename__ = 'url_tracker'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_url = Column(String(500), unique=True, nullable=False, index=True)
    doc_id = Column(String(50), index=True)
    title = Column(String(500))
    citation = Column(String(500))
    court = Column(String(200))

    # Collection metadata
    collected_at = Column(DateTime, default=datetime.now)
    collection_page = Column(Integer)  # Which search page it was collected from

    # Download status
    download_status = Column(Enum(DownloadStatus), default=DownloadStatus.PENDING, index=True)
    download_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    error_message = Column(Text)

    # PDF information
    pdf_downloaded = Column(Boolean, default=False, index=True)
    pdf_path = Column(String(500))
    pdf_size = Column(Integer)  # Size in bytes

    # Drive upload status
    uploaded_to_drive = Column(Boolean, default=False, index=True)
    drive_file_id = Column(String(200))
    uploaded_at = Column(DateTime)

    # Processing metadata
    metadata_json = Column(Text)  # Additional metadata as JSON

    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_status_attempts', 'download_status', 'download_attempts'),
        Index('idx_pdf_drive', 'pdf_downloaded', 'uploaded_to_drive'),
    )

    def __repr__(self):
        return f"<URLTracker(id={self.id}, doc_id={self.doc_id}, status={self.download_status.value}, pdf={self.pdf_downloaded})>"


class LegalCase(Base):
    """Model for storing legal case data."""
    __tablename__ = 'legal_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_url = Column(String(500), unique=True, nullable=False)
    title = Column(String(500))
    citation = Column(String(500))
    court = Column(String(200))  # Original court field (kept for compatibility)
    case_date = Column(String(100))
    bench = Column(String(300))
    author = Column(String(200))
    snippet = Column(Text)
    full_text = Column(Text)
    pdf_link = Column(String(500))
    pdf_downloaded = Column(Boolean, default=False)
    pdf_path = Column(String(500))
    scraped_at = Column(DateTime, default=datetime.now)
    case_metadata = Column(Text)

    # NEW FIELDS for comprehensive coverage
    court_type = Column(Enum(CourtType), index=True)  # SUPREME, HIGH, TRIBUNAL, etc.
    court_name = Column(String(200), index=True)  # "Delhi High Court", "Karnataka High Court"
    state = Column(String(100))  # For High Courts (Delhi, Karnataka, etc.)
    document_type = Column(String(100), index=True)  # judgment, act, statute, notification
    year = Column(Integer, index=True)  # Extracted from case_date for easy querying
    scrape_tier = Column(Integer, default=1)  # 1=Priority, 2=High, 3=Medium, 4=Complete
    pagination_page = Column(Integer)  # Which search result page this came from
    is_historical = Column(Boolean, default=False)  # True if before 2015

    # Add composite indexes for common queries
    __table_args__ = (
        # Composite indexes for multi-column queries
        Index('idx_court_year', 'court_type', 'year'),
        Index('idx_document_year', 'document_type', 'year'),
        Index('idx_tier_downloaded', 'scrape_tier', 'pdf_downloaded'),
        Index('idx_court_name_year', 'court_name', 'year'),  # NEW: For court + year filtering

        # Single column indexes for critical fields
        Index('idx_case_url', 'case_url'),  # NEW: For URL lookups
        Index('idx_pdf_link', 'pdf_link'),  # NEW: For PDF availability checks
    )

    def __repr__(self):
        return f"<LegalCase(id={self.id}, court_type={self.court_type}, year={self.year}, title='{self.title[:50] if self.title else 'N/A'}...')>"


class CaseDatabase:
    """Manage database operations for legal cases."""

    def __init__(self, connection_string: str):
        """
        Initialize database connection with proper session management.

        Args:
            connection_string: SQLAlchemy connection string
        """
        # Create engine with connection pooling for better resource management
        self.engine = create_engine(
            connection_string,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False           # Set to True for SQL debugging
        )
        Base.metadata.create_all(self.engine)

        # Use scoped_session for thread-safe session management
        from sqlalchemy.orm import scoped_session
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        self.session = self.Session()
        logger.info("Database initialized with connection pooling")

    def save_case(self, case_data: Dict[str, Any]) -> Optional[int]:
        """
        Save a legal case to the database.

        Args:
            case_data: Dictionary containing case information

        Returns:
            ID of the saved case, or None if case already exists
        """
        try:
            # Check if case already exists
            existing = self.session.query(LegalCase).filter_by(
                case_url=case_data.get('url', '')
            ).first()

            if existing:
                logger.debug(f"Case already exists: {case_data.get('url')}")
                return existing.id

            # Create new case record
            case = LegalCase(
                case_url=case_data.get('url', ''),
                title=case_data.get('title', ''),
                citation=case_data.get('citation', ''),
                court=case_data.get('court', ''),
                case_date=case_data.get('date', ''),
                bench=case_data.get('bench', ''),
                author=case_data.get('author', ''),
                snippet=case_data.get('snippet', ''),
                full_text=case_data.get('full_text', ''),
                pdf_link=case_data.get('pdf_link', ''),
                pdf_downloaded=case_data.get('pdf_downloaded', False),
                pdf_path=case_data.get('pdf_path', ''),
                case_metadata=json.dumps(case_data.get('metadata', {}))
            )

            self.session.add(case)
            self.session.commit()

            logger.info(f"Saved case: {case.id} - {case.title[:50]}...")
            return case.id

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving case: {e}")
            return None

    def bulk_save_cases(self, cases: List[Dict[str, Any]]) -> int:
        """
        Save multiple cases to database.

        Args:
            cases: List of case dictionaries

        Returns:
            Number of cases successfully saved
        """
        saved_count = 0
        for case_data in cases:
            if self.save_case(case_data):
                saved_count += 1

        logger.info(f"Bulk saved {saved_count} cases")
        return saved_count

    def get_case_by_url(self, url: str) -> Optional[LegalCase]:
        """
        Retrieve a case by its URL.

        Args:
            url: Case URL

        Returns:
            LegalCase object or None
        """
        return self.session.query(LegalCase).filter_by(case_url=url).first()

    @log_slow_queries(threshold_seconds=1.0)
    def get_cases(self, limit: int = 100, court: Optional[str] = None,
                  year: Optional[str] = None) -> List[LegalCase]:
        """
        Retrieve cases from database with optional filters.

        Args:
            limit: Maximum number of cases to retrieve
            court: Filter by court name
            year: Filter by year

        Returns:
            List of LegalCase objects
        """
        query = self.session.query(LegalCase)

        if court:
            query = query.filter(LegalCase.court.contains(court))

        if year:
            query = query.filter(LegalCase.case_date.contains(year))

        return query.order_by(LegalCase.scraped_at.desc()).limit(limit).all()

    def get_cases_without_pdfs(self, limit: int = 100) -> List[LegalCase]:
        """
        Get cases that haven't had their PDFs downloaded yet.

        Args:
            limit: Maximum number of cases to retrieve

        Returns:
            List of LegalCase objects
        """
        return self.session.query(LegalCase).filter(
            LegalCase.pdf_link.isnot(None),
            LegalCase.pdf_link != '',
            LegalCase.pdf_downloaded.is_(False)  # Use .is_() for boolean comparisons
        ).limit(limit).all()

    def update_pdf_status(self, case_id: int, pdf_path: str) -> bool:
        """
        Update the PDF download status for a case.

        Args:
            case_id: ID of the case
            pdf_path: Path where PDF was saved

        Returns:
            True if successful, False otherwise
        """
        try:
            case = self.session.query(LegalCase).filter_by(id=case_id).first()
            if case:
                case.pdf_downloaded = True
                case.pdf_path = pdf_path
                self.session.commit()
                logger.info(f"Updated PDF status for case {case_id}")
                return True
            return False

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating PDF status: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the database.

        Returns:
            Dictionary with statistics
        """
        total_cases = self.session.query(LegalCase).count()
        cases_with_pdfs = self.session.query(LegalCase).filter(
            LegalCase.pdf_downloaded.is_(True)  # Use .is_() for boolean
        ).count()

        courts = self.session.query(LegalCase.court).distinct().all()
        court_list = [c[0] for c in courts if c[0]]

        # NEW: Get statistics by court type
        by_court_type = {}
        for court_type in CourtType:
            count = self.session.query(LegalCase).filter_by(court_type=court_type).count()
            if count > 0:
                by_court_type[court_type.value] = count

        # NEW: Get statistics by year
        years = self.session.query(LegalCase.year).distinct().all()
        year_list = sorted([y[0] for y in years if y[0]])

        # NEW: Get statistics by tier
        by_tier = {}
        for tier in [1, 2, 3, 4]:
            count = self.session.query(LegalCase).filter_by(scrape_tier=tier).count()
            if count > 0:
                by_tier[f'tier_{tier}'] = count

        return {
            'total_cases': total_cases,
            'cases_with_pdfs': cases_with_pdfs,
            'cases_without_pdfs': total_cases - cases_with_pdfs,
            'unique_courts': len(court_list),
            'courts': court_list,
            'by_court_type': by_court_type,
            'years_covered': year_list,
            'by_tier': by_tier
        }

    def get_cases_by_court_type(self, court_type: CourtType, limit: int = 100) -> List[LegalCase]:
        """Get cases by court type (SUPREME, HIGH, TRIBUNAL, etc.)"""
        return self.session.query(LegalCase).filter_by(court_type=court_type).limit(limit).all()

    def get_cases_by_year(self, year: int, limit: int = 100) -> List[LegalCase]:
        """Get cases by year"""
        return self.session.query(LegalCase).filter_by(year=year).limit(limit).all()

    def get_cases_by_tier(self, tier: int, limit: int = 100) -> List[LegalCase]:
        """Get cases by scraping tier"""
        return self.session.query(LegalCase).filter_by(scrape_tier=tier).limit(limit).all()

    def get_progress_by_court(self, court_name: str) -> Dict[str, Any]:
        """Get scraping progress for a specific court"""
        total = self.session.query(LegalCase).filter_by(court_name=court_name).count()
        with_pdfs = self.session.query(LegalCase).filter(
            LegalCase.court_name == court_name,
            LegalCase.pdf_downloaded.is_(True)
        ).count()

        return {
            'court_name': court_name,
            'total_cases': total,
            'cases_with_pdfs': with_pdfs,
            'completion_rate': (with_pdfs / total * 100) if total > 0 else 0
        }

    def get_progress_by_year(self, year: int) -> Dict[str, Any]:
        """Get scraping progress for a specific year"""
        total = self.session.query(LegalCase).filter_by(year=year).count()
        with_pdfs = self.session.query(LegalCase).filter(
            LegalCase.year == year,
            LegalCase.pdf_downloaded.is_(True)
        ).count()

        return {
            'year': year,
            'total_cases': total,
            'cases_with_pdfs': with_pdfs,
            'completion_rate': (with_pdfs / total * 100) if total > 0 else 0
        }

    # ==================================================================================
    # URL TRACKER METHODS (NEW for production scraper)
    # ==================================================================================

    def save_url(self, url_data: Dict[str, Any]) -> Optional[int]:
        """
        Save a URL to the tracker table.

        Args:
            url_data: Dictionary with url, doc_id, title, etc.

        Returns:
            ID of saved URL or None
        """
        try:
            # Check if URL already exists
            existing = self.session.query(URLTracker).filter_by(
                doc_url=url_data.get('url', '')
            ).first()

            if existing:
                return existing.id

            # Create new URL record
            url_record = URLTracker(
                doc_url=url_data.get('url', ''),
                doc_id=url_data.get('doc_id', ''),
                title=url_data.get('title', ''),
                citation=url_data.get('citation', ''),
                court=url_data.get('court', ''),
                collection_page=url_data.get('page', 0),
                metadata_json=json.dumps(url_data.get('metadata', {}))
            )

            self.session.add(url_record)
            self.session.commit()

            return url_record.id

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving URL: {e}")
            return None

    def bulk_save_urls(self, urls: List[Dict[str, Any]]) -> int:
        """
        Bulk save URLs to tracker table.

        Args:
            urls: List of URL dictionaries

        Returns:
            Number of URLs saved
        """
        saved_count = 0
        for url_data in urls:
            if self.save_url(url_data):
                saved_count += 1

        logger.info(f"Bulk saved {saved_count} URLs to tracker")
        return saved_count

    def get_pending_urls(self, limit: int = 1000) -> List[URLTracker]:
        """Get URLs pending download."""
        return self.session.query(URLTracker).filter_by(
            download_status=DownloadStatus.PENDING
        ).limit(limit).all()

    def get_failed_urls(self, max_attempts: int = 3, limit: int = 1000) -> List[URLTracker]:
        """Get failed URLs that can be retried."""
        return self.session.query(URLTracker).filter(
            URLTracker.download_status == DownloadStatus.FAILED,
            URLTracker.download_attempts < max_attempts
        ).limit(limit).all()

    def update_download_status(
        self,
        url_id: int,
        status: DownloadStatus,
        pdf_path: Optional[str] = None,
        pdf_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update download status for a URL."""
        try:
            url_record = self.session.query(URLTracker).filter_by(id=url_id).first()
            if url_record:
                url_record.download_status = status
                url_record.download_attempts += 1
                url_record.last_attempt_at = datetime.now()

                if pdf_path:
                    url_record.pdf_downloaded = True
                    url_record.pdf_path = pdf_path
                    url_record.pdf_size = pdf_size

                if error_message:
                    url_record.error_message = error_message

                self.session.commit()
                return True
            return False

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating download status: {e}")
            return False

    def update_drive_status(self, url_id: int, drive_file_id: str) -> bool:
        """Update Drive upload status for a URL."""
        try:
            url_record = self.session.query(URLTracker).filter_by(id=url_id).first()
            if url_record:
                url_record.uploaded_to_drive = True
                url_record.drive_file_id = drive_file_id
                url_record.uploaded_at = datetime.now()
                self.session.commit()
                return True
            return False

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating Drive status: {e}")
            return False

    def get_download_progress(self) -> Dict[str, Any]:
        """Get comprehensive download progress statistics."""
        total_urls = self.session.query(URLTracker).count()

        status_counts = {}
        for status in DownloadStatus:
            count = self.session.query(URLTracker).filter_by(download_status=status).count()
            status_counts[status.value] = count

        pdfs_downloaded = self.session.query(URLTracker).filter(
            URLTracker.pdf_downloaded.is_(True)
        ).count()
        uploaded_to_drive = self.session.query(URLTracker).filter(
            URLTracker.uploaded_to_drive.is_(True)
        ).count()

        return {
            'total_urls': total_urls,
            'status_breakdown': status_counts,
            'pdfs_downloaded': pdfs_downloaded,
            'uploaded_to_drive': uploaded_to_drive,
            'completion_rate': (pdfs_downloaded / total_urls * 100) if total_urls > 0 else 0,
            'upload_rate': (uploaded_to_drive / pdfs_downloaded * 100) if pdfs_downloaded > 0 else 0
        }

    def get_urls_to_download(self, batch_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Get URLs ready for download in dictionary format.

        Args:
            batch_size: Number of URLs to retrieve

        Returns:
            List of dictionaries with url, doc_id, metadata
        """
        pending = self.get_pending_urls(limit=batch_size)

        urls = []
        for record in pending:
            urls.append({
                'id': record.id,
                'url': record.doc_url,
                'doc_id': record.doc_id,
                'title': record.title,
                'citation': record.citation,
                'court': record.court,
                'metadata': json.loads(record.metadata_json) if record.metadata_json else {}
            })

        return urls

    def _commit_with_retry(self, max_retries: int = 3) -> None:
        """
        Commit transaction with retry logic.

        Args:
            max_retries: Maximum number of retry attempts

        Raises:
            Exception: If commit fails after all retries
        """
        for attempt in range(max_retries):
            try:
                self.session.commit()
                return
            except Exception as e:
                self.session.rollback()
                if attempt == max_retries - 1:
                    logger.error(f"Failed to commit after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Commit failed (attempt {attempt + 1}/{max_retries}): {e}")
                import time
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff

    # ==================================================================================
    # CHECKPOINT METHODS (NEW for auto-resume functionality)
    # ==================================================================================

    def save_checkpoint(
        self,
        process_name: str,
        last_case_id: int,
        last_offset: int,
        stats: Dict = None
    ) -> Optional[int]:
        """
        Save or update a checkpoint for a process.

        Args:
            process_name: Name of the process (e.g., 'bulk_download')
            last_case_id: ID of the last successfully processed case
            last_offset: Offset position in the batch processing
            stats: Optional dictionary with statistics (pdfs_downloaded, etc.)

        Returns:
            Checkpoint ID or None if failed
        """
        try:
            # Get active checkpoint for this process or create new one
            checkpoint = self.session.query(Checkpoint).filter_by(
                process_name=process_name,
                status=CheckpointStatus.ACTIVE
            ).first()

            if checkpoint:
                # Update existing checkpoint
                checkpoint.last_case_id = last_case_id
                checkpoint.last_offset = last_offset
                checkpoint.updated_at = datetime.now()
                checkpoint.total_processed += 1

                if stats:
                    checkpoint.pdfs_downloaded = stats.get('pdfs_downloaded', checkpoint.pdfs_downloaded)
                    checkpoint.details_fetched = stats.get('details_fetched', checkpoint.details_fetched)
                    checkpoint.failures = stats.get('failures', checkpoint.failures)
                    if stats.get('metadata'):
                        checkpoint.metadata_json = json.dumps(stats['metadata'])
            else:
                # Create new checkpoint
                checkpoint = Checkpoint(
                    process_name=process_name,
                    last_case_id=last_case_id,
                    last_offset=last_offset,
                    total_processed=1,
                    pdfs_downloaded=stats.get('pdfs_downloaded', 0) if stats else 0,
                    details_fetched=stats.get('details_fetched', 0) if stats else 0,
                    failures=stats.get('failures', 0) if stats else 0,
                    metadata_json=json.dumps(stats.get('metadata', {})) if stats else None
                )
                self.session.add(checkpoint)

            self.session.commit()
            logger.debug(f"Checkpoint saved: {checkpoint.id} at case_id={last_case_id}, offset={last_offset}")
            return checkpoint.id

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving checkpoint: {e}")
            return None

    def get_latest_checkpoint(self, process_name: str) -> Optional[Checkpoint]:
        """
        Get the latest active checkpoint for a process.

        Args:
            process_name: Name of the process

        Returns:
            Checkpoint object or None
        """
        try:
            return self.session.query(Checkpoint).filter_by(
                process_name=process_name,
                status=CheckpointStatus.ACTIVE
            ).order_by(Checkpoint.updated_at.desc()).first()
        except Exception as e:
            logger.error(f"Error getting latest checkpoint: {e}")
            return None

    def validate_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """
        Validate checkpoint integrity.

        Args:
            checkpoint: Checkpoint object to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if the last_case_id exists in the database
            case_exists = self.session.query(LegalCase).filter_by(id=checkpoint.last_case_id).first()
            if not case_exists:
                logger.warning(f"Checkpoint validation failed: Case ID {checkpoint.last_case_id} not found")
                return False

            # Check if offset is reasonable
            total_cases = self.session.query(LegalCase).count()
            if checkpoint.last_offset >= total_cases:
                logger.warning(f"Checkpoint validation failed: Offset {checkpoint.last_offset} exceeds total cases {total_cases}")
                return False

            # Check if checkpoint is not too old (optional: add timestamp validation)
            return True

        except Exception as e:
            logger.error(f"Error validating checkpoint: {e}")
            return False

    def invalidate_checkpoint(self, checkpoint_id: int, error_message: str = None) -> bool:
        """
        Mark a checkpoint as invalidated.

        Args:
            checkpoint_id: ID of the checkpoint to invalidate
            error_message: Optional error message

        Returns:
            True if successful, False otherwise
        """
        try:
            checkpoint = self.session.query(Checkpoint).filter_by(id=checkpoint_id).first()
            if checkpoint:
                checkpoint.status = CheckpointStatus.INVALIDATED
                if error_message:
                    checkpoint.error_message = error_message
                checkpoint.updated_at = datetime.now()
                self.session.commit()
                logger.info(f"Checkpoint {checkpoint_id} invalidated")
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error invalidating checkpoint: {e}")
            return False

    def complete_checkpoint(self, checkpoint_id: int) -> bool:
        """
        Mark a checkpoint as completed.

        Args:
            checkpoint_id: ID of the checkpoint to complete

        Returns:
            True if successful, False otherwise
        """
        try:
            checkpoint = self.session.query(Checkpoint).filter_by(id=checkpoint_id).first()
            if checkpoint:
                checkpoint.status = CheckpointStatus.COMPLETED
                checkpoint.updated_at = datetime.now()
                self.session.commit()
                logger.info(f"Checkpoint {checkpoint_id} completed")
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error completing checkpoint: {e}")
            return False

    def get_checkpoint_stats(self, process_name: str = None) -> Dict:
        """
        Get statistics about checkpoints.

        Args:
            process_name: Optional filter by process name

        Returns:
            Dictionary with checkpoint statistics
        """
        try:
            query = self.session.query(Checkpoint)
            if process_name:
                query = query.filter_by(process_name=process_name)

            total_checkpoints = query.count()
            active_checkpoints = query.filter_by(status=CheckpointStatus.ACTIVE).count()
            completed_checkpoints = query.filter_by(status=CheckpointStatus.COMPLETED).count()
            failed_checkpoints = query.filter_by(status=CheckpointStatus.FAILED).count()

            return {
                'total_checkpoints': total_checkpoints,
                'active': active_checkpoints,
                'completed': completed_checkpoints,
                'failed': failed_checkpoints,
                'process_name': process_name
            }
        except Exception as e:
            logger.error(f"Error getting checkpoint stats: {e}")
            return {}

    def close(self) -> None:
        """Close database session and dispose engine safely."""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
            if hasattr(self, 'Session'):
                self.Session.remove()  # Remove scoped session
            logger.info("Database session closed")
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
        finally:
            try:
                if hasattr(self, 'engine') and self.engine:
                    self.engine.dispose()
                    logger.debug("Database engine disposed")
            except Exception as e:
                logger.error(f"Error disposing database engine: {e}")

    def __enter__(self) -> "CaseDatabase":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> bool:
        """
        Context manager exit with proper cleanup.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            False to propagate any exception that occurred
        """
        try:
            if exc_type is not None:
                # An exception occurred, rollback the transaction
                self.session.rollback()
                logger.warning(f"Transaction rolled back due to exception: {exc_type.__name__}")
            else:
                # No exception, commit any pending changes
                try:
                    self.session.commit()
                except Exception as e:
                    logger.error(f"Error committing in __exit__: {e}")
                    self.session.rollback()
        finally:
            self.close()

        # Don't suppress the exception
        return False

    def __del__(self) -> None:
        """Destructor to ensure resources are cleaned up."""
        try:
            self.close()
        except:
            pass  # Silently fail in destructor

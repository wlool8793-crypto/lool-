"""
Unified Database Manager
Handles all database operations for multi-country legal documents
Supports both legacy and universal schema
"""

import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

# Import universal system components
try:
    from .naming.id_generator import IDGenerator
    from .naming.universal_namer import UniversalNamer
    from .taxonomy.subjects import SubjectClassifier
except ImportError:
    try:
        # Try without relative import
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from naming.id_generator import IDGenerator
        from naming.universal_namer import UniversalNamer
        from taxonomy.subjects import SubjectClassifier
    except ImportError:
        # Fallback for standalone usage
        IDGenerator = None
        UniversalNamer = None
        SubjectClassifier = None


class UnifiedDatabase:
    """Database manager for unified multi-country legal documents"""

    def __init__(self, db_path: str = None, use_universal: bool = False):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
            use_universal: Use universal schema (default: False for backward compatibility)
        """
        if db_path is None:
            db_path = 'data/universal_legal.db' if use_universal else 'data/indiankanoon.db'

        self.db_path = db_path
        self.use_universal = use_universal
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.logger = logging.getLogger(__name__)

        # Initialize universal system components
        if use_universal and IDGenerator:
            self.id_generator = IDGenerator(db_path)
            self.namer = UniversalNamer()
            self.classifier = SubjectClassifier()
        else:
            self.id_generator = None
            self.namer = None
            self.classifier = None

    def save_legal_document(self, doc_data: Dict[str, Any]) -> int:
        """
        Save a legal document to the database.

        Args:
            doc_data: Dictionary containing document information

        Returns:
            ID of inserted/updated document
        """
        cursor = self.conn.cursor()

        # Required fields
        required = ['country', 'title', 'source_url', 'source_site']
        for field in required:
            if field not in doc_data:
                raise ValueError(f"Missing required field: {field}")

        # Insert or update
        cursor.execute("""
            INSERT INTO legal_documents (
                country, country_doc_id, title, short_title, doc_type,
                year, category, court_or_ministry, citation, bench,
                source_url, source_site, source_index,
                html_content, plain_text, summary,
                pdf_url, pdf_path, pdf_downloaded, pdf_size_kb, pdf_hash,
                status, effective_date, last_amended_date,
                scraped_at, scrape_status, error_message, scraper_version
            ) VALUES (
                :country, :country_doc_id, :title, :short_title, :doc_type,
                :year, :category, :court_or_ministry, :citation, :bench,
                :source_url, :source_site, :source_index,
                :html_content, :plain_text, :summary,
                :pdf_url, :pdf_path, :pdf_downloaded, :pdf_size_kb, :pdf_hash,
                :status, :effective_date, :last_amended_date,
                :scraped_at, :scrape_status, :error_message, :scraper_version
            )
            ON CONFLICT(country, source_url) DO UPDATE SET
                title = excluded.title,
                html_content = excluded.html_content,
                plain_text = excluded.plain_text,
                pdf_url = excluded.pdf_url,
                updated_at = CURRENT_TIMESTAMP
        """, {
            'country': doc_data.get('country'),
            'country_doc_id': doc_data.get('country_doc_id'),
            'title': doc_data.get('title'),
            'short_title': doc_data.get('short_title'),
            'doc_type': doc_data.get('doc_type'),
            'year': doc_data.get('year'),
            'category': doc_data.get('category'),
            'court_or_ministry': doc_data.get('court_or_ministry'),
            'citation': doc_data.get('citation'),
            'bench': doc_data.get('bench'),
            'source_url': doc_data.get('source_url'),
            'source_site': doc_data.get('source_site'),
            'source_index': doc_data.get('source_index'),
            'html_content': doc_data.get('html_content'),
            'plain_text': doc_data.get('plain_text'),
            'summary': doc_data.get('summary'),
            'pdf_url': doc_data.get('pdf_url'),
            'pdf_path': doc_data.get('pdf_path'),
            'pdf_downloaded': 1 if doc_data.get('pdf_downloaded') else 0,
            'pdf_size_kb': doc_data.get('pdf_size_kb'),
            'pdf_hash': doc_data.get('pdf_hash'),
            'status': doc_data.get('status', 'active'),
            'effective_date': doc_data.get('effective_date'),
            'last_amended_date': doc_data.get('last_amended_date'),
            'scraped_at': doc_data.get('scraped_at', datetime.now().isoformat()),
            'scrape_status': doc_data.get('scrape_status', 'complete'),
            'error_message': doc_data.get('error_message'),
            'scraper_version': doc_data.get('scraper_version', '1.0')
        })

        self.conn.commit()
        doc_id = cursor.lastrowid

        # Save metadata if provided
        if 'metadata' in doc_data and doc_data['metadata']:
            self.save_metadata(doc_id, doc_data['metadata'])

        return doc_id

    def save_metadata(self, doc_id: int, metadata: Dict[str, Any]):
        """
        Save document metadata (flexible key-value storage).

        Args:
            doc_id: Document ID
            metadata: Dictionary of metadata key-value pairs
        """
        cursor = self.conn.cursor()

        for key, value in metadata.items():
            cursor.execute("""
                INSERT INTO document_metadata (document_id, metadata_key, metadata_value)
                VALUES (?, ?, ?)
                ON CONFLICT(document_id, metadata_key) DO UPDATE SET
                    metadata_value = excluded.metadata_value
            """, (doc_id, key, str(value)))

        self.conn.commit()

    def update_pdf_path(self, doc_id: int, pdf_path: str):
        """
        Update PDF path and mark as downloaded.

        Args:
            doc_id: Document ID
            pdf_path: Local path to downloaded PDF
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE legal_documents
            SET pdf_path = ?, pdf_downloaded = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pdf_path, doc_id))
        self.conn.commit()

    def get_scraped_urls(self, country: str) -> List[str]:
        """
        Get list of already scraped URLs for a country.

        Args:
            country: Country code

        Returns:
            List of URLs
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT source_url FROM legal_documents
            WHERE country = ?
        """, (country,))

        return [row['source_url'] for row in cursor.fetchall()]

    def get_stats(self, country: str = None) -> Dict[str, Any]:
        """
        Get statistics for a country or all countries.

        Args:
            country: Country code (None for all countries)

        Returns:
            Dictionary of statistics
        """
        cursor = self.conn.cursor()

        if country:
            cursor.execute("""
                SELECT * FROM country_stats WHERE country = ?
            """, (country,))
        else:
            cursor.execute("SELECT * FROM overall_stats")

        row = cursor.fetchone()
        return dict(row) if row else {}

    def get_country_stats(self, country: str) -> Dict[str, Any]:
        """Get statistics for a specific country"""
        return self.get_stats(country=country)

    def get_all_countries(self) -> List[str]:
        """Get list of all countries in database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT country FROM legal_documents ORDER BY country")
        return [row['country'] for row in cursor.fetchall()]

    def get_documents(self, country: str = None, limit: int = 100) -> List[Dict]:
        """
        Get list of documents.

        Args:
            country: Filter by country (None for all)
            limit: Maximum number of documents to return

        Returns:
            List of document dictionaries
        """
        cursor = self.conn.cursor()

        if country:
            cursor.execute("""
                SELECT * FROM legal_documents
                WHERE country = ?
                ORDER BY scraped_at DESC
                LIMIT ?
            """, (country, limit))
        else:
            cursor.execute("""
                SELECT * FROM legal_documents
                ORDER BY scraped_at DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def search_documents(self, query: str, country: str = None) -> List[Dict]:
        """
        Search documents by title or text.

        Args:
            query: Search query
            country: Filter by country (optional)

        Returns:
            List of matching documents
        """
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"

        if country:
            cursor.execute("""
                SELECT * FROM legal_documents
                WHERE country = ? AND (
                    title LIKE ? OR
                    plain_text LIKE ? OR
                    summary LIKE ?
                )
                ORDER BY scraped_at DESC
                LIMIT 100
            """, (country, search_pattern, search_pattern, search_pattern))
        else:
            cursor.execute("""
                SELECT * FROM legal_documents
                WHERE
                    title LIKE ? OR
                    plain_text LIKE ? OR
                    summary LIKE ?
                ORDER BY scraped_at DESC
                LIMIT 100
            """, (search_pattern, search_pattern, search_pattern))

        return [dict(row) for row in cursor.fetchall()]

    def save_universal_document(self, doc_data: Dict[str, Any]) -> int:
        """
        Save a document using the universal schema.

        Args:
            doc_data: Dictionary containing document information

        Returns:
            ID of inserted/updated document
        """
        if not self.use_universal:
            raise RuntimeError("Universal schema not enabled. Initialize with use_universal=True")

        # Generate IDs if not present
        if 'global_id_numeric' not in doc_data or 'global_id' not in doc_data:
            numeric_id, formatted_id = self.id_generator.generate_global_id()
            doc_data['global_id_numeric'] = numeric_id
            doc_data['global_id'] = formatted_id

        if 'uuid' not in doc_data:
            doc_data['uuid'] = self.id_generator.generate_uuid()

        # Generate yearly sequence if year and category present
        if 'doc_year' in doc_data and 'doc_category' in doc_data and 'country_code' in doc_data:
            yearly_seq = self.id_generator.get_next_yearly_sequence(
                doc_data['country_code'],
                doc_data['doc_category'],
                doc_data['doc_year']
            )
            doc_data['yearly_sequence'] = yearly_seq

        # Classify subject if not present
        if 'subject_primary' not in doc_data or 'subject_code' not in doc_data:
            title = doc_data.get('title_full', '')
            content = doc_data.get('plain_text', '')
            country = doc_data.get('country_code', '')

            primary, subcat, code = self.classifier.classify(title, content, country_code=country)
            doc_data.setdefault('subject_primary', primary)
            doc_data.setdefault('subject_secondary', subcat)
            doc_data.setdefault('subject_code', code)

        # Generate universal filename
        if 'filename_universal' not in doc_data:
            filename = self.namer.generate_filename(doc_data)
            doc_data['filename_universal'] = filename

        # Generate folder path
        if 'file_path_relative' not in doc_data:
            folder = self.namer.generate_folder_path(doc_data)
            doc_data['file_path_relative'] = folder

        cursor = self.conn.cursor()

        # Insert into universal_legal_documents table
        cursor.execute("""
            INSERT INTO universal_legal_documents (
                global_id, uuid,
                country_code, country_name, jurisdiction_level, jurisdiction_name,
                doc_category, doc_type, doc_subcategory,
                doc_number, doc_year, yearly_sequence, country_doc_id,
                title_full, title_short, title_alternate,
                subject_primary, subject_secondary, subject_code, subject_tags,
                court_level, court_name, court_code, bench_type, bench_size, judges,
                issuing_authority, authority_code,
                citation_primary, citation_alternate, citation_neutral,
                legal_status, date_enacted, date_effective, date_published,
                date_last_amended, date_repealed,
                html_content, plain_text, summary, headnotes, preamble, key_provisions,
                filename_universal, file_path_relative, file_path_absolute,
                folder_category, folder_subcategory,
                pdf_url, pdf_filename, pdf_path, pdf_downloaded,
                pdf_size_bytes, pdf_pages, pdf_hash_sha256, pdf_ocr_done,
                source_url, source_domain, source_database, source_index, source_last_checked,
                parent_doc_id, supersedes_doc_id, amended_by, cited_by_count, cites_count,
                version, checksum, language, encoding,
                scraper_name, scraper_version, scrape_timestamp, scrape_status,
                scrape_error, scrape_duration_ms,
                data_quality_score, validation_status, validation_errors, manual_review_needed
            ) VALUES (
                :global_id, :uuid,
                :country_code, :country_name, :jurisdiction_level, :jurisdiction_name,
                :doc_category, :doc_type, :doc_subcategory,
                :doc_number, :doc_year, :yearly_sequence, :country_doc_id,
                :title_full, :title_short, :title_alternate,
                :subject_primary, :subject_secondary, :subject_code, :subject_tags,
                :court_level, :court_name, :court_code, :bench_type, :bench_size, :judges,
                :issuing_authority, :authority_code,
                :citation_primary, :citation_alternate, :citation_neutral,
                :legal_status, :date_enacted, :date_effective, :date_published,
                :date_last_amended, :date_repealed,
                :html_content, :plain_text, :summary, :headnotes, :preamble, :key_provisions,
                :filename_universal, :file_path_relative, :file_path_absolute,
                :folder_category, :folder_subcategory,
                :pdf_url, :pdf_filename, :pdf_path, :pdf_downloaded,
                :pdf_size_bytes, :pdf_pages, :pdf_hash_sha256, :pdf_ocr_done,
                :source_url, :source_domain, :source_database, :source_index, :source_last_checked,
                :parent_doc_id, :supersedes_doc_id, :amended_by, :cited_by_count, :cites_count,
                :version, :checksum, :language, :encoding,
                :scraper_name, :scraper_version, :scrape_timestamp, :scrape_status,
                :scrape_error, :scrape_duration_ms,
                :data_quality_score, :validation_status, :validation_errors, :manual_review_needed
            )
            ON CONFLICT(country_code, source_url) DO UPDATE SET
                title_full = excluded.title_full,
                html_content = excluded.html_content,
                plain_text = excluded.plain_text,
                pdf_url = excluded.pdf_url,
                updated_at = CURRENT_TIMESTAMP
        """, {
            'global_id': doc_data.get('global_id'),
            'uuid': doc_data.get('uuid'),
            'country_code': doc_data.get('country_code'),
            'country_name': doc_data.get('country_name'),
            'jurisdiction_level': doc_data.get('jurisdiction_level'),
            'jurisdiction_name': doc_data.get('jurisdiction_name'),
            'doc_category': doc_data.get('doc_category'),
            'doc_type': doc_data.get('doc_type'),
            'doc_subcategory': doc_data.get('doc_subcategory'),
            'doc_number': doc_data.get('doc_number'),
            'doc_year': doc_data.get('doc_year'),
            'yearly_sequence': doc_data.get('yearly_sequence'),
            'country_doc_id': doc_data.get('country_doc_id'),
            'title_full': doc_data.get('title_full'),
            'title_short': doc_data.get('title_short'),
            'title_alternate': doc_data.get('title_alternate'),
            'subject_primary': doc_data.get('subject_primary'),
            'subject_secondary': doc_data.get('subject_secondary'),
            'subject_code': doc_data.get('subject_code'),
            'subject_tags': doc_data.get('subject_tags'),
            'court_level': doc_data.get('court_level'),
            'court_name': doc_data.get('court_name'),
            'court_code': doc_data.get('court_code'),
            'bench_type': doc_data.get('bench_type'),
            'bench_size': doc_data.get('bench_size'),
            'judges': doc_data.get('judges'),
            'issuing_authority': doc_data.get('issuing_authority'),
            'authority_code': doc_data.get('authority_code'),
            'citation_primary': doc_data.get('citation_primary'),
            'citation_alternate': doc_data.get('citation_alternate'),
            'citation_neutral': doc_data.get('citation_neutral'),
            'legal_status': doc_data.get('legal_status', 'ACTIVE'),
            'date_enacted': doc_data.get('date_enacted'),
            'date_effective': doc_data.get('date_effective'),
            'date_published': doc_data.get('date_published'),
            'date_last_amended': doc_data.get('date_last_amended'),
            'date_repealed': doc_data.get('date_repealed'),
            'html_content': doc_data.get('html_content'),
            'plain_text': doc_data.get('plain_text'),
            'summary': doc_data.get('summary'),
            'headnotes': doc_data.get('headnotes'),
            'preamble': doc_data.get('preamble'),
            'key_provisions': doc_data.get('key_provisions'),
            'filename_universal': doc_data.get('filename_universal'),
            'file_path_relative': doc_data.get('file_path_relative'),
            'file_path_absolute': doc_data.get('file_path_absolute'),
            'folder_category': doc_data.get('folder_category', doc_data.get('doc_category')),
            'folder_subcategory': doc_data.get('folder_subcategory'),
            'pdf_url': doc_data.get('pdf_url'),
            'pdf_filename': doc_data.get('pdf_filename', doc_data.get('filename_universal')),
            'pdf_path': doc_data.get('pdf_path'),
            'pdf_downloaded': 1 if doc_data.get('pdf_downloaded') else 0,
            'pdf_size_bytes': doc_data.get('pdf_size_bytes'),
            'pdf_pages': doc_data.get('pdf_pages'),
            'pdf_hash_sha256': doc_data.get('pdf_hash_sha256'),
            'pdf_ocr_done': 1 if doc_data.get('pdf_ocr_done') else 0,
            'source_url': doc_data.get('source_url'),
            'source_domain': doc_data.get('source_domain'),
            'source_database': doc_data.get('source_database'),
            'source_index': doc_data.get('source_index'),
            'source_last_checked': doc_data.get('source_last_checked'),
            'parent_doc_id': doc_data.get('parent_doc_id'),
            'supersedes_doc_id': doc_data.get('supersedes_doc_id'),
            'amended_by': doc_data.get('amended_by'),
            'cited_by_count': doc_data.get('cited_by_count', 0),
            'cites_count': doc_data.get('cites_count', 0),
            'version': doc_data.get('version', 1),
            'checksum': doc_data.get('checksum'),
            'language': doc_data.get('language', 'en'),
            'encoding': doc_data.get('encoding', 'UTF-8'),
            'scraper_name': doc_data.get('scraper_name', 'universal_scraper'),
            'scraper_version': doc_data.get('scraper_version', '2.0'),
            'scrape_timestamp': doc_data.get('scrape_timestamp', datetime.now().isoformat()),
            'scrape_status': doc_data.get('scrape_status', 'COMPLETE'),
            'scrape_error': doc_data.get('scrape_error'),
            'scrape_duration_ms': doc_data.get('scrape_duration_ms'),
            'data_quality_score': doc_data.get('data_quality_score'),
            'validation_status': doc_data.get('validation_status'),
            'validation_errors': doc_data.get('validation_errors'),
            'manual_review_needed': 1 if doc_data.get('manual_review_needed') else 0
        })

        self.conn.commit()
        doc_id = cursor.lastrowid

        # Save metadata if provided
        if 'metadata' in doc_data and doc_data['metadata']:
            self._save_universal_metadata(doc_id, doc_data['metadata'])

        return doc_id

    def _save_universal_metadata(self, doc_id: int, metadata: Dict[str, Any]):
        """Save metadata for universal document"""
        cursor = self.conn.cursor()

        for key, value in metadata.items():
            # Determine type
            if isinstance(value, bool):
                meta_type = 'boolean'
                meta_value = '1' if value else '0'
            elif isinstance(value, (int, float)):
                meta_type = 'number'
                meta_value = str(value)
            elif isinstance(value, dict) or isinstance(value, list):
                meta_type = 'json'
                import json
                meta_value = json.dumps(value)
            else:
                meta_type = 'text'
                meta_value = str(value)

            cursor.execute("""
                INSERT INTO document_metadata (document_id, metadata_key, metadata_value, metadata_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(document_id, metadata_key) DO UPDATE SET
                    metadata_value = excluded.metadata_value,
                    metadata_type = excluded.metadata_type
            """, (doc_id, key, meta_value, meta_type))

        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Test database
    db = UnifiedDatabase()

    print("Overall Stats:")
    print(db.get_stats())

    print("\nCountries:")
    print(db.get_all_countries())

    print("\nIndia Stats:")
    print(db.get_country_stats('india'))

    db.close()

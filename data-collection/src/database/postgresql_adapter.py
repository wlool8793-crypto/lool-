#!/usr/bin/env python3
"""
PostgreSQL Database Adapter for Production Scraper
Handles all database operations for the scraping system
"""

import hashlib
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class PostgreSQLAdapter:
    """Database adapter for PostgreSQL operations"""

    def __init__(self, db_config: dict):
        """
        Initialize PostgreSQL adapter

        Args:
            db_config: Database configuration dict with host, port, database, user, password
        """
        self.config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5433),
            'database': db_config.get('database', 'indiankanoon'),
            'user': db_config.get('user', 'indiankanoon_user'),
            'password': db_config.get('password', 'postgres')
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(**self.config)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_documents_to_process(self, limit: Optional[int] = None) -> List[Tuple[int, str]]:
        """
        Get documents that need to be downloaded

        Returns:
            List of (doc_id, source_url) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Find documents without file storage records
            query = """
                SELECT d.id, d.source_url
                FROM documents d
                LEFT JOIN file_storage fs ON d.id = fs.document_id
                WHERE fs.id IS NULL
                AND d.source_url IS NOT NULL
                AND d.source_url LIKE '%indiankanoon.org%'
                AND d.source_url NOT LIKE '%/docfragment/%'
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            results = cursor.fetchall()

            return results

    def mark_document_downloaded(self, doc_id: int, pdf_path: str, pdf_size: int) -> bool:
        """
        Mark document as downloaded by creating file_storage record

        Args:
            doc_id: Document ID
            pdf_path: Path to downloaded PDF
            pdf_size: Size in bytes

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Generate required fields
                pdf_filename = f"doc_{doc_id}.pdf"

                # Generate PDF hash
                try:
                    with open(pdf_path, 'rb') as f:
                        pdf_hash = hashlib.sha256(f.read()).hexdigest()
                except:
                    # Fallback if file not found
                    pdf_hash = hashlib.sha256(f"{doc_id}{pdf_path}".encode()).hexdigest()

                # Insert into file_storage
                cursor.execute("""
                    INSERT INTO file_storage (
                        document_id, version_number, storage_tier,
                        pdf_filename, pdf_hash_sha256, pdf_size_bytes,
                        is_current_version, upload_status, download_status,
                        download_count, cache_priority, cache_hits, cache_misses,
                        upload_attempts, integrity_check_count,
                        cache_tier, local_cache_path,
                        uploaded_at, created_at, updated_at
                    ) VALUES (
                        %s, 1, 'local',
                        %s, %s, %s,
                        true, 'completed', 'completed',
                        0, 1, 0, 0,
                        1, 1,
                        'hot', %s,
                        %s, %s, %s
                    )
                    ON CONFLICT (document_id, version_number) DO UPDATE SET
                        pdf_size_bytes = EXCLUDED.pdf_size_bytes,
                        pdf_hash_sha256 = EXCLUDED.pdf_hash_sha256,
                        local_cache_path = EXCLUDED.local_cache_path,
                        upload_status = EXCLUDED.upload_status,
                        updated_at = EXCLUDED.updated_at
                """, (
                    doc_id, pdf_filename, pdf_hash, pdf_size,
                    pdf_path,
                    datetime.now(), datetime.now(), datetime.now()
                ))

                return True

        except Exception as e:
            raise Exception(f"Failed to mark document {doc_id} as downloaded: {e}")

    def get_stats(self) -> dict:
        """
        Get database statistics

        Returns:
            Dict with total, downloaded, pending counts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            total = cursor.fetchone()[0]

            # Downloaded (have file_storage records)
            cursor.execute("SELECT COUNT(DISTINCT document_id) FROM file_storage")
            downloaded = cursor.fetchone()[0]

            # Pending (exclude docfragments)
            cursor.execute("""
                SELECT COUNT(*)
                FROM documents d
                LEFT JOIN file_storage fs ON d.id = fs.document_id
                WHERE fs.id IS NULL
                AND d.source_url NOT LIKE '%/docfragment/%'
            """)
            pending = cursor.fetchone()[0]

            return {
                'total': total,
                'downloaded': downloaded,
                'pending': pending
            }

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                return True
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")

    def get_next_global_id(self, country_code: str = 'BD') -> str:
        """
        Get next available global ID for a country

        Args:
            country_code: 2-letter country code (default: BD for Bangladesh)

        Returns:
            Next global ID like 'BD00000001'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(CAST(SUBSTRING(global_id FROM 3) AS INTEGER))
                FROM documents
                WHERE global_id LIKE %s
            """, (f"{country_code}%",))
            result = cursor.fetchone()[0]
            next_num = (result or 0) + 1
            return f"{country_code}{next_num:08d}"

    def insert_bangladesh_document(self, doc_data: dict) -> int:
        """
        Insert a Bangladesh legal document

        Args:
            doc_data: Dictionary with document fields

        Returns:
            Document ID
        """
        import re

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Generate identifiers
            global_id = self.get_next_global_id('BD')

            # Generate content hash
            content = doc_data.get('content', doc_data.get('title', ''))
            content_hash = hashlib.md5(content.encode()).hexdigest()[:16]

            # Parse year from title or date
            year = doc_data.get('year')
            if not year:
                year_match = re.search(r'\b(18\d{2}|19\d{2}|20\d{2})\b', doc_data.get('title', ''))
                year = int(year_match.group(1)) if year_match else 2024

            # Generate filename
            doc_type = doc_data.get('doc_type', 'ACT').upper()[:3]
            doc_number = doc_data.get('doc_number', '0')
            safe_title = re.sub(r'[^\w\s-]', '', doc_data.get('title', 'Unknown')[:50])
            safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
            filename = f"BD_{year}_{doc_type}_{doc_number}_{safe_title}.pdf"

            cursor.execute("""
                INSERT INTO documents (
                    global_id, filename_universal, content_hash,
                    country_code, doc_type, title_full, title_short,
                    doc_year, doc_number, source_url, source_domain,
                    source_database, legal_status, embedding_status,
                    validation_status, scraper_name, scraper_version,
                    scraped_at, created_at, updated_at
                ) VALUES (
                    %s, %s, %s,
                    'BD', %s, %s, %s,
                    %s, %s, %s, 'bdlaws.minlaw.gov.bd',
                    'bdlaws', 'ACT', 'pending',
                    'pending', 'bangladesh_scraper', '1.0',
                    %s, %s, %s
                )
                ON CONFLICT (global_id) DO UPDATE SET
                    updated_at = EXCLUDED.updated_at
                RETURNING id
            """, (
                global_id,
                filename,
                content_hash,
                doc_type,
                doc_data.get('title', 'Unknown'),
                doc_data.get('title_short', doc_data.get('title', '')[:100]),
                year,
                str(doc_number),
                doc_data.get('url', ''),
                datetime.now(),
                datetime.now(),
                datetime.now()
            ))

            doc_id = cursor.fetchone()[0]
            return doc_id

    def insert_file_storage_bangladesh(self, doc_id: int, pdf_path: str, pdf_size: int,
                                        drive_file_id: Optional[str] = None,
                                        drive_folder_path: Optional[str] = None) -> bool:
        """
        Insert file storage record for Bangladesh document

        Args:
            doc_id: Document ID
            pdf_path: Local path to PDF
            pdf_size: File size in bytes
            drive_file_id: Google Drive file ID (optional)
            drive_folder_path: Drive folder path (optional)

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get filename from path
                import os
                pdf_filename = os.path.basename(pdf_path)

                # Generate hash
                try:
                    with open(pdf_path, 'rb') as f:
                        pdf_hash = hashlib.sha256(f.read()).hexdigest()
                except:
                    pdf_hash = hashlib.sha256(f"{doc_id}{pdf_path}".encode()).hexdigest()

                # Determine storage tier (allowed: drive, cache, both, none)
                storage_tier = 'both' if drive_file_id else 'cache'
                upload_status = 'completed' if drive_file_id else 'pending'

                cursor.execute("""
                    INSERT INTO file_storage (
                        document_id, version_number, storage_tier,
                        drive_file_id, drive_folder_path,
                        local_cache_path, cache_tier,
                        pdf_filename, pdf_hash_sha256, pdf_size_bytes,
                        is_current_version, upload_status, download_status,
                        download_count, cache_priority, cache_hits, cache_misses,
                        upload_attempts, integrity_check_count,
                        uploaded_at, created_at, updated_at
                    ) VALUES (
                        %s, 1, %s,
                        %s, %s,
                        %s, 'hot',
                        %s, %s, %s,
                        true, %s, 'completed',
                        0, 1, 0, 0,
                        1, 1,
                        %s, %s, %s
                    )
                    ON CONFLICT (document_id, version_number) DO UPDATE SET
                        drive_file_id = COALESCE(EXCLUDED.drive_file_id, file_storage.drive_file_id),
                        drive_folder_path = COALESCE(EXCLUDED.drive_folder_path, file_storage.drive_folder_path),
                        storage_tier = CASE
                            WHEN EXCLUDED.drive_file_id IS NOT NULL THEN 'both'
                            ELSE file_storage.storage_tier
                        END,
                        upload_status = CASE
                            WHEN EXCLUDED.drive_file_id IS NOT NULL THEN 'completed'
                            ELSE file_storage.upload_status
                        END,
                        updated_at = EXCLUDED.updated_at
                """, (
                    doc_id, storage_tier,
                    drive_file_id, drive_folder_path,
                    pdf_path,
                    pdf_filename, pdf_hash, pdf_size,
                    upload_status,
                    datetime.now() if drive_file_id else None,
                    datetime.now(), datetime.now()
                ))

                return True

        except Exception as e:
            raise Exception(f"Failed to insert file storage for doc {doc_id}: {e}")

    def update_drive_info(self, doc_id: int, drive_file_id: str, drive_folder_path: str) -> bool:
        """
        Update file storage with Google Drive information

        Args:
            doc_id: Document ID
            drive_file_id: Google Drive file ID
            drive_folder_path: Drive folder path

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE file_storage
                    SET drive_file_id = %s,
                        drive_folder_path = %s,
                        storage_tier = 'both',
                        upload_status = 'completed',
                        uploaded_at = %s,
                        updated_at = %s
                    WHERE document_id = %s
                """, (
                    drive_file_id, drive_folder_path,
                    datetime.now(), datetime.now(),
                    doc_id
                ))

                return cursor.rowcount > 0

        except Exception as e:
            raise Exception(f"Failed to update Drive info for doc {doc_id}: {e}")

    def get_pending_uploads(self, limit: int = 50) -> List[Tuple[int, str]]:
        """
        Get documents pending Google Drive upload

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of (doc_id, local_cache_path) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT document_id, local_cache_path
                FROM file_storage
                WHERE upload_status = 'pending'
                AND local_cache_path IS NOT NULL
                LIMIT %s
            """, (limit,))

            return cursor.fetchall()

    def get_bangladesh_stats(self) -> dict:
        """
        Get statistics for Bangladesh documents

        Returns:
            Dictionary with counts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN fs.id IS NOT NULL THEN 1 END) as with_pdf,
                    COUNT(CASE WHEN fs.drive_file_id IS NOT NULL THEN 1 END) as on_drive
                FROM documents d
                LEFT JOIN file_storage fs ON d.id = fs.document_id
                WHERE d.country_code = 'BD'
            """)

            row = cursor.fetchone()
            return {
                'total_documents': row[0],
                'with_pdf': row[1],
                'on_drive': row[2],
                'pending_upload': row[1] - row[2]
            }

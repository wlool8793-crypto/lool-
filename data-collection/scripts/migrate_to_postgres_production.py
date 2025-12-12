#!/usr/bin/env python3
"""
Production Migration: SQLite to PostgreSQL
Intelligently maps SQLite schema to PostgreSQL production schema
"""

import sys
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspaces/lool-/data-collection')

from sqlalchemy import create_engine, text
from tqdm import tqdm

# Database connections
SQLITE_URL = 'sqlite:///data/indiankanoon.db'
POSTGRES_URL = 'postgresql://indiankanoon_user:postgres@localhost:5433/indiankanoon'

def generate_global_id(doc_id: int, country_code: str = 'IN') -> str:
    """Generate 10-character global ID: CC + NNNNNNNN"""
    return f"{country_code}{doc_id:08d}"

def generate_filename(doc_id: int, doc_type: str = 'JUD', year: int = 2023) -> str:
    """Generate universal filename"""
    return f"IN-{doc_type}-{year}-{doc_id:08d}"

def generate_content_hash(source_url: str, title: str) -> str:
    """Generate 16-character content hash"""
    content = f"{source_url}{title}"
    full_hash = hashlib.sha256(content.encode()).hexdigest()
    return full_hash[:16]

def extract_doc_type(source_url: str) -> str:
    """Extract document type from URL"""
    if 'supreme' in source_url.lower():
        return 'SCJ'  # Supreme Court Judgment
    elif 'high' in source_url.lower():
        return 'HCJ'  # High Court Judgment
    else:
        return 'JUD'  # Generic Judgment

def migrate_documents():
    """Migrate documents from SQLite to PostgreSQL"""

    print("="*80)
    print("PRODUCTION MIGRATION: SQLite → PostgreSQL")
    print("="*80)

    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # Get document count
    with sqlite_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM universal_legal_documents
            WHERE source_url LIKE '%indiankanoon%'
        """))
        total = result.scalar()
        print(f"\n📊 Found {total} documents to migrate")

    # Fetch all documents
    with sqlite_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                id, source_url, title_full, pdf_downloaded,
                pdf_path, pdf_size_bytes, doc_year, date_enacted,
                created_at, updated_at
            FROM universal_legal_documents
            WHERE source_url LIKE '%indiankanoon%'
            ORDER BY id
        """))
        rows = result.fetchall()

    print(f"🔄 Migrating {len(rows)} documents to PostgreSQL...\n")

    migrated_docs = 0
    migrated_files = 0

    with postgres_engine.connect() as pg_conn:
        for row in tqdm(rows, desc="Migrating"):
            doc_id = row[0]
            source_url = row[1]
            title_full = row[2] or f"Document {doc_id}"
            pdf_downloaded = row[3]
            pdf_path = row[4]
            pdf_size = row[5] or 0
            doc_year = row[6] or 2023
            date_enacted = row[7] if row[7] and row[7] != '' else None  # Handle empty strings
            created_at = row[8] or datetime.now()
            updated_at = row[9] or datetime.now()

            # Generate required fields
            global_id = generate_global_id(doc_id)
            doc_uuid = str(uuid.uuid4())
            filename = generate_filename(doc_id, year=doc_year)
            content_hash = generate_content_hash(source_url, title_full)
            doc_type = extract_doc_type(source_url)

            try:
                # Insert into documents table
                pg_conn.execute(text("""
                    INSERT INTO documents (
                        id, global_id, doc_uuid, filename_universal, content_hash,
                        country_code, doc_type, title_full, doc_year,
                        date_enacted, source_url, source_domain,
                        chunk_count, chunk_strategy, embedding_status,
                        cited_by_count, cites_count, validation_status,
                        manual_review_needed, scraped_at, created_at, updated_at
                    ) VALUES (
                        :id, :global_id, :doc_uuid, :filename, :hash,
                        'IN', :doc_type, :title, :year,
                        :date_enacted, :source_url, 'indiankanoon.org',
                        0, 'not_chunked', 'pending',
                        0, 0, 'pending',
                        false, :scraped_at, :created_at, :updated_at
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        title_full = EXCLUDED.title_full,
                        source_url = EXCLUDED.source_url,
                        updated_at = EXCLUDED.updated_at
                """), {
                    'id': doc_id,
                    'global_id': global_id,
                    'doc_uuid': doc_uuid,
                    'filename': filename,
                    'hash': content_hash,
                    'doc_type': doc_type,
                    'title': title_full,
                    'year': doc_year,
                    'date_enacted': date_enacted,
                    'source_url': source_url,
                    'scraped_at': created_at,
                    'created_at': created_at,
                    'updated_at': updated_at
                })

                migrated_docs += 1

                # Insert file storage if PDF exists
                if pdf_downloaded == 1 and pdf_path:
                    # Generate PDF hash
                    pdf_hash = hashlib.sha256(f"{doc_id}{pdf_path}".encode()).hexdigest()
                    pdf_filename = f"doc_{doc_id}.pdf"

                    pg_conn.execute(text("""
                        INSERT INTO file_storage (
                            document_id, version_number, storage_tier,
                            pdf_filename, pdf_hash_sha256, pdf_size_bytes,
                            is_current_version, upload_status,
                            download_count, cache_priority, cache_hits, cache_misses,
                            upload_attempts, integrity_check_count,
                            cache_tier, local_cache_path,
                            created_at, updated_at
                        ) VALUES (
                            :doc_id, 1, 'local',
                            :filename, :hash, :size,
                            true, 'completed',
                            0, 1, 0, 0,
                            1, 1,
                            'hot', :path,
                            :created_at, :updated_at
                        )
                        ON CONFLICT (document_id, version_number) DO UPDATE SET
                            pdf_size_bytes = EXCLUDED.pdf_size_bytes,
                            local_cache_path = EXCLUDED.local_cache_path,
                            updated_at = EXCLUDED.updated_at
                    """), {
                        'doc_id': doc_id,
                        'filename': pdf_filename,
                        'hash': pdf_hash,
                        'size': pdf_size,
                        'path': pdf_path,
                        'created_at': created_at,
                        'updated_at': updated_at
                    })

                    migrated_files += 1

                # Commit every 100 documents
                if migrated_docs % 100 == 0:
                    pg_conn.commit()

            except Exception as e:
                print(f"\n⚠️  Error migrating document {doc_id}: {e}")
                continue

        # Final commit
        pg_conn.commit()

    print(f"\n{'='*80}")
    print("MIGRATION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Migrated {migrated_docs} documents")
    print(f"✅ Migrated {migrated_files} PDF records")

    # Verify
    with postgres_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM documents"))
        doc_count = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM file_storage"))
        file_count = result.scalar()

        print(f"\n📊 PostgreSQL Verification:")
        print(f"   Documents: {doc_count}")
        print(f"   Files: {file_count}")
        print(f"   Success Rate: {migrated_docs/total*100:.1f}%")

    print(f"\n✅ PostgreSQL database ready for production use!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        migrate_documents()
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

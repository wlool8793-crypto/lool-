#!/usr/bin/env python3
"""
Migration script to convert legacy legal_cases to universal schema
"""

import sqlite3
import uuid
from datetime import datetime
from src.naming.id_generator import IDGenerator
from src.naming.universal_namer import UniversalNamer
from src.taxonomy.subjects import SubjectClassifier

def migrate_cases():
    """Migrate all cases from legal_cases to universal_legal_documents"""

    db_path = 'data/indiankanoon.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize helpers
    id_gen = IDGenerator(db_path)
    namer = UniversalNamer()
    classifier = SubjectClassifier()

    # Get all cases from legacy table
    cursor.execute("""
        SELECT
            id, case_url, title, citation, court, case_date,
            snippet, full_text, pdf_link, pdf_downloaded, pdf_path,
            scraped_at, year
        FROM legal_cases
    """)

    cases = cursor.fetchall()
    print(f"Found {len(cases)} cases to migrate...")

    migrated = 0
    skipped = 0
    errors = 0

    for case in cases:
        try:
            (legacy_id, case_url, title, citation, court, case_date,
             snippet, full_text, pdf_link, pdf_downloaded, pdf_path,
             scraped_at, year) = case

            # Skip if already migrated (check by source_url)
            cursor.execute(
                "SELECT COUNT(*) FROM universal_legal_documents WHERE source_url = ?",
                (case_url,)
            )
            if cursor.fetchone()[0] > 0:
                skipped += 1
                continue

            # Generate IDs
            numeric_id, global_id = id_gen.generate_global_id()
            doc_uuid = str(uuid.uuid4())

            # Classify subject from title and snippet
            text_for_classification = f"{title or ''} {snippet or ''}"
            try:
                primary_subject, subcategory, subject_code = classifier.classify(
                    title=text_for_classification,
                    content=None,
                    doc_type='CASE',
                    country_code='IN'
                )
                subject_info = {
                    'primary': primary_subject,
                    'secondary': subcategory,
                    'code': subject_code,
                    'subcategory_codes': [subcategory] if subcategory else ['GEN'],
                    'tags': []
                }
            except Exception as e:
                # Default classification if error
                subject_info = {
                    'primary': 'GENERAL',
                    'secondary': 'MISC',
                    'code': 'GEN',
                    'subcategory_codes': ['MISC'],
                    'tags': []
                }

            # Determine court level from court name
            court_level = None
            if court:
                court_lower = court.lower()
                if 'supreme' in court_lower:
                    court_level = 'SC'
                elif 'high' in court_lower:
                    court_level = 'HC'
                elif 'district' in court_lower or 'sessions' in court_lower:
                    court_level = 'DISTRICT'

            # Extract year from case_date or use provided year
            doc_year = year
            if not doc_year and case_date:
                try:
                    # Try to extract year from date string
                    if case_date:
                        parts = case_date.split()
                        for part in parts:
                            if len(part) == 4 and part.isdigit():
                                doc_year = int(part)
                                break
                except:
                    pass

            # Get yearly sequence
            if doc_year and court_level:
                yearly_seq = id_gen.get_next_yearly_sequence('IN', 'CASE', doc_year)
            else:
                yearly_seq = None

            # Generate filename and folder
            metadata = {
                'country_code': 'IN',
                'doc_category': 'CASE',
                'court_level': court_level or 'MISC',
                'doc_year': doc_year or 2023,
                'yearly_sequence': yearly_seq or numeric_id,
                'title_short': (title[:30] if title else f'Case_{legacy_id}'),
                'subject_code': subject_info.get('code', 'MISC'),
                'subcategory_code': subject_info.get('subcategory_codes', ['GEN'])[0],
                'legal_status': 'ACTIVE',
                'global_sequence': numeric_id
            }

            filename = namer.generate_filename(metadata)
            folder_path = namer.generate_folder_path(metadata)

            # Insert into universal table
            cursor.execute("""
                INSERT INTO universal_legal_documents (
                    global_id, uuid,
                    country_code, country_name, jurisdiction_level,
                    doc_category, doc_year, yearly_sequence,
                    title_full, title_short,
                    subject_primary, subject_secondary, subject_code, subject_tags,
                    court_level, court_name, citation_primary,
                    legal_status, date_enacted,
                    html_content, plain_text, summary,
                    pdf_url, pdf_path, pdf_downloaded,
                    source_url, source_domain,
                    scraper_name, scrape_timestamp,
                    filename_universal, file_path_relative,
                    created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                global_id, doc_uuid,
                'IN', 'India', 'CENTRAL',
                'CASE', doc_year, yearly_seq,
                title, (title[:100] if title else None),
                subject_info.get('primary'), subject_info.get('secondary'),
                subject_info.get('code'), str(subject_info.get('tags', [])),
                court_level, court, citation,
                'ACTIVE', case_date,
                full_text, full_text, snippet,
                pdf_link, pdf_path, pdf_downloaded,
                case_url, 'indiankanoon.org',
                'indiankanoon_scraper', scraped_at,
                filename, folder_path,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            migrated += 1

            if migrated % 50 == 0:
                print(f"Migrated {migrated} cases...")
                conn.commit()

        except Exception as e:
            errors += 1
            print(f"Error migrating case {legacy_id}: {e}")
            continue

    # Final commit
    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"Total cases processed: {len(cases)}")
    print(f"Successfully migrated: {migrated}")
    print(f"Skipped (already exists): {skipped}")
    print(f"Errors: {errors}")
    print("="*60)

if __name__ == '__main__':
    migrate_cases()

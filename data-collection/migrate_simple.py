#!/usr/bin/env python3
"""
Simple migration script - without heavy ID/naming generation
"""

import sqlite3
import uuid
from datetime import datetime

def migrate_cases():
    """Migrate all cases from legal_cases to universal_legal_documents"""

    db_path = 'data/indiankanoon.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

            # Skip if already migrated
            cursor.execute(
                "SELECT COUNT(*) FROM universal_legal_documents WHERE source_url = ?",
                (case_url,)
            )
            if cursor.fetchone()[0] > 0:
                skipped += 1
                continue

            # Simple ID generation
            global_id = f"ULEGAL-{str(legacy_id).zfill(10)}"
            doc_uuid = str(uuid.uuid4())

            # Simple classification based on keywords
            title_lower = (title or '').lower()
            snippet_lower = (snippet or '').lower()
            combined = title_lower + ' ' + snippet_lower

            # Basic subject detection
            if any(word in combined for word in ['criminal', 'penal', 'murder', 'theft', 'robbery']):
                subject_primary, subject_code = 'CRIMINAL', 'CRM'
            elif any(word in combined for word in ['civil', 'contract', 'property', 'tort']):
                subject_primary, subject_code = 'CIVIL', 'CIV'
            elif any(word in combined for word in ['constitution', 'fundamental rights', 'writ']):
                subject_primary, subject_code = 'CONSTITUTIONAL', 'CON'
            elif any(word in combined for word in ['tax', 'revenue', 'gst', 'income tax']):
                subject_primary, subject_code = 'TAX', 'TAX'
            elif any(word in combined for word in ['labor', 'labour', 'employment', 'worker']):
                subject_primary, subject_code = 'LABOR', 'LAB'
            else:
                subject_primary, subject_code = 'GENERAL', 'GEN'

            # Court level detection
            if court:
                court_lower = court.lower()
                if 'supreme' in court_lower:
                    court_level = 'SC'
                elif 'high' in court_lower:
                    court_level = 'HC'
                elif 'district' in court_lower or 'sessions' in court_lower:
                    court_level = 'DISTRICT'
                else:
                    court_level = 'MISC'
            else:
                court_level = 'MISC'

            # Extract year
            doc_year = year
            if not doc_year and case_date:
                try:
                    parts = case_date.split()
                    for part in parts:
                        if len(part) == 4 and part.isdigit():
                            doc_year = int(part)
                            break
                except:
                    pass

            # Simple filename
            title_clean = (title[:50] if title else f'Case_{legacy_id}').replace(' ', '_').replace('/', '_')
            filename = f"IN_CASE_{court_level}_{doc_year or 2023}_{title_clean}_{subject_code}_{global_id}.pdf"
            folder_path = f"Legal_Database/IN/CASE/{court_level}/"

            # Insert into universal table
            cursor.execute("""
                INSERT INTO universal_legal_documents (
                    global_id, uuid,
                    country_code, country_name,
                    doc_category, doc_year,
                    title_full, title_short,
                    subject_primary, subject_code,
                    court_level, court_name, citation_primary,
                    legal_status, date_enacted,
                    plain_text, summary,
                    pdf_url, pdf_path, pdf_downloaded,
                    source_url, source_domain,
                    scraper_name, scrape_timestamp,
                    filename_universal, file_path_relative,
                    created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                global_id, doc_uuid,
                'IN', 'India',
                'CASE', doc_year,
                title, (title[:100] if title else None),
                subject_primary, subject_code,
                court_level, court, citation,
                'ACTIVE', case_date,
                full_text, snippet,
                pdf_link, pdf_path, pdf_downloaded,
                case_url, 'indiankanoon.org',
                'indiankanoon_scraper', scraped_at,
                filename, folder_path,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))

            migrated += 1

            if migrated % 100 == 0:
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

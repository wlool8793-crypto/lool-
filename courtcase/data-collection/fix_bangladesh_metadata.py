#!/usr/bin/env python3
"""
Fix Bangladesh Metadata
Re-parses saved HTML files to fix incorrect titles and years
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sqlite3
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from src.scrapers.bangladesh_scraper import BangladeshLawsScraper
from src.unified_database import UnifiedDatabase

def main():
    print("="*70)
    print("FIXING BANGLADESH METADATA")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Setup
    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': 0,
        'use_selenium': False,
        'pdf_dir': './data/pdfs/bangladesh',
        'html_dir': './data/html/bangladesh'
    }

    db_path = 'data/indiankanoon.db'
    db = UnifiedDatabase(db_path, use_universal=True)
    scraper = BangladeshLawsScraper(config, db)

    # Get all Bangladesh documents with "Related Links" title
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n📋 Finding documents to fix...")
    cursor.execute("""
        SELECT id, global_id, country_doc_id, source_url
        FROM universal_legal_documents
        WHERE country_code='BD'
        AND (title_full LIKE '%Related Links%' OR doc_year IS NULL OR doc_year = 0)
    """)

    docs = cursor.fetchall()
    total = len(docs)
    print(f"✅ Found {total} documents to fix\n")

    # Process each document
    print("="*70)
    print("PROCESSING DOCUMENTS")
    print("="*70)

    start_time = datetime.now()
    fixed = 0
    failed = 0
    skipped = 0

    for idx, doc in enumerate(docs, start=1):
        try:
            doc_id = doc['id']
            global_id = doc['global_id']
            country_doc_id = doc['country_doc_id']

            # Find corresponding HTML file
            html_file = Path(f"data/html/bangladesh/bangladesh_{country_doc_id}.html")

            if not html_file.exists():
                print(f"[{idx}/{total}] ⏭️  {global_id} - HTML file not found")
                skipped += 1
                continue

            # Read and parse HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'lxml')

            # Extract correct title and year
            title = scraper._extract_title(soup)
            year = scraper._extract_year(soup, title) if title else None

            if not title or title == "Related Links":
                print(f"[{idx}/{total}] ❌ {global_id} - Failed to extract title")
                failed += 1
                continue

            # Update database
            cursor.execute("""
                UPDATE universal_legal_documents
                SET title_full = ?,
                    doc_year = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (title, year, doc_id))

            conn.commit()

            print(f"[{idx}/{total}] ✅ {global_id}")
            print(f"   Title: {title[:60]}")
            print(f"   Year:  {year}")

            fixed += 1

            # Progress report every 100
            if fixed % 100 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = fixed / elapsed if elapsed > 0 else 0
                print(f"\n  📊 Progress: {fixed} fixed, {skipped} skipped, {failed} failed")
                print(f"  ⚡ Rate: {rate:.2f} docs/second\n")

        except Exception as e:
            print(f"[{idx}/{total}] ❌ {global_id} - Error: {e}")
            failed += 1
            continue

    # Final statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*70)
    print("FIXING COMPLETE")
    print("="*70)
    print(f"Total documents processed: {total}")
    print(f"Successfully fixed: {fixed}")
    print(f"Skipped (no HTML): {skipped}")
    print(f"Failed: {failed}")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    if fixed > 0:
        print(f"Average rate: {fixed/duration:.2f} docs/second")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Verify results
    print("\n📊 VERIFICATION")
    print("="*70)

    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN title_full LIKE '%Related Links%' THEN 1 END) as bad_titles,
               COUNT(CASE WHEN doc_year IS NOT NULL AND doc_year > 1700 THEN 1 END) as has_year
        FROM universal_legal_documents
        WHERE country_code='BD'
    """)

    stats = cursor.fetchone()
    print(f"Total Bangladesh documents: {stats['total']}")
    print(f"Still have 'Related Links': {stats['bad_titles']}")
    print(f"Documents with valid year: {stats['has_year']}")

    if stats['bad_titles'] == 0:
        print("\n🎉 ALL DOCUMENTS FIXED SUCCESSFULLY!")
    elif stats['bad_titles'] < 50:
        print(f"\n✅ Almost done! Only {stats['bad_titles']} remaining.")
    else:
        print(f"\n⚠️  Still have {stats['bad_titles']} documents to fix")

    conn.close()

if __name__ == '__main__':
    main()

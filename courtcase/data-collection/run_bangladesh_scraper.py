#!/usr/bin/env python3
"""
Bangladesh Laws Scraper Runner
Scrapes all laws from http://bdlaws.minlaw.gov.bd/

Usage:
    python run_bangladesh_scraper.py
    python run_bangladesh_scraper.py --limit 100
    python run_bangladesh_scraper.py --start-from 50
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.scrapers.bangladesh_scraper import BangladeshLawsScraper
from src.unified_database import UnifiedDatabase
from src.naming.id_generator import IDGenerator
from src.taxonomy.subjects import SubjectClassifier


def main():
    parser = argparse.ArgumentParser(description='Scrape Bangladesh Laws from bdlaws.minlaw.gov.bd')

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of laws to scrape (default: all)'
    )

    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Start from index (for resuming, default: 0)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - only scrape first 5 documents'
    )

    args = parser.parse_args()

    # Test mode
    if args.test:
        args.limit = 5
        args.start_from = 0

    print("="*70)
    print("BANGLADESH LAWS SCRAPER")
    print("="*70)
    print(f"Source: http://bdlaws.minlaw.gov.bd/")
    print(f"Target Database: universal_legal_documents")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Configuration
    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': 2,  # 2 seconds between requests
        'use_selenium': False,  # Use requests for speed
        'headless': True,
        'download_pdfs': True,
        'pdf_dir': './data/pdfs/bangladesh',
        'html_dir': './data/html/bangladesh',
        'indexes': {
            'chronological': '/laws-of-bangladesh-chronological-index.html',
            'alphabetical': '/laws-of-bangladesh-alphabetical-index.html'
        }
    }

    # Initialize database with universal schema
    db_path = 'data/indiankanoon.db'
    print(f"\n📊 Connecting to database: {db_path}")
    db = UnifiedDatabase(db_path, use_universal=True)

    # Initialize scraper
    print("🚀 Initializing Bangladesh scraper...")
    scraper = BangladeshLawsScraper(config, db)

    # Initialize helpers for universal schema
    id_gen = IDGenerator(db_path)
    classifier = SubjectClassifier()

    # Get list of all law URLs
    print("\n" + "="*70)
    print("PHASE 1: DISCOVERING DOCUMENTS")
    print("="*70)

    print("📋 Fetching document list from indexes...")
    all_urls = scraper.get_document_list()

    print(f"\n✅ Found {len(all_urls)} total laws")

    # Apply start and limit
    if args.start_from > 0:
        all_urls = all_urls[args.start_from:]
        print(f"⏩ Starting from index {args.start_from}")

    if args.limit:
        all_urls = all_urls[:args.limit]
        print(f"🔢 Limiting to {args.limit} documents")

    print(f"📝 Will scrape {len(all_urls)} documents")

    # Scrape each document
    print("\n" + "="*70)
    print("PHASE 2: SCRAPING DOCUMENTS")
    print("="*70)

    start_time = datetime.now()
    scraped = 0
    saved = 0
    skipped = 0
    errors = 0

    for idx, url in enumerate(all_urls, start=1):
        try:
            print(f"\n[{idx}/{len(all_urls)}] Scraping: {url}")

            # Check if already exists
            cursor = db.conn.cursor()
            existing = cursor.execute(
                "SELECT COUNT(*) FROM universal_legal_documents WHERE source_url = ?",
                (url,)
            ).fetchone()

            if existing and existing[0] > 0:
                print(f"  ⏭️  Already in database, skipping...")
                skipped += 1
                continue

            # Parse document
            doc_data = scraper.parse_document(url)

            if not doc_data:
                print(f"  ❌ Failed to parse document")
                errors += 1
                continue

            print(f"  📄 Title: {doc_data.get('title', 'Unknown')[:60]}...")

            # Convert to universal schema format
            universal_doc = convert_to_universal_schema(
                doc_data,
                id_gen,
                classifier
            )

            # Save to database
            db.save_universal_document(universal_doc)

            scraped += 1
            saved += 1

            print(f"  ✅ Saved as {universal_doc.get('global_id')}")

            # Progress report every 10 documents
            if scraped % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = scraped / elapsed if elapsed > 0 else 0
                print(f"\n  📊 Progress: {scraped} scraped, {saved} saved, {skipped} skipped, {errors} errors")
                print(f"  ⚡ Rate: {rate:.2f} docs/second")

        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping interrupted by user")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
            continue

    # Final statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*70)
    print("SCRAPING COMPLETE")
    print("="*70)
    print(f"Total URLs found: {len(all_urls)}")
    print(f"Successfully scraped: {scraped}")
    print(f"Saved to database: {saved}")
    print(f"Skipped (already exists): {skipped}")
    print(f"Errors: {errors}")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    if scraped > 0:
        print(f"Average rate: {scraped/duration:.2f} docs/second")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Show sample results
    print("\n📋 Sample results in database:")
    cursor = db.conn.cursor()
    sample = cursor.execute("""
        SELECT global_id, title_full, doc_year, subject_primary
        FROM universal_legal_documents
        WHERE country_code = 'BD'
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()

    for row in sample:
        print(f"  {row[0]} | {row[1][:50]}... | {row[2]} | {row[3]}")


def convert_to_universal_schema(doc_data: dict, id_gen, classifier) -> dict:
    """
    Convert Bangladesh scraper format to universal schema format

    Args:
        doc_data: Document data from Bangladesh scraper
        id_gen: ID generator for global IDs
        classifier: Subject classifier

    Returns:
        Dictionary in universal schema format
    """
    # Generate global ID
    numeric_id, global_id = id_gen.generate_global_id()

    # Classify subject
    text_for_classification = f"{doc_data.get('title', '')} {doc_data.get('summary', '')}"
    try:
        primary_subject, subcategory, subject_code = classifier.classify(
            title=text_for_classification,
            content=doc_data.get('plain_text', '')[:1000],
            doc_type='ACT',
            country_code='BD'
        )
    except:
        # Default classification
        primary_subject = 'GENERAL'
        subcategory = 'MISC'
        subject_code = 'GEN'

    # Determine jurisdiction level
    jurisdiction_level = 'CENTRAL'
    if doc_data.get('year'):
        year = doc_data['year']
        if year < 1947:
            jurisdiction_level = 'COLONIAL'
        elif 1947 <= year < 1971:
            jurisdiction_level = 'PAKISTAN'
        else:
            jurisdiction_level = 'CENTRAL'

    # Get yearly sequence
    doc_year = doc_data.get('year')
    if doc_year:
        yearly_seq = id_gen.get_next_yearly_sequence('BD', 'ACT', doc_year)
    else:
        yearly_seq = None

    # Build universal document
    universal_doc = {
        # IDs
        'global_id': global_id,
        'uuid': str(__import__('uuid').uuid4()),

        # Country & Jurisdiction
        'country_code': 'BD',
        'country_name': 'Bangladesh',
        'jurisdiction_level': jurisdiction_level,

        # Document Classification
        'doc_category': 'ACT',
        'doc_type': doc_data.get('doc_type', 'Act'),
        'doc_year': doc_year,
        'yearly_sequence': yearly_seq,
        'country_doc_id': doc_data.get('country_doc_id'),

        # Titles
        'title_full': doc_data.get('title'),
        'title_short': doc_data.get('title', '')[:100] if doc_data.get('title') else None,

        # Subject Classification
        'subject_primary': primary_subject,
        'subject_secondary': subcategory,
        'subject_code': subject_code,

        # Authority
        'issuing_authority': doc_data.get('court_or_ministry'),

        # Citation
        'citation_primary': doc_data.get('citation'),

        # Legal Status
        'legal_status': doc_data.get('status', 'ACTIVE').upper(),

        # Content
        'html_content': doc_data.get('html_content'),
        'plain_text': doc_data.get('plain_text'),
        'summary': doc_data.get('summary'),

        # PDF
        'pdf_url': doc_data.get('pdf_url'),

        # Source
        'source_url': doc_data.get('source_url'),
        'source_domain': 'bdlaws.minlaw.gov.bd',
        'source_index': doc_data.get('source_index'),

        # Scraping metadata
        'scraper_name': 'bangladesh_laws_scraper',
        'scrape_timestamp': datetime.now().isoformat(),
    }

    return universal_doc


if __name__ == '__main__':
    main()

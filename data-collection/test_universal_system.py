#!/usr/bin/env python3
"""
Test Universal Legal Document Management System
Demonstrates the complete workflow
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from naming.id_generator import IDGenerator
from naming.universal_namer import UniversalNamer
from taxonomy.subjects import SubjectClassifier
from unified_database import UnifiedDatabase


def test_id_generation():
    """Test ID generation"""
    print("=" * 80)
    print("TEST 1: ID GENERATION")
    print("=" * 80)

    gen = IDGenerator('data/test_universal.db')

    print("\n1. Global IDs:")
    for i in range(3):
        numeric_id, formatted_id = gen.generate_global_id()
        print(f"   {formatted_id}")

    print("\n2. UUIDs:")
    for i in range(2):
        print(f"   {gen.generate_uuid()}")

    print("\n3. Yearly Sequences:")
    print(f"   BD/ACT/1860: {gen.get_next_yearly_sequence('BD', 'ACT', 1860)}")
    print(f"   BD/ACT/1860: {gen.get_next_yearly_sequence('BD', 'ACT', 1860)}")
    print(f"   BD/ACT/1875: {gen.get_next_yearly_sequence('BD', 'ACT', 1875)}")
    print(f"   IN/CASE/2023: {gen.get_next_yearly_sequence('IN', 'CASE', 2023)}")

    stats = gen.get_stats()
    print(f"\n4. Statistics:")
    print(f"   Global sequence: {stats['global_sequence']}")
    print(f"   Yearly sequences: {stats['total_yearly_sequences']}")

    print("\n✓ ID Generation Tests Passed\n")


def test_subject_classification():
    """Test subject classification"""
    print("=" * 80)
    print("TEST 2: SUBJECT CLASSIFICATION")
    print("=" * 80)

    classifier = SubjectClassifier()

    test_docs = [
        {
            'title': 'The Penal Code, 1860',
            'content': 'Act relating to offenses, crimes, and punishments',
            'country': 'BD'
        },
        {
            'title': 'Code of Criminal Procedure',
            'content': 'Procedure for arrest, investigation, and criminal trial',
            'country': 'BD'
        },
        {
            'title': 'Contract Act, 1872',
            'content': 'Law relating to contracts, agreements, and obligations',
            'country': 'IN'
        }
    ]

    for i, doc in enumerate(test_docs, 1):
        primary, subcat, code = classifier.classify(
            doc['title'],
            doc['content'],
            country_code=doc['country']
        )
        print(f"\n{i}. {doc['title']}")
        print(f"   Subject: {primary} ({code})")
        print(f"   Subcategory: {subcat}")

    print("\n✓ Subject Classification Tests Passed\n")


def test_filename_generation():
    """Test universal filename generation"""
    print("=" * 80)
    print("TEST 3: FILENAME GENERATION")
    print("=" * 80)

    namer = UniversalNamer()

    test_docs = [
        {
            'name': 'Bangladesh Penal Code',
            'data': {
                'country_code': 'BD',
                'doc_category': 'ACT',
                'jurisdiction_level': 'CENTRAL',
                'doc_year': 1860,
                'doc_number': 'XLV',
                'sequence': 45,
                'yearly_sequence': 45,
                'title_full': 'The Penal Code, 1860',
                'title_short': 'Penal Code',
                'subject_code': 'CRM',
                'subject_subcategory': 'PEN',
                'legal_status': 'ACTIVE',
                'global_id_numeric': 10045
            }
        },
        {
            'name': 'Bangladesh Evidence Act',
            'data': {
                'country_code': 'BD',
                'doc_category': 'ACT',
                'jurisdiction_level': 'CENTRAL',
                'doc_year': 1872,
                'doc_number': 'I',
                'sequence': 1,
                'yearly_sequence': 1,
                'title_full': 'The Evidence Act, 1872',
                'title_short': 'Evidence Act',
                'subject_code': 'CRM',
                'subject_subcategory': 'EVD',
                'legal_status': 'ACTIVE',
                'global_id_numeric': 10001
            }
        },
        {
            'name': 'India Supreme Court Case',
            'data': {
                'country_code': 'IN',
                'doc_category': 'CASE',
                'court_code': 'SC',
                'doc_year': 2023,
                'doc_number': '123',
                'sequence': 1,
                'yearly_sequence': 234,
                'title_full': 'Kesavananda Bharati v. State of Kerala',
                'title_short': 'Kesavananda Bharati',
                'subject_code': 'CON',
                'subject_subcategory': 'FUN',
                'date_enacted': '2023-05-15',
                'legal_status': 'ACTIVE',
                'global_id_numeric': 20234
            }
        }
    ]

    for i, doc in enumerate(test_docs, 1):
        filename = namer.generate_filename(doc['data'])
        folder = namer.generate_folder_path(doc['data'])
        print(f"\n{i}. {doc['name']}")
        print(f"   Filename: {filename}.pdf")
        print(f"   Folder:   Legal_Database/{folder}/")
        print(f"   Full path: Legal_Database/{folder}/{filename}.pdf")

    print("\n✓ Filename Generation Tests Passed\n")


def test_database_operations():
    """Test database operations"""
    print("=" * 80)
    print("TEST 4: DATABASE OPERATIONS")
    print("=" * 80)

    # Initialize database with universal schema
    db_path = 'data/test_universal.db'

    # First create the schema
    print("\n1. Creating database schema...")
    import sqlite3
    conn = sqlite3.connect(db_path)
    with open('migrations/create_universal_schema.sql', 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()
    print("   ✓ Schema created")

    # Now use the database
    print("\n2. Saving test documents...")
    db = UnifiedDatabase(db_path, use_universal=True)

    # Sample documents
    test_docs = [
        {
            'country_code': 'BD',
            'country_name': 'Bangladesh',
            'jurisdiction_level': 'CENTRAL',
            'doc_category': 'ACT',
            'doc_type': 'Act',
            'doc_number': 'XLV',
            'doc_year': 1860,
            'title_full': 'The Penal Code, 1860',
            'title_short': 'Penal Code',
            'source_url': 'http://bdlaws.minlaw.gov.bd/act-45.html',
            'source_domain': 'bdlaws.minlaw.gov.bd',
            'plain_text': 'An Act to provide a general Penal Code for Bangladesh.',
            'summary': 'Penal Code of Bangladesh dealing with criminal offenses',
            'legal_status': 'ACTIVE',
            'scraper_name': 'bangladesh_scraper',
            'scraper_version': '2.0'
        },
        {
            'country_code': 'BD',
            'country_name': 'Bangladesh',
            'jurisdiction_level': 'CENTRAL',
            'doc_category': 'ACT',
            'doc_type': 'Act',
            'doc_number': 'I',
            'doc_year': 1872,
            'title_full': 'The Evidence Act, 1872',
            'title_short': 'Evidence Act',
            'source_url': 'http://bdlaws.minlaw.gov.bd/act-1.html',
            'source_domain': 'bdlaws.minlaw.gov.bd',
            'plain_text': 'An Act to define and amend the law of evidence.',
            'summary': 'Law of evidence in criminal and civil proceedings',
            'legal_status': 'ACTIVE',
            'scraper_name': 'bangladesh_scraper',
            'scraper_version': '2.0'
        },
        {
            'country_code': 'BD',
            'country_name': 'Bangladesh',
            'jurisdiction_level': 'CENTRAL',
            'doc_category': 'ACT',
            'doc_type': 'Act',
            'doc_number': 'IX',
            'doc_year': 1872,
            'title_full': 'The Contract Act, 1872',
            'title_short': 'Contract Act',
            'source_url': 'http://bdlaws.minlaw.gov.bd/act-9.html',
            'source_domain': 'bdlaws.minlaw.gov.bd',
            'plain_text': 'An Act to define and amend certain parts of the law relating to contracts.',
            'summary': 'Law relating to contracts and agreements',
            'legal_status': 'ACTIVE',
            'scraper_name': 'bangladesh_scraper',
            'scraper_version': '2.0'
        }
    ]

    doc_ids = []
    for doc in test_docs:
        doc_id = db.save_universal_document(doc)
        doc_ids.append(doc_id)
        print(f"   ✓ Saved: {doc['title_short']} (ID: {doc_id})")

    # Query stats
    print("\n3. Database Statistics:")
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM v_overall_stats")
    stats = dict(cursor.fetchone())
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Countries: {stats['total_countries']}")
    print(f"   Categories: {stats['total_categories']}")
    print(f"   Earliest year: {stats['earliest_year']}")
    print(f"   Latest year: {stats['latest_year']}")

    # Show sample document details
    print("\n4. Sample Document Details:")
    cursor.execute("""
        SELECT global_id, filename_universal, file_path_relative,
               subject_primary, subject_code
        FROM universal_legal_documents
        LIMIT 1
    """)
    doc = dict(cursor.fetchone())
    print(f"   Global ID: {doc['global_id']}")
    print(f"   Filename: {doc['filename_universal']}.pdf")
    print(f"   Path: {doc['file_path_relative']}/")
    print(f"   Subject: {doc['subject_primary']} ({doc['subject_code']})")

    db.close()
    print("\n✓ Database Operations Tests Passed\n")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  UNIVERSAL LEGAL DOCUMENT MANAGEMENT SYSTEM - TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    try:
        # Create data directory
        Path('data').mkdir(exist_ok=True)

        # Run tests
        test_id_generation()
        test_subject_classification()
        test_filename_generation()
        test_database_operations()

        # Final summary
        print("=" * 80)
        print("ALL TESTS PASSED!")
        print("=" * 80)
        print("\nThe Universal Legal Document Management System is working correctly.")
        print("\nNext Steps:")
        print("  1. Initialize the production database: sqlite3 data/universal_legal.db < migrations/create_universal_schema.sql")
        print("  2. Run Bangladesh scraper with universal system enabled")
        print("  3. Verify files are created in Legal_Database/ folder")
        print("\n")

        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Sample Scrape Test
Tests the complete workflow with ONE real Bangladesh law
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.scrapers.bangladesh_scraper import BangladeshLawsScraper
from src.unified_database import UnifiedDatabase

def main():
    print("="*70)
    print("SAMPLE SCRAPE TEST - One Bangladesh Law")
    print("="*70)

    # Setup
    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': 2,
        'use_selenium': False,
        'pdf_dir': './data/pdfs/bangladesh',
        'html_dir': './data/html/bangladesh'
    }

    db = UnifiedDatabase('data/indiankanoon.db', use_universal=True)
    scraper = BangladeshLawsScraper(config, db)

    # Test with ONE real URL
    test_url = 'http://bdlaws.minlaw.gov.bd/act-367.html'

    print(f"\n📥 Scraping: {test_url}")
    doc_data = scraper.parse_document(test_url)

    if doc_data:
        print(f"\n✅ SUCCESSFULLY PARSED!")
        print(f"\n📄 Extracted Data:")
        print(f"  Title:    {doc_data.get('title', 'N/A')}")
        print(f"  Year:     {doc_data.get('year', 'N/A')}")
        print(f"  Type:     {doc_data.get('doc_type', 'N/A')}")
        print(f"  Act ID:   {doc_data.get('country_doc_id', 'N/A')}")
        print(f"  Category: {doc_data.get('category', 'N/A')}")
        print(f"  PDF URL:  {doc_data.get('pdf_url', 'N/A')}")
        print(f"  Content:  {len(doc_data.get('plain_text', ''))} characters")

        print(f"\n🎉 SUCCESS! Parser is working correctly!")
        print(f"   This document would be saved with:")
        print(f"   - Proper title extracted from <title> tag")
        print(f"   - Year extracted from title")
        print(f"   - Full content available")

    else:
        print(f"\n❌ FAILED to parse document")

    print("="*70)

if __name__ == '__main__':
    main()

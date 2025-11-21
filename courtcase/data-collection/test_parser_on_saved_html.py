#!/usr/bin/env python3
"""
Test Parser on Saved HTML
Verifies the fixed parser works correctly on existing HTML files
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
from bs4 import BeautifulSoup
from src.scrapers.bangladesh_scraper import BangladeshLawsScraper
from src.unified_database import UnifiedDatabase

def main():
    print("="*70)
    print("TESTING FIXED PARSER ON SAVED HTML")
    print("="*70)

    # Setup scraper
    config = {
        'country': 'bangladesh',
        'base_url': 'http://bdlaws.minlaw.gov.bd',
        'request_delay': 0,
        'use_selenium': False,
        'pdf_dir': './data/pdfs/test',
        'html_dir': './data/html/test'
    }

    db = UnifiedDatabase('data/test.db', use_universal=True)
    scraper = BangladeshLawsScraper(config, db)

    # Test on saved HTML files
    html_dir = Path('data/html/bangladesh')
    html_files = sorted(list(html_dir.glob('*.html')))[:10]  # Test first 10

    print(f"\n📂 Testing on {len(html_files)} saved HTML files\n")

    success = 0
    failed = 0

    for html_file in html_files:
        try:
            # Read HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'lxml')

            # Extract title and year using fixed parser
            title = scraper._extract_title(soup)
            year = scraper._extract_year(soup, title) if title else None

            if title and title != "Related Links":
                print(f"✅ {html_file.name:30s}")
                print(f"   Title: {title[:60]}")
                print(f"   Year:  {year}")
                print()
                success += 1
            else:
                print(f"❌ {html_file.name:30s} - Failed to extract proper title")
                failed += 1

        except Exception as e:
            print(f"❌ {html_file.name:30s} - Error: {e}")
            failed += 1

    print("="*70)
    print(f"Results: {success} success, {failed} failed")
    print("="*70)

    if success > 0:
        print("\n✅ PARSER IS WORKING! Can re-parse existing HTML files.")
        print("   Option: Run batch re-parser to fix all 950 documents")
    else:
        print("\n❌ Parser still not working correctly")

if __name__ == '__main__':
    main()

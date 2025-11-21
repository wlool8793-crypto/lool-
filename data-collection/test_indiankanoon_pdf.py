"""
Comprehensive test script for IndianKanoon PDF download functionality
Tests the new download_indiankanoon_pdf method with real cases
"""

import os
from pathlib import Path
from src.database import CaseDatabase, LegalCase
from src.scraper import IndianKanoonScraper

def test_pdf_download():
    """Test PDF download with real IndianKanoon cases"""

    print("=" * 70)
    print("IndianKanoon PDF Download Test")
    print("=" * 70)
    print()

    # Initialize database and scraper
    db = CaseDatabase('sqlite:///data/indiankanoon.db')
    scraper = IndianKanoonScraper(delay=2)

    # Get a few cases from database
    cases = db.session.query(LegalCase).limit(5).all()

    print(f"Testing PDF download for {len(cases)} cases...\n")

    pdf_dir = Path('./data/pdfs')
    pdf_dir.mkdir(parents=True, exist_ok=True)

    successful_downloads = 0
    failed_downloads = 0

    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/{len(cases)}] Testing Case ID: {case.id}")
        print(f"Title: {case.title[:70]}...")
        print(f"URL: {case.case_url}")

        # First, fetch case details to get PDF link
        if not case.pdf_link or case.pdf_link == '':
            print("  → Fetching case details to get PDF link...")
            details = scraper.get_case_details(case.case_url)

            if details and details.get('pdf_link'):
                case.pdf_link = details['pdf_link']
                case.full_text = details.get('full_text', case.full_text)
                db.session.commit()
                print(f"  ✓ PDF link found: {case.pdf_link[:60]}...")
            else:
                print(f"  ✗ No PDF link found")
                failed_downloads += 1
                continue

        # Download PDF
        filename = f"case_{case.id}.pdf"
        filepath = pdf_dir / filename

        print(f"  → Downloading PDF to: {filepath}")
        success = scraper.download_indiankanoon_pdf(case.pdf_link, str(filepath))

        if success and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ PDF downloaded successfully!")
            print(f"    File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

            # Update database
            db.update_pdf_status(case.id, str(filepath))
            print(f"  ✓ Database updated")
            successful_downloads += 1

            # Verify it's a valid PDF
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print(f"  ✓ Valid PDF file confirmed")
                else:
                    print(f"  ⚠ Warning: File may not be a valid PDF")
        else:
            print(f"  ✗ PDF download failed")
            failed_downloads += 1

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total cases tested: {len(cases)}")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {failed_downloads}")
    print(f"Success rate: {(successful_downloads/len(cases)*100):.1f}%")

    # Show database statistics
    stats = db.get_statistics()
    print("\n" + "=" * 70)
    print("DATABASE STATISTICS")
    print("=" * 70)
    print(f"Total cases in database: {stats['total_cases']}")
    print(f"Cases with PDFs downloaded: {stats['cases_with_pdfs']}")
    print(f"Cases without PDFs: {stats['cases_without_pdfs']}")

    # List downloaded files
    print("\n" + "=" * 70)
    print("DOWNLOADED PDF FILES")
    print("=" * 70)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    for pdf_file in sorted(pdf_files):
        size = os.path.getsize(pdf_file)
        print(f"{pdf_file.name:<30} {size:>10,} bytes ({size/1024:.2f} KB)")

    print("\n" + "=" * 70)

    db.close()
    scraper.close_driver()

    return successful_downloads > 0


if __name__ == "__main__":
    success = test_pdf_download()
    exit(0 if success else 1)

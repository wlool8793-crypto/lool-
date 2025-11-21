"""Test script to verify PDF download functionality"""
from src.database import CaseDatabase, LegalCase
from pathlib import Path
import os

db = CaseDatabase('sqlite:///data/indiankanoon.db')

# For testing, let's manually add a test PDF URL to a case
# We'll use a publicly available test PDF
test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

# Get the first case and add a test PDF link
case = db.session.query(LegalCase).first()
if case:
    print(f"Adding test PDF link to case: {case.title[:60]}")
    case.pdf_link = test_pdf_url
    db.session.commit()
    print(f"PDF link added: {case.pdf_link}")
    print(f"Case ID: {case.id}")

    # Now let's test the download
    from src.scraper import IndianKanoonScraper

    pdf_dir = Path('./data/pdfs')
    pdf_dir.mkdir(parents=True, exist_ok=True)

    scraper = IndianKanoonScraper(delay=1)

    filename = f"test_case_{case.id}.pdf"
    filepath = pdf_dir / filename

    print(f"\nAttempting to download PDF to: {filepath}")
    success = scraper.download_pdf(test_pdf_url, str(filepath))

    if success:
        print(f"✓ PDF downloaded successfully!")
        print(f"File size: {os.path.getsize(filepath)} bytes")

        # Update database
        db.update_pdf_status(case.id, str(filepath))
        print(f"✓ Database updated with PDF path")
    else:
        print(f"✗ PDF download failed")
else:
    print("No cases found in database")

db.close()

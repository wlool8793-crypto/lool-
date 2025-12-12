#!/usr/bin/env python3
"""
Example usage of Legal RAG Extraction System - Phase 3
Demonstrates basic extraction, batch processing, and integration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors import (
    extract_document,
    ExtractionPipeline,
    CitationExtractor,
    SubjectClassifier,
    QualityAnalyzer,
    apply_naming_conventions,
    generate_filename
)
from extractors.pipeline import extract_batch, get_metrics_summary


def example_1_basic_extraction():
    """Example 1: Basic document extraction"""
    print("=" * 60)
    print("Example 1: Basic Document Extraction")
    print("=" * 60)

    # Extract from PDF (replace with actual PDF path)
    pdf_path = 'sample_case.pdf'

    print(f"\nExtracting from: {pdf_path}")

    try:
        result = extract_document(pdf_path)

        # Display extracted data
        print(f"\n✓ Extraction successful!")
        print(f"  Document ID: {result.get('document_id')}")
        print(f"  Title: {result.get('title')}")
        print(f"  Year: {result.get('year')}")
        print(f"  Citations found: {len(result.get('citations', []))}")
        print(f"  Judges: {len(result.get('judges', []))}")
        print(f"  Quality score: {result.get('quality_analysis', {}).get('overall_score', 0):.2%}")

        # Show first citation
        citations = result.get('citations', [])
        if citations:
            print(f"\n  First citation:")
            print(f"    Text: {citations[0]['citation_text']}")
            print(f"    Encoded: {citations[0]['citation_encoded']}")
            print(f"    Confidence: {citations[0]['confidence']:.2%}")

    except FileNotFoundError:
        print(f"✗ File not found: {pdf_path}")
        print("  (This is a demo - replace with actual PDF path)")

    except Exception as e:
        print(f"✗ Extraction failed: {e}")


def example_2_with_progress():
    """Example 2: Extraction with progress tracking"""
    print("\n" + "=" * 60)
    print("Example 2: Extraction with Progress Tracking")
    print("=" * 60)

    def progress_callback(stage, progress):
        """Display progress"""
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r  [{bar}] {progress:3.0f}% - {stage}", end='', flush=True)

    print("\nExtracting with progress tracking...")

    try:
        pipeline = ExtractionPipeline()
        result = pipeline.extract_from_pdf(
            'sample_case.pdf',
            progress_callback=progress_callback
        )

        print("\n✓ Complete!")

    except FileNotFoundError:
        print("\n✗ File not found (demo example)")

    except Exception as e:
        print(f"\n✗ Failed: {e}")


def example_3_individual_extractors():
    """Example 3: Using individual extractors"""
    print("\n" + "=" * 60)
    print("Example 3: Using Individual Extractors")
    print("=" * 60)

    sample_text = """
    BANGLADESH SUPREME COURT
    HIGH COURT DIVISION

    Md. Rahman vs. State of Bangladesh
    22 (1998) DLR (HCD) 205

    BEFORE: Hon'ble Mr. Justice A.B.M. Khairul Haque, J

    Date of Judgment: 15th January, 1998

    This case involves Section 302 of the Penal Code, 1860.
    The petitioner was convicted of murder and sentenced to life imprisonment.
    """

    print("\nSample text:")
    print(sample_text[:200] + "...")

    # Citation extraction
    print("\n1. Citation Extraction:")
    citation_extractor = CitationExtractor()
    citation_result = citation_extractor.extract(sample_text)

    for citation in citation_result['data']['citations']:
        print(f"   Found: {citation['citation_text']}")
        print(f"   Encoded: {citation['citation_encoded']}")

    # Subject classification
    print("\n2. Subject Classification:")
    classifier = SubjectClassifier()
    subject_result = classifier.extract(sample_text)

    subject = subject_result['data']
    print(f"   Primary: {subject['primary_subject']} - {subject['primary_subject_name']}")
    print(f"   Confidence: {subject['primary_confidence']:.2%}")

    # Quality analysis (on mock extraction result)
    print("\n3. Quality Analysis:")
    mock_result = {
        'title': 'Md. Rahman vs. State',
        'citations': citation_result['data']['citations'],
        'parties': {'petitioner': ['Md. Rahman'], 'respondent': ['State of Bangladesh']},
        'judges': [{'name': 'A.B.M. Khairul Haque', 'is_presiding': True}],
        'dates': {'judgment_date': '1998-01-15'},
        'year': 1998,
        'full_text': sample_text,
        'sections_cited': [{'section_number': '302', 'act_name': 'Penal Code, 1860'}],
        'keywords': ['murder', 'conviction', 'imprisonment'],
        'subject_classification': subject
    }

    analyzer = QualityAnalyzer()
    quality_result = analyzer.extract(mock_result)

    quality = quality_result['data']
    print(f"   Overall score: {quality['overall_score']:.2%}")
    print(f"   Grade: {quality['quality_grade']}")
    print(f"   Validation: {quality['validation_status']}")


def example_4_batch_processing():
    """Example 4: Batch processing multiple files"""
    print("\n" + "=" * 60)
    print("Example 4: Batch Processing")
    print("=" * 60)

    # Mock file list (replace with actual files)
    pdf_files = [
        'case1.pdf',
        'case2.pdf',
        'case3.pdf'
    ]

    print(f"\nProcessing {len(pdf_files)} files...")

    def batch_progress(current, total, document_id):
        print(f"  [{current}/{total}] Processing: {document_id}")

    try:
        results = extract_batch(pdf_files, progress_callback=batch_progress)

        successful = sum(1 for r in results if r.get('status') != 'failed')
        print(f"\n✓ Batch complete: {successful}/{len(results)} successful")

        # Show metrics
        print("\nMetrics:")
        print(get_metrics_summary())

    except Exception as e:
        print(f"✗ Batch failed: {e}")
        print("  (This is a demo - replace with actual PDF paths)")


def example_5_phase1_integration():
    """Example 5: Phase 1 naming convention integration"""
    print("\n" + "=" * 60)
    print("Example 5: Phase 1 Integration (Naming Conventions)")
    print("=" * 60)

    # Mock extraction result
    mock_result = {
        'document_id': 'test_case',
        'title': 'Md. Rahman vs. State of Bangladesh',
        'citations': [{
            'citation_text': '22 (1998) DLR (HCD) 205',
            'citation_encoded': '22DLR98H205',
            'is_primary': True,
            'volume': 22,
            'year': 1998,
            'reporter': 'DLR',
            'court': 'HCD',
            'page': 205,
            'confidence': 0.95
        }],
        'parties': {
            'petitioner': ['Md. Rahman'],
            'respondent': ['State of Bangladesh']
        },
        'year': 1998,
        'full_text': 'Sample case text...',
        'subject_classification': {
            'primary_subject': 'CRM',
            'primary_subject_name': 'Criminal Law'
        }
    }

    print("\nApplying Phase 1 naming conventions...")

    # Apply naming conventions
    result = apply_naming_conventions(mock_result)

    # Generate filename
    filename = generate_filename(result)

    print(f"\n✓ Applied naming conventions")
    print(f"  Citation encoded: {result['citations'][0]['citation_encoded']}")
    print(f"  Content hash: {result.get('text_hash', 'N/A')}")
    print(f"  Suggested filename: {filename}")
    print(f"\nFilename format: {'{CitationEncoded}_{PartyAbbrev}_{ContentHash}.pdf'}")


def example_6_quality_report():
    """Example 6: Detailed quality report"""
    print("\n" + "=" * 60)
    print("Example 6: Quality Analysis Report")
    print("=" * 60)

    from extractors.analysis.quality_analyzer import get_quality_report

    # Mock extraction result with varying quality
    mock_result = {
        'title': 'Complete Case',
        'full_text': 'A' * 5000,  # Sufficient text
        'citations': [{
            'citation_text': '22 DLR 98',
            'citation_encoded': '22DLR98H205',
            'is_primary': True,
            'confidence': 0.85
        }],
        'parties': {
            'petitioner': ['Rahman'],
            'respondent': ['State']
        },
        'judges': [{'name': 'Justice A', 'is_presiding': True}],
        'dates': {
            'judgment_date': '1998-01-15',
            'filing_date': '1997-12-01'
        },
        'year': 1998,
        'sections_cited': [{'section_number': '302', 'act_name': 'Penal Code'}],
        'keywords': ['murder', 'conviction', 'appeal', 'evidence', 'sentence'],
        'subject_classification': {
            'primary_subject': 'CRM',
            'primary_confidence': 0.92
        }
    }

    print("\nGenerating quality report...")

    report = get_quality_report(mock_result)
    print(report)


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  Legal RAG Extraction System - Phase 3 Examples         ║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    examples = [
        example_1_basic_extraction,
        example_2_with_progress,
        example_3_individual_extractors,
        example_4_batch_processing,
        example_5_phase1_integration,
        example_6_quality_report
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example {i} error: {e}")

    print("\n" + "=" * 60)
    print("All examples complete!")
    print("=" * 60)
    print("\nNote: Examples use mock data for demonstration.")
    print("Replace with actual PDF paths for real extraction.")
    print("\nFor more information, see README.md")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()

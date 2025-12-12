# Legal RAG Extraction System - Phase 3

**Complete metadata extraction system for legal documents**

Version: 3.0.0

## Overview

Phase 3 provides comprehensive metadata extraction for legal documents (PDFs and HTML). It extracts citations, parties, judges, dates, statutory sections, keywords, and performs quality analysis.

## Features

### Core Extraction
- **Multi-engine PDF extraction** (pdfplumber, PyPDF2, pdfminer, Tesseract OCR)
- **HTML metadata extraction** (Open Graph, Dublin Core, etc.)
- **Advanced text normalization** (Unicode, ligatures, OCR error correction)

### Legal Metadata
- **Citation extraction** - 11 reporters (DLR, BLD, AIR, SCC, PLD, etc.)
- **Party extraction** - Petitioners, respondents with abbreviation
- **Judge extraction** - Bench composition, presiding judge, authors
- **Date extraction** - Judgment, filing, hearing dates
- **Section extraction** - Statutory references with context

### Analysis
- **Keyword extraction** - TF-IDF with legal term weighting
- **Subject classification** - 16 subject codes (CRM, CIV, CON, etc.)
- **Quality analysis** - 5-dimensional quality scoring

### Integration
- **Phase 1 integration** - Citation encoding, party abbreviation, content hashing
- **Phase 2 integration** - PostgreSQL database storage

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For OCR support
sudo apt-get install tesseract-ocr poppler-utils

# Verify installation
python -c "import extractors; print(extractors.__version__)"
```

## Quick Start

### Basic Extraction

```python
from extractors import extract_document

# Extract from PDF
result = extract_document('case.pdf')

# Access extracted data
print(result['title'])
print(result['citations'])
print(result['parties'])
print(result['quality_analysis']['overall_score'])
```

### With Progress Tracking

```python
from extractors import ExtractionPipeline

def progress_callback(stage, progress):
    print(f"{stage}: {progress:.0f}%")

pipeline = ExtractionPipeline()
result = pipeline.extract_from_pdf(
    'case.pdf',
    progress_callback=progress_callback
)
```

### Batch Processing

```python
from extractors.pipeline import extract_batch

pdf_files = ['case1.pdf', 'case2.pdf', 'case3.pdf']

results = extract_batch(
    pdf_files,
    progress_callback=lambda i, total, doc: print(f"{i}/{total}: {doc}")
)
```

## Architecture

```
src/extractors/
├── core/               # PDF, HTML, text processing
│   ├── pdf_extractor.py
│   ├── html_extractor.py
│   └── text_normalizer.py
│
├── legal/              # Legal metadata extraction
│   ├── citation_extractor.py
│   ├── party_extractor.py
│   ├── judge_extractor.py
│   ├── date_extractor.py
│   └── section_extractor.py
│
├── analysis/           # Keywords, classification, quality
│   ├── keyword_extractor.py
│   ├── subject_classifier.py
│   └── quality_analyzer.py
│
├── pipeline/           # Orchestration and metrics
│   ├── extraction_pipeline.py
│   ├── retry_handler.py
│   └── metrics_collector.py
│
├── integration/        # Phase 1 & 2 integration
│   ├── phase1_integration.py
│   └── phase2_integration.py
│
├── patterns/           # YAML pattern files
│   ├── citations.yaml
│   ├── parties.yaml
│   ├── judges.yaml
│   ├── dates.yaml
│   ├── sections.yaml
│   └── legal_terms.yaml
│
└── config.py          # Configuration
```

## Components

### Core Extractors

#### PDFExtractor
Multi-engine PDF extraction with automatic fallback:
```python
from extractors import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract('case.pdf', enable_ocr=True)

print(result['data']['full_text'])
print(result['data']['page_count'])
print(result['data']['extraction_engine'])  # Which engine succeeded
```

#### HTMLExtractor
Extract metadata from HTML pages:
```python
from extractors import HTMLExtractor

extractor = HTMLExtractor()
result = extractor.extract(html_content, base_url='https://example.com')

print(result['data']['title'])
print(result['data']['pdf_url'])  # Auto-detected PDF link
```

#### TextNormalizer
Clean and normalize text:
```python
from extractors import TextNormalizer

normalizer = TextNormalizer()
result = normalizer.extract(raw_text)

print(result['data']['normalized_text'])
```

### Legal Extractors

#### CitationExtractor
Extract and encode citations:
```python
from extractors import CitationExtractor

extractor = CitationExtractor()
result = extractor.extract(text)

for citation in result['data']['citations']:
    print(f"{citation['citation_text']} → {citation['citation_encoded']}")
    print(f"Confidence: {citation['confidence']:.2%}")
```

Supported reporters:
- Bangladesh: DLR, BLD, BLC, BCR, MLR
- India: AIR, SCC, SCR
- Pakistan: PLD, PLJ, SCMR

#### PartyExtractor
Extract party names:
```python
from extractors import PartyExtractor

extractor = PartyExtractor()
result = extractor.extract(text, title="Md. Rahman v. State")

parties = result['data']
print(f"Petitioners: {parties['petitioner']}")
print(f"Respondents: {parties['respondent']}")
```

#### JudgeExtractor
Extract judge information:
```python
from extractors import JudgeExtractor

extractor = JudgeExtractor()
result = extractor.extract(text)

for judge in result['data']['judges']:
    print(f"{judge['name']}")
    print(f"  Presiding: {judge['is_presiding']}")
    print(f"  Opinion: {judge['opinion_type']}")
```

#### DateExtractor
Extract dates with validation:
```python
from extractors import DateExtractor

extractor = DateExtractor()
result = extractor.extract(text)

dates = result['data']
print(f"Judgment: {dates['judgment_date']}")
print(f"Filing: {dates['filing_date']}")
print(f"Year: {dates['year']}")
```

#### SectionExtractor
Extract statutory references:
```python
from extractors import SectionExtractor

extractor = SectionExtractor()
result = extractor.extract(text)

for section in result['data']['sections']:
    print(f"Section {section['section_number']}")
    print(f"Act: {section['act_name']}")
    print(f"Frequency: {section['frequency']}")
```

### Analysis

#### KeywordExtractor
TF-IDF keyword extraction:
```python
from extractors import KeywordExtractor

extractor = KeywordExtractor()
result = extractor.extract(text, max_keywords=20)

for keyword in result['data']['keywords']:
    print(f"{keyword['keyword']}: {keyword['final_score']:.4f}")
    print(f"  Type: {keyword['keyword_type']}")
    print(f"  Legal term: {keyword['is_legal_term']}")
```

#### SubjectClassifier
Multi-method classification:
```python
from extractors import SubjectClassifier

classifier = SubjectClassifier()
result = classifier.extract(text, method='ensemble')

subject = result['data']
print(f"Primary: {subject['primary_subject']} ({subject['primary_confidence']:.2%})")
print(f"Secondary: {subject['secondary_subjects']}")
```

Subject codes:
- CRM: Criminal Law
- CIV: Civil Law
- CON: Constitutional Law
- FAM: Family Law
- LAB: Labour Law
- TAX: Taxation
- COM: Commercial Law
- And 9 more...

#### QualityAnalyzer
Multi-dimensional quality analysis:
```python
from extractors import QualityAnalyzer

analyzer = QualityAnalyzer()
result = analyzer.extract(extraction_result)

quality = result['data']
print(f"Overall score: {quality['overall_score']:.2%}")
print(f"Grade: {quality['quality_grade']}")
print(f"Status: {quality['validation_status']}")
print(f"Dimensions: {quality['dimension_scores']}")
```

Quality dimensions:
1. Completeness (0-1)
2. Citation quality (0-1)
3. Text quality (0-1)
4. Metadata quality (0-1)
5. Consistency (0-1)

### Pipeline

#### ExtractionPipeline
Orchestrates all extractors:
```python
from extractors import ExtractionPipeline

pipeline = ExtractionPipeline(
    skip_on_error=True,      # Continue on errors
    enable_ocr=True,         # Enable OCR
    enable_quality_check=True,  # Run quality analysis
    min_quality_score=0.60   # Minimum acceptable quality
)

result = pipeline.extract_from_pdf('case.pdf')
```

#### RetryHandler
Advanced retry logic:
```python
from extractors.pipeline import RetryHandler

handler = RetryHandler(
    max_retries=5,
    base_delay=2.0,
    backoff_factor=2.0,
    jitter=True
)

result = handler.retry(
    risky_operation,
    operation_name='pdf_extraction'
)

# Check stats
stats = handler.get_stats()
print(stats)
```

#### MetricsCollector
Track extraction metrics:
```python
from extractors.pipeline import get_global_metrics, get_metrics_summary

# Metrics are collected automatically

# Get summary
print(get_metrics_summary())

# Get complete report
report = get_global_metrics().get_complete_report()
print(report['performance'])
print(report['quality'])
```

### Integration

#### Phase 1 Integration
Apply naming conventions:
```python
from extractors.integration import apply_naming_conventions, generate_filename

# Apply conventions
result = apply_naming_conventions(extraction_result)

# Generate standardized filename
filename = generate_filename(result)
# Example: "22DLR98H205_Rahman_A3F5D8E2.pdf"

print(f"Suggested filename: {filename}")
```

#### Phase 2 Integration
Save to database:
```python
from extractors.integration import save_to_database

# Save single result
save_result = save_to_database(extraction_result, db_connection=db)

if save_result['success']:
    print(f"Saved: case_id={save_result['case_id']}")
```

## Configuration

### Environment Variables

```bash
# Extraction settings
EXTRACTION_MIN_QUALITY_SCORE=0.70
EXTRACTION_MAX_RETRIES=3
EXTRACTION_RETRY_DELAY=1.0
EXTRACTION_RETRY_BACKOFF=2.0

# PDF settings
PDF_MAX_PAGES=1000
PDF_ENABLE_OCR=true

# Caching
ENABLE_CACHING=true
CACHE_TTL=3600
```

### Configuration File

```python
from extractors import config

# Override settings
config.min_quality_score = 0.80
config.max_retries = 5
config.enable_ocr = True
```

## Pattern Files

Pattern files (YAML) define extraction patterns:

### citations.yaml
```yaml
bangladesh:
  DLR:
    pattern: '(\d+)\s*\((\d{4})\)\s*DLR\s*\(([A-Z]{2,})\)\s*(\d+)'
    encoding_format: "{volume}DLR{year_short}{court_code}{page}"
```

### legal_terms.yaml
```yaml
categories:
  criminal_law:
    weight: 1.5
    terms: [murder, theft, assault, robbery, ...]
```

## Error Handling

```python
from extractors import ExtractionError, extract_document

try:
    result = extract_document('case.pdf')

except ExtractionError as e:
    print(f"Extraction failed: {e}")
    print(f"Details: {e.details}")

# Skip errors mode (default)
pipeline = ExtractionPipeline(skip_on_error=True)
result = pipeline.extract_from_pdf('case.pdf')

# Check execution log
for log_entry in result['extraction_metadata']['execution_log']:
    if log_entry['status'] == 'error':
        print(f"Extractor {log_entry['extractor']} failed")
```

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=extractors tests/

# Specific test
pytest tests/test_citation_extractor.py
```

## Performance

### Benchmarks (Intel i7, 16GB RAM)

- **PDF extraction**: 2-5 seconds/document
- **Complete pipeline**: 8-12 seconds/document
- **Throughput**: ~300 documents/hour
- **OCR (when needed)**: +10-20 seconds

### Optimization Tips

1. **Disable OCR** if not needed: `enable_ocr=False`
2. **Batch processing**: Use `extract_batch()` for multiple files
3. **Quality check**: Disable for faster processing: `enable_quality_check=False`
4. **Caching**: Keep enabled for pattern files: `enable_caching=True`

## Troubleshooting

### Common Issues

**1. OCR not working**
```bash
sudo apt-get install tesseract-ocr poppler-utils
pip install pytesseract pdf2image
```

**2. PDF extraction fails**
- Check file is valid PDF
- Try enabling OCR
- Check file size limits

**3. Low quality scores**
- Check text extraction quality
- Verify date formats
- Ensure citations are present

**4. Import errors**
```python
# Check installation
import extractors
print(extractors.__version__)
```

## Examples

See `examples/` directory for complete examples:
- `basic_extraction.py` - Simple extraction
- `batch_processing.py` - Batch extraction
- `custom_pipeline.py` - Custom pipeline configuration
- `database_integration.py` - Phase 2 integration
- `quality_analysis.py` - Quality analysis examples

## API Reference

Complete API documentation available at: [docs/api/README.md](docs/api/README.md)

## Contributing

Phase 3 is part of the Legal RAG system. For contributions:
1. Follow existing code style
2. Add tests for new features
3. Update pattern files as needed
4. Document all public APIs

## License

Part of Legal RAG project - Phase 3 Metadata Extraction

## Support

For issues and questions:
- Check troubleshooting section
- Review examples
- Check execution logs in results

## Version History

### 3.0.0 (Current)
- Complete extraction pipeline
- 11 extractors (core + legal + analysis)
- Phase 1 & 2 integration
- Quality analysis
- OCR support
- Retry logic
- Metrics collection

## Acknowledgments

Built on:
- PyPDF2, pdfplumber, pdfminer.six for PDF extraction
- BeautifulSoup4 for HTML parsing
- scikit-learn for ML classification
- python-dateutil for date parsing
- Tesseract OCR for scanned documents

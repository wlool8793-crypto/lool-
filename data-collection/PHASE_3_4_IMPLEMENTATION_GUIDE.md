# Phase 3 & 4: Production Implementation Guide

## 🎯 Overview

This guide provides the complete implementation roadmap for Phases 3 & 4 with production-grade quality standards.

**Quality Standard**: Production-grade (95%+ accuracy, comprehensive error handling, 80%+ test coverage)
**Total Scope**: 42 tasks, ~12,840 lines of code, 122 hours
**Timeline**: 15-16 working days

---

## ✅ Dependencies Installed

```bash
PyPDF2        # PDF text extraction
pdfplumber    # Advanced PDF parsing
python-dateutil  # Date parsing
scikit-learn  # TF-IDF, ML classification
```

---

## 📁 Directory Structure Created

```
src/extractors/
├── core/          # Core extraction (PDF, HTML, text)
├── legal/         # Legal-specific (citations, parties, judges)
├── analysis/      # Analysis (keywords, subject, quality)
├── pipeline/      # Orchestration and metrics
├── patterns/      # YAML pattern files
└── tests/         # Test suite
```

---

## 🚀 QUICK START: Implementation Order

### Week 1: Core Extraction (Days 1-5)

**Day 1: Infrastructure**
1. Create `config.py` (100 lines)
2. Create `exceptions.py` (80 lines)
3. Create `schemas.py` (200 lines)
4. Create `base_extractor.py` (250 lines)

**Day 2-3: PDF Extraction**
1. Create `core/pdf_extractor.py` (550 lines)
2. Create `core/text_normalizer.py` (200 lines)
3. Test with sample PDFs

**Day 4-5: Legal Extractors**
1. Create `legal/citation_extractor.py` (450 lines)
2. Create `legal/party_extractor.py` (350 lines)
3. Create citation patterns (`patterns/citations.yaml`)

### Week 2: Analysis & Pipeline (Days 6-10)

**Day 6-7: More Legal Extractors**
1. Create `legal/judge_extractor.py` (300 lines)
2. Create `legal/date_extractor.py` (300 lines)
3. Create `legal/section_extractor.py` (350 lines)

**Day 8-9: Analysis**
1. Create `analysis/keyword_extractor.py` (300 lines)
2. Create `analysis/subject_classifier.py` (400 lines)
3. Create `analysis/quality_analyzer.py` (350 lines)

**Day 10: Pipeline**
1. Create `pipeline/extraction_pipeline.py` (400 lines)
2. Create `pipeline/retry_handler.py` (200 lines)
3. Create `pipeline/metrics_collector.py` (150 lines)

### Week 3: Storage & Integration (Days 11-15)

**Day 11-12: Storage Infrastructure**
1. Create `storage/storage_manager.py` (450 lines)
2. Create `storage/google_drive_client.py` (400 lines)
3. Create `storage/cache_manager.py` (350 lines)

**Day 13-14: Scraper Integration**
1. Update `scrapers/base_scraper.py` (+400 lines)
2. Update Bangladesh tier1 scrapers (4 files, +250 lines each)

**Day 15: Testing**
1. Create integration tests (600 lines)
2. End-to-end testing
3. Documentation

---

## 📋 FILE TEMPLATES

### 1. Configuration (`src/extractors/config.py`)

```python
from pydantic import BaseSettings, Field
from typing import List

class ExtractionConfig(BaseSettings):
    """Production extraction configuration."""

    # Quality thresholds
    min_quality_score: float = 0.7
    citation_confidence_threshold: float = 0.90

    # Retry
    max_retries: int = 3
    retry_delay: float = 1.0

    # PDF
    pdf_max_pages: int = 1000
    pdf_fallback_engines: List[str] = ['pdfplumber', 'PyPDF2']

    # Paths
    pattern_dir: str = 'src/extractors/patterns'

    class Config:
        env_prefix = 'EXTRACT_'
```

### 2. Exceptions (`src/extractors/exceptions.py`)

```python
class ExtractionError(Exception):
    """Base extraction error."""
    pass

class PDFExtractionError(ExtractionError):
    """PDF extraction failed."""
    pass

class CitationExtractionError(ExtractionError):
    """Citation extraction failed."""
    pass

class QualityThresholdError(ExtractionError):
    """Quality below threshold."""
    def __init__(self, score: float, threshold: float):
        self.score = score
        self.threshold = threshold
        super().__init__(f'Quality {score:.2f} < {threshold:.2f}')
```

### 3. Base Extractor Pattern

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
import time

class BaseExtractor(ABC):
    """Abstract base for all extractors."""

    @abstractmethod
    def _extract_impl(self, input_data: Any) -> Dict:
        """Implementation (override this)."""
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input."""
        pass

    @abstractmethod
    def validate_output(self, output: Dict) -> bool:
        """Validate output."""
        pass

    def extract(self, input_data: Any) -> Dict:
        """Main extraction with error handling."""
        try:
            if not self.validate_input(input_data):
                raise ExtractionError('Invalid input')

            result = self._extract_impl(input_data)

            if not self.validate_output(result):
                result['status'] = 'partial'
            else:
                result['status'] = 'success'

            return result

        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'data': None
            }
```

---

## 🎯 CRITICAL PATTERN FILES

### `patterns/citations.yaml`

```yaml
bangladesh:
  DLR:
    pattern: '(\d+)\s*\((\d{4})\)\s*DLR\s*\(?(AD|HCD)?\)?\s*(\d+)'
    components: [volume, year, court, page]
    example: '22 (1998) DLR (HCD) 205'
    encoding: '{volume}DLR{year_short}{court_abbr}{page}'

  BLD:
    pattern: '(\d+)\s*BLD\s*\(?(AD|HCD)?\)?\s*(\d+)'
    components: [volume, court, page]

  BLC:
    pattern: '(\d+)\s*BLC\s*\(?(AD|HCD)?\)?\s*(\d+)'

india:
  AIR:
    pattern: 'AIR\s*(\d{4})\s*(SC|Del|Bom|Mad|Cal)\s*(\d+)'
    components: [year, court, page]

  SCC:
    pattern: '\((\d{4})\)\s*(\d+)\s*SCC\s*(\d+)'
    components: [year, volume, page]
```

### `patterns/parties.yaml`

```yaml
patterns:
  versus:
    - '(?P<petitioner>.+?)\s+v\.?\s+(?P<respondent>.+)'
    - '(?P<petitioner>.+?)\s+vs\.?\s+(?P<respondent>.+)'
    - '(?P<petitioner>.+?)\s+versus\s+(?P<respondent>.+)'

special_parties:
  government:
    - 'State of Bangladesh'
    - 'Government of Bangladesh'
    - 'Union of India'
    - 'State'

  abbreviations:
    'Secretary, Ministry': 'SecyMin'
    'Government of': 'Govt'
    'Corporation': 'Corp'
```

---

## 🔧 INTEGRATION POINTS

### Phase 1 Integration (Naming)

```python
from naming import EnhancedNamer, DocumentMetadata, CitationEncoder

# In extraction pipeline:
namer = EnhancedNamer()
doc_meta = DocumentMetadata(
    country_code='BD',
    doc_type='CAS',
    year=extracted_data['year'],
    citation=extracted_data['primary_citation'],
    **extracted_data
)
filename = namer.generate_filename(doc_meta)
global_id = namer.generate_global_id('BD')
```

### Phase 2 Integration (Database)

```python
from database import DatabaseConnection, Document, Content, Party, Citation

db = DatabaseConnection()
with db.session_scope() as session:
    doc = Document(
        global_id=global_id,
        filename_universal=filename,
        content_hash=extracted_data['hash'],
        **extracted_data
    )
    session.add(doc)
    session.flush()

    # Add related data
    for party in extracted_data['parties']:
        session.add(Party(document_id=doc.id, **party))
```

---

## 📊 TESTING STRATEGY

### Unit Tests (per extractor)
```python
def test_pdf_extractor_valid_pdf():
    extractor = PDFExtractor()
    result = extractor.extract('tests/fixtures/sample.pdf')

    assert result['status'] == 'success'
    assert len(result['full_text']) > 100
    assert result['page_count'] > 0
    assert len(result['hash']) == 16

def test_citation_extractor_bangladesh():
    extractor = CitationExtractor()
    text = "In 22 (1998) DLR (HCD) 205, the court held..."
    result = extractor.extract(text)

    assert len(result['citations']) == 1
    assert result['citations'][0]['citation_encoded'] == '22DLR98H205'
    assert result['citations'][0]['confidence'] >= 0.90
```

### Integration Tests
```python
def test_full_extraction_pipeline():
    """Test complete extraction workflow."""
    pipeline = ExtractionPipeline()

    result = pipeline.process_document(
        html_content=sample_html,
        pdf_path='tests/fixtures/sample.pdf'
    )

    assert result['status'] == 'success'
    assert result['quality_score'] >= 0.80
    assert len(result['citations']) > 0
    assert len(result['parties']) > 0
```

---

## 🚨 ERROR HANDLING STRATEGY

```python
# Skip and continue (production strategy)
try:
    result = extractor.extract(data)

    if result['status'] == 'failed':
        logger.error(f"Extraction failed: {result['error']}")
        # Log to error queue for manual review
        error_queue.add(document_id, result['error'])
        # Continue with next document
        return None

    if result['quality_score'] < 0.70:
        logger.warning(f"Low quality: {result['quality_score']}")
        # Flag for manual review
        review_queue.add(document_id, 'low_quality')

    return result

except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Continue processing other documents
    return None
```

---

## 📈 MONITORING & METRICS

```python
# Track extraction metrics
metrics = {
    'total_documents': 0,
    'successful_extractions': 0,
    'failed_extractions': 0,
    'partial_extractions': 0,
    'average_quality_score': 0.0,
    'average_extraction_time_ms': 0,
    'citation_accuracy': 0.95,  # Target
    'party_accuracy': 0.95,     # Target
}

# Log metrics every 100 documents
if metrics['total_documents'] % 100 == 0:
    logger.info(f"Metrics: {metrics}")

    # Alert if error rate too high
    error_rate = metrics['failed_extractions'] / metrics['total_documents']
    if error_rate > 0.10:
        send_alert(f"High error rate: {error_rate:.2%}")
```

---

## 🎓 NEXT STEPS

1. **Start with Infrastructure** (Day 1):
   - Create `config.py`, `exceptions.py`, `schemas.py`
   - Create `base_extractor.py`
   - Set up logging configuration

2. **Build Core Extractors** (Days 2-3):
   - PDF extractor (highest priority)
   - Citation extractor (critical for Phase 1 integration)
   - Test thoroughly

3. **Add Legal Extractors** (Days 4-5):
   - Party, judge, date extractors
   - Create pattern files

4. **Build Pipeline** (Days 6-7):
   - Orchestration
   - Error handling
   - Metrics

5. **Storage Integration** (Days 8-9):
   - Google Drive client
   - Cache manager

6. **Scraper Updates** (Days 10-12):
   - Update base scraper
   - Update Bangladesh scrapers

7. **Testing** (Days 13-15):
   - Unit tests
   - Integration tests
   - End-to-end validation

---

## 📞 Support & Resources

- **Phase 1 Naming**: `/src/naming/` - Use `EnhancedNamer`, `CitationEncoder`
- **Phase 2 Database**: `/src/database/` - Use `DatabaseConnection`, models
- **Existing Scrapers**: `/src/scrapers/bangladesh/` - 9 scrapers to update
- **Pattern Reference**: See `/src/naming/constants.py` for subject codes, court codes

---

**Status**: Infrastructure created, dependencies installed, ready to implement!

**Next**: Create `src/extractors/config.py` and begin implementation.

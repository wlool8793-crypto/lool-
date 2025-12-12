"""
Extraction Pipeline for Legal RAG Extraction System (Phase 3)
Orchestrates all extractors to produce complete extraction result
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
import traceback

from ..core.pdf_extractor import PDFExtractor
from ..core.html_extractor import HTMLExtractor
from ..core.text_normalizer import TextNormalizer

from ..legal.citation_extractor import CitationExtractor
from ..legal.party_extractor import PartyExtractor
from ..legal.judge_extractor import JudgeExtractor
from ..legal.date_extractor import DateExtractor
from ..legal.section_extractor import SectionExtractor

from ..analysis.keyword_extractor import KeywordExtractor
from ..analysis.subject_classifier import SubjectClassifier
from ..analysis.quality_analyzer import QualityAnalyzer

from ..schemas import CompleteExtractionResult, ExtractionStatus
from ..config import config
from ..logging_config import get_logger
from ..validators import validate_pdf_file, validate_html_content
from ..utils import hash_content

logger = get_logger(__name__)


class ExtractionPipeline:
    """
    Complete extraction pipeline orchestrating all extractors.

    Pipeline Stages:
    1. Input Validation
    2. Content Extraction (PDF/HTML)
    3. Text Normalization
    4. Legal Metadata Extraction (Citations, Parties, Judges, Dates, Sections)
    5. Analysis (Keywords, Subject Classification)
    6. Quality Analysis
    7. Result Assembly

    Features:
    - Error tolerance: Continue on errors, log and skip failed extractors
    - Progress tracking: Optional progress callbacks
    - Flexible input: PDF files or HTML content
    - Quality scoring: Automated quality analysis
    - Structured output: Complete extraction result with all metadata
    """

    def __init__(
        self,
        skip_on_error: bool = True,
        enable_ocr: bool = True,
        enable_quality_check: bool = True,
        min_quality_score: float = None
    ):
        """
        Initialize extraction pipeline.

        Args:
            skip_on_error: Continue processing if extractor fails
            enable_ocr: Enable OCR for scanned PDFs
            enable_quality_check: Run quality analysis
            min_quality_score: Minimum quality score (default from config)
        """
        self.skip_on_error = skip_on_error
        self.enable_ocr = enable_ocr
        self.enable_quality_check = enable_quality_check
        self.min_quality_score = min_quality_score or config.min_quality_score

        # Initialize extractors
        self._initialize_extractors()

        # Execution metadata
        self.execution_log = []

    def _initialize_extractors(self):
        """Initialize all extractor instances."""
        # Core extractors
        self.pdf_extractor = PDFExtractor()
        self.html_extractor = HTMLExtractor()
        self.text_normalizer = TextNormalizer()

        # Legal extractors
        self.citation_extractor = CitationExtractor()
        self.party_extractor = PartyExtractor()
        self.judge_extractor = JudgeExtractor()
        self.date_extractor = DateExtractor()
        self.section_extractor = SectionExtractor()

        # Analysis extractors
        self.keyword_extractor = KeywordExtractor()
        self.subject_classifier = SubjectClassifier()
        self.quality_analyzer = QualityAnalyzer()

        logger.info("Extraction pipeline initialized with all extractors")

    def extract_from_pdf(
        self,
        pdf_path: str,
        document_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Extract complete metadata from PDF file.

        Args:
            pdf_path: Path to PDF file
            document_id: Optional document identifier
            progress_callback: Optional callback(stage_name, progress_pct)

        Returns:
            CompleteExtractionResult dict
        """
        start_time = datetime.utcnow()

        # Generate document ID if not provided
        if not document_id:
            document_id = Path(pdf_path).stem

        logger.info(f"Starting PDF extraction for {document_id}")

        # Stage 1: Validate PDF
        self._report_progress(progress_callback, "Validating PDF", 0.0)

        try:
            is_valid, error = validate_pdf_file(pdf_path)
            if not is_valid:
                return self._create_error_result(
                    document_id,
                    f"PDF validation failed: {error}",
                    start_time
                )
        except Exception as e:
            return self._create_error_result(
                document_id,
                f"PDF validation error: {str(e)}",
                start_time
            )

        # Stage 2: Extract PDF content
        self._report_progress(progress_callback, "Extracting PDF", 10.0)

        pdf_result = self._safe_extract(
            self.pdf_extractor,
            pdf_path,
            enable_ocr=self.enable_ocr
        )

        if pdf_result.get('status') != 'success':
            return self._create_error_result(
                document_id,
                "PDF extraction failed",
                start_time,
                pdf_result
            )

        # Get extracted text
        full_text = pdf_result.get('data', {}).get('full_text', '')

        if not full_text or len(full_text) < 100:
            return self._create_error_result(
                document_id,
                "Insufficient text extracted from PDF",
                start_time
            )

        # Continue with text processing
        return self._process_text(
            document_id,
            full_text,
            start_time,
            progress_callback,
            source_type='pdf',
            pdf_metadata=pdf_result.get('data', {})
        )

    def extract_from_html(
        self,
        html_content: str,
        document_id: Optional[str] = None,
        base_url: Optional[str] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, Any]:
        """
        Extract complete metadata from HTML content.

        Args:
            html_content: HTML content string
            document_id: Optional document identifier
            base_url: Optional base URL for link resolution
            progress_callback: Optional callback(stage_name, progress_pct)

        Returns:
            CompleteExtractionResult dict
        """
        start_time = datetime.utcnow()

        # Generate document ID if not provided
        if not document_id:
            document_id = hash_content(html_content)

        logger.info(f"Starting HTML extraction for {document_id}")

        # Stage 1: Validate HTML
        self._report_progress(progress_callback, "Validating HTML", 0.0)

        try:
            is_valid, error = validate_html_content(html_content)
            if not is_valid:
                return self._create_error_result(
                    document_id,
                    f"HTML validation failed: {error}",
                    start_time
                )
        except Exception as e:
            return self._create_error_result(
                document_id,
                f"HTML validation error: {str(e)}",
                start_time
            )

        # Stage 2: Extract HTML metadata
        self._report_progress(progress_callback, "Extracting HTML", 10.0)

        html_result = self._safe_extract(
            self.html_extractor,
            html_content,
            base_url=base_url
        )

        html_data = html_result.get('data', {})
        full_text = html_data.get('full_text', '')

        if not full_text or len(full_text) < 100:
            return self._create_error_result(
                document_id,
                "Insufficient text extracted from HTML",
                start_time
            )

        # Continue with text processing
        return self._process_text(
            document_id,
            full_text,
            start_time,
            progress_callback,
            source_type='html',
            html_metadata=html_data
        )

    def _process_text(
        self,
        document_id: str,
        full_text: str,
        start_time: datetime,
        progress_callback: Optional[Callable],
        source_type: str = 'pdf',
        pdf_metadata: Optional[Dict] = None,
        html_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process extracted text through all extractors.

        Args:
            document_id: Document identifier
            full_text: Extracted text
            start_time: Extraction start time
            progress_callback: Progress callback
            source_type: 'pdf' or 'html'
            pdf_metadata: PDF extraction metadata
            html_metadata: HTML extraction metadata

        Returns:
            CompleteExtractionResult dict
        """
        # Stage 3: Normalize text
        self._report_progress(progress_callback, "Normalizing text", 20.0)

        normalized_result = self._safe_extract(
            self.text_normalizer,
            full_text
        )

        normalized_text = normalized_result.get('data', {}).get('normalized_text', full_text)

        # Stage 4: Extract legal metadata
        self._report_progress(progress_callback, "Extracting citations", 30.0)
        citations_result = self._safe_extract(self.citation_extractor, normalized_text)

        self._report_progress(progress_callback, "Extracting parties", 40.0)
        parties_result = self._safe_extract(
            self.party_extractor,
            normalized_text,
            title=html_metadata.get('title') if html_metadata else None
        )

        self._report_progress(progress_callback, "Extracting judges", 50.0)
        judges_result = self._safe_extract(self.judge_extractor, normalized_text)

        self._report_progress(progress_callback, "Extracting dates", 60.0)
        dates_result = self._safe_extract(self.date_extractor, normalized_text)

        self._report_progress(progress_callback, "Extracting sections", 70.0)
        sections_result = self._safe_extract(self.section_extractor, normalized_text)

        # Stage 5: Analysis
        self._report_progress(progress_callback, "Extracting keywords", 80.0)
        keywords_result = self._safe_extract(self.keyword_extractor, normalized_text)

        self._report_progress(progress_callback, "Classifying subject", 85.0)
        subject_result = self._safe_extract(self.subject_classifier, normalized_text)

        # Stage 6: Assemble result
        self._report_progress(progress_callback, "Assembling result", 90.0)

        complete_result = self._assemble_result(
            document_id=document_id,
            full_text=normalized_text,
            original_text=full_text,
            source_type=source_type,
            citations=citations_result.get('data', {}),
            parties=parties_result.get('data', {}),
            judges=judges_result.get('data', {}),
            dates=dates_result.get('data', {}),
            sections=sections_result.get('data', {}),
            keywords=keywords_result.get('data', {}),
            subject=subject_result.get('data', {}),
            pdf_metadata=pdf_metadata,
            html_metadata=html_metadata
        )

        # Stage 7: Quality analysis
        if self.enable_quality_check:
            self._report_progress(progress_callback, "Analyzing quality", 95.0)

            quality_result = self._safe_extract(
                self.quality_analyzer,
                complete_result
            )

            complete_result['quality_analysis'] = quality_result.get('data', {})

            # Check minimum quality
            quality_score = quality_result.get('data', {}).get('overall_score', 0.0)

            if quality_score < self.min_quality_score:
                logger.warning(
                    f"Document {document_id} quality score {quality_score:.2f} "
                    f"below minimum {self.min_quality_score:.2f}"
                )

        # Add execution metadata
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        complete_result['extraction_metadata'] = {
            'document_id': document_id,
            'extraction_timestamp': end_time.isoformat() + 'Z',
            'duration_seconds': round(duration, 2),
            'source_type': source_type,
            'pipeline_version': '3.0.0',
            'extractors_run': self._get_extractors_run(),
            'execution_log': self.execution_log
        }

        self._report_progress(progress_callback, "Complete", 100.0)

        logger.info(
            f"Extraction complete for {document_id} in {duration:.2f}s",
            extra={'document_id': document_id}
        )

        return complete_result

    def _safe_extract(self, extractor, *args, **kwargs) -> Dict[str, Any]:
        """
        Safely execute extractor with error handling.

        Args:
            extractor: Extractor instance
            *args: Positional arguments for extractor
            **kwargs: Keyword arguments for extractor

        Returns:
            Extraction result (with status)
        """
        extractor_name = extractor.__class__.__name__

        try:
            result = extractor.extract(*args, **kwargs)

            # Log execution
            self.execution_log.append({
                'extractor': extractor_name,
                'status': result.get('status', 'unknown'),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

            return result

        except Exception as e:
            error_msg = f"{extractor_name} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Log execution
            self.execution_log.append({
                'extractor': extractor_name,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

            if not self.skip_on_error:
                raise

            # Return empty result
            return {
                'status': 'failed',
                'data': {},
                'error': error_msg
            }

    def _assemble_result(
        self,
        document_id: str,
        full_text: str,
        original_text: str,
        source_type: str,
        citations: Dict,
        parties: Dict,
        judges: Dict,
        dates: Dict,
        sections: Dict,
        keywords: Dict,
        subject: Dict,
        pdf_metadata: Optional[Dict],
        html_metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Assemble complete extraction result."""
        result = {
            'document_id': document_id,
            'source_type': source_type,

            # Text
            'full_text': full_text,
            'text_hash': hash_content(full_text),
            'text_length': len(full_text),

            # Metadata from HTML (if available)
            'title': html_metadata.get('title') if html_metadata else None,
            'url': html_metadata.get('url') if html_metadata else None,

            # Legal metadata
            'citations': citations.get('citations', []),
            'parties': {
                'petitioner': parties.get('petitioner', []),
                'respondent': parties.get('respondent', []),
                'all_parties': parties.get('all_parties', [])
            },
            'judges': judges.get('judges', []),
            'bench_size': judges.get('bench_size', 0),
            'dates': {
                'judgment_date': dates.get('judgment_date'),
                'filing_date': dates.get('filing_date'),
                'hearing_date': dates.get('hearing_date')
            },
            'year': dates.get('year'),
            'sections_cited': sections.get('sections', []),

            # Analysis
            'keywords': keywords.get('keywords', []),
            'subject_classification': {
                'primary_subject': subject.get('primary_subject', 'GEN'),
                'primary_subject_name': subject.get('primary_subject_name', 'General'),
                'primary_confidence': subject.get('primary_confidence', 0.0),
                'secondary_subjects': subject.get('secondary_subjects', [])
            },

            # Source-specific metadata
            'pdf_metadata': pdf_metadata,
            'html_metadata': html_metadata
        }

        return result

    def _create_error_result(
        self,
        document_id: str,
        error_message: str,
        start_time: datetime,
        partial_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create error result."""
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        return {
            'document_id': document_id,
            'status': 'failed',
            'error': error_message,
            'partial_result': partial_result,
            'extraction_metadata': {
                'document_id': document_id,
                'extraction_timestamp': end_time.isoformat() + 'Z',
                'duration_seconds': round(duration, 2),
                'pipeline_version': '3.0.0',
                'execution_log': self.execution_log
            }
        }

    def _get_extractors_run(self) -> List[str]:
        """Get list of extractors that were executed."""
        return [log['extractor'] for log in self.execution_log]

    def _report_progress(
        self,
        callback: Optional[Callable],
        stage: str,
        progress: float
    ):
        """Report progress to callback."""
        if callback:
            try:
                callback(stage, progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")


# ==================== Convenience Functions ====================

def extract_document(
    input_path: str,
    document_id: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Extract metadata from document (auto-detect PDF/HTML).

    Args:
        input_path: Path to PDF file or HTML file
        document_id: Optional document identifier
        progress_callback: Optional progress callback

    Returns:
        CompleteExtractionResult dict
    """
    pipeline = ExtractionPipeline()

    # Check file extension
    path = Path(input_path)

    if path.suffix.lower() == '.pdf':
        return pipeline.extract_from_pdf(
            str(path),
            document_id=document_id,
            progress_callback=progress_callback
        )
    elif path.suffix.lower() in ['.html', '.htm']:
        with open(path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return pipeline.extract_from_html(
            html_content,
            document_id=document_id,
            progress_callback=progress_callback
        )
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def extract_batch(
    input_paths: List[str],
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[Dict[str, Any]]:
    """
    Extract metadata from multiple documents.

    Args:
        input_paths: List of document paths
        progress_callback: Optional callback(current, total, document_id)

    Returns:
        List of extraction results
    """
    pipeline = ExtractionPipeline()
    results = []

    total = len(input_paths)

    for i, input_path in enumerate(input_paths, 1):
        document_id = Path(input_path).stem

        if progress_callback:
            progress_callback(i, total, document_id)

        try:
            result = extract_document(input_path, document_id=document_id)
            results.append(result)

        except Exception as e:
            logger.error(f"Failed to extract {input_path}: {e}")
            results.append({
                'document_id': document_id,
                'status': 'failed',
                'error': str(e)
            })

    return results

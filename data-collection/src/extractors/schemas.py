"""
Pydantic schemas for Legal RAG Extraction System (Phase 3)
Data validation models for all extraction inputs and outputs
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum


# ==================== Enums ====================

class ExtractionStatus(str, Enum):
    """Extraction status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ValidationStatus(str, Enum):
    """Quality validation status"""
    VALID = "valid"
    NEEDS_REVIEW = "needs_review"
    INVALID = "invalid"


class PDFQuality(str, Enum):
    """PDF extraction quality"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PartyType(str, Enum):
    """Legal party type"""
    PETITIONER = "petitioner"
    RESPONDENT = "respondent"
    APPELLANT = "appellant"
    DEFENDANT = "defendant"
    PLAINTIFF = "plaintiff"


class OpinionType(str, Enum):
    """Judicial opinion type"""
    MAJORITY = "majority"
    DISSENTING = "dissenting"
    CONCURRING = "concurring"


class KeywordType(str, Enum):
    """Keyword classification"""
    LEGAL_TERM = "legal_term"
    ENTITY = "entity"
    CONCEPT = "concept"


# ==================== Input Schemas ====================

class ExtractionInput(BaseModel):
    """Input for extraction pipeline"""

    document_id: Optional[str] = Field(None, description="Optional document identifier")
    html_content: Optional[str] = Field(None, description="HTML page content")
    pdf_path: Optional[str] = Field(None, description="Path to PDF file")
    title: Optional[str] = Field(None, description="Document title (from scraper)")
    source_url: Optional[str] = Field(None, description="Source URL")
    pdf_url: Optional[str] = Field(None, description="PDF download URL")

    @validator('html_content', 'pdf_path')
    def at_least_one_input(cls, v, values):
        """Ensure at least HTML or PDF is provided"""
        if not v and not values.get('html_content') and not values.get('pdf_path'):
            raise ValueError("At least one of html_content or pdf_path must be provided")
        return v

    class Config:
        schema_extra = {
            "example": {
                "document_id": "temp_001",
                "html_content": "<html>...</html>",
                "pdf_path": "/path/to/case.pdf",
                "title": "Rahman v. State",
                "source_url": "http://example.com/case/123"
            }
        }


# ==================== PDF Extraction Schemas ====================

class PDFPageSchema(BaseModel):
    """Single PDF page"""
    page_num: int = Field(..., description="Page number (1-indexed)")
    text: str = Field(..., description="Extracted text")
    char_count: int = Field(..., description="Character count")


class PDFExtractionResult(BaseModel):
    """PDF extraction output"""

    status: ExtractionStatus
    full_text: str = Field("", description="Complete extracted text")
    page_count: int = Field(0, description="Total pages")
    word_count: int = Field(0, description="Word count")
    character_count: int = Field(0, description="Character count")
    hash: str = Field("", description="16-char content hash (Phase 1)")
    pdf_hash_sha256: str = Field("", description="Full 64-char SHA-256 hash")
    quality: PDFQuality = Field(PDFQuality.MEDIUM, description="Extraction quality")
    is_scanned: bool = Field(False, description="Whether PDF is scanned image")
    extraction_method: str = Field("", description="Engine used (pdfplumber/PyPDF2/pdfminer/tesseract)")
    ocr_confidence: Optional[float] = Field(None, description="OCR confidence if scanned", ge=0.0, le=1.0)
    pages: List[PDFPageSchema] = Field(default_factory=list, description="Page-by-page text")
    error: Optional[str] = Field(None, description="Error message if failed")


# ==================== HTML Extraction Schemas ====================

class HTMLExtractionResult(BaseModel):
    """HTML extraction output"""

    status: ExtractionStatus
    title_full: str = Field("", description="Full title")
    source_url: str = Field("", description="Source URL")
    pdf_url: str = Field("", description="PDF download URL")
    court_name: Optional[str] = Field(None, description="Court name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata")
    error: Optional[str] = Field(None, description="Error message if failed")


# ==================== Citation Schemas ====================

class CitationSchema(BaseModel):
    """Legal citation"""

    citation_text: str = Field(..., description="Original citation text")
    citation_encoded: str = Field(..., description="Encoded citation (Phase 1 format)")
    volume: Optional[int] = Field(None, description="Volume number")
    year: int = Field(..., description="Year", ge=1800, le=2100)
    reporter: str = Field(..., description="Reporter abbreviation (DLR, AIR, etc.)")
    court: Optional[str] = Field(None, description="Court abbreviation")
    page: int = Field(..., description="Page number", ge=1)
    is_primary: bool = Field(False, description="Whether this is the primary citation")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class CitationExtractionResult(BaseModel):
    """Citation extraction output"""

    status: ExtractionStatus
    citations: List[CitationSchema] = Field(default_factory=list)
    primary_citation: Optional[CitationSchema] = Field(None, description="Primary citation")
    error: Optional[str] = None


# ==================== Party Schemas ====================

class PartySchema(BaseModel):
    """Legal party"""

    party_type: PartyType
    party_name: str = Field(..., description="Full party name")
    party_name_abbr: str = Field(..., description="Abbreviated name (Phase 1 format)")
    party_order: int = Field(..., description="Order among parties of same type", ge=1)
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class PartyExtractionResult(BaseModel):
    """Party extraction output"""

    status: ExtractionStatus
    parties: List[PartySchema] = Field(default_factory=list)
    error: Optional[str] = None


# ==================== Judge Schemas ====================

class JudgeSchema(BaseModel):
    """Judge information"""

    judge_name: str = Field(..., description="Judge name")
    is_presiding: bool = Field(False, description="Whether presiding judge")
    is_author: bool = Field(False, description="Whether judgment author")
    opinion_type: OpinionType = Field(OpinionType.MAJORITY)
    judge_order: int = Field(..., description="Order in bench", ge=1)


class JudgeExtractionResult(BaseModel):
    """Judge extraction output"""

    status: ExtractionStatus
    judges: List[JudgeSchema] = Field(default_factory=list)
    bench_size: int = Field(0, description="Total judges")
    error: Optional[str] = None


# ==================== Date Schemas ====================

class DateExtractionResult(BaseModel):
    """Date extraction output"""

    status: ExtractionStatus
    date_judgment: Optional[date] = Field(None, description="Judgment date")
    date_filing: Optional[date] = Field(None, description="Filing date")
    date_hearing: Optional[date] = Field(None, description="Hearing date")
    error: Optional[str] = None


# ==================== Section Schemas ====================

class SectionSchema(BaseModel):
    """Statutory section/article reference"""

    act_name: str = Field(..., description="Act/statute name")
    section_number: str = Field(..., description="Section/article number")
    context: str = Field("", description="Surrounding context")
    mention_count: int = Field(1, description="Times mentioned", ge=1)


class SectionExtractionResult(BaseModel):
    """Section extraction output"""

    status: ExtractionStatus
    sections_cited: List[SectionSchema] = Field(default_factory=list)
    error: Optional[str] = None


# ==================== Keyword Schemas ====================

class KeywordSchema(BaseModel):
    """Extracted keyword"""

    keyword: str = Field(..., description="Keyword term")
    weight: float = Field(..., description="TF-IDF weight", ge=0.0, le=1.0)
    keyword_type: KeywordType
    frequency: int = Field(..., description="Frequency in document", ge=1)


class KeywordExtractionResult(BaseModel):
    """Keyword extraction output"""

    status: ExtractionStatus
    keywords: List[KeywordSchema] = Field(default_factory=list)
    error: Optional[str] = None


# ==================== Subject Classification Schemas ====================

class SubjectClassificationResult(BaseModel):
    """Subject classification output"""

    status: ExtractionStatus
    subject_primary: str = Field("GEN", description="Primary subject code")
    subject_secondary: Optional[str] = Field(None, description="Secondary subject code")
    confidence: float = Field(..., description="Classification confidence", ge=0.0, le=1.0)
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that matched")
    error: Optional[str] = None


# ==================== Quality Analysis Schemas ====================

class QualityBreakdown(BaseModel):
    """Quality score breakdown"""

    completeness: float = Field(..., description="Completeness score", ge=0.0, le=1.0)
    citation_quality: float = Field(..., description="Citation quality", ge=0.0, le=1.0)
    text_quality: float = Field(..., description="Text quality", ge=0.0, le=1.0)
    metadata_quality: float = Field(..., description="Metadata quality", ge=0.0, le=1.0)
    consistency: float = Field(..., description="Consistency score", ge=0.0, le=1.0)


class QualityAnalysisResult(BaseModel):
    """Quality analysis output"""

    status: ExtractionStatus
    data_quality_score: float = Field(..., description="Overall quality", ge=0.0, le=1.0)
    validation_status: ValidationStatus
    validation_errors: List[str] = Field(default_factory=list)
    quality_breakdown: QualityBreakdown
    manual_review_needed: bool = Field(False)
    recommendations: List[str] = Field(default_factory=list, description="Automated recommendations")
    error: Optional[str] = None


# ==================== Complete Extraction Result ====================

class CompleteExtractionResult(BaseModel):
    """Complete extraction result combining all extractors"""

    # Metadata
    document_id: Optional[str] = None
    status: ExtractionStatus
    extraction_time_ms: int = Field(..., description="Total extraction time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # PDF extraction
    pdf_result: Optional[PDFExtractionResult] = None

    # HTML extraction
    html_result: Optional[HTMLExtractionResult] = None

    # Legal extraction
    citations: List[CitationSchema] = Field(default_factory=list)
    parties: List[PartySchema] = Field(default_factory=list)
    judges: List[JudgeSchema] = Field(default_factory=list)
    date_judgment: Optional[date] = None
    date_filing: Optional[date] = None
    date_hearing: Optional[date] = None
    sections_cited: List[SectionSchema] = Field(default_factory=list)

    # Analysis
    keywords: List[KeywordSchema] = Field(default_factory=list)
    subject_primary: str = "GEN"
    subject_secondary: Optional[str] = None
    subject_confidence: float = 0.0

    # Quality
    data_quality_score: float = 0.0
    validation_status: ValidationStatus = ValidationStatus.INVALID
    quality_breakdown: Optional[QualityBreakdown] = None

    # Errors
    errors: List[str] = Field(default_factory=list, description="All errors encountered")
    warnings: List[str] = Field(default_factory=list, description="All warnings")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }

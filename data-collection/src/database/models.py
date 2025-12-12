"""
SQLAlchemy ORM Models for Legal RAG System
PostgreSQL database models with Phase 1 naming integration
"""

from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import (
    Boolean, Column, Integer, String, Text, Date, DateTime, Numeric,
    ForeignKey, CheckConstraint, UniqueConstraint, Index, CHAR, BigInteger,
    Enum as SQLEnum, DECIMAL
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR, ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum


# ============================================================================
# Base Class
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ============================================================================
# Enums
# ============================================================================

class DocType(str, enum.Enum):
    """Document types."""
    CASE = "CAS"
    ACT = "ACT"
    RULE = "RUL"
    ORDER = "ORD"
    ORDINANCE = "ORN"
    TREATY = "TRE"
    CONSTITUTION = "CON"
    REGULATION = "REG"


class SubjectCode(str, enum.Enum):
    """Subject area codes."""
    CRIMINAL = "CRM"
    CIVIL = "CIV"
    CONSTITUTIONAL = "CON"
    PROPERTY = "PRO"
    FAMILY = "FAM"
    COMMERCIAL = "COM"
    TAX = "TAX"
    LABOR = "LAB"
    ENVIRONMENTAL = "ENV"
    IPR = "IPR"
    ADMINISTRATIVE = "ADM"
    CONSUMER = "CSM"
    IT = "IT"
    INTERNATIONAL = "INT"
    HUMAN_RIGHTS = "HUM"
    GENERAL = "GEN"


class LegalStatus(str, enum.Enum):
    """Legal status."""
    ACTIVE = "ACT"
    REPEALED = "REP"
    AMENDED = "AMD"
    SUPERSEDED = "SUP"
    OVERRULED = "OVR"
    PENDING = "PND"


class EmbeddingStatus(str, enum.Enum):
    """Embedding status for RAG."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StorageTier(str, enum.Enum):
    """Storage tier for PDFs."""
    DRIVE = "drive"
    CACHE = "cache"
    BOTH = "both"
    NONE = "none"


# ============================================================================
# Core Models
# ============================================================================

class Document(Base):
    """
    Main document model with Phase 1 naming integration.
    """
    __tablename__ = "documents"

    # Primary Keys
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    global_id: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    doc_uuid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)

    # Phase 1 Naming Integration
    filename_universal: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    content_hash: Mapped[str] = mapped_column(CHAR(16), nullable=False)

    # Document Classification
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False, index=True)
    doc_type: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    doc_subtype: Mapped[Optional[str]] = mapped_column(String(4))

    # Title & Identification
    title_full: Mapped[str] = mapped_column(Text, nullable=False)
    title_short: Mapped[Optional[str]] = mapped_column(String(500))
    title_alternate: Mapped[Optional[str]] = mapped_column(Text)
    doc_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doc_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Subject Classification
    subject_primary: Mapped[Optional[str]] = mapped_column(String(3), index=True)
    subject_secondary: Mapped[Optional[str]] = mapped_column(String(3))
    subject_tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)

    # Legal Status & Dates
    legal_status: Mapped[Optional[str]] = mapped_column(String(3), index=True)
    date_judgment: Mapped[Optional[datetime]] = mapped_column(Date)
    date_enacted: Mapped[Optional[datetime]] = mapped_column(Date)
    date_effective: Mapped[Optional[datetime]] = mapped_column(Date)
    date_published: Mapped[Optional[datetime]] = mapped_column(Date)
    date_last_amended: Mapped[Optional[datetime]] = mapped_column(Date)
    date_repealed: Mapped[Optional[datetime]] = mapped_column(Date)

    # Source Information
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(100))
    source_database: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    parent_doc_id: Mapped[Optional[int]] = mapped_column(ForeignKey('documents.id', ondelete='SET NULL'))
    supersedes_doc_id: Mapped[Optional[int]] = mapped_column(ForeignKey('documents.id', ondelete='SET NULL'))

    # RAG Metadata
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_strategy: Mapped[str] = mapped_column(String(20), default='semantic')
    embedding_model: Mapped[Optional[str]] = mapped_column(String(50))
    embedding_status: Mapped[str] = mapped_column(String(20), default='pending', index=True)
    last_embedded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Statistics
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)
    cites_count: Mapped[int] = mapped_column(Integer, default=0)

    # Data Quality
    data_quality_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    validation_status: Mapped[str] = mapped_column(String(20), default='pending')
    validation_errors: Mapped[Optional[str]] = mapped_column(Text)
    manual_review_needed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Scraping Metadata
    scraper_name: Mapped[Optional[str]] = mapped_column(String(100))
    scraper_version: Mapped[Optional[str]] = mapped_column(String(20))
    scrape_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
    scrape_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Timestamps
    scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    content: Mapped[Optional["Content"]] = relationship("Content", back_populates="document", uselist=False)
    file_storage: Mapped[List["FileStorage"]] = relationship("FileStorage", back_populates="document")
    parties: Mapped[List["Party"]] = relationship("Party", back_populates="document")
    judges: Mapped[List["Judge"]] = relationship("Judge", back_populates="document")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="document")
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document")

    __table_args__ = (
        CheckConstraint('doc_year >= 1800 AND doc_year <= 2100', name='chk_doc_year'),
        Index('idx_doc_country_type', 'country_code', 'doc_type'),
        Index('idx_doc_country_type_year', 'country_code', 'doc_type', 'doc_year'),
    )

    def __repr__(self):
        return f"<Document(global_id='{self.global_id}', title='{self.title_full[:50]}...')>"


class FileStorage(Base):
    """Multi-tier PDF storage tracking."""
    __tablename__ = "file_storage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Storage Locations
    storage_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    drive_file_id: Mapped[Optional[str]] = mapped_column(String(100))
    drive_folder_path: Mapped[Optional[str]] = mapped_column(Text)
    drive_web_link: Mapped[Optional[str]] = mapped_column(Text)
    drive_md5_checksum: Mapped[Optional[str]] = mapped_column(String(32))
    local_cache_path: Mapped[Optional[str]] = mapped_column(String(500))
    cache_tier: Mapped[str] = mapped_column(String(20), default='cold')

    # File Properties
    pdf_filename: Mapped[str] = mapped_column(String(150), nullable=False)
    pdf_hash_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    pdf_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pdf_pages: Mapped[Optional[int]] = mapped_column(Integer)

    # Versioning
    is_current_version: Mapped[bool] = mapped_column(Boolean, default=True)
    version_notes: Mapped[Optional[str]] = mapped_column(Text)
    replaced_by_version: Mapped[Optional[int]] = mapped_column(Integer)
    supersedes_version: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    upload_status: Mapped[str] = mapped_column(String(20), default='pending')
    download_status: Mapped[Optional[str]] = mapped_column(String(20))
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Access Tracking
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cache_priority: Mapped[int] = mapped_column(Integer, default=0)
    cache_hits: Mapped[int] = mapped_column(Integer, default=0)
    cache_misses: Mapped[int] = mapped_column(Integer, default=0)

    # Integrity
    checksum_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    checksum_match: Mapped[Optional[bool]] = mapped_column(Boolean)
    integrity_check_count: Mapped[int] = mapped_column(Integer, default=0)

    # Errors
    upload_error: Mapped[Optional[str]] = mapped_column(Text)
    download_error: Mapped[Optional[str]] = mapped_column(Text)
    upload_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="file_storage")

    __table_args__ = (
        UniqueConstraint('document_id', 'version_number', name='uk_doc_version'),
        Index('idx_storage_document', 'document_id'),
        Index('idx_storage_tier', 'storage_tier'),
    )

    def __repr__(self):
        return f"<FileStorage(doc_id={self.document_id}, v={self.version_number}, tier='{self.storage_tier}')>"


class Party(Base):
    """Case parties."""
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    party_type: Mapped[str] = mapped_column(String(20), nullable=False)
    party_name: Mapped[str] = mapped_column(Text, nullable=False)
    party_name_abbr: Mapped[Optional[str]] = mapped_column(String(50))
    party_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    representation: Mapped[Optional[str]] = mapped_column(Text)
    lawyer_name: Mapped[Optional[str]] = mapped_column(String(200))
    law_firm: Mapped[Optional[str]] = mapped_column(String(200))
    party_category: Mapped[Optional[str]] = mapped_column(String(50))
    party_identifier: Mapped[Optional[str]] = mapped_column(String(100))
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="parties")

    __table_args__ = (
        UniqueConstraint('document_id', 'party_type', 'party_order', name='uk_doc_party_type_order'),
        Index('idx_party_document', 'document_id'),
    )


class Judge(Base):
    """Bench composition."""
    __tablename__ = "judges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    judge_name: Mapped[str] = mapped_column(String(200), nullable=False)
    judge_title: Mapped[Optional[str]] = mapped_column(String(50))
    judge_designation: Mapped[Optional[str]] = mapped_column(String(50))
    is_author: Mapped[bool] = mapped_column(Boolean, default=False)
    is_presiding: Mapped[bool] = mapped_column(Boolean, default=False)
    opinion_type: Mapped[Optional[str]] = mapped_column(String(20))
    judge_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    opinion_summary: Mapped[Optional[str]] = mapped_column(Text)
    opinion_pages: Mapped[Optional[dict]] = mapped_column(JSONB)
    judge_identifier: Mapped[Optional[str]] = mapped_column(String(100))
    judge_court: Mapped[Optional[str]] = mapped_column(String(100))
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="judges")

    __table_args__ = (
        UniqueConstraint('document_id', 'judge_name', 'opinion_type', name='uk_doc_judge_name_opinion'),
        Index('idx_judge_document', 'document_id'),
    )


class Citation(Base):
    """Citation details with Phase 1 integration."""
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    citation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    volume: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    reporter: Mapped[Optional[str]] = mapped_column(String(20))
    court_code: Mapped[Optional[str]] = mapped_column(String(10))
    page: Mapped[Optional[int]] = mapped_column(Integer)
    series: Mapped[Optional[str]] = mapped_column(String(10))
    citation_encoded: Mapped[Optional[str]] = mapped_column(String(50))
    citation_display: Mapped[Optional[str]] = mapped_column(Text)
    citation_full: Mapped[Optional[str]] = mapped_column(Text)
    neutral_citation: Mapped[Optional[str]] = mapped_column(String(100))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="citations")

    __table_args__ = (
        UniqueConstraint('document_id', 'citation_type', 'citation_encoded', name='uk_doc_citation_type_encoded'),
        Index('idx_citation_document', 'document_id'),
    )


class Content(Base):
    """Full text storage with FTS."""
    __tablename__ = "content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_text: Mapped[Optional[str]] = mapped_column(Text)
    headnote: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    judgment: Mapped[Optional[str]] = mapped_column(Text)
    ratio_decidendi: Mapped[Optional[str]] = mapped_column(Text)
    obiter_dicta: Mapped[Optional[str]] = mapped_column(Text)
    preamble: Mapped[Optional[str]] = mapped_column(Text)
    sections: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    schedules: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    appendices: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)
    search_vector_headnote: Mapped[Optional[str]] = mapped_column(TSVECTOR)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    character_count: Mapped[Optional[int]] = mapped_column(Integer)
    paragraph_count: Mapped[Optional[int]] = mapped_column(Integer)
    section_count: Mapped[int] = mapped_column(Integer, default=0)
    language_code: Mapped[str] = mapped_column(CHAR(2), default='en')
    ocr_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    text_quality: Mapped[Optional[str]] = mapped_column(String(20))
    extraction_method: Mapped[Optional[str]] = mapped_column(String(20))
    extraction_tool: Mapped[Optional[str]] = mapped_column(String(50))
    extraction_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="content")


class DocumentChunk(Base):
    """RAG text chunks."""
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_id: Mapped[Optional[str]] = mapped_column(String(50))
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_hash: Mapped[Optional[str]] = mapped_column(CHAR(16))
    chunk_level: Mapped[Optional[str]] = mapped_column(String(20))
    start_char: Mapped[Optional[int]] = mapped_column(Integer)
    end_char: Mapped[Optional[int]] = mapped_column(Integer)
    start_page: Mapped[Optional[int]] = mapped_column(Integer)
    end_page: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_words: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_chars: Mapped[Optional[int]] = mapped_column(Integer)
    parent_chunk_id: Mapped[Optional[int]] = mapped_column(ForeignKey('document_chunks.id', ondelete='SET NULL'))
    child_chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_depth: Mapped[int] = mapped_column(Integer, default=0)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(50))
    embedding_model: Mapped[Optional[str]] = mapped_column(String(50))
    embedding_dimension: Mapped[Optional[int]] = mapped_column(Integer)
    embedding_status: Mapped[str] = mapped_column(String(20), default='pending')
    embedded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    context_before: Mapped[Optional[str]] = mapped_column(Text)
    context_after: Mapped[Optional[str]] = mapped_column(Text)
    section_title: Mapped[Optional[str]] = mapped_column(String(500))
    section_number: Mapped[Optional[str]] = mapped_column(String(50))
    is_heading: Mapped[bool] = mapped_column(Boolean, default=False)
    is_citation: Mapped[bool] = mapped_column(Boolean, default=False)
    is_footnote: Mapped[bool] = mapped_column(Boolean, default=False)
    is_table: Mapped[bool] = mapped_column(Boolean, default=False)
    is_list_item: Mapped[bool] = mapped_column(Boolean, default=False)
    chunk_quality_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    has_meaningful_content: Mapped[bool] = mapped_column(Boolean, default=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint('document_id', 'chunk_index', name='uk_doc_chunk_index'),
        Index('idx_chunk_document', 'document_id'),
        Index('idx_chunk_embedding_status', 'embedding_status'),
    )


# ============================================================================
# Additional models would go here (LegalReference, SectionCited, etc.)
# Truncated for brevity - the pattern is the same
# ============================================================================

if __name__ == "__main__":
    # Print all table names
    print("SQLAlchemy Models:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

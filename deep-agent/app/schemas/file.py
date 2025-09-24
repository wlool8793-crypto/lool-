"""
File schemas for the Deep Agent application.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import os


class FileUploadBase(BaseModel):
    """Base file upload schema."""
    filename: str = Field(..., description="Filename")
    original_filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    file_type: str = Field(..., description="File type")
    processed: bool = Field(default=False, description="Processing status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['document', 'image', 'audio', 'video', 'other']
        if v not in allowed_types:
            raise ValueError(f'File type must be one of: {allowed_types}')
        return v


class FileUploadCreate(FileUploadBase):
    """File upload creation schema."""
    user_id: int = Field(..., description="User ID")
    conversation_id: Optional[int] = Field(None, description="Conversation ID")


class FileUploadResponse(FileUploadBase):
    """File upload response schema."""
    id: int = Field(..., description="File ID")
    user_id: int = Field(..., description="User ID")
    conversation_id: Optional[int] = Field(None, description="Conversation ID")
    created_at: datetime = Field(..., description="Upload time")

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Simplified file upload response for listing."""
    id: int = Field(..., description="File ID")
    filename: str = Field(..., description="Filename")
    original_filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    file_type: str = Field(..., description="File type")
    processed: bool = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Upload time")

    class Config:
        from_attributes = True


class FileMetadataResponse(FileUploadBase):
    """File metadata response schema."""
    id: int = Field(..., description="File ID")
    user_id: int = Field(..., description="User ID")
    conversation_id: Optional[int] = Field(None, description="Conversation ID")
    created_at: datetime = Field(..., description="Upload time")
    processing_history: Optional[List[Dict[str, Any]]] = Field(None, description="Processing history")

    class Config:
        from_attributes = True


class FileProcessRequest(BaseModel):
    """File processing request schema."""
    processing_type: str = Field(..., description="Processing type")
    options: Optional[Dict[str, Any]] = Field(None, description="Processing options")

    @validator('processing_type')
    def validate_processing_type(cls, v):
        allowed_types = [
            'text_extraction', 'image_analysis', 'document_parsing',
            'audio_transcription', 'video_analysis', 'data_analysis',
            'content_summarization', 'sentiment_analysis', 'entity_extraction'
        ]
        if v not in allowed_types:
            raise ValueError(f'Processing type must be one of: {allowed_types}')
        return v


class FileProcessResponse(BaseModel):
    """File processing response schema."""
    file_id: int = Field(..., description="File ID")
    processing_type: str = Field(..., description="Processing type")
    success: bool = Field(..., description="Processing success status")
    result: Optional[Any] = Field(None, description="Processing result")
    execution_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class FileSearchRequest(BaseModel):
    """File search request schema."""
    query: str = Field(..., min_length=1, description="Search query")
    file_type: Optional[str] = Field(None, description="Filter by file type")
    mime_type: Optional[str] = Field(None, description="Filter by MIME type")
    processed: Optional[bool] = Field(None, description="Filter by processing status")
    conversation_id: Optional[int] = Field(None, description="Filter by conversation ID")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class FileSearchResponse(BaseModel):
    """File search response schema."""
    files: List[FileListResponse] = Field(default_factory=list, description="Search results")
    total_count: int = Field(0, description="Total results count")
    query: str = Field(..., description="Search query used")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class FileExportRequest(BaseModel):
    """File export request schema."""
    file_ids: List[int] = Field(..., description="List of file IDs to export")
    format: str = Field(default="zip", description="Export format")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    compression_level: int = Field(default=6, ge=1, le=9, description="Compression level")

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['zip', 'tar', 'tar.gz']
        if v not in allowed_formats:
            raise ValueError(f'Format must be one of: {allowed_formats}')
        return v


class FileExportResponse(BaseModel):
    """File export response schema."""
    export_path: str = Field(..., description="Export file path")
    format: str = Field(..., description="Export format")
    file_count: int = Field(..., description="Number of files exported")
    total_size: int = Field(..., description="Total size of exported files")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Export time")


class FileStatsResponse(BaseModel):
    """File statistics response schema."""
    total_files: int = Field(0, description="Total files")
    total_size: int = Field(0, description="Total size in bytes")
    files_by_type: Dict[str, int] = Field(default_factory=dict, description="Files by type")
    files_by_mime_type: Dict[str, int] = Field(default_factory=dict, description="Files by MIME type")
    processed_files: int = Field(0, description="Processed files")
    unprocessed_files: int = Field(0, description="Unprocessed files")
    upload_history: List[Dict[str, Any]] = Field(default_factory=list, description="Upload history")
    storage_usage: Dict[str, Any] = Field(default_factory=dict, description="Storage usage")


class FileQuota(BaseModel):
    """File quota schema."""
    max_files: int = Field(..., description="Maximum files allowed")
    max_storage_size: int = Field(..., description="Maximum storage size in bytes")
    current_files: int = Field(0, description="Current file count")
    current_storage_size: int = Field(0, description="Current storage size in bytes")
    files_remaining: int = Field(..., description="Files remaining")
    storage_remaining: int = Field(..., description="Storage remaining in bytes")
    quota_percentage: float = Field(..., description="Quota usage percentage")


class FileProcessingTemplate(BaseModel):
    """File processing template schema."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    processing_type: str = Field(..., description="Processing type")
    default_options: Dict[str, Any] = Field(..., description="Default options")
    supported_mime_types: List[str] = Field(..., description="Supported MIME types")
    is_builtin: bool = Field(default=True, description="Is built-in template")
    category: str = Field(..., description="Template category")


class FileProcessingHistory(BaseModel):
    """File processing history schema."""
    id: int = Field(..., description="History ID")
    file_id: int = Field(..., description="File ID")
    processing_type: str = Field(..., description="Processing type")
    status: str = Field(..., description="Processing status")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Processing result")
    error_message: Optional[str] = Field(None, description="Error message if any")
    options_used: Dict[str, Any] = Field(..., description="Options used")

    class Config:
        from_attributes = True


class FileValidationResult(BaseModel):
    """File validation result schema."""
    is_valid: bool = Field(..., description="Validation result")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    file_info: Optional[Dict[str, Any]] = Field(None, description="File information")
    security_scan: Optional[Dict[str, Any]] = Field(None, description="Security scan results")


class FileBatchOperation(BaseModel):
    """File batch operation schema."""
    operation_type: str = Field(..., description="Operation type")
    file_ids: List[int] = Field(..., description="List of file IDs")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")

    @validator('operation_type')
    def validate_operation_type(cls, v):
        allowed_types = ['delete', 'process', 'move', 'copy', 'compress']
        if v not in allowed_types:
            raise ValueError(f'Operation type must be one of: {allowed_types}')
        return v


class FileBatchOperationResponse(BaseModel):
    """File batch operation response schema."""
    operation_type: str = Field(..., description="Operation type")
    total_files: int = Field(..., description="Total files")
    successful_operations: int = Field(0, description="Successful operations")
    failed_operations: int = Field(0, description="Failed operations")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Operation results")
    execution_time: float = Field(..., description="Execution time in seconds")
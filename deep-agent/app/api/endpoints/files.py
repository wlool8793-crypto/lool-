"""
File management endpoints for the Deep Agent application.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models import User, FileUpload, Conversation
from app.schemas.file import (
    FileUploadResponse, FileListResponse, FileMetadataResponse,
    FileProcessRequest, FileProcessResponse
)
from app.services.file import FileService
from app.api.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file."""
    file_service = FileService(db)

    # Verify conversation belongs to user if provided
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Create file upload record
    file_record = file_service.create_file_upload(
        user_id=current_user.id,
        conversation_id=conversation_id,
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        file_path=str(file_path),
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type or "application/octet-stream"
    )

    return FileUploadResponse.from_orm(file_record)


@router.get("/", response_model=List[FileListResponse])
async def get_user_files(
    conversation_id: Optional[int] = None,
    file_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files uploaded by the user."""
    file_service = FileService(db)

    # Verify conversation belongs to user if provided
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    files = file_service.get_user_files(
        user_id=current_user.id,
        conversation_id=conversation_id,
        file_type=file_type,
        skip=skip,
        limit=limit
    )
    return [FileListResponse.from_orm(file) for file in files]


@router.get("/{file_id}", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file metadata."""
    file_service = FileService(db)
    file_record = file_service.get_file_by_id(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return FileMetadataResponse.from_orm(file_record)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file."""
    file_service = FileService(db)
    file_record = file_service.get_file_by_id(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not os.path.exists(file_record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    return FileResponse(
        path=file_record.file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file."""
    file_service = FileService(db)
    file_record = file_service.get_file_by_id(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Delete file from disk
    try:
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file from disk: {str(e)}"
        )

    # Delete database record
    file_service.delete_file(file_id)
    return {"message": "File deleted successfully"}


@router.post("/{file_id}/process", response_model=FileProcessResponse)
async def process_file(
    file_id: int,
    request: FileProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a file for analysis or extraction."""
    file_service = FileService(db)
    file_record = file_service.get_file_by_id(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        result = await file_service.process_file(
            file_id=file_id,
            processing_type=request.processing_type,
            options=request.options
        )

        return FileProcessResponse(
            file_id=file_id,
            processing_type=request.processing_type,
            success=result["success"],
            result=result.get("result"),
            execution_time=result.get("execution_time", 0),
            error_message=result.get("error_message")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )


@router.get("/types/available")
async def get_available_file_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available file processing types."""
    file_service = FileService(db)
    processing_types = file_service.get_available_processing_types()
    return {
        "processing_types": processing_types,
        "supported_mime_types": [
            "text/plain",
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/json",
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
    }


@router.get("/stats/user")
async def get_user_file_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file upload statistics for the user."""
    file_service = FileService(db)
    stats = file_service.get_user_file_stats(current_user.id)
    return {
        "user_id": current_user.id,
        "total_files": stats["total_files"],
        "total_size": stats["total_size"],
        "files_by_type": stats["files_by_type"],
        "processed_files": stats["processed_files"],
        "upload_history": stats["upload_history"]
    }


@router.post("/batch-upload")
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    conversation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple files in batch."""
    file_service = FileService(db)

    # Verify conversation belongs to user if provided
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)

    results = []
    for file in files:
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Create file upload record
            file_record = file_service.create_file_upload(
                user_id=current_user.id,
                conversation_id=conversation_id,
                filename=unique_filename,
                original_filename=file.filename or "unknown",
                file_path=str(file_path),
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type or "application/octet-stream"
            )

            results.append({
                "filename": file.filename,
                "file_id": file_record.id,
                "success": True,
                "error": None
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "file_id": None,
                "success": False,
                "error": str(e)
            })

    return {
        "batch_id": f"batch_{current_user.id}_{len(results)}",
        "total_files": len(files),
        "successful_uploads": sum(1 for r in results if r["success"]),
        "failed_uploads": sum(1 for r in results if not r["success"]),
        "results": results
    }
"""
File service for the Deep Agent application.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from pathlib import Path
from app.models import FileUpload
from app.core.config import settings


class FileService:
    """Service for file management and processing."""

    def __init__(self, db: Session):
        self.db = db

    def get_file_by_id(self, file_id: int) -> Optional[FileUpload]:
        """Get file by ID."""
        return self.db.query(FileUpload).filter(FileUpload.id == file_id).first()

    def get_user_files(
        self,
        user_id: int,
        conversation_id: Optional[int] = None,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[FileUpload]:
        """Get files for a user with optional filters."""
        query = self.db.query(FileUpload).filter(FileUpload.user_id == user_id)

        if conversation_id:
            query = query.filter(FileUpload.conversation_id == conversation_id)

        if file_type:
            query = query.filter(FileUpload.file_type == file_type)

        return query.order_by(FileUpload.created_at.desc()).offset(skip).limit(limit).all()

    def create_file_upload(
        self,
        user_id: int,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        conversation_id: Optional[int] = None
    ) -> FileUpload:
        """Create a new file upload record."""
        # Determine file type
        file_type = self._determine_file_type(mime_type, filename)

        file_upload = FileUpload(
            user_id=user_id,
            conversation_id=conversation_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_type=file_type
        )
        self.db.add(file_upload)
        self.db.commit()
        self.db.refresh(file_upload)
        return file_upload

    def delete_file(self, file_id: int) -> bool:
        """Delete a file record."""
        file_upload = self.get_file_by_id(file_id)
        if not file_upload:
            return False

        self.db.delete(file_upload)
        self.db.commit()
        return True

    async def process_file(
        self,
        file_id: int,
        processing_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a file for analysis or extraction."""
        file_upload = self.get_file_by_id(file_id)
        if not file_upload:
            raise ValueError("File not found")

        start_time = datetime.utcnow()

        try:
            # Simulate file processing
            result = await self._execute_file_processing(
                file_upload.file_path,
                processing_type,
                options or {}
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Update file record
            file_upload.processed = True
            file_upload.metadata = file_upload.metadata or {}
            file_upload.metadata["processing_history"] = file_upload.metadata.get("processing_history", [])
            file_upload.metadata["processing_history"].append({
                "type": processing_type,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_time": execution_time,
                "options": options,
                "result_summary": self._get_result_summary(result)
            })
            self.db.commit()

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }

        except Exception as e:
            return {
                "success": False,
                "result": None,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "error_message": str(e)
            }

    async def _execute_file_processing(
        self,
        file_path: str,
        processing_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual file processing."""
        import asyncio

        # Simulate processing time
        await asyncio.sleep(0.5)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if processing_type == "text_extraction":
            # Simulate text extraction
            return {
                "extracted_text": "Sample extracted text content from file",
                "text_length": 1024,
                "language": "en",
                "confidence": 0.95
            }

        elif processing_type == "image_analysis":
            # Simulate image analysis
            return {
                "objects": ["object1", "object2"],
                "description": "Sample image description",
                "colors": ["red", "blue", "green"],
                "dimensions": {"width": 800, "height": 600}
            }

        elif processing_type == "document_parsing":
            # Simulate document parsing
            return {
                "pages": 5,
                "text_content": "Parsed document content",
                "metadata": {
                    "title": "Document Title",
                    "author": "Unknown",
                    "created_date": "2023-01-01"
                }
            }

        elif processing_type == "sentiment_analysis":
            # Simulate sentiment analysis
            return {
                "sentiment": "positive",
                "confidence": 0.85,
                "emotions": ["joy", "trust"],
                "text_sample": "Sample text from file"
            }

        elif processing_type == "entity_extraction":
            # Simulate entity extraction
            return {
                "entities": [
                    {"text": "Entity 1", "type": "PERSON", "confidence": 0.9},
                    {"text": "Entity 2", "type": "ORGANIZATION", "confidence": 0.85}
                ],
                "total_entities": 2
            }

        elif processing_type == "content_summarization":
            # Simulate content summarization
            return {
                "summary": "This is a summary of the file content",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "compression_ratio": 0.3
            }

        else:
            raise ValueError(f"Unsupported processing type: {processing_type}")

    def _determine_file_type(self, mime_type: str, filename: str) -> str:
        """Determine file type based on MIME type and filename."""
        mime_type = mime_type.lower()

        if mime_type.startswith("text/"):
            return "document"
        elif mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("application/"):
            if "pdf" in mime_type or "document" in mime_type or "text" in mime_type:
                return "document"
            elif "json" in mime_type or "xml" in mime_type:
                return "document"
        else:
            # Check file extension
            ext = Path(filename).suffix.lower()
            document_extensions = ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
            audio_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.aac']
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']

            if ext in document_extensions:
                return "document"
            elif ext in image_extensions:
                return "image"
            elif ext in audio_extensions:
                return "audio"
            elif ext in video_extensions:
                return "video"

        return "other"

    def _get_result_summary(self, result: Dict[str, Any]) -> str:
        """Get a summary of the processing result."""
        if "extracted_text" in result:
            return f"Extracted {result.get('text_length', 0)} characters"
        elif "objects" in result:
            return f"Found {len(result.get('objects', []))} objects"
        elif "sentiment" in result:
            return f"Sentiment: {result.get('sentiment', 'unknown')}"
        elif "entities" in result:
            return f"Extracted {len(result.get('entities', []))} entities"
        elif "summary" in result:
            return f"Generated summary with {len(result.get('key_points', []))} key points"
        else:
            return "Processing completed"

    def get_user_file_stats(self, user_id: int) -> Dict[str, Any]:
        """Get file upload statistics for a user."""
        files = self.db.query(FileUpload).filter(FileUpload.user_id == user_id).all()

        total_files = len(files)
        total_size = sum(f.file_size for f in files)

        # Files by type
        files_by_type = {}
        for file in files:
            file_type = file.file_type
            files_by_type[file_type] = files_by_type.get(file_type, 0) + 1

        # Processed files
        processed_files = len([f for f in files if f.processed])

        # Upload history (last 7 days)
        upload_history = []
        from datetime import timedelta
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            daily_files = len([f for f in files if f.created_at.date() == date.date()])
            upload_history.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": daily_files
            })

        return {
            "total_files": total_files,
            "total_size": total_size,
            "files_by_type": files_by_type,
            "processed_files": processed_files,
            "unprocessed_files": total_files - processed_files,
            "upload_history": upload_history
        }

    def get_available_processing_types(self) -> List[str]:
        """Get available file processing types."""
        return [
            "text_extraction",
            "image_analysis",
            "document_parsing",
            "sentiment_analysis",
            "entity_extraction",
            "content_summarization"
        ]

    def search_files(
        self,
        user_id: int,
        query: str,
        file_type: Optional[str] = None,
        mime_type: Optional[str] = None,
        processed: Optional[bool] = None,
        conversation_id: Optional[int] = None,
        limit: int = 50
    ) -> List[FileUpload]:
        """Search files based on various criteria."""
        search_query = self.db.query(FileUpload).filter(FileUpload.user_id == user_id)

        if file_type:
            search_query = search_query.filter(FileUpload.file_type == file_type)

        if mime_type:
            search_query = search_query.filter(FileUpload.mime_type.ilike(f"%{mime_type}%"))

        if processed is not None:
            search_query = search_query.filter(FileUpload.processed == processed)

        if conversation_id:
            search_query = search_query.filter(FileUpload.conversation_id == conversation_id)

        # Search in filename and original filename
        search_pattern = f"%{query}%"
        search_query = search_query.filter(
            (FileUpload.filename.ilike(search_pattern)) |
            (FileUpload.original_filename.ilike(search_pattern))
        )

        return search_query.order_by(FileUpload.created_at.desc()).limit(limit).all()

    def get_storage_usage(self, user_id: int) -> Dict[str, Any]:
        """Get storage usage statistics for a user."""
        files = self.db.query(FileUpload).filter(FileUpload.user_id == user_id).all()

        total_size = sum(f.file_size for f in files)
        max_storage_size = settings.max_file_size * 100  # 100 files max as example

        return {
            "total_size": total_size,
            "max_size": max_storage_size,
            "used_percentage": (total_size / max_storage_size) * 100 if max_storage_size > 0 else 0,
            "remaining_size": max(0, max_storage_size - total_size),
            "file_count": len(files)
        }
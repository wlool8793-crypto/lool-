"""
Logging configuration for Legal RAG Extraction System (Phase 3)
Structured JSON logging for production monitoring
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Outputs logs in JSON format for easy parsing by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""

        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "document_id"):
            log_data["document_id"] = record.document_id

        if hasattr(record, "extraction_stage"):
            log_data["extraction_stage"] = record.extraction_stage

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if hasattr(record, "error_category"):
            log_data["error_category"] = record.error_category

        # Add any other custom attributes
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info", "document_id", "extraction_stage",
                          "duration_ms", "error_category"]:
                try:
                    json.dumps(value)  # Test if JSON serializable
                    log_data[key] = value
                except (TypeError, ValueError):
                    pass

        return json.dumps(log_data)


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for extraction system.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Whether to log to console
        enable_file: Whether to log to file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """

    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (human-readable)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)

    # File handler (JSON format)
    if enable_file:
        # Main extraction log
        extraction_log = log_path / "extraction.json"
        extraction_handler = logging.handlers.RotatingFileHandler(
            extraction_log,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        extraction_handler.setLevel(logging.DEBUG)
        extraction_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(extraction_handler)

        # Error log (errors only)
        error_log = log_path / "errors.json"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)

    # Set specific log levels for modules
    logging.getLogger("PIL").setLevel(logging.WARNING)  # Suppress PIL debug logs
    logging.getLogger("pdfminer").setLevel(logging.WARNING)  # Suppress pdfminer debug logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # Suppress urllib3 debug logs


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class ExtractionLogger:
    """
    Convenience wrapper for extraction-specific logging.
    Automatically adds extraction context to log messages.
    """

    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    def log_extraction_start(self, document_id: str):
        """Log extraction start"""
        self.logger.info(
            f"Starting extraction for document {document_id}",
            extra={"document_id": document_id, "extraction_stage": "start"}
        )

    def log_extraction_complete(self, document_id: str, duration_ms: int, status: str):
        """Log extraction completion"""
        self.logger.info(
            f"Extraction complete for {document_id}: {status}",
            extra={
                "document_id": document_id,
                "extraction_stage": "complete",
                "duration_ms": duration_ms,
                "status": status
            }
        )

    def log_stage_start(self, document_id: str, stage_name: str):
        """Log stage start"""
        self.logger.debug(
            f"Starting stage: {stage_name}",
            extra={"document_id": document_id, "extraction_stage": stage_name}
        )

    def log_stage_complete(self, document_id: str, stage_name: str, duration_ms: int):
        """Log stage completion"""
        self.logger.debug(
            f"Completed stage: {stage_name}",
            extra={
                "document_id": document_id,
                "extraction_stage": stage_name,
                "duration_ms": duration_ms
            }
        )

    def log_error(self, document_id: str, error: Exception, error_category: str):
        """Log extraction error"""
        self.logger.error(
            f"Extraction error: {str(error)}",
            extra={
                "document_id": document_id,
                "error_category": error_category,
                "error_type": type(error).__name__
            },
            exc_info=True
        )

    def log_warning(self, document_id: str, message: str, **kwargs):
        """Log extraction warning"""
        self.logger.warning(
            message,
            extra={"document_id": document_id, **kwargs}
        )

    def log_quality_score(self, document_id: str, quality_score: float, validation_status: str):
        """Log quality score"""
        self.logger.info(
            f"Quality score: {quality_score:.2f} ({validation_status})",
            extra={
                "document_id": document_id,
                "quality_score": quality_score,
                "validation_status": validation_status
            }
        )


# Initialize logging on module import
setup_logging()

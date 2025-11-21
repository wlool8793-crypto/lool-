"""
Configuration Schema Module
Defines the structure and validation rules for application configuration.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Valid log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration schema"""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

    def validate(self) -> List[str]:
        """Validate database configuration"""
        errors = []
        if not self.url:
            errors.append("Database URL is required")
        if self.pool_size < 1:
            errors.append("Pool size must be at least 1")
        if self.max_overflow < 0:
            errors.append("Max overflow cannot be negative")
        if self.pool_timeout < 1:
            errors.append("Pool timeout must be at least 1 second")
        return errors


@dataclass
class RateLimitConfig:
    """Rate limiting configuration schema"""
    request_delay: int = 2
    retry_delay_multiplier: int = 2
    max_retry_attempts: int = 3
    delay_between_pages: int = 1
    delay_between_courts: int = 5

    def validate(self) -> List[str]:
        """Validate rate limit configuration"""
        errors = []
        if self.request_delay < 0:
            errors.append("Request delay cannot be negative")
        if self.retry_delay_multiplier < 1:
            errors.append("Retry delay multiplier must be at least 1")
        if self.max_retry_attempts < 1:
            errors.append("Max retry attempts must be at least 1")
        return errors


@dataclass
class TimeoutConfig:
    """Timeout configuration schema"""
    request_timeout: int = 90
    pdf_download_timeout: int = 120
    general_timeout: int = 10

    def validate(self) -> List[str]:
        """Validate timeout configuration"""
        errors = []
        if self.request_timeout < 1:
            errors.append("Request timeout must be at least 1 second")
        if self.pdf_download_timeout < 1:
            errors.append("PDF download timeout must be at least 1 second")
        if self.general_timeout < 1:
            errors.append("General timeout must be at least 1 second")
        return errors


@dataclass
class PDFConfig:
    """PDF download and validation configuration schema"""
    enabled: bool = True
    download_timeout: int = 120
    validate_file: bool = True
    validate_pdf_header: bool = True
    min_file_size: int = 1024
    max_retries: int = 3
    skip_if_exists: bool = True
    chunk_size: int = 8192

    def validate(self) -> List[str]:
        """Validate PDF configuration"""
        errors = []
        if self.download_timeout < 1:
            errors.append("Download timeout must be at least 1 second")
        if self.min_file_size < 0:
            errors.append("Minimum file size cannot be negative")
        if self.max_retries < 1:
            errors.append("Max retries must be at least 1")
        if self.chunk_size < 1024:
            errors.append("Chunk size should be at least 1024 bytes")
        return errors


@dataclass
class BatchConfig:
    """Batch processing configuration schema"""
    batch_size: int = 50
    max_concurrent_workers: int = 20
    db_query_limit: int = 100
    url_tracker_limit: int = 1000

    def validate(self) -> List[str]:
        """Validate batch configuration"""
        errors = []
        if self.batch_size < 1:
            errors.append("Batch size must be at least 1")
        if self.max_concurrent_workers < 1:
            errors.append("Max concurrent workers must be at least 1")
        if self.db_query_limit < 1:
            errors.append("DB query limit must be at least 1")
        if self.url_tracker_limit < 1:
            errors.append("URL tracker limit must be at least 1")
        return errors


@dataclass
class CheckpointConfig:
    """Checkpoint and progress tracking configuration schema"""
    checkpoint_interval: int = 100
    heartbeat_interval: int = 60
    report_interval: int = 1000
    save_interval: int = 500

    def validate(self) -> List[str]:
        """Validate checkpoint configuration"""
        errors = []
        if self.checkpoint_interval < 1:
            errors.append("Checkpoint interval must be at least 1")
        if self.heartbeat_interval < 1:
            errors.append("Heartbeat interval must be at least 1")
        if self.report_interval < 1:
            errors.append("Report interval must be at least 1")
        if self.save_interval < 1:
            errors.append("Save interval must be at least 1")
        return errors


@dataclass
class StorageConfig:
    """Storage configuration schema"""
    pdf_path: str = "./data/pdfs"
    database_path: str = "./data/indiankanoon.db"
    checkpoint_path: str = "./data/checkpoints"
    reports_path: str = "./reports"
    logs_path: str = "./logs"
    max_disk_space_gb: int = 500
    min_free_space_gb: int = 50
    auto_pause_on_low_space: bool = True
    auto_cleanup_failed_downloads: bool = True

    def validate(self) -> List[str]:
        """Validate storage configuration"""
        errors = []
        if not self.pdf_path:
            errors.append("PDF path is required")
        if self.max_disk_space_gb < 1:
            errors.append("Max disk space must be at least 1 GB")
        if self.min_free_space_gb < 0:
            errors.append("Min free space cannot be negative")
        if self.min_free_space_gb >= self.max_disk_space_gb:
            errors.append("Min free space must be less than max disk space")
        return errors


@dataclass
class ScraperConfig:
    """Scraper configuration schema"""
    base_url: str = "https://indiankanoon.org"
    headless_mode: bool = True
    delay: int = 2
    max_pages: int = 10
    results_per_page: int = 10
    max_pagination_check: int = 100
    window_width: int = 1920
    window_height: int = 1080

    def validate(self) -> List[str]:
        """Validate scraper configuration"""
        errors = []
        if not self.base_url:
            errors.append("Base URL is required")
        if not self.base_url.startswith(('http://', 'https://')):
            errors.append("Base URL must start with http:// or https://")
        if self.delay < 0:
            errors.append("Delay cannot be negative")
        if self.max_pages < 1:
            errors.append("Max pages must be at least 1")
        if self.results_per_page < 1:
            errors.append("Results per page must be at least 1")
        return errors


@dataclass
class ParallelConfig:
    """Parallel processing configuration schema"""
    parallel_courts: int = 3
    parallel_years: int = 2

    def validate(self) -> List[str]:
        """Validate parallel configuration"""
        errors = []
        if self.parallel_courts < 1:
            errors.append("Parallel courts must be at least 1")
        if self.parallel_years < 1:
            errors.append("Parallel years must be at least 1")
        return errors


@dataclass
class YearRangeConfig:
    """Year range configuration schema"""
    start_year: int = 2020
    end_year: int = 2024
    historical_start_year: int = 1950
    historical_end_year: int = 2014
    historical_batch_years: int = 5

    def validate(self) -> List[str]:
        """Validate year range configuration"""
        errors = []
        if self.start_year > self.end_year:
            errors.append("Start year must be before or equal to end year")
        if self.historical_start_year > self.historical_end_year:
            errors.append("Historical start year must be before or equal to historical end year")
        if self.historical_batch_years < 1:
            errors.append("Historical batch years must be at least 1")
        if self.start_year < 1900 or self.start_year > 2100:
            errors.append("Start year must be between 1900 and 2100")
        if self.end_year < 1900 or self.end_year > 2100:
            errors.append("End year must be between 1900 and 2100")
        return errors


@dataclass
class LoggingConfig:
    """Logging configuration schema"""
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    log_file_path: str = "./logs/scraper.log"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"

    def validate(self) -> List[str]:
        """Validate logging configuration"""
        errors = []
        valid_levels = [level.value for level in LogLevel]
        if self.log_level not in valid_levels:
            errors.append(f"Log level must be one of: {', '.join(valid_levels)}")
        if not self.log_to_file and not self.log_to_console:
            errors.append("At least one logging output (file or console) must be enabled")
        return errors


@dataclass
class AppConfig:
    """Main application configuration schema"""
    environment: str = "development"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    pdf: PDFConfig = field(default_factory=PDFConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    parallel: ParallelConfig = field(default_factory=ParallelConfig)
    year_range: YearRangeConfig = field(default_factory=YearRangeConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def validate(self) -> Dict[str, List[str]]:
        """
        Validate entire configuration

        Returns:
            Dictionary mapping section names to lists of error messages
        """
        all_errors = {}

        # Validate environment
        valid_environments = [env.value for env in Environment]
        if self.environment not in valid_environments:
            all_errors['environment'] = [f"Environment must be one of: {', '.join(valid_environments)}"]

        # Validate each section
        sections = {
            'database': self.database,
            'rate_limit': self.rate_limit,
            'timeouts': self.timeouts,
            'pdf': self.pdf,
            'batch': self.batch,
            'checkpoint': self.checkpoint,
            'storage': self.storage,
            'scraper': self.scraper,
            'parallel': self.parallel,
            'year_range': self.year_range,
            'logging': self.logging,
        }

        for section_name, section_config in sections.items():
            errors = section_config.validate()
            if errors:
                all_errors[section_name] = errors

        return all_errors

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        errors = self.validate()
        return len(errors) == 0

    def get_validation_summary(self) -> str:
        """Get a human-readable validation summary"""
        errors = self.validate()
        if not errors:
            return "Configuration is valid"

        summary = ["Configuration validation errors:"]
        for section, error_list in errors.items():
            summary.append(f"\n[{section}]")
            for error in error_list:
                summary.append(f"  - {error}")

        return "\n".join(summary)

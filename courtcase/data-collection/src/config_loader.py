"""
Configuration Loader Module
Unified configuration loading from environment variables with validation.
Simplified version that doesn't depend on complex schemas.
"""

import os
from pathlib import Path
from typing import Any, Optional, Dict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Simple configuration loader with environment variable support.
    Provides type-safe configuration access with defaults.
    """

    def __init__(self, env_file: str = '.env', auto_load: bool = True):
        """
        Initialize configuration loader.

        Args:
            env_file: Path to .env file
            auto_load: Automatically load .env file if it exists
        """
        self.env_file = env_file
        self._loaded = False

        if auto_load:
            self.load()

    def load(self):
        """Load environment variables from .env file."""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {self.env_file}")
            self._loaded = True
        else:
            logger.warning(f"Environment file not found: {self.env_file}")

    def get_string(self, key: str, default: str = '', required: bool = False) -> str:
        """
        Get string configuration value.

        Args:
            key: Environment variable name
            default: Default value if not found
            required: Raise error if not found

        Returns:
            Configuration value
        """
        value = os.getenv(key, default)
        if required and not value:
            raise ValueError(f"Required configuration key not found: {key}")
        return value

    def get_int(self, key: str, default: int = 0, required: bool = False) -> int:
        """Get integer configuration value."""
        value = os.getenv(key)
        if value is None:
            if required:
                raise ValueError(f"Required configuration key not found: {key}")
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default {default}")
            return default

    def get_float(self, key: str, default: float = 0.0, required: bool = False) -> float:
        """Get float configuration value."""
        value = os.getenv(key)
        if value is None:
            if required:
                raise ValueError(f"Required configuration key not found: {key}")
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}, using default {default}")
            return default

    def get_bool(self, key: str, default: bool = False, required: bool = False) -> bool:
        """Get boolean configuration value."""
        value = os.getenv(key)
        if value is None:
            if required:
                raise ValueError(f"Required configuration key not found: {key}")
            return default

        # Handle boolean strings
        return value.lower() in ('true', 'yes', '1', 'on')

    def get_path(self, key: str, default: str = '', required: bool = False) -> Path:
        """Get path configuration value."""
        value = self.get_string(key, default, required)
        return Path(value)


class AppConfig:
    """
    Application configuration with common settings.
    Centralizes all environment variable access.
    """

    def __init__(self, loader: Optional[ConfigLoader] = None):
        """
        Initialize application configuration.

        Args:
            loader: Optional ConfigLoader instance
        """
        self.loader = loader or ConfigLoader()

    # Database Configuration
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.loader.get_string('DATABASE_URL', 'sqlite:///data/indiankanoon.db')

    # Logging Configuration
    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.loader.get_string('LOG_LEVEL', 'INFO')

    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.loader.get_string('LOG_FILE', 'logs/scraper.log')

    @property
    def log_dir(self) -> Path:
        """Get log directory."""
        return self.loader.get_path('LOG_DIR', 'logs')

    # PDF Download Configuration
    @property
    def download_pdfs(self) -> bool:
        """Check if PDF download is enabled."""
        return self.loader.get_bool('DOWNLOAD_PDFS', False)

    @property
    def pdf_download_path(self) -> Path:
        """Get PDF download directory."""
        return self.loader.get_path('PDF_DOWNLOAD_PATH', './data/pdfs')

    # Scraper Configuration
    @property
    def base_url(self) -> str:
        """Get base URL for scraping."""
        return self.loader.get_string('BASE_URL', 'https://indiankanoon.org')

    @property
    def headless_mode(self) -> bool:
        """Check if browser should run headless."""
        return self.loader.get_bool('HEADLESS_MODE', True)

    @property
    def request_delay(self) -> float:
        """Get request delay in seconds."""
        return self.loader.get_float('REQUEST_DELAY', 2.0)

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts."""
        return self.loader.get_int('MAX_RETRIES', 3)

    @property
    def timeout(self) -> int:
        """Get request timeout in seconds."""
        return self.loader.get_int('TIMEOUT', 30)

    # Performance Configuration
    @property
    def num_threads(self) -> int:
        """Get number of worker threads."""
        return self.loader.get_int('NUM_THREADS', 10)

    @property
    def batch_size(self) -> int:
        """Get batch processing size."""
        return self.loader.get_int('BATCH_SIZE', 50)

    # Storage Configuration
    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.loader.get_path('DATA_DIR', './data')

    @property
    def temp_dir(self) -> Path:
        """Get temporary directory."""
        return self.loader.get_path('TEMP_DIR', './data/temp')

    def ensure_directories(self):
        """Create all required directories."""
        directories = [
            self.log_dir,
            self.pdf_download_path,
            self.data_dir,
            self.temp_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def validate(self):
        """
        Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        # Ensure directories exist
        self.ensure_directories()

        # Validate values
        if self.request_delay < 0:
            raise ValueError("REQUEST_DELAY must be non-negative")

        if self.max_retries < 1:
            raise ValueError("MAX_RETRIES must be at least 1")

        if self.timeout < 1:
            raise ValueError("TIMEOUT must be at least 1 second")

        if self.num_threads < 1:
            raise ValueError("NUM_THREADS must be at least 1")

        logger.info("Configuration validated successfully")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.

        Returns:
            Dictionary with all configuration values
        """
        return {
            'database_url': self.database_url,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'log_dir': str(self.log_dir),
            'download_pdfs': self.download_pdfs,
            'pdf_download_path': str(self.pdf_download_path),
            'base_url': self.base_url,
            'headless_mode': self.headless_mode,
            'request_delay': self.request_delay,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'num_threads': self.num_threads,
            'batch_size': self.batch_size,
            'data_dir': str(self.data_dir),
            'temp_dir': str(self.temp_dir),
        }


# Global configuration instance
_config: Optional[AppConfig] = None


def load_config(env_file: str = '.env') -> AppConfig:
    """
    Load global configuration.

    Args:
        env_file: Path to .env file

    Returns:
        AppConfig instance
    """
    global _config
    loader = ConfigLoader(env_file=env_file)
    _config = AppConfig(loader)
    _config.validate()
    return _config


def get_config() -> AppConfig:
    """
    Get global configuration instance.

    Returns:
        AppConfig instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config():
    """Reset global configuration (useful for testing)."""
    global _config
    _config = None

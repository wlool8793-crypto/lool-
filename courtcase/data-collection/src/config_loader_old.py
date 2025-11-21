"""
Configuration Loader Module
Loads configuration from .env and config.yaml files with validation.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .config_schema import (
    AppConfig,
    DatabaseConfig,
    RateLimitConfig,
    TimeoutConfig,
    PDFConfig,
    BatchConfig,
    CheckpointConfig,
    StorageConfig,
    ScraperConfig,
    ParallelConfig,
    YearRangeConfig,
    LoggingConfig,
)
from .constants import (
    DEFAULT_DELAY_SECONDS,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY_MULTIPLIER,
    REQUEST_TIMEOUT_SECONDS,
    PDF_DOWNLOAD_TIMEOUT_SECONDS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_POOL_SIZE,
    MAX_POOL_OVERFLOW,
    POOL_TIMEOUT_SECONDS,
    POOL_RECYCLE_SECONDS,
    CHECKPOINT_INTERVAL,
    HEARTBEAT_INTERVAL,
    DEFAULT_START_YEAR,
    DEFAULT_END_YEAR,
)

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate application configuration from multiple sources"""

    def __init__(
        self,
        env_file: Optional[str] = None,
        yaml_file: Optional[str] = None,
        validate: bool = True
    ):
        """
        Initialize configuration loader

        Args:
            env_file: Path to .env file (default: .env in current directory)
            yaml_file: Path to YAML config file (default: config/config.yaml)
            validate: Whether to validate configuration on load
        """
        self.env_file = env_file or ".env"
        self.yaml_file = yaml_file or "config/config.yaml"
        self.validate = validate
        self.config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        """
        Load configuration from all sources

        Returns:
            AppConfig instance with merged configuration

        Raises:
            ValueError: If configuration is invalid
        """
        # Load environment variables
        env_config = self._load_env()

        # Load YAML configuration
        yaml_config = self._load_yaml()

        # Merge configurations (env takes precedence over yaml)
        merged_config = self._merge_configs(yaml_config, env_config)

        # Create AppConfig instance
        self.config = self._create_app_config(merged_config)

        # Validate if requested
        if self.validate:
            errors = self.config.validate()
            if errors:
                error_msg = self.config.get_validation_summary()
                logger.error(error_msg)
                raise ValueError(f"Configuration validation failed:\n{error_msg}")

        logger.info("Configuration loaded successfully")
        return self.config

    def _load_env(self) -> Dict[str, Any]:
        """Load configuration from .env file"""
        config = {}

        # Load .env file if it exists
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment variables from {self.env_file}")
        else:
            logger.warning(f".env file not found: {self.env_file}")

        # Database
        if os.getenv('DATABASE_URL'):
            config['database_url'] = os.getenv('DATABASE_URL')

        # Scraper
        if os.getenv('BASE_URL'):
            config['base_url'] = os.getenv('BASE_URL')
        if os.getenv('HEADLESS_MODE'):
            config['headless_mode'] = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        if os.getenv('REQUEST_DELAY'):
            config['request_delay'] = int(os.getenv('REQUEST_DELAY', DEFAULT_DELAY_SECONDS))

        # PDFs
        if os.getenv('DOWNLOAD_PDFS'):
            config['download_pdfs'] = os.getenv('DOWNLOAD_PDFS', 'true').lower() == 'true'
        if os.getenv('PDF_DOWNLOAD_PATH'):
            config['pdf_path'] = os.getenv('PDF_DOWNLOAD_PATH', './data/pdfs')

        # Years
        if os.getenv('START_YEAR'):
            config['start_year'] = int(os.getenv('START_YEAR', DEFAULT_START_YEAR))
        if os.getenv('END_YEAR'):
            config['end_year'] = int(os.getenv('END_YEAR', DEFAULT_END_YEAR))

        # Courts
        if os.getenv('COURTS'):
            config['courts'] = os.getenv('COURTS', 'supremecourt').split(',')

        # Logging
        if os.getenv('LOG_LEVEL'):
            config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
        if os.getenv('LOG_FILE'):
            config['log_file'] = os.getenv('LOG_FILE', './logs/scraper.log')

        # Environment
        if os.getenv('ENVIRONMENT'):
            config['environment'] = os.getenv('ENVIRONMENT', 'development')

        return config

    def _load_yaml(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config = {}

        if os.path.exists(self.yaml_file):
            try:
                with open(self.yaml_file, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                    if yaml_data:
                        config = yaml_data
                        logger.info(f"Loaded YAML configuration from {self.yaml_file}")
            except Exception as e:
                logger.error(f"Error loading YAML configuration: {e}")
        else:
            logger.warning(f"YAML config file not found: {self.yaml_file}")

        return config

    def _merge_configs(self, yaml_config: Dict, env_config: Dict) -> Dict:
        """
        Merge YAML and environment configurations
        Environment variables take precedence over YAML

        Args:
            yaml_config: Configuration from YAML file
            env_config: Configuration from environment variables

        Returns:
            Merged configuration dictionary
        """
        merged = yaml_config.copy()

        # Simple merge - env vars override yaml
        for key, value in env_config.items():
            merged[key] = value

        return merged

    def _create_app_config(self, config: Dict) -> AppConfig:
        """
        Create AppConfig instance from merged configuration

        Args:
            config: Merged configuration dictionary

        Returns:
            AppConfig instance
        """
        # Extract database config
        db_config = config.get('database', {})
        database = DatabaseConfig(
            url=config.get('database_url', db_config.get('url', 'sqlite:///data/indiankanoon.db')),
            pool_size=db_config.get('pool_size', DEFAULT_POOL_SIZE),
            max_overflow=db_config.get('max_overflow', MAX_POOL_OVERFLOW),
            pool_timeout=db_config.get('pool_timeout', POOL_TIMEOUT_SECONDS),
            pool_recycle=db_config.get('pool_recycle', POOL_RECYCLE_SECONDS),
            echo=db_config.get('echo', False),
        )

        # Extract performance/rate limit config
        perf_config = config.get('performance', {})
        rate_limit = RateLimitConfig(
            request_delay=config.get('request_delay', perf_config.get('delay_between_requests', DEFAULT_DELAY_SECONDS)),
            retry_delay_multiplier=perf_config.get('retry_backoff_multiplier', RETRY_DELAY_MULTIPLIER),
            max_retry_attempts=perf_config.get('retry_attempts', MAX_RETRY_ATTEMPTS),
            delay_between_pages=perf_config.get('delay_between_pages', 1),
            delay_between_courts=perf_config.get('delay_between_courts', 5),
        )

        # Extract timeout config
        timeouts = TimeoutConfig(
            request_timeout=perf_config.get('request_timeout', REQUEST_TIMEOUT_SECONDS),
            pdf_download_timeout=perf_config.get('pdf_download_timeout', PDF_DOWNLOAD_TIMEOUT_SECONDS),
            general_timeout=REQUEST_TIMEOUT_SECONDS,
        )

        # Extract PDF config
        pdf_config = config.get('pdfs', {})
        pdf = PDFConfig(
            enabled=config.get('download_pdfs', pdf_config.get('enabled', True)),
            download_timeout=pdf_config.get('download_timeout', PDF_DOWNLOAD_TIMEOUT_SECONDS),
            validate_file=pdf_config.get('validate_file', True),
            validate_pdf_header=pdf_config.get('validate_pdf_header', True),
            min_file_size=pdf_config.get('min_file_size', 1024),
            max_retries=pdf_config.get('max_retries', MAX_RETRY_ATTEMPTS),
            skip_if_exists=pdf_config.get('skip_if_exists', True),
        )

        # Extract batch config
        batch = BatchConfig(
            batch_size=DEFAULT_BATCH_SIZE,
        )

        # Extract checkpoint config
        monitoring_config = config.get('monitoring', {})
        checkpoint = CheckpointConfig(
            checkpoint_interval=monitoring_config.get('checkpoint_every', CHECKPOINT_INTERVAL),
            heartbeat_interval=HEARTBEAT_INTERVAL,
            report_interval=monitoring_config.get('generate_report_every', 1000),
            save_interval=monitoring_config.get('save_progress_every', 100),
        )

        # Extract storage config
        storage_config = config.get('storage', {})
        storage = StorageConfig(
            pdf_path=config.get('pdf_path', storage_config.get('pdf_path', './data/pdfs')),
            database_path=storage_config.get('database_path', './data/indiankanoon.db'),
            checkpoint_path=storage_config.get('checkpoint_path', './data/checkpoints'),
            reports_path=storage_config.get('reports_path', './reports'),
            logs_path=storage_config.get('logs_path', './logs'),
            max_disk_space_gb=storage_config.get('max_disk_space_gb', 500),
            min_free_space_gb=storage_config.get('min_free_space_gb', 50),
        )

        # Extract scraper config
        scraper = ScraperConfig(
            base_url=config.get('base_url', 'https://indiankanoon.org'),
            headless_mode=config.get('headless_mode', True),
            delay=config.get('request_delay', DEFAULT_DELAY_SECONDS),
        )

        # Extract parallel config
        parallel = ParallelConfig(
            parallel_courts=perf_config.get('parallel_courts', 3),
            parallel_years=perf_config.get('parallel_years', 2),
        )

        # Extract year range config
        year_range = YearRangeConfig(
            start_year=config.get('start_year', DEFAULT_START_YEAR),
            end_year=config.get('end_year', DEFAULT_END_YEAR),
        )

        # Extract logging config
        logging_config = LoggingConfig(
            log_level=config.get('log_level', monitoring_config.get('log_level', 'INFO')),
            log_to_file=monitoring_config.get('log_to_file', True),
            log_to_console=monitoring_config.get('log_to_console', True),
            log_file_path=config.get('log_file', './logs/scraper.log'),
        )

        # Create main AppConfig
        app_config = AppConfig(
            environment=config.get('environment', 'development'),
            database=database,
            rate_limit=rate_limit,
            timeouts=timeouts,
            pdf=pdf,
            batch=batch,
            checkpoint=checkpoint,
            storage=storage,
            scraper=scraper,
            parallel=parallel,
            year_range=year_range,
            logging=logging_config,
        )

        return app_config

    def get_config(self) -> AppConfig:
        """
        Get loaded configuration

        Returns:
            AppConfig instance

        Raises:
            RuntimeError: If configuration hasn't been loaded yet
        """
        if self.config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        return self.config

    def reload(self) -> AppConfig:
        """
        Reload configuration from files

        Returns:
            Reloaded AppConfig instance
        """
        return self.load()


# Global configuration instance
_global_config: Optional[AppConfig] = None


def load_config(
    env_file: Optional[str] = None,
    yaml_file: Optional[str] = None,
    validate: bool = True
) -> AppConfig:
    """
    Load global configuration

    Args:
        env_file: Path to .env file
        yaml_file: Path to YAML config file
        validate: Whether to validate configuration

    Returns:
        AppConfig instance
    """
    global _global_config
    loader = ConfigLoader(env_file=env_file, yaml_file=yaml_file, validate=validate)
    _global_config = loader.load()
    return _global_config


def get_config() -> AppConfig:
    """
    Get global configuration instance

    Returns:
        AppConfig instance

    Raises:
        RuntimeError: If configuration hasn't been loaded
    """
    global _global_config
    if _global_config is None:
        # Try to load with defaults
        _global_config = load_config()
    return _global_config


def reset_config():
    """Reset global configuration (useful for testing)"""
    global _global_config
    _global_config = None

"""
Logging Configuration Module
Centralized logging setup with structured formatting and multiple handlers.
Provides consistent logging configuration across the entire application.
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class LoggingConfig:
    """
    Centralized logging configuration manager.
    Provides structured logging with file and console handlers.
    """

    # Standard log format
    STANDARD_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    def __init__(
        self,
        log_dir: str = 'logs',
        log_level: str = 'INFO',
        log_format: str = STANDARD_FORMAT,
        app_name: str = 'app'
    ):
        """
        Initialize logging configuration.

        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Log message format
            app_name: Application name for log file naming
        """
        self.log_dir = Path(log_dir)
        self.log_level = self._parse_log_level(log_level)
        self.log_format = log_format
        self.app_name = app_name
        self.handlers: List[logging.Handler] = []

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _parse_log_level(self, level: str) -> int:
        """
        Parse log level string to logging constant.

        Args:
            level: Log level as string

        Returns:
            Logging level constant
        """
        level = level.upper()
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(level, logging.INFO)

    def setup_logging(
        self,
        console: bool = True,
        file: bool = True,
        timestamped_file: bool = False,
        file_name: Optional[str] = None
    ) -> logging.Logger:
        """
        Setup logging with console and/or file handlers.

        Args:
            console: Enable console (stdout) logging
            file: Enable file logging
            timestamped_file: Add timestamp to log filename
            file_name: Custom log filename (overrides app_name)

        Returns:
            Configured root logger
        """
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        # Remove existing handlers
        root_logger.handlers.clear()
        self.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(self.log_format)

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            self.handlers.append(console_handler)

        # File handler
        if file:
            if file_name:
                log_filename = file_name
            elif timestamped_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_filename = f"{self.app_name}_{timestamp}.log"
            else:
                log_filename = f"{self.app_name}.log"

            log_file_path = self.log_dir / log_filename

            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            self.handlers.append(file_handler)

        return root_logger

    def setup_module_logger(
        self,
        module_name: str,
        level: Optional[str] = None
    ) -> logging.Logger:
        """
        Setup a logger for a specific module.

        Args:
            module_name: Name of the module
            level: Optional custom log level for this module

        Returns:
            Configured module logger
        """
        logger = logging.getLogger(module_name)

        if level:
            logger.setLevel(self._parse_log_level(level))

        return logger

    def add_file_handler(
        self,
        filename: str,
        level: Optional[str] = None,
        format: Optional[str] = None
    ) -> logging.FileHandler:
        """
        Add an additional file handler to the root logger.

        Args:
            filename: Log filename
            level: Optional log level for this handler
            format: Optional custom format for this handler

        Returns:
            The created file handler
        """
        log_path = self.log_dir / filename

        handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        handler.setLevel(self._parse_log_level(level) if level else self.log_level)

        formatter = logging.Formatter(format if format else self.log_format)
        handler.setFormatter(formatter)

        logging.getLogger().addHandler(handler)
        self.handlers.append(handler)

        return handler

    def cleanup_handlers(self):
        """Close and remove all handlers."""
        root_logger = logging.getLogger()

        for handler in self.handlers:
            try:
                handler.close()
                root_logger.removeHandler(handler)
            except Exception as e:
                print(f"Error closing handler: {e}", file=sys.stderr)

        self.handlers.clear()

    @staticmethod
    def from_env(
        app_name: str = 'app',
        console: bool = True,
        file: bool = True,
        timestamped_file: bool = False
    ) -> 'LoggingConfig':
        """
        Create logging configuration from environment variables.

        Environment variables:
            LOG_DIR: Log directory path (default: 'logs')
            LOG_LEVEL: Log level (default: 'INFO')
            LOG_FILE: Log filename (optional)

        Args:
            app_name: Application name
            console: Enable console logging
            file: Enable file logging
            timestamped_file: Add timestamp to filename

        Returns:
            Configured LoggingConfig instance
        """
        log_dir = os.getenv('LOG_DIR', 'logs')
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE')

        config = LoggingConfig(
            log_dir=log_dir,
            log_level=log_level,
            app_name=app_name
        )

        config.setup_logging(
            console=console,
            file=file,
            timestamped_file=timestamped_file,
            file_name=log_file
        )

        return config


def setup_basic_logging(
    log_dir: str = 'logs',
    log_level: str = 'INFO',
    app_name: str = 'app',
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """
    Quick setup for basic logging configuration.

    Args:
        log_dir: Directory for log files
        log_level: Logging level
        app_name: Application name for log files
        console: Enable console logging
        file: Enable file logging

    Returns:
        Configured root logger
    """
    config = LoggingConfig(
        log_dir=log_dir,
        log_level=log_level,
        app_name=app_name
    )

    return config.setup_logging(console=console, file=file)


def setup_logging_from_env(
    app_name: str = 'app',
    console: bool = True,
    file: bool = True,
    timestamped_file: bool = False
) -> logging.Logger:
    """
    Quick setup for logging from environment variables.

    Args:
        app_name: Application name
        console: Enable console logging
        file: Enable file logging
        timestamped_file: Add timestamp to filename

    Returns:
        Configured root logger
    """
    config = LoggingConfig.from_env(
        app_name=app_name,
        console=console,
        file=file,
        timestamped_file=timestamped_file
    )

    return logging.getLogger()


# Convenience function for simple setup
def quick_setup(log_file: str = 'app.log', level: str = 'INFO'):
    """
    Simplest logging setup for quick scripts.

    Args:
        log_file: Log filename
        level: Log level

    Returns:
        Root logger
    """
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LoggingConfig.STANDARD_FORMAT,
        handlers=[
            logging.FileHandler(log_dir / log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger()

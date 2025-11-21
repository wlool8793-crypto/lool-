"""
IndianKanoon Production Scraper Module
High-performance scraping system for downloading 1.4M legal PDFs
"""

from .url_collector import URLCollector
from .drive_manager import DriveManager
from .download_manager import DownloadManager

__all__ = ['URLCollector', 'DriveManager', 'DownloadManager']
__version__ = '1.0.0'

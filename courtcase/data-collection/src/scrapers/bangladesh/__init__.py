"""
Bangladesh Legal Data Scrapers
Comprehensive modular scraping system for Bangladesh legal data from 62+ sources
"""

from .plugin_manager import PluginManager
from .source_registry import BangladeshSourceRegistry
from .base_scraper import BaseLegalScraper

__all__ = ['PluginManager', 'BangladeshSourceRegistry', 'BaseLegalScraper']
__version__ = '1.0.0'
"""
Sales Agent Scrapers Module

This module provides interfaces and adapters for various web scrapers
that can be used to collect lead data for the sales agent.
"""

from .web_scraper_adapter import WebScraperAdapter
from .base_scraper import BaseScraper, LeadData

__all__ = ['WebScraperAdapter', 'BaseScraper', 'LeadData']

"""
Base scraper interface for the sales agent system.

This module defines the abstract base class that all scrapers must implement,
ensuring a consistent interface for lead data collection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class LeadData:
    """Standardized lead data structure."""
    name: str
    company: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    source_url: Optional[str] = None
    scraped_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lead data to dictionary format."""
        return {
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'title': self.title,
            'industry': self.industry,
            'location': self.location,
            'description': self.description,
            'social_links': self.social_links or {},
            'source_url': self.source_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers in the sales agent system.
    
    This ensures a consistent interface for different scraping implementations
    and allows for easy swapping of scrapers without changing the main agent code.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scraper with optional configuration.
        
        Args:
            config: Configuration dictionary for the scraper
        """
        self.config = config or {}
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the scraper (e.g., start services, check dependencies).
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def scrape_leads(self, search_criteria: Dict[str, Any]) -> List[LeadData]:
        """
        Scrape leads based on search criteria.
        
        Args:
            search_criteria: Dictionary containing search parameters like:
                - keywords: List of search keywords
                - industry: Target industry
                - location: Geographic location
                - max_results: Maximum number of leads to return
                - additional_filters: Any additional filtering criteria
        
        Returns:
            List[LeadData]: List of scraped lead data
        """
        pass
    
    @abstractmethod
    def get_scraper_info(self) -> Dict[str, Any]:
        """
        Get information about the scraper.
        
        Returns:
            Dict containing scraper metadata like name, version, capabilities
        """
        pass
    
    def validate_search_criteria(self, search_criteria: Dict[str, Any]) -> bool:
        """
        Validate search criteria before scraping.
        
        Args:
            search_criteria: The search criteria to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['keywords']
        return all(field in search_criteria for field in required_fields)
    
    def cleanup(self) -> None:
        """
        Clean up resources used by the scraper.
        Override in subclasses if cleanup is needed.
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

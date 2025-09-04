"""
Web Scraper Adapter for Node.js Web Scraper

This module provides a Python interface to the Node.js web scraper backend,
converting the scraper's output into standardized LeadData objects.
"""

import json
import requests
import subprocess
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .base_scraper import BaseScraper, LeadData

logger = logging.getLogger(__name__)


class WebScraperAdapter(BaseScraper):
    """
    Python adapter for the Node.js web scraper.
    
    This class provides a Python interface to the existing Node.js web scraper,
    handling the communication and data transformation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the web scraper adapter.
        
        Args:
            config: Configuration dictionary containing:
                - scraper_port: Port for the Node.js scraper (default: 3001)
                - scraper_host: Host for the Node.js scraper (default: localhost)
                - scraper_path: Path to the webScraper directory
                - timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.scraper_port = self.config.get('scraper_port', 3001)
        self.scraper_host = self.config.get('scraper_host', 'localhost')
        self.scraper_path = self.config.get('scraper_path', '../webScraper/backend')
        self.timeout = self.config.get('timeout', 30)
        self.base_url = f"http://{self.scraper_host}:{self.scraper_port}"
        self.scraper_process = None
    
    def initialize(self) -> bool:
        """
        Initialize the web scraper by starting the Node.js backend.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check if scraper is already running
            if self._is_scraper_running():
                logger.info("Web scraper is already running")
                self.is_initialized = True
                return True
            
            # Start the Node.js scraper
            if not self._start_scraper():
                logger.error("Failed to start web scraper")
                return False
            
            # Wait for scraper to be ready
            if not self._wait_for_scraper():
                logger.error("Web scraper failed to start properly")
                return False
            
            self.is_initialized = True
            logger.info("Web scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing web scraper: {e}")
            return False
    
    def scrape_leads(self, search_criteria: Dict[str, Any]) -> List[LeadData]:
        """
        Scrape leads using the web scraper.
        
        Args:
            search_criteria: Dictionary containing:
                - keywords: List of search keywords
                - urls: List of URLs to scrape (optional)
                - max_results: Maximum number of results (default: 10)
                - industry: Target industry (optional)
                - location: Geographic location (optional)
        
        Returns:
            List[LeadData]: List of scraped lead data
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize web scraper")
        
        try:
            # Convert search criteria to scraper format
            scraper_request = self._build_scraper_request(search_criteria)
            
            # Make request to scraper
            response = requests.post(
                f"{self.base_url}/api/scrape",
                json=scraper_request,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            scraper_data = response.json()
            
            # Convert to LeadData objects
            leads = self._convert_to_leads(scraper_data, search_criteria)
            
            logger.info(f"Successfully scraped {len(leads)} leads")
            return leads
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to web scraper failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scraping leads: {e}")
            raise
    
    def get_scraper_info(self) -> Dict[str, Any]:
        """Get information about the web scraper."""
        return {
            'name': 'Web Scraper Adapter',
            'version': '1.0.0',
            'type': 'nodejs_adapter',
            'capabilities': [
                'web_scraping',
                'contact_extraction',
                'social_media_links',
                'content_analysis'
            ],
            'supported_data_types': [
                'emails',
                'phones',
                'headlines',
                'social_links',
                'prices',
                'contact_info'
            ]
        }
    
    def cleanup(self) -> None:
        """Clean up the scraper process."""
        if self.scraper_process:
            try:
                self.scraper_process.terminate()
                self.scraper_process.wait(timeout=5)
                logger.info("Web scraper process terminated")
            except subprocess.TimeoutExpired:
                self.scraper_process.kill()
                logger.warning("Web scraper process killed")
            except Exception as e:
                logger.error(f"Error cleaning up scraper process: {e}")
            finally:
                self.scraper_process = None
    
    def _is_scraper_running(self) -> bool:
        """Check if the scraper is already running."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _start_scraper(self) -> bool:
        """Start the Node.js scraper process."""
        try:
            scraper_dir = os.path.join(os.path.dirname(__file__), self.scraper_path)
            if not os.path.exists(scraper_dir):
                logger.error(f"Scraper directory not found: {scraper_dir}")
                return False
            
            # Start the Node.js process
            self.scraper_process = subprocess.Popen(
                ['node', 'index.js'],
                cwd=scraper_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Started web scraper process (PID: {self.scraper_process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scraper: {e}")
            return False
    
    def _wait_for_scraper(self, max_wait: int = 30) -> bool:
        """Wait for the scraper to be ready."""
        for i in range(max_wait):
            if self._is_scraper_running():
                return True
            time.sleep(1)
        return False
    
    def _build_scraper_request(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Build the request payload for the web scraper."""
        # Extract URLs from keywords or use default search URLs
        urls = search_criteria.get('urls', [])
        if not urls and 'keywords' in search_criteria:
            # Convert keywords to search URLs (this is a simplified approach)
            # In a real implementation, you might want to use search engines
            keywords = search_criteria['keywords']
            if isinstance(keywords, str):
                keywords = [keywords]
            
            # For demo purposes, we'll use some example URLs
            # In production, you'd want to implement proper search URL generation
            urls = [
                f"https://example.com/search?q={'+'.join(keywords)}",
                f"https://linkedin.com/search/results/companies/?keywords={'+'.join(keywords)}"
            ]
        
        return {
            'url': urls[0] if urls else 'https://example.com',  # Use first URL for now
            'scrapingRules': {
                'maxDepth': 2,
                'delay': 1000,
                'maxPages': search_criteria.get('max_results', 10),
                'respectRobots': True,
                'followLinks': True
            },
            'userIntent': 'lead_generation',
            'selectedDataTypes': {
                'text': True,
                'structured': True,
                'links': True
            },
            'filters': {
                'minTextLength': 10,
                'excludeNavigation': True
            },
            'scrapingMode': 'comprehensive'
        }
    
    def _convert_to_leads(self, scraper_data: Dict[str, Any], search_criteria: Dict[str, Any]) -> List[LeadData]:
        """Convert scraper output to LeadData objects."""
        leads = []
        scraped_items = scraper_data.get('scrapedData', [])
        
        # Group items by URL to create leads
        url_groups = {}
        for item in scraped_items:
            url = item.get('url', 'unknown')
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(item)
        
        # Create leads from grouped data
        for url, items in url_groups.items():
            lead_data = self._extract_lead_from_items(items, url, search_criteria)
            if lead_data:
                leads.append(lead_data)
        
        return leads
    
    def _extract_lead_from_items(self, items: List[Dict[str, Any]], url: str, search_criteria: Dict[str, Any]) -> Optional[LeadData]:
        """Extract lead information from scraped items."""
        # Extract different types of data
        emails = []
        phones = []
        headlines = []
        social_links = {}
        
        for item in items:
            item_type = item.get('type', '')
            
            if item_type == 'email':
                emails.append(item.get('value', ''))
            elif item_type == 'phone':
                phones.append(item.get('value', ''))
            elif item_type == 'headline':
                headlines.append(item.get('text', ''))
            elif item_type == 'social_link':
                platform = item.get('platform', 'unknown')
                social_links[platform] = item.get('url', '')
        
        # Create lead data
        if not headlines and not emails and not phones:
            return None
        
        # Use the first headline as company name, or generate from URL
        company = headlines[0] if headlines else self._extract_company_from_url(url)
        
        return LeadData(
            name=f"Contact at {company}",
            company=company,
            email=emails[0] if emails else None,
            phone=phones[0] if phones else None,
            website=url,
            description=' '.join(headlines[:3]),  # Use first 3 headlines as description
            social_links=social_links if social_links else None,
            source_url=url,
            scraped_at=datetime.now(),
            industry=search_criteria.get('industry'),
            location=search_criteria.get('location')
        )
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. and common TLDs
            company = domain.replace('www.', '').split('.')[0]
            return company.title()
        except:
            return "Unknown Company"

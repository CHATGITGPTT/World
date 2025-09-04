#!/usr/bin/env python3
"""
Data Agent
Handles data collection, web scraping, and data processing
"""

import asyncio
import json
import requests
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask

class DataAgent(BaseAgent):
    """Agent responsible for data collection and processing"""
    
    def __init__(self, services: Dict[str, Any]):
        super().__init__("data", services)
        
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process data-related tasks"""
        try:
            task_type = task.type
            description = task.description.lower()
            
            if task_type == "scrape_data" or "scrape" in description:
                return await self._scrape_data(task)
            elif "analyze" in description:
                return await self._analyze_data(task)
            elif "collect" in description:
                return await self._collect_data(task)
            else:
                return await self._general_data_task(task)
                
        except Exception as e:
            self.logger.error(f"Data task failed: {e}")
            return {"error": str(e)}
    
    async def _scrape_data(self, task: AgentTask) -> Dict[str, Any]:
        """Scrape data from web sources"""
        try:
            data = task.data
            url = data.get("url", "https://example.com")
            
            # Use the existing web scraper
            scraper_result = await self._use_web_scraper(url)
            
            # Save scraped data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = self.file_manager.base_path / "data" / "scraped" / f"scraped_data_{timestamp}.json"
            data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(data_file, 'w') as f:
                json.dump(scraper_result, f, indent=2)
            
            return {
                "success": True,
                "url": url,
                "data": scraper_result,
                "file_path": str(data_file),
                "records_count": len(scraper_result.get("scrapedData", []))
            }
            
        except Exception as e:
            return {"error": f"Data scraping failed: {e}"}
    
    async def _use_web_scraper(self, url: str) -> Dict[str, Any]:
        """Use the existing web scraper service"""
        try:
            # Try to use the Node.js scraper if available
            scraper_path = self.file_manager.base_path / "scrapers" / "webScraper" / "backend"
            
            if scraper_path.exists():
                # Use the existing scraper
                import subprocess
                import os
                
                # Change to scraper directory and run
                result = subprocess.run(
                    ["node", "scraper.js", url],
                    cwd=scraper_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
                else:
                    # Fallback to simple scraping
                    return await self._simple_scrape(url)
            else:
                # Fallback to simple scraping
                return await self._simple_scrape(url)
                
        except Exception as e:
            self.logger.warning(f"Web scraper failed, using fallback: {e}")
            return await self._simple_scrape(url)
    
    async def _simple_scrape(self, url: str) -> Dict[str, Any]:
        """Simple web scraping fallback"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Basic data extraction
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "headings": [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])],
                "links": [a.get('href') for a in soup.find_all('a', href=True)],
                "text_content": soup.get_text()[:1000],  # First 1000 chars
                "scraped_at": datetime.now().isoformat()
            }
            
            return {"scrapedData": [data]}
            
        except Exception as e:
            return {"error": f"Simple scraping failed: {e}"}
    
    async def _analyze_data(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze collected data"""
        try:
            data_source = task.data.get("data_source", "scraped_data")
            
            # Look for recent scraped data files
            scraped_dir = self.file_manager.base_path / "data" / "scraped"
            if scraped_dir.exists():
                data_files = list(scraped_dir.glob("*.json"))
                if data_files:
                    # Use the most recent file
                    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
                    
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                    
                    # Basic analysis
                    analysis = {
                        "file": str(latest_file),
                        "total_records": len(data.get("scrapedData", [])),
                        "data_types": self._analyze_data_types(data),
                        "summary": self._generate_data_summary(data),
                        "analyzed_at": datetime.now().isoformat()
                    }
                    
                    # Save analysis
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    analysis_file = self.file_manager.base_path / "data" / "analytics" / f"analysis_{timestamp}.json"
                    analysis_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(analysis_file, 'w') as f:
                        json.dump(analysis, f, indent=2)
                    
                    return {
                        "success": True,
                        "analysis": analysis,
                        "file_path": str(analysis_file)
                    }
            
            return {"error": "No data found to analyze"}
            
        except Exception as e:
            return {"error": f"Data analysis failed: {e}"}
    
    def _analyze_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data types in the scraped data"""
        scraped_data = data.get("scrapedData", [])
        
        if not scraped_data:
            return {"error": "No data to analyze"}
        
        # Analyze first record
        first_record = scraped_data[0]
        
        types_analysis = {}
        for key, value in first_record.items():
            if isinstance(value, str):
                types_analysis[key] = "text"
            elif isinstance(value, list):
                types_analysis[key] = "list"
            elif isinstance(value, dict):
                types_analysis[key] = "object"
            else:
                types_analysis[key] = "other"
        
        return types_analysis
    
    def _generate_data_summary(self, data: Dict[str, Any]) -> str:
        """Generate a summary of the data"""
        scraped_data = data.get("scrapedData", [])
        
        if not scraped_data:
            return "No data available"
        
        total_records = len(scraped_data)
        first_record = scraped_data[0]
        
        summary = f"Data Summary:\n"
        summary += f"- Total records: {total_records}\n"
        summary += f"- Fields: {', '.join(first_record.keys())}\n"
        
        if "title" in first_record:
            summary += f"- Sample title: {first_record['title'][:100]}...\n"
        
        if "headings" in first_record:
            summary += f"- Headings found: {len(first_record['headings'])}\n"
        
        if "links" in first_record:
            summary += f"- Links found: {len(first_record['links'])}\n"
        
        return summary
    
    async def _collect_data(self, task: AgentTask) -> Dict[str, Any]:
        """Collect data from various sources"""
        return {"message": "Data collection functionality not yet implemented"}
    
    async def _general_data_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle general data tasks"""
        return {
            "message": f"Data agent received task: {task.description}",
            "status": "processed"
        }

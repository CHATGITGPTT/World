"""
Market Intelligence Mode for Sales Agent

This module provides market intelligence capabilities by integrating
features from the ai-sales-agent implementation.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from ..ai_tools import GeminiTool
from ..scrapers import BaseScraper
from ..config.env_loader import get_config_from_env

logger = logging.getLogger(__name__)


class MarketIntelligenceMode:
    """
    Market Intelligence Mode - Adapted from ai-sales-agent implementation
    
    Provides real-time market data collection and AI-powered analysis
    without disrupting existing sales agent functionality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Market Intelligence Mode.
        
        Args:
            config: Configuration dictionary containing:
                - gemini_api_key: Google Gemini API key
                - targets: Dictionary with tickers, keywords, companies
                - output_dir: Output directory for results
        """
        self.config = config or {}
        
        # Get configuration from environment if not provided
        if not self.config:
            self.config = get_config_from_env()
        
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize AI tools
        api_key = self.config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
        self.gemini_tool = GeminiTool({'api_key': api_key}) if api_key else None
        
        # Initialize scrapers (will be populated based on targets)
        self.scrapers: List[BaseScraper] = []
        
        logger.info("Market Intelligence Mode initialized")
    
    def run(self, targets: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute market intelligence analysis.
        
        Args:
            targets: Optional targets override (tickers, keywords, companies)
        
        Returns:
            Dict containing analysis results and file paths
        """
        logger.info("📊 Starting Market Intelligence Mode")
        
        # Use provided targets or config targets
        analysis_targets = targets or self.config.get('targets', {})
        
        if not analysis_targets:
            logger.error("No targets specified for intelligence gathering")
            return {'error': 'No targets specified'}
        
        # Initialize scrapers based on targets
        self._initialize_scrapers(analysis_targets)
        
        if not self.scrapers:
            logger.warning("No scrapers initialized - no data sources available")
            return {'error': 'No data sources available'}
        
        # Collect data from all sources
        aggregated_data = self._collect_market_data()
        
        if not aggregated_data:
            logger.warning("No data collected from any source")
            return {'error': 'No data collected'}
        
        # Generate timestamp for file naming
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        # Save raw data
        raw_filename = f"market_results_raw_{timestamp}.json"
        raw_path = self._save_json(raw_filename, aggregated_data)
        logger.info(f"💾 Raw data saved: {raw_path}")
        
        # AI Analysis with Gemini
        analysis = None
        if self.gemini_tool:
            logger.info("🤖 Analyzing data with Gemini AI...")
            try:
                analysis = self._analyze_with_gemini(aggregated_data, analysis_targets)
                
                # Save analysis results
                analysis_filename = f"market_results_analysis_{timestamp}.json"
                analysis_path = self._save_json(analysis_filename, analysis)
                logger.info(f"📈 Analysis saved: {analysis_path}")
                
                # Generate executive summary CSV
                summary_filename = f"market_results_summary_{timestamp}.csv"
                summary_path = self._save_summary_csv(summary_filename, analysis)
                logger.info(f"📋 Summary saved: {summary_path}")
                
                # Print key insights to console
                self._print_key_insights(analysis)
                
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis = {'error': f'AI analysis failed: {e}'}
        else:
            logger.warning("Gemini API not configured - skipping AI analysis")
            analysis = {'error': 'Gemini API not configured'}
        
        logger.info("✅ Market intelligence mode completed successfully")
        
        return {
            'success': True,
            'raw_data_file': raw_path,
            'analysis_file': analysis_path if analysis and 'error' not in analysis else None,
            'summary_file': summary_path if analysis and 'error' not in analysis else None,
            'data_count': len(aggregated_data),
            'timestamp': timestamp,
            'analysis': analysis
        }
    
    def _initialize_scrapers(self, targets: Dict[str, Any]):
        """Initialize appropriate scrapers based on targets."""
        self.scrapers = []
        
        # For now, we'll use mock scrapers since the new scrapers aren't fully implemented
        # TODO: Integrate Google News scraper and financial scrapers when ready
        
        tickers = targets.get('tickers', [])
        keywords = targets.get('keywords', [])
        companies = targets.get('companies', [])
        
        if keywords or companies:
            # Mock news scraper for demonstration
            mock_scraper = MockNewsScraper(keywords + companies)
            self.scrapers.append(mock_scraper)
            logger.info(f"📰 Mock news scraper initialized for: {keywords + companies}")
        
        if tickers:
            # Mock financial scraper for demonstration
            mock_financial = MockFinancialScraper(tickers)
            self.scrapers.append(mock_financial)
            logger.info(f"💹 Mock financial scraper initialized for: {tickers}")
    
    def _collect_market_data(self) -> List[Dict[str, Any]]:
        """Collect data from all initialized scrapers."""
        aggregated_data = []
        
        for scraper in self.scrapers:
            scraper_name = scraper.__class__.__name__
            logger.info(f"🔍 Scraping with {scraper_name}...")
            
            try:
                data = scraper.scrape()
                aggregated_data.extend(data)
                logger.info(f"✅ {scraper_name}: collected {len(data)} items")
            except Exception as e:
                logger.error(f"❌ {scraper_name} failed: {str(e)}")
                continue
        
        logger.info(f"📊 Total items collected: {len(aggregated_data)}")
        return aggregated_data
    
    def _analyze_with_gemini(self, market_data: List[Dict[str, Any]], 
                           targets: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data using Gemini AI."""
        
        # Create market intelligence prompt
        prompt = self._create_market_intelligence_prompt(market_data, targets)
        
        try:
            response = self.gemini_tool.generate(
                prompt,
                system_instruction="You are a senior market intelligence analyst. Provide strategic insights based on the data provided."
            )
            
            return self._parse_market_analysis(response)
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _create_market_intelligence_prompt(self, market_data: List[Dict[str, Any]], 
                                         targets: Dict[str, Any]) -> str:
        """Create specialized prompt for market intelligence analysis."""
        
        # Summarize data for context
        data_summary = self._summarize_market_data(market_data)
        tickers = targets.get('tickers', [])
        keywords = targets.get('keywords', [])
        
        prompt = f"""
As a senior market intelligence analyst, analyze the following market data and provide strategic insights.

ANALYSIS TARGETS:
- Stock Tickers: {', '.join(tickers) if tickers else 'None'}
- Keywords/Themes: {', '.join(keywords) if keywords else 'None'}

MARKET DATA SUMMARY:
{data_summary}

Please provide a comprehensive analysis in the following structured format:

EXECUTIVE_SUMMARY: [2-3 sentence overview of key findings]

TRENDS: [List 3-5 key market trends identified from the data]

SENTIMENT: [Overall market sentiment: Bullish/Bearish/Neutral with confidence level]

COMPETITOR_ACTIONS: [Notable competitor activities or announcements]

RISKS: [Top 3 risks or threats identified]

OPPORTUNITIES: [Top 3 opportunities or positive developments]

PRICE_CATALYSTS: [Events or factors that could significantly impact prices]

RECOMMENDATIONS: [2-3 specific actionable recommendations]

Keep analysis focused, data-driven, and actionable for investment/business decisions.
"""
        return prompt
    
    def _summarize_market_data(self, market_data: List[Dict[str, Any]]) -> str:
        """Create concise summary of market data for prompt."""
        if not market_data:
            return "No data available"
        
        # Group data by source
        sources = {}
        for item in market_data:
            source = item.get('source', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(item)
        
        summary_parts = []
        for source, items in sources.items():
            sample_titles = [item.get('title', '')[:100] for item in items[:3]]
            summary_parts.append(f"{source} ({len(items)} items): {'; '.join(sample_titles)}")
        
        return '\n'.join(summary_parts)
    
    def _parse_market_analysis(self, response: str) -> Dict[str, Any]:
        """Parse Gemini response into structured market analysis."""
        
        # Simple parsing - look for section headers
        sections = {
            'executive_summary': '',
            'trends': [],
            'sentiment': {'overall': 'Neutral', 'confidence': 0.5},
            'competitor_actions': [],
            'risks': [],
            'opportunities': [],
            'price_catalysts': [],
            'recommendations': []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if 'EXECUTIVE_SUMMARY:' in line.upper():
                current_section = 'executive_summary'
                sections[current_section] = line.split(':', 1)[1].strip()
            elif 'TRENDS:' in line.upper():
                current_section = 'trends'
            elif 'SENTIMENT:' in line.upper():
                current_section = 'sentiment'
                sentiment_text = line.split(':', 1)[1].strip()
                sections[current_section] = self._parse_sentiment(sentiment_text)
            elif 'COMPETITOR_ACTIONS:' in line.upper():
                current_section = 'competitor_actions'
            elif 'RISKS:' in line.upper():
                current_section = 'risks'
            elif 'OPPORTUNITIES:' in line.upper():
                current_section = 'opportunities'
            elif 'PRICE_CATALYSTS:' in line.upper():
                current_section = 'price_catalysts'
            elif 'RECOMMENDATIONS:' in line.upper():
                current_section = 'recommendations'
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # List item
                if current_section in ['trends', 'competitor_actions', 'risks', 'opportunities', 'price_catalysts', 'recommendations']:
                    item = line.lstrip('•-* ').strip()
                    if item:
                        sections[current_section].append(item)
        
        # Add metadata
        sections['analysis_timestamp'] = time.time()
        sections['model_used'] = 'gemini-pro'
        
        return sections
    
    def _parse_sentiment(self, sentiment_text: str) -> Dict[str, Any]:
        """Parse sentiment from text."""
        sentiment_text = sentiment_text.lower()
        
        if 'bullish' in sentiment_text:
            overall = 'Bullish'
            confidence = 0.7
        elif 'bearish' in sentiment_text:
            overall = 'Bearish'
            confidence = 0.7
        else:
            overall = 'Neutral'
            confidence = 0.5
        
        return {'overall': overall, 'confidence': confidence}
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return basic analysis when Gemini API fails."""
        return {
            'executive_summary': 'Analysis unavailable - API error',
            'trends': ['Data analysis incomplete'],
            'sentiment': {'overall': 'Neutral', 'confidence': 0.0},
            'competitor_actions': [],
            'risks': ['API analysis unavailable'],
            'opportunities': [],
            'price_catalysts': [],
            'recommendations': ['Retry analysis with API connection'],
            'error': True
        }
    
    def _save_json(self, filename: str, data: Any) -> str:
        """Save data as JSON file."""
        import json
        
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def _save_summary_csv(self, filename: str, analysis: Dict[str, Any]) -> str:
        """Save analysis summary as CSV."""
        import csv
        
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Category', 'Item'])
            
            # Write analysis data
            if analysis.get('executive_summary'):
                writer.writerow(['Executive Summary', analysis['executive_summary']])
            
            for trend in analysis.get('trends', []):
                writer.writerow(['Trend', trend])
            
            for risk in analysis.get('risks', []):
                writer.writerow(['Risk', risk])
            
            for opportunity in analysis.get('opportunities', []):
                writer.writerow(['Opportunity', opportunity])
            
            for recommendation in analysis.get('recommendations', []):
                writer.writerow(['Recommendation', recommendation])
        
        return str(file_path)
    
    def _print_key_insights(self, analysis: Dict[str, Any]):
        """Print key insights to console for immediate visibility."""
        print("\n" + "="*60)
        print("🎯 KEY MARKET INSIGHTS")
        print("="*60)
        
        if analysis.get('executive_summary'):
            print(f"\n📋 EXECUTIVE SUMMARY:")
            print(f"   {analysis['executive_summary']}")
        
        if analysis.get('trends'):
            print(f"\n📈 TRENDS:")
            for trend in analysis['trends'][:3]:  # Top 3 trends
                print(f"   • {trend}")
        
        if analysis.get('sentiment'):
            sentiment = analysis['sentiment']
            print(f"\n😊 MARKET SENTIMENT: {sentiment.get('overall', 'Neutral')}")
            print(f"   Confidence: {sentiment.get('confidence', 0):.1%}")
        
        if analysis.get('risks'):
            print(f"\n⚠️  TOP RISKS:")
            for risk in analysis['risks'][:2]:  # Top 2 risks
                print(f"   • {risk}")
        
        if analysis.get('opportunities'):
            print(f"\n🚀 OPPORTUNITIES:")
            for opp in analysis['opportunities'][:2]:  # Top 2 opportunities
                print(f"   • {opp}")
        
        print("\n" + "="*60)
        print(f"📁 Full reports saved in: {self.output_dir}")
        print("="*60 + "\n")


# Mock scrapers for demonstration (will be replaced with real implementations)
class MockNewsScraper(BaseScraper):
    """Mock news scraper for demonstration purposes."""
    
    def __init__(self, keywords: List[str]):
        super().__init__()
        self.keywords = keywords
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Return mock news data."""
        mock_data = []
        for keyword in self.keywords:
            mock_data.append({
                'source': 'Mock News',
                'title': f'Breaking: {keyword} market update',
                'link': f'https://example.com/news/{keyword.replace(" ", "-")}',
                'published': datetime.now().isoformat(),
                'summary': f'Latest developments in {keyword} sector',
                'keyword': keyword,
                'category': 'news'
            })
        return mock_data


class MockFinancialScraper(BaseScraper):
    """Mock financial scraper for demonstration purposes."""
    
    def __init__(self, tickers: List[str]):
        super().__init__()
        self.tickers = tickers
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Return mock financial data."""
        mock_data = []
        for ticker in self.tickers:
            mock_data.append({
                'source': 'Mock Financial',
                'ticker': ticker,
                'price': 150.0,
                'change': 2.5,
                'change_percent': 1.69,
                'volume': 1000000,
                'market_cap': '2.5T',
                'category': 'financial'
            })
        return mock_data

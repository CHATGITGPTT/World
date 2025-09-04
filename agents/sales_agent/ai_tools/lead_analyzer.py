"""
Lead Analyzer for the sales agent system.

This module provides AI-powered lead analysis capabilities,
including lead scoring, categorization, and summary generation.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base_ai_tool import BaseAITool
from .gemini_tool import GeminiTool
from ..scrapers.base_scraper import LeadData

logger = logging.getLogger(__name__)


class LeadAnalyzer:
    """
    AI-powered lead analyzer for processing and analyzing scraped leads.
    
    This class provides capabilities for:
    - Lead scoring and prioritization
    - Lead categorization and segmentation
    - Summary report generation
    - Lead quality assessment
    """
    
    def __init__(self, ai_tool: Optional[BaseAITool] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the lead analyzer.
        
        Args:
            ai_tool: AI tool instance to use (default: GeminiTool)
            config: Configuration dictionary
        """
        self.config = config or {}
        self.ai_tool = ai_tool or GeminiTool(self.config)
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the lead analyzer.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not self.ai_tool.is_initialized:
                if not self.ai_tool.initialize():
                    logger.error("Failed to initialize AI tool for lead analyzer")
                    return False
            
            self.is_initialized = True
            logger.info("Lead analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize lead analyzer: {e}")
            return False
    
    def analyze_leads(self, leads: List[LeadData]) -> Dict[str, Any]:
        """
        Analyze a list of leads and generate insights.
        
        Args:
            leads: List of LeadData objects to analyze
        
        Returns:
            Dict containing analysis results:
                - total_leads: Total number of leads
                - summary: Overall summary
                - categories: Lead categorization
                - top_leads: Highest scoring leads
                - insights: Key insights and recommendations
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize lead analyzer")
        
        try:
            # Convert leads to analysis format
            leads_data = [lead.to_dict() for lead in leads]
            
            # Generate analysis prompt
            analysis_prompt = self._build_analysis_prompt(leads_data)
            
            # Get AI analysis
            analysis_text = self.ai_tool.generate(
                analysis_prompt,
                system_instruction="You are an expert sales analyst. Provide detailed, actionable insights about the leads provided."
            )
            
            # Parse and structure the analysis
            analysis_result = self._parse_analysis(analysis_text, leads_data)
            
            logger.info(f"Successfully analyzed {len(leads)} leads")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing leads: {e}")
            raise
    
    def generate_summary_report(self, leads: List[LeadData], analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a comprehensive summary report for the leads.
        
        Args:
            leads: List of LeadData objects
            analysis: Optional pre-computed analysis results
        
        Returns:
            str: Formatted summary report
        """
        if not analysis:
            analysis = self.analyze_leads(leads)
        
        try:
            # Build summary prompt
            summary_prompt = self._build_summary_prompt(leads, analysis)
            
            # Generate summary
            summary = self.ai_tool.generate(
                summary_prompt,
                system_instruction="You are a professional sales manager. Create a clear, concise executive summary of the lead analysis."
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise
    
    def score_lead(self, lead: LeadData) -> Dict[str, Any]:
        """
        Score a single lead based on various criteria.
        
        Args:
            lead: LeadData object to score
        
        Returns:
            Dict containing:
                - score: Overall score (0-100)
                - factors: Scoring factors and weights
                - recommendations: Action recommendations
        """
        try:
            # Build scoring prompt
            scoring_prompt = self._build_scoring_prompt(lead)
            
            # Get AI scoring
            scoring_text = self.ai_tool.generate(
                scoring_prompt,
                system_instruction="You are a lead scoring expert. Provide a numerical score (0-100) and detailed reasoning."
            )
            
            # Parse scoring result
            score_result = self._parse_scoring(scoring_text)
            
            return score_result
            
        except Exception as e:
            logger.error(f"Error scoring lead: {e}")
            raise
    
    def _build_analysis_prompt(self, leads_data: List[Dict[str, Any]]) -> str:
        """Build the analysis prompt for AI processing."""
        prompt = f"""
        Analyze the following {len(leads_data)} leads and provide insights:

        LEAD DATA:
        {self._format_leads_for_analysis(leads_data)}

        Please provide analysis in the following format:
        1. OVERALL SUMMARY: Brief overview of the lead quality and potential
        2. CATEGORIES: Group leads by industry, company size, or other relevant factors
        3. TOP LEADS: Identify the 3-5 most promising leads with reasoning
        4. INSIGHTS: Key patterns, opportunities, and recommendations
        5. NEXT STEPS: Suggested actions for follow-up

        Focus on actionable insights that will help with sales strategy.
        """
        return prompt
    
    def _build_summary_prompt(self, leads: List[LeadData], analysis: Dict[str, Any]) -> str:
        """Build the summary report prompt."""
        prompt = f"""
        Create an executive summary report for the following lead analysis:

        ANALYSIS RESULTS:
        {analysis.get('summary', 'No summary available')}

        LEAD COUNT: {len(leads)}
        ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Please create a professional summary report that includes:
        - Executive summary
        - Key metrics and statistics
        - Top opportunities
        - Strategic recommendations
        - Action items

        Format the report in a clear, professional manner suitable for management review.
        """
        return prompt
    
    def _build_scoring_prompt(self, lead: LeadData) -> str:
        """Build the lead scoring prompt."""
        prompt = f"""
        Score this lead on a scale of 0-100 and provide detailed reasoning:

        LEAD INFORMATION:
        - Company: {lead.company}
        - Name: {lead.name}
        - Title: {lead.title or 'Not specified'}
        - Industry: {lead.industry or 'Not specified'}
        - Location: {lead.location or 'Not specified'}
        - Email: {lead.email or 'Not provided'}
        - Phone: {lead.phone or 'Not provided'}
        - Website: {lead.website or 'Not provided'}
        - Description: {lead.description or 'No description available'}

        Please provide:
        1. Overall score (0-100)
        2. Scoring factors (company size, contact quality, industry fit, etc.)
        3. Strengths and weaknesses
        4. Recommended next steps
        5. Priority level (High/Medium/Low)

        Consider factors like:
        - Contact information completeness
        - Company relevance to target market
        - Industry alignment
        - Geographic location
        - Company size indicators
        - Contact title/role
        """
        return prompt
    
    def _format_leads_for_analysis(self, leads_data: List[Dict[str, Any]]) -> str:
        """Format leads data for analysis prompt."""
        formatted = []
        for i, lead in enumerate(leads_data, 1):
            formatted.append(f"""
            Lead {i}:
            - Company: {lead.get('company', 'N/A')}
            - Contact: {lead.get('name', 'N/A')}
            - Title: {lead.get('title', 'N/A')}
            - Industry: {lead.get('industry', 'N/A')}
            - Location: {lead.get('location', 'N/A')}
            - Email: {lead.get('email', 'N/A')}
            - Phone: {lead.get('phone', 'N/A')}
            - Description: {lead.get('description', 'N/A')[:200]}...
            """)
        return '\n'.join(formatted)
    
    def _parse_analysis(self, analysis_text: str, leads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse AI analysis text into structured format."""
        return {
            'total_leads': len(leads_data),
            'summary': analysis_text,
            'categories': self._extract_categories(analysis_text),
            'top_leads': self._extract_top_leads(analysis_text, leads_data),
            'insights': self._extract_insights(analysis_text),
            'generated_at': datetime.now().isoformat()
        }
    
    def _parse_scoring(self, scoring_text: str) -> Dict[str, Any]:
        """Parse AI scoring text into structured format."""
        # This is a simplified parser - in production, you'd want more robust parsing
        lines = scoring_text.split('\n')
        score = 50  # Default score
        
        # Try to extract numerical score
        for line in lines:
            if 'score' in line.lower() and any(char.isdigit() for char in line):
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    break
                except:
                    continue
        
        return {
            'score': min(max(score, 0), 100),  # Ensure score is between 0-100
            'reasoning': scoring_text,
            'factors': self._extract_scoring_factors(scoring_text),
            'recommendations': self._extract_recommendations(scoring_text),
            'generated_at': datetime.now().isoformat()
        }
    
    def _extract_categories(self, analysis_text: str) -> List[str]:
        """Extract categories from analysis text."""
        # Simplified category extraction
        categories = []
        if 'industry' in analysis_text.lower():
            categories.append('Industry-based')
        if 'size' in analysis_text.lower():
            categories.append('Company Size')
        if 'location' in analysis_text.lower():
            categories.append('Geographic')
        return categories or ['General']
    
    def _extract_top_leads(self, analysis_text: str, leads_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract top leads from analysis text."""
        # Return first 3 leads as top leads (simplified)
        return leads_data[:3]
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Extract key insights from analysis text."""
        # Simplified insight extraction
        insights = []
        if 'opportunity' in analysis_text.lower():
            insights.append('High opportunity potential identified')
        if 'follow' in analysis_text.lower():
            insights.append('Immediate follow-up recommended')
        return insights or ['Standard lead processing recommended']
    
    def _extract_scoring_factors(self, scoring_text: str) -> List[str]:
        """Extract scoring factors from scoring text."""
        factors = []
        if 'email' in scoring_text.lower():
            factors.append('Contact Information Quality')
        if 'company' in scoring_text.lower():
            factors.append('Company Relevance')
        if 'industry' in scoring_text.lower():
            factors.append('Industry Alignment')
        return factors or ['General Lead Quality']
    
    def _extract_recommendations(self, scoring_text: str) -> List[str]:
        """Extract recommendations from scoring text."""
        recommendations = []
        if 'contact' in scoring_text.lower():
            recommendations.append('Initiate contact')
        if 'research' in scoring_text.lower():
            recommendations.append('Conduct additional research')
        return recommendations or ['Standard follow-up process']

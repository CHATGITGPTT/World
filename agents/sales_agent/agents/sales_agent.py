"""
Main Sales Agent implementation using smolagents.

This module provides the core sales agent that orchestrates web scraping,
lead analysis, and email generation to create a complete sales automation system.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import smolagents components
from smolagents import CodeAgent, tool
from smolagents.models import LiteLLMModel

# Import our custom components
from ..scrapers import WebScraperAdapter, LeadData
from ..ai_tools import LeadAnalyzer, EmailGenerator, GeminiTool

logger = logging.getLogger(__name__)


class SalesAgent:
    """
    Main Sales Agent that orchestrates the entire sales automation workflow.
    
    This agent combines web scraping, lead analysis, and email generation
    to provide a complete sales automation solution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Sales Agent.
        
        Args:
            config: Configuration dictionary containing:
                - gemini_api_key: Google Gemini API key
                - scraper_config: Configuration for web scraper
                - ai_config: Configuration for AI tools
                - output_dir: Directory for output files
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', './output')
        
        # Initialize components
        self.scraper = WebScraperAdapter(self.config.get('scraper_config', {}))
        self.ai_tool = GeminiTool(self.config.get('ai_config', {}))
        self.lead_analyzer = LeadAnalyzer(self.ai_tool, self.config.get('ai_config', {}))
        self.email_generator = EmailGenerator(self.ai_tool, self.config.get('ai_config', {}))
        
        # Initialize smolagents CodeAgent
        self.agent = None
        self._setup_smolagents()
        
        self.is_initialized = False
    
    def _setup_smolagents(self):
        """Set up the smolagents CodeAgent with custom tools."""
        # Create custom tools for the agent
        tools = [
            self._create_scrape_leads_tool(),
            self._create_analyze_leads_tool(),
            self._create_generate_emails_tool(),
            self._create_save_results_tool()
        ]
        
        # Initialize the CodeAgent
        self.agent = CodeAgent(
            tools=tools,
            model=self.ai_tool,  # Use our Gemini tool as the model
            stream_outputs=True,
            verbosity_level=2
        )
    
    def initialize(self) -> bool:
        """
        Initialize all components of the sales agent.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Initialize scraper
            if not self.scraper.initialize():
                logger.error("Failed to initialize web scraper")
                return False
            
            # Initialize AI tools
            if not self.lead_analyzer.initialize():
                logger.error("Failed to initialize lead analyzer")
                return False
            
            if not self.email_generator.initialize():
                logger.error("Failed to initialize email generator")
                return False
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.is_initialized = True
            logger.info("Sales agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize sales agent: {e}")
            return False
    
    def run_sales_workflow(self, search_criteria: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete sales workflow.
        
        Args:
            search_criteria: Dictionary containing:
                - keywords: List of search keywords
                - industry: Target industry (optional)
                - location: Geographic location (optional)
                - max_results: Maximum number of leads (default: 10)
            context: Optional context for email generation
        
        Returns:
            Dict containing workflow results:
                - leads: List of scraped leads
                - analysis: Lead analysis results
                - emails: Generated emails
                - summary: Workflow summary
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize sales agent")
        
        try:
            # Build the workflow prompt
            workflow_prompt = self._build_workflow_prompt(search_criteria, context)
            
            # Run the agent
            result = self.agent.run(workflow_prompt)
            
            # Parse and return results
            return self._parse_workflow_result(result, search_criteria)
            
        except Exception as e:
            logger.error(f"Error running sales workflow: {e}")
            raise
    
    def _create_scrape_leads_tool(self):
        """Create the scrape leads tool for smolagents."""
        
        @tool
        def scrape_leads(keywords: str, industry: str = None, location: str = None, max_results: int = 10) -> str:
            """
            Scrape leads from the web based on search criteria.
            
            Args:
                keywords: Comma-separated keywords to search for
                industry: Target industry (optional)
                location: Geographic location (optional)
                max_results: Maximum number of leads to return (default: 10)
            
            Returns:
                JSON string containing scraped leads data
            """
            try:
                # Convert keywords string to list
                keyword_list = [k.strip() for k in keywords.split(',')]
                
                # Build search criteria
                search_criteria = {
                    'keywords': keyword_list,
                    'max_results': max_results
                }
                
                if industry:
                    search_criteria['industry'] = industry
                if location:
                    search_criteria['location'] = location
                
                # Scrape leads
                leads = self.scraper.scrape_leads(search_criteria)
                
                # Convert to JSON string
                leads_data = [lead.to_dict() for lead in leads]
                return json.dumps({
                    'success': True,
                    'leads_count': len(leads_data),
                    'leads': leads_data
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in scrape_leads tool: {e}")
                return json.dumps({
                    'success': False,
                    'error': str(e),
                    'leads': []
                })
        
        return scrape_leads
    
    def _create_analyze_leads_tool(self):
        """Create the analyze leads tool for smolagents."""
        
        @tool
        def analyze_leads(leads_json: str) -> str:
            """
            Analyze scraped leads and generate insights.
            
            Args:
                leads_json: JSON string containing leads data
            
            Returns:
                JSON string containing analysis results
            """
            try:
                # Parse leads data
                leads_data = json.loads(leads_json)
                
                if not leads_data.get('success', False):
                    return json.dumps({
                        'success': False,
                        'error': 'Invalid leads data provided'
                    })
                
                # Convert to LeadData objects
                leads = []
                for lead_dict in leads_data.get('leads', []):
                    lead = LeadData(**lead_dict)
                    leads.append(lead)
                
                # Analyze leads
                analysis = self.lead_analyzer.analyze_leads(leads)
                
                return json.dumps({
                    'success': True,
                    'analysis': analysis
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in analyze_leads tool: {e}")
                return json.dumps({
                    'success': False,
                    'error': str(e)
                })
        
        return analyze_leads
    
    def _create_generate_emails_tool(self):
        """Create the generate emails tool for smolagents."""
        
        @tool
        def generate_emails(leads_json: str, product_service: str = "Our solution", company_info: str = "Our company", value_proposition: str = "We help businesses grow") -> str:
            """
            Generate personalized emails for leads.
            
            Args:
                leads_json: JSON string containing leads data
                product_service: Description of product/service being offered
                company_info: Information about your company
                value_proposition: Key value proposition
            
            Returns:
                JSON string containing generated emails
            """
            try:
                # Parse leads data
                leads_data = json.loads(leads_json)
                
                if not leads_data.get('success', False):
                    return json.dumps({
                        'success': False,
                        'error': 'Invalid leads data provided'
                    })
                
                # Convert to LeadData objects
                leads = []
                for lead_dict in leads_data.get('leads', []):
                    lead = LeadData(**lead_dict)
                    leads.append(lead)
                
                # Build context for email generation
                context = {
                    'product_service': product_service,
                    'company_info': company_info,
                    'value_proposition': value_proposition,
                    'call_to_action': 'Schedule a meeting',
                    'tone': 'professional'
                }
                
                # Generate emails
                emails = self.email_generator.generate_bulk_emails(leads, context)
                
                return json.dumps({
                    'success': True,
                    'emails_count': len(emails),
                    'emails': emails
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in generate_emails tool: {e}")
                return json.dumps({
                    'success': False,
                    'error': str(e)
                })
        
        return generate_emails
    
    def _create_save_results_tool(self):
        """Create the save results tool for smolagents."""
        
        @tool
        def save_results(leads_json: str, analysis_json: str = None, emails_json: str = None, filename_prefix: str = "sales_results") -> str:
            """
            Save workflow results to files.
            
            Args:
                leads_json: JSON string containing leads data
                analysis_json: JSON string containing analysis results (optional)
                emails_json: JSON string containing generated emails (optional)
                filename_prefix: Prefix for output files
            
            Returns:
                JSON string containing file paths and summary
            """
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results = {
                    'success': True,
                    'files_created': [],
                    'summary': {}
                }
                
                # Save leads
                leads_file = os.path.join(self.output_dir, f"{filename_prefix}_leads_{timestamp}.json")
                with open(leads_file, 'w') as f:
                    f.write(leads_json)
                results['files_created'].append(leads_file)
                
                # Save analysis if provided
                if analysis_json:
                    analysis_file = os.path.join(self.output_dir, f"{filename_prefix}_analysis_{timestamp}.json")
                    with open(analysis_file, 'w') as f:
                        f.write(analysis_json)
                    results['files_created'].append(analysis_file)
                
                # Save emails if provided
                if emails_json:
                    emails_file = os.path.join(self.output_dir, f"{filename_prefix}_emails_{timestamp}.json")
                    with open(emails_file, 'w') as f:
                        f.write(emails_json)
                    results['files_created'].append(emails_file)
                
                # Create CSV summary
                csv_file = os.path.join(self.output_dir, f"{filename_prefix}_summary_{timestamp}.csv")
                self._create_csv_summary(leads_json, analysis_json, emails_json, csv_file)
                results['files_created'].append(csv_file)
                
                # Add summary
                leads_data = json.loads(leads_json)
                results['summary'] = {
                    'leads_found': leads_data.get('leads_count', 0),
                    'files_created': len(results['files_created']),
                    'timestamp': timestamp
                }
                
                return json.dumps(results, indent=2)
                
            except Exception as e:
                logger.error(f"Error in save_results tool: {e}")
                return json.dumps({
                    'success': False,
                    'error': str(e)
                })
        
        return save_results
    
    def _build_workflow_prompt(self, search_criteria: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build the workflow prompt for the agent."""
        keywords = ', '.join(search_criteria.get('keywords', []))
        industry = search_criteria.get('industry', 'any industry')
        location = search_criteria.get('location', 'any location')
        max_results = search_criteria.get('max_results', 10)
        
        context = context or {}
        product_service = context.get('product_service', 'our solution')
        company_info = context.get('company_info', 'our company')
        value_proposition = context.get('value_proposition', 'we help businesses grow')
        
        prompt = f"""
        Execute a complete sales lead generation and outreach workflow with the following parameters:

        SEARCH CRITERIA:
        - Keywords: {keywords}
        - Industry: {industry}
        - Location: {location}
        - Max Results: {max_results}

        CONTEXT:
        - Product/Service: {product_service}
        - Company Info: {company_info}
        - Value Proposition: {value_proposition}

        WORKFLOW STEPS:
        1. Use scrape_leads() to find leads based on the search criteria
        2. Use analyze_leads() to analyze the scraped leads and generate insights
        3. Use generate_emails() to create personalized emails for each lead
        4. Use save_results() to save all results to files

        Please execute this workflow step by step and provide a summary of the results.
        Make sure to handle any errors gracefully and provide meaningful feedback.
        """
        
        return prompt
    
    def _parse_workflow_result(self, result: str, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the workflow result from the agent."""
        return {
            'success': True,
            'result': result,
            'search_criteria': search_criteria,
            'timestamp': datetime.now().isoformat(),
            'output_directory': self.output_dir
        }
    
    def _create_csv_summary(self, leads_json: str, analysis_json: str, emails_json: str, csv_file: str):
        """Create a CSV summary of the results."""
        try:
            import csv
            
            leads_data = json.loads(leads_json)
            leads = leads_data.get('leads', [])
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Company', 'Contact Name', 'Title', 'Email', 'Phone', 
                    'Industry', 'Location', 'Description', 'Source URL'
                ])
                
                # Write lead data
                for lead in leads:
                    writer.writerow([
                        lead.get('company', ''),
                        lead.get('name', ''),
                        lead.get('title', ''),
                        lead.get('email', ''),
                        lead.get('phone', ''),
                        lead.get('industry', ''),
                        lead.get('location', ''),
                        lead.get('description', '')[:100] + '...' if len(lead.get('description', '')) > 100 else lead.get('description', ''),
                        lead.get('source_url', '')
                    ])
            
            logger.info(f"Created CSV summary: {csv_file}")
            
        except Exception as e:
            logger.error(f"Error creating CSV summary: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.scraper:
            self.scraper.cleanup()
        if self.ai_tool:
            self.ai_tool.cleanup()
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

"""
Main CLI interface for the Sales Agent.

This module provides a command-line interface for running the sales agent
workflow with various options and configurations.
"""

import os
import sys
import argparse
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from sales_agent.agents import SalesAgent
from sales_agent.config.env_loader import get_config_from_env, validate_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Sales Agent - AI-powered lead generation and email automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic lead generation
  python -m sales_agent.cli.main --keywords "AI startups,tech companies" --max-results 5
  
  # Industry-specific search
  python -m sales_agent.cli.main --keywords "fintech" --industry "Financial Services" --location "San Francisco"
  
  # With custom context
  python -m sales_agent.cli.main --keywords "SaaS" --product "Our CRM solution" --company "TechCorp Inc"
  
  # Using config file
  python -m sales_agent.cli.main --config config.json
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--keywords',
        required=True,
        help='Comma-separated keywords to search for (e.g., "AI startups,tech companies")'
    )
    
    # Optional search parameters
    parser.add_argument(
        '--industry',
        help='Target industry (e.g., "Technology", "Healthcare")'
    )
    parser.add_argument(
        '--location',
        help='Geographic location (e.g., "San Francisco", "New York")'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Maximum number of leads to generate (default: 10)'
    )
    
    # Context parameters
    parser.add_argument(
        '--product',
        help='Description of your product/service'
    )
    parser.add_argument(
        '--company',
        help='Information about your company'
    )
    parser.add_argument(
        '--value-prop',
        help='Your key value proposition'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '--output-dir',
        default='./output',
        help='Output directory for results (default: ./output)'
    )
    parser.add_argument(
        '--gemini-api-key',
        help='Google Gemini API key (or set GEMINI_API_KEY environment variable)'
    )
    
    # Scraper configuration
    parser.add_argument(
        '--scraper-port',
        type=int,
        default=3001,
        help='Port for the web scraper (default: 3001)'
    )
    parser.add_argument(
        '--scraper-path',
        default='../webScraper/backend',
        help='Path to the web scraper backend directory'
    )
    
    # Output options
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without actually executing the workflow (for testing)'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        config = load_configuration(args)
        
        # Validate configuration
        if not validate_configuration(config):
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Run the sales agent
        if args.dry_run:
            logger.info("Dry run mode - configuration validated successfully")
            print_configuration(config)
        else:
            run_sales_agent(config, args)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def load_configuration(args) -> Dict[str, Any]:
    """Load configuration from arguments, config file, and environment variables."""
    # Start with environment variables
    config = get_config_from_env()
    
    # Load from config file if provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load config file {args.config}: {e}")
            raise
    
    # Override with command line arguments
    if args.output_dir:
        config['output_dir'] = args.output_dir
    if args.gemini_api_key:
        config['gemini_api_key'] = args.gemini_api_key
        config['ai_config']['api_key'] = args.gemini_api_key
    if args.scraper_port:
        config['scraper_config']['scraper_port'] = args.scraper_port
    if args.scraper_path:
        config['scraper_config']['scraper_path'] = args.scraper_path
    
    return config


def validate_configuration(config: Dict[str, Any]) -> bool:
    """Validate the configuration."""
    # Use the centralized validation function
    if not validate_config(config):
        return False
    
    # Check output directory
    output_dir = config.get('output_dir', './output')
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
    except Exception as e:
        logger.error(f"Cannot create output directory {output_dir}: {e}")
        return False
    
    return True


def print_configuration(config: Dict[str, Any]):
    """Print the configuration for dry run mode."""
    print("\n" + "="*50)
    print("SALES AGENT CONFIGURATION")
    print("="*50)
    print(f"Output Directory: {config.get('output_dir')}")
    print(f"Gemini API Key: {'*' * 20 if config.get('gemini_api_key') else 'NOT SET'}")
    print(f"Scraper Port: {config.get('scraper_config', {}).get('scraper_port')}")
    print(f"Scraper Path: {config.get('scraper_config', {}).get('scraper_path')}")
    print(f"AI Model: {config.get('ai_config', {}).get('model')}")
    print(f"Temperature: {config.get('ai_config', {}).get('temperature')}")
    print("="*50)


def run_sales_agent(config: Dict[str, Any], args):
    """Run the sales agent workflow."""
    logger.info("Starting Sales Agent workflow...")
    
    # Build search criteria
    search_criteria = {
        'keywords': [k.strip() for k in args.keywords.split(',')],
        'max_results': args.max_results
    }
    
    if args.industry:
        search_criteria['industry'] = args.industry
    if args.location:
        search_criteria['location'] = args.location
    
    # Build context
    context = {}
    if args.product:
        context['product_service'] = args.product
    if args.company:
        context['company_info'] = args.company
    if args.value_prop:
        context['value_proposition'] = args.value_prop
    
    logger.info(f"Search criteria: {search_criteria}")
    logger.info(f"Context: {context}")
    
    # Initialize and run the sales agent
    try:
        with SalesAgent(config) as agent:
            logger.info("Sales agent initialized successfully")
            
            # Run the workflow
            result = agent.run_sales_workflow(search_criteria, context)
            
            # Print results
            print_results(result)
            
            logger.info("Sales Agent workflow completed successfully")
            
    except Exception as e:
        logger.error(f"Sales Agent workflow failed: {e}")
        raise


def print_results(result: Dict[str, Any]):
    """Print the workflow results."""
    print("\n" + "="*50)
    print("SALES AGENT RESULTS")
    print("="*50)
    print(f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
    print(f"Timestamp: {result.get('timestamp')}")
    print(f"Output Directory: {result.get('output_directory')}")
    print(f"Search Criteria: {result.get('search_criteria')}")
    
    if result.get('success'):
        print("\nFiles created:")
        # The actual file paths would be in the agent's output
        print("- Leads data (JSON)")
        print("- Analysis results (JSON)")
        print("- Generated emails (JSON)")
        print("- Summary report (CSV)")
    
    print("="*50)


if __name__ == '__main__':
    main()

"""
Unified CLI for Sales Agent with Dual-Mode Support

This module extends the existing CLI to support both:
- Sales Mode: Lead generation and email automation (existing functionality)
- Market Intelligence Mode: Real-time market data analysis (new functionality)

Preserves all existing CLI functionality while adding new market intelligence capabilities.
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

from sales_agent.unified_agent import UnifiedSalesAgent
from sales_agent.config.env_loader import get_config_from_env, validate_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point with dual-mode support."""
    parser = argparse.ArgumentParser(
        description='Unified Sales Agent - AI-powered lead generation and market intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sales Mode (existing functionality)
  python -m sales_agent.cli.unified_cli --mode sales --keywords "AI startups,tech companies" --max-results 5
  
  # Market Intelligence Mode (new functionality)
  python -m sales_agent.cli.unified_cli --mode intel --tickers "AAPL,TSLA" --keywords "AI,EV"
  
  # Sales Mode with custom context
  python -m sales_agent.cli.unified_cli --mode sales --keywords "fintech" --product "Our CRM solution"
  
  # Market Intelligence with config file
  python -m sales_agent.cli.unified_cli --mode intel --config config/intel_config.json
        """
    )
    
    # Mode selection (required)
    parser.add_argument(
        '--mode',
        choices=['sales', 'intel'],
        required=True,
        help='Operation mode: sales (lead generation) or intel (market intelligence)'
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
    
    # Sales Mode Arguments (existing functionality)
    parser.add_argument(
        '--keywords',
        help='Comma-separated keywords to search for (sales mode)'
    )
    parser.add_argument(
        '--industry',
        help='Target industry (sales mode)'
    )
    parser.add_argument(
        '--location',
        help='Geographic location (sales mode)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Maximum number of leads to generate (sales mode, default: 10)'
    )
    parser.add_argument(
        '--product',
        help='Description of your product/service (sales mode)'
    )
    parser.add_argument(
        '--company',
        help='Information about your company (sales mode)'
    )
    parser.add_argument(
        '--value-prop',
        help='Your key value proposition (sales mode)'
    )
    
    # Market Intelligence Mode Arguments (new functionality)
    parser.add_argument(
        '--tickers',
        help='Comma-separated list of stock tickers (intel mode, e.g., AAPL,TSLA,MSFT)'
    )
    parser.add_argument(
        '--intel-keywords',
        help='Comma-separated list of keywords to monitor (intel mode)'
    )
    parser.add_argument(
        '--companies',
        help='Comma-separated list of companies to monitor (intel mode)'
    )
    
    # General options
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
        if not validate_configuration(config, args.mode):
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Run the appropriate mode
        if args.dry_run:
            logger.info("Dry run mode - configuration validated successfully")
            print_configuration(config, args.mode)
        else:
            run_agent(args.mode, config, args)
            
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
        if 'ai_config' in config:
            config['ai_config']['api_key'] = args.gemini_api_key
    
    return config


def validate_configuration(config: Dict[str, Any], mode: str) -> bool:
    """Validate the configuration for the specified mode."""
    # Use the centralized validation function
    if not validate_config(config):
        return False
    
    # Mode-specific validation
    if mode == 'sales':
        # Sales mode validation (existing logic)
        if not config.get('keywords') and not config.get('gemini_api_key'):
            logger.warning("No keywords provided for sales mode")
    
    elif mode == 'intel':
        # Market intelligence mode validation
        targets = config.get('targets', {})
        if not (targets.get('tickers') or targets.get('keywords') or targets.get('companies')):
            logger.error("No targets specified for market intelligence mode")
            logger.error("Use --tickers, --intel-keywords, or --companies")
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


def print_configuration(config: Dict[str, Any], mode: str):
    """Print the configuration for dry run mode."""
    print("\n" + "="*50)
    print(f"UNIFIED SALES AGENT CONFIGURATION - {mode.upper()} MODE")
    print("="*50)
    print(f"Mode: {mode}")
    print(f"Output Directory: {config.get('output_dir')}")
    print(f"Gemini API Key: {'*' * 20 if config.get('gemini_api_key') else 'NOT SET'}")
    
    if mode == 'sales':
        print(f"Keywords: {config.get('keywords', 'Not specified')}")
        print(f"Industry: {config.get('industry', 'Not specified')}")
        print(f"Location: {config.get('location', 'Not specified')}")
        print(f"Max Results: {config.get('max_results', 10)}")
    elif mode == 'intel':
        targets = config.get('targets', {})
        print(f"Tickers: {', '.join(targets.get('tickers', [])) or 'None'}")
        print(f"Keywords: {', '.join(targets.get('keywords', [])) or 'None'}")
        print(f"Companies: {', '.join(targets.get('companies', [])) or 'None'}")
    
    print("="*50)


def run_agent(mode: str, config: Dict[str, Any], args):
    """Run the appropriate agent mode."""
    logger.info(f"Starting {mode} mode...")
    
    try:
        with UnifiedSalesAgent(mode=mode, config=config) as agent:
            logger.info(f"Agent initialized successfully in {mode} mode")
            
            # Prepare mode-specific arguments
            if mode == 'sales':
                # Sales mode arguments
                search_criteria = {
                    'keywords': [k.strip() for k in args.keywords.split(',')] if args.keywords else [],
                    'max_results': args.max_results
                }
                
                if args.industry:
                    search_criteria['industry'] = args.industry
                if args.location:
                    search_criteria['location'] = args.location
                
                context = {}
                if args.product:
                    context['product_service'] = args.product
                if args.company:
                    context['company_info'] = args.company
                if args.value_prop:
                    context['value_proposition'] = args.value_prop
                
                logger.info(f"Sales search criteria: {search_criteria}")
                logger.info(f"Sales context: {context}")
                
                result = agent.run(
                    search_criteria=search_criteria,
                    context=context
                )
                
            elif mode == 'intel':
                # Market intelligence mode arguments
                targets = {}
                
                if args.tickers:
                    targets['tickers'] = [t.strip() for t in args.tickers.split(',')]
                if args.intel_keywords:
                    targets['keywords'] = [k.strip() for k in args.intel_keywords.split(',')]
                if args.companies:
                    targets['companies'] = [c.strip() for c in args.companies.split(',')]
                
                # Also check config for targets
                config_targets = config.get('targets', {})
                if config_targets:
                    targets.update(config_targets)
                
                logger.info(f"Market intelligence targets: {targets}")
                
                result = agent.run(targets=targets)
            
            # Print results
            print_results(result, mode)
            
            logger.info(f"{mode.capitalize()} mode completed successfully")
            
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise


def print_results(result: Dict[str, Any], mode: str):
    """Print the workflow results."""
    print("\n" + "="*50)
    print(f"UNIFIED SALES AGENT RESULTS - {mode.upper()} MODE")
    print("="*50)
    print(f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
    print(f"Mode: {mode}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        if mode == 'sales':
            print(f"Search Criteria: {result.get('search_criteria', {})}")
            print(f"Output Directory: {result.get('output_directory', 'N/A')}")
        elif mode == 'intel':
            print(f"Data Count: {result.get('data_count', 0)}")
            print(f"Raw Data File: {result.get('raw_data_file', 'N/A')}")
            print(f"Analysis File: {result.get('analysis_file', 'N/A')}")
            print(f"Summary File: {result.get('summary_file', 'N/A')}")
        
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
    
    print("="*50)


if __name__ == '__main__':
    main()

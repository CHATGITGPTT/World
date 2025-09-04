"""
Environment variable loader for the sales agent system.

This module provides utilities for loading configuration from environment variables
and .env files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_env_file(env_file_path: Optional[str] = None) -> bool:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file (default: .env in current directory)
    
    Returns:
        bool: True if file was loaded successfully, False otherwise
    """
    if env_file_path is None:
        env_file_path = ".env"
    
    env_path = Path(env_file_path)
    
    if not env_path.exists():
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Set environment variable if not already set
                    if key not in os.environ:
                        os.environ[key] = value
        
        return True
        
    except Exception as e:
        print(f"Warning: Failed to load .env file {env_file_path}: {e}")
        return False


def get_config_from_env() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    
    Returns:
        Dict containing configuration loaded from environment variables
    """
    config = {}
    
    # Load .env file if it exists
    load_env_file()
    
    # Get Gemini API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        config['gemini_api_key'] = gemini_api_key
    
    # Get output directory
    output_dir = os.getenv('SALES_AGENT_OUTPUT_DIR', './output')
    config['output_dir'] = output_dir
    
    # Get scraper configuration
    scraper_config = {
        'scraper_port': int(os.getenv('SCRAPER_PORT', '3001')),
        'scraper_host': os.getenv('SCRAPER_HOST', 'localhost'),
        'scraper_path': os.getenv('SCRAPER_PATH', '../webScraper/backend'),
        'timeout': int(os.getenv('SCRAPER_TIMEOUT', '30'))
    }
    config['scraper_config'] = scraper_config
    
    # Get AI configuration
    ai_config = {
        'api_key': gemini_api_key,
        'model': os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'),
        'temperature': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', '1000')),
        'timeout': int(os.getenv('GEMINI_TIMEOUT', '30'))
    }
    config['ai_config'] = ai_config
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that required configuration is present.
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    # Check for required API key
    if not config.get('gemini_api_key'):
        print("❌ GEMINI_API_KEY is required")
        print("Set it using one of these methods:")
        print("1. Environment variable: export GEMINI_API_KEY='your-key'")
        print("2. .env file: Create .env with GEMINI_API_KEY=your-key")
        print("3. Command line: --gemini-api-key 'your-key'")
        print("4. Config file: Add 'gemini_api_key' to your config.json")
        return False
    
    return True

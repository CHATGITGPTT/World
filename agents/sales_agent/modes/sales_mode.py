"""
Sales Mode for Sales Agent

This module wraps the existing sales agent functionality to maintain
backward compatibility while supporting the new dual-mode architecture.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..agents import SalesAgent

logger = logging.getLogger(__name__)


class SalesMode:
    """
    Sales Mode - Wrapper for existing sales agent functionality
    
    Preserves all existing sales agent capabilities while integrating
    with the new dual-mode architecture.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Sales Mode.
        
        Args:
            config: Configuration dictionary (same as existing sales agent)
        """
        self.config = config or {}
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize the existing sales agent
        self.sales_agent = SalesAgent(self.config)
        
        logger.info("Sales Mode initialized (using existing sales agent)")
    
    def run(self, search_criteria: Optional[Dict[str, Any]] = None, 
            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute sales lead generation workflow.
        
        Args:
            search_criteria: Search criteria for lead generation
            context: Context for email generation
        
        Returns:
            Dict containing sales workflow results
        """
        logger.info("🚀 Starting Sales Lead Generation Mode")
        
        try:
            # Use the existing sales agent workflow
            result = self.sales_agent.run_sales_workflow(search_criteria or {}, context or {})
            
            logger.info("✅ Sales mode completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Sales mode failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'mode': 'sales'
            }
    
    def initialize(self) -> bool:
        """Initialize the sales agent."""
        try:
            return self.sales_agent.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize sales agent: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self.sales_agent, 'cleanup'):
            self.sales_agent.cleanup()

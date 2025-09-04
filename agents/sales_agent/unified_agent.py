"""
Unified Sales Agent with Dual-Mode Support

This module provides a unified interface that supports both:
- Sales Mode: Lead generation and email automation (existing functionality)
- Market Intelligence Mode: Real-time market data analysis (new functionality)

Adapted from ai-sales-agent implementation while preserving all existing code.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .modes import SalesMode, MarketIntelligenceMode
from .config.env_loader import get_config_from_env, validate_config

logger = logging.getLogger(__name__)


class UnifiedSalesAgent:
    """
    Unified Sales Agent supporting both sales and market intelligence modes.
    
    This agent preserves all existing sales agent functionality while adding
    new market intelligence capabilities from the ai-sales-agent implementation.
    """
    
    def __init__(self, mode: str = 'sales', config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Unified Sales Agent.
        
        Args:
            mode: Operation mode ('sales' or 'intel')
            config: Configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        
        # Get configuration from environment if not provided
        if not self.config:
            self.config = get_config_from_env()
        
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize the appropriate mode
        if mode == 'sales':
            self.mode_handler = SalesMode(self.config)
        elif mode == 'intel':
            self.mode_handler = MarketIntelligenceMode(self.config)
        else:
            raise ValueError(f"Unknown mode: {mode}. Supported modes: 'sales', 'intel'")
        
        logger.info(f"Unified Sales Agent initialized in {mode} mode")
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent based on the selected mode.
        
        Args:
            **kwargs: Mode-specific arguments:
                - For sales mode: search_criteria, context
                - For intel mode: targets
        
        Returns:
            Dict containing execution results
        """
        try:
            if self.mode == 'sales':
                return self.mode_handler.run(
                    search_criteria=kwargs.get('search_criteria'),
                    context=kwargs.get('context')
                )
            elif self.mode == 'intel':
                return self.mode_handler.run(
                    targets=kwargs.get('targets')
                )
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'mode': self.mode
            }
    
    def initialize(self) -> bool:
        """Initialize the agent."""
        try:
            if hasattr(self.mode_handler, 'initialize'):
                return self.mode_handler.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self.mode_handler, 'cleanup'):
            self.mode_handler.cleanup()
    
    def __enter__(self):
        """Context manager entry."""
        if not self.initialize():
            raise RuntimeError(f"Failed to initialize {self.mode} mode")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    @classmethod
    def create_sales_agent(cls, config: Optional[Dict[str, Any]] = None):
        """Create a sales mode agent (backward compatibility)."""
        return cls(mode='sales', config=config)
    
    @classmethod
    def create_intel_agent(cls, config: Optional[Dict[str, Any]] = None):
        """Create a market intelligence mode agent."""
        return cls(mode='intel', config=config)

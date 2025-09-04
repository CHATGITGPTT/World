"""
Base AI Tool interface for the sales agent system.

This module defines the abstract base class for AI-powered tools,
ensuring a consistent interface for different AI providers and capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseAITool(ABC):
    """
    Abstract base class for AI tools in the sales agent system.
    
    This ensures a consistent interface for different AI implementations
    and allows for easy swapping of AI providers without changing the main agent code.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI tool with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - api_key: API key for the AI provider
                - model: Model name/ID to use
                - temperature: Temperature for generation (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 1000)
                - timeout: Request timeout in seconds (default: 30)
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.timeout = self.config.get('timeout', 30)
        self.is_initialized = False
        
        if not self.api_key:
            logger.warning("No API key provided for AI tool")
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the AI tool (e.g., test API connection).
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the AI model.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional parameters for generation
        
        Returns:
            str: Generated text
        """
        pass
    
    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get information about the AI tool.
        
        Returns:
            Dict containing tool metadata like name, version, capabilities
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = ['api_key', 'model']
        return all(field in self.config and self.config[field] for field in required_fields)
    
    def cleanup(self) -> None:
        """
        Clean up resources used by the AI tool.
        Override in subclasses if cleanup is needed.
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

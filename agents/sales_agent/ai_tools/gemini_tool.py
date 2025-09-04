"""
Gemini AI Tool implementation for the sales agent system.

This module provides AI capabilities using Google's Gemini API for
lead analysis and email generation.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
import logging

from .base_ai_tool import BaseAITool

logger = logging.getLogger(__name__)


class GeminiTool(BaseAITool):
    """
    Google Gemini AI tool implementation.
    
    This class provides AI capabilities using Google's Gemini API
    for various sales agent tasks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Gemini AI tool.
        
        Args:
            config: Configuration dictionary containing:
                - api_key: Google AI API key (or use GEMINI_API_KEY env var)
                - model: Model name (default: gemini-1.5-flash)
                - temperature: Temperature for generation (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 1000)
        """
        # Get API key from config or environment
        api_key = config.get('api_key') if config else None
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass in config.")
        
        # Set default config
        default_config = {
            'api_key': api_key,
            'model': 'gemini-1.5-flash',
            'temperature': 0.7,
            'max_tokens': 1000,
            'timeout': 30
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(default_config)
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.api_key = api_key
        self.model_name = self.model
    
    def initialize(self) -> bool:
        """
        Initialize the Gemini AI tool by testing the API connection.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Test API connection with a simple request
            test_prompt = "Hello, this is a test."
            response = self._make_request(test_prompt)
            
            if response and 'candidates' in response:
                self.is_initialized = True
                logger.info("Gemini AI tool initialized successfully")
                return True
            else:
                logger.error("Failed to initialize Gemini AI tool: Invalid response")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI tool: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Gemini API.
        
        Args:
            prompt: The input prompt for generation
            **kwargs: Additional parameters:
                - temperature: Override default temperature
                - max_tokens: Override default max_tokens
                - system_instruction: System instruction for the model
        
        Returns:
            str: Generated text
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize Gemini AI tool")
        
        try:
            # Prepare request parameters
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            system_instruction = kwargs.get('system_instruction', '')
            
            # Make request
            response = self._make_request(
                prompt, 
                temperature=temperature,
                max_tokens=max_tokens,
                system_instruction=system_instruction
            )
            
            if response and 'candidates' in response:
                candidate = response['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    generated_text = candidate['content']['parts'][0]['text']
                    return generated_text.strip()
                else:
                    logger.error("Invalid response format from Gemini API")
                    return ""
            else:
                logger.error("No valid response from Gemini API")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            raise
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the Gemini AI tool."""
        return {
            'name': 'Gemini AI Tool',
            'version': '1.0.0',
            'provider': 'Google',
            'model': self.model_name,
            'capabilities': [
                'text_generation',
                'lead_analysis',
                'email_generation',
                'content_summarization'
            ],
            'max_tokens': self.max_tokens,
            'temperature_range': [0.0, 1.0]
        }
    
    def _make_request(self, prompt: str, temperature: float = None, max_tokens: int = None, system_instruction: str = '') -> Optional[Dict[str, Any]]:
        """
        Make a request to the Gemini API.
        
        Args:
            prompt: The input prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            system_instruction: System instruction for the model
        
        Returns:
            Dict containing the API response or None if failed
        """
        try:
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Prepare request data
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt}
                        ]
                    }
                ],
                'generationConfig': {
                    'temperature': temperature or self.temperature,
                    'maxOutputTokens': max_tokens or self.max_tokens,
                }
            }
            
            # Add system instruction if provided
            if system_instruction:
                data['systemInstruction'] = {
                    'parts': [{'text': system_instruction}]
                }
            
            # Make request
            response = requests.post(
                url,
                headers=headers,
                json=data,
                params={'key': self.api_key},
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Gemini API failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making request to Gemini API: {e}")
            raise

"""
Sales Agent Modes Module

This module provides different operational modes for the sales agent:
- Sales Mode: Lead generation and email automation
- Market Intelligence Mode: Real-time market data analysis
"""

from .market_intelligence import MarketIntelligenceMode
from .sales_mode import SalesMode

__all__ = ['MarketIntelligenceMode', 'SalesMode']

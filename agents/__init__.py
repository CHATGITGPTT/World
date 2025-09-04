"""
World Agents
AI Agents for the World system
"""

from .base_agent import BaseAgent
from .coding_agent import CodingAgent

try:
    from .orchestrator import OrchestratorAgent
    from .data_agent import DataAgent
    from .communication_agent import CommunicationAgent
    from .business_agent import BusinessAgent
    from .analytics_agent import AnalyticsAgent
except Exception:  # pragma: no cover - optional deps
    OrchestratorAgent = None
    DataAgent = None
    CommunicationAgent = None
    BusinessAgent = None
    AnalyticsAgent = None

__all__ = [
    'BaseAgent',
    'CodingAgent',
    'OrchestratorAgent',
    'DataAgent',
    'CommunicationAgent',
    'BusinessAgent',
    'AnalyticsAgent',
]

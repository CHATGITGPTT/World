#!/usr/bin/env python3
"""
Base Agent Class
Base class for all World AI agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    type: str
    description: str
    data: Dict[str, Any]
    priority: int = 1
    created_at: datetime = None

class BaseAgent(ABC):
    """Base class for all World AI agents"""
    
    def __init__(self, name: str, services: Dict[str, Any]):
        self.name = name
        self.services = services
        self.logger = services.get('logger', logging.getLogger(name))
        self.memory = services.get('memory')
        self.file_manager = services.get('file_manager')
        self.running = False
        self.tasks = []
        
    async def start(self):
        """Start the agent"""
        self.running = True
        self.logger.info(f"Agent {self.name} started")
        
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.logger.info(f"Agent {self.name} stopped")
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass
    
    async def execute_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command"""
        try:
            task = AgentTask(
                id=f"{self.name}_{datetime.now().timestamp()}",
                type="command",
                description=command,
                data=context or {},
                created_at=datetime.now()
            )
            
            result = await self.process_task(task)
            
            # Store in memory
            if self.memory:
                await self.memory.store_experience({
                    "agent": self.name,
                    "command": command,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "tasks": len(self.tasks),
            "type": self.__class__.__name__
        }

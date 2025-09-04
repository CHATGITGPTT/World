#!/usr/bin/env python3
"""
World Orchestrator
Main orchestrator that coordinates all agents and services
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a task to be executed"""
    id: str
    type: str
    description: str
    priority: int = 1
    data: Dict[str, Any] = None
    status: str = "pending"
    created_at: datetime = None
    assigned_agent: str = None
    result: Any = None

class WorldOrchestrator:
    """Main orchestrator for the World AI Agent System"""
    
    def __init__(self, services: Dict[str, Any], agents: Dict[str, Any]):
        self.services = services
        self.agents = agents
        self.logger = services.get('logger')
        self.memory = services.get('memory')
        self.tasks = []
        self.running = False
        
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        self.logger.info("World Orchestrator started")
        
        # Start task processing loop
        asyncio.create_task(self._task_processing_loop())
        
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        self.logger.info("World Orchestrator stopped")
    
    async def execute_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command through the orchestrator"""
        try:
            # Create task
            task = Task(
                id=f"task_{datetime.now().timestamp()}",
                type="command",
                description=command,
                data=context or {},
                created_at=datetime.now()
            )
            
            # Add to task queue
            self.tasks.append(task)
            
            # Process the task
            result = await self._process_task(task)
            
            return {
                "success": True,
                "task_id": task.id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_task(self, task: Task) -> Any:
        """Process a task by assigning it to the appropriate agent"""
        try:
            # Determine which agent should handle this task
            agent_name = await self._select_agent(task)
            
            if not agent_name:
                raise ValueError(f"No suitable agent found for task: {task.description}")
            
            # Assign task to agent
            task.assigned_agent = agent_name
            task.status = "processing"
            
            # Get the agent
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            # Execute task
            result = await agent.process_task(task)
            
            # Update task status
            task.status = "completed"
            task.result = result
            
            # Store in memory
            if self.memory:
                await self.memory.store_experience({
                    "type": "task_completion",
                    "task": task.description,
                    "agent": agent_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            
            return result
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            raise
    
    async def _select_agent(self, task: Task) -> Optional[str]:
        """Select the most appropriate agent for a task"""
        task_lower = task.description.lower()
        
        # Agent selection logic
        if any(keyword in task_lower for keyword in ['code', 'program', 'script', 'build', 'create', 'develop']):
            return 'coding'
        elif any(keyword in task_lower for keyword in ['scrape', 'data', 'collect', 'extract', 'analyze']):
            return 'data'
        elif any(keyword in task_lower for keyword in ['chat', 'message', 'email', 'communicate']):
            return 'communication'
        elif any(keyword in task_lower for keyword in ['sales', 'lead', 'business', 'marketing']):
            return 'business'
        elif any(keyword in task_lower for keyword in ['report', 'analytics', 'insights', 'metrics']):
            return 'analytics'
        else:
            # Default to orchestrator for complex tasks
            return 'orchestrator'
    
    async def _task_processing_loop(self):
        """Background task processing loop"""
        while self.running:
            try:
                # Process pending tasks
                pending_tasks = [t for t in self.tasks if t.status == "pending"]
                
                for task in pending_tasks:
                    try:
                        await self._process_task(task)
                    except Exception as e:
                        self.logger.error(f"Task processing failed: {e}")
                
                # Clean up old completed tasks
                self._cleanup_old_tasks()
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Task processing loop error: {e}")
                await asyncio.sleep(5)
    
    def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        self.tasks = [
            task for task in self.tasks 
            if task.created_at.timestamp() > cutoff_time or task.status == "processing"
        ]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "orchestrator": {
                "status": "running" if self.running else "stopped",
                "tasks": {
                    "total": len(self.tasks),
                    "pending": len([t for t in self.tasks if t.status == "pending"]),
                    "processing": len([t for t in self.tasks if t.status == "processing"]),
                    "completed": len([t for t in self.tasks if t.status == "completed"]),
                    "failed": len([t for t in self.tasks if t.status == "failed"])
                }
            },
            "agents": {
                name: {"status": "active", "type": type(agent).__name__}
                for name, agent in self.agents.items()
            },
            "services": {
                name: {"status": "active", "type": type(service).__name__}
                for name, service in self.services.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def create_project(self, name: str, project_type: str = "python") -> Dict[str, Any]:
        """Create a new project"""
        return await self.execute_command(
            f"create project {name} of type {project_type}",
            {"project_name": name, "project_type": project_type}
        )
    
    async def analyze_data(self, data_source: str) -> Dict[str, Any]:
        """Analyze data from a source"""
        return await self.execute_command(
            f"analyze data from {data_source}",
            {"data_source": data_source}
        )
    
    async def generate_content(self, content_type: str, topic: str) -> Dict[str, Any]:
        """Generate content of a specific type"""
        return await self.execute_command(
            f"generate {content_type} about {topic}",
            {"content_type": content_type, "topic": topic}
        )

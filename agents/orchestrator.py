#!/usr/bin/env python3
"""
Orchestrator Agent
Coordinates all other agents and manages complex workflows
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask

class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that coordinates all other agents"""
    
    def __init__(self, services: Dict[str, Any]):
        super().__init__("orchestrator", services)
        self.other_agents = {}
        
    async def start(self):
        """Start the orchestrator"""
        await super().start()
        
        # Initialize other agents
        await self._initialize_agents()
        
    async def _initialize_agents(self):
        """Initialize other agents"""
        from .coding_agent import CodingAgent
        from .data_agent import DataAgent
        from .communication_agent import CommunicationAgent
        from .business_agent import BusinessAgent
        from .analytics_agent import AnalyticsAgent
        
        # Create agent instances
        self.other_agents = {
            "coding": CodingAgent(self.services),
            "data": DataAgent(self.services),
            "communication": CommunicationAgent(self.services),
            "business": BusinessAgent(self.services),
            "analytics": AnalyticsAgent(self.services)
        }
        
        # Start all agents
        for agent in self.other_agents.values():
            await agent.start()
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a complex task by coordinating other agents"""
        try:
            self.logger.info(f"Processing orchestrator task: {task.description}")
            
            # Analyze the task to determine workflow
            workflow = await self._analyze_task(task)
            
            # Execute workflow
            results = []
            for step in workflow:
                agent_name = step["agent"]
                step_task = step["task"]
                
                if agent_name in self.other_agents:
                    agent = self.other_agents[agent_name]
                    result = await agent.process_task(step_task)
                    results.append({
                        "agent": agent_name,
                        "step": step["description"],
                        "result": result
                    })
                else:
                    results.append({
                        "agent": agent_name,
                        "step": step["description"],
                        "error": f"Agent {agent_name} not found"
                    })
            
            return {
                "success": True,
                "workflow": workflow,
                "results": results,
                "summary": await self._generate_summary(results)
            }
            
        except Exception as e:
            self.logger.error(f"Orchestrator task failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_task(self, task: AgentTask) -> List[Dict[str, Any]]:
        """Analyze task and create workflow"""
        description = task.description.lower()
        
        # Simple workflow creation based on keywords
        workflow = []
        
        if "create project" in description:
            workflow.extend([
                {
                    "agent": "coding",
                    "description": "Create project structure",
                    "task": AgentTask(
                        id=f"create_project_{datetime.now().timestamp()}",
                        type="create_project",
                        description=task.description,
                        data=task.data
                    )
                }
            ])
        
        if "scrape" in description or "data" in description:
            workflow.extend([
                {
                    "agent": "data",
                    "description": "Collect and process data",
                    "task": AgentTask(
                        id=f"scrape_data_{datetime.now().timestamp()}",
                        type="scrape_data",
                        description=task.description,
                        data=task.data
                    )
                },
                {
                    "agent": "analytics",
                    "description": "Analyze collected data",
                    "task": AgentTask(
                        id=f"analyze_data_{datetime.now().timestamp()}",
                        type="analyze_data",
                        description="Analyze the scraped data",
                        data=task.data
                    )
                }
            ])
        
        if "generate" in description:
            workflow.extend([
                {
                    "agent": "communication",
                    "description": "Generate content",
                    "task": AgentTask(
                        id=f"generate_content_{datetime.now().timestamp()}",
                        type="generate_content",
                        description=task.description,
                        data=task.data
                    )
                }
            ])
        
        if "business" in description or "sales" in description or "lead" in description:
            workflow.extend([
                {
                    "agent": "business",
                    "description": "Handle business task",
                    "task": AgentTask(
                        id=f"business_task_{datetime.now().timestamp()}",
                        type="business_task",
                        description=task.description,
                        data=task.data
                    )
                }
            ])
        
        # If no specific workflow found, create a general one
        if not workflow:
            workflow = [
                {
                    "agent": "coding",
                    "description": "Handle general task",
                    "task": task
                }
            ]
        
        return workflow
    
    async def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate a summary of workflow results"""
        successful_steps = [r for r in results if "error" not in r]
        failed_steps = [r for r in results if "error" in r]
        
        summary = f"Workflow completed with {len(successful_steps)} successful steps"
        if failed_steps:
            summary += f" and {len(failed_steps)} failed steps"
        
        return summary
    
    async def stop(self):
        """Stop the orchestrator and all agents"""
        # Stop all other agents
        for agent in self.other_agents.values():
            await agent.stop()
        
        await super().stop()

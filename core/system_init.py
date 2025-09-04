#!/usr/bin/env python3
"""
World System Initializer
Initializes the complete World AI Agent System
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class SystemInitializer:
    """Initializes the World AI Agent System"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.config = {}
        self.services = {}
        self.agents = {}
        
    async def initialize(self) -> bool:
        """Initialize the complete system"""
        try:
            print("🌍 Initializing World AI Agent System...")
            
            # Step 1: Setup directories
            await self._setup_directories()
            
            # Step 2: Load configuration
            await self._load_configuration()
            
            # Step 3: Initialize core services
            await self._initialize_core_services()
            
            # Step 4: Initialize agents
            await self._initialize_agents()
            
            # Step 5: Setup API endpoints
            await self._setup_api()
            
            # Step 6: Start background services
            await self._start_background_services()
            
            print("✅ World AI Agent System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    async def _setup_directories(self):
        """Setup required directories"""
        directories = [
            "data", "logs", "backups", "cache", "temp",
            "data/projects", "data/scraped", "data/analytics",
            "logs/system", "logs/agents", "logs/api"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    async def _load_configuration(self):
        """Load system configuration"""
        config_file = self.base_path / "config" / "system.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Create default configuration
            self.config = {
                "system": {
                    "name": "World AI Agent System",
                    "version": "1.0.0",
                    "mode": "development"
                },
                "api": {
                    "port": 8000,
                    "host": "localhost",
                    "cors_origins": ["*"]
                },
                "agents": {
                    "orchestrator": {"enabled": True},
                    "coding": {"enabled": True},
                    "data": {"enabled": True},
                    "communication": {"enabled": True},
                    "business": {"enabled": True},
                    "analytics": {"enabled": True}
                },
                "services": {
                    "database": {"type": "sqlite", "path": "data/world.db"},
                    "redis": {"enabled": False},
                    "logging": {"level": "INFO"}
                }
            }
            
            # Save default configuration
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        
        print("⚙️ Configuration loaded")
    
    async def _initialize_core_services(self):
        """Initialize core services"""
        from .logger import WorldLogger
        from .memory import WorldMemory
        from .file_manager import WorldFileManager
        
        # Initialize logger
        self.services['logger'] = WorldLogger(self.base_path)
        
        # Initialize memory system
        self.services['memory'] = WorldMemory(self.base_path)
        
        # Initialize file manager
        self.services['file_manager'] = WorldFileManager(self.base_path)
        
        print("🔧 Core services initialized")
    
    async def _initialize_agents(self):
        """Initialize AI agents"""
        from agents.orchestrator import OrchestratorAgent
        from agents.coding_agent import CodingAgent
        from agents.data_agent import DataAgent
        from agents.communication_agent import CommunicationAgent
        from agents.business_agent import BusinessAgent
        from agents.analytics_agent import AnalyticsAgent
        
        # Initialize orchestrator
        self.agents['orchestrator'] = OrchestratorAgent(self.services)
        
        # Initialize specialized agents
        if self.config['agents']['coding']['enabled']:
            self.agents['coding'] = CodingAgent(self.services)
        
        if self.config['agents']['data']['enabled']:
            self.agents['data'] = DataAgent(self.services)
        
        if self.config['agents']['communication']['enabled']:
            self.agents['communication'] = CommunicationAgent(self.services)
        
        if self.config['agents']['business']['enabled']:
            self.agents['business'] = BusinessAgent(self.services)
        
        if self.config['agents']['analytics']['enabled']:
            self.agents['analytics'] = AnalyticsAgent(self.services)
        
        print("🤖 Agents initialized")
    
    async def _setup_api(self):
        """Setup API endpoints"""
        # API setup will be implemented later
        print("🌐 API endpoints configured")
    
    async def _start_background_services(self):
        """Start background services"""
        # Start memory refinement
        asyncio.create_task(self._memory_refinement_loop())
        
        # Start cleanup tasks
        asyncio.create_task(self._cleanup_loop())
        
        print("🔄 Background services started")
    
    async def _memory_refinement_loop(self):
        """Background memory refinement"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                if 'memory' in self.services:
                    await self.services['memory'].refine()
            except Exception as e:
                print(f"Memory refinement error: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup tasks"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hour
                if 'file_manager' in self.services:
                    await self.services['file_manager'].cleanup_temp_files()
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "services": list(self.services.keys()),
            "agents": list(self.agents.keys())
        }

async def main():
    """Main initialization function"""
    initializer = SystemInitializer()
    success = await initializer.initialize()
    
    if success:
        print("🎉 World system is ready!")
        return initializer
    else:
        print("💥 World system initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

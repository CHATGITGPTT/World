#!/usr/bin/env python3
"""
World AI Agent System - Main Entry Point
Universal AI Agent System that integrates all tools and capabilities
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# Add the World directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.system_init import SystemInitializer
from core.orchestrator import WorldOrchestrator

class WorldSystem:
    """Main World AI Agent System"""
    
    def __init__(self):
        self.initializer = None
        self.orchestrator = None
        self.running = False
    
    async def start(self, config_path: str = None):
        """Start the World system"""
        try:
            print("🌍 Starting World AI Agent System...")
            
            # Initialize system
            self.initializer = SystemInitializer()
            success = await self.initializer.initialize()
            
            if not success:
                print("❌ System initialization failed!")
                return False
            
            # Create orchestrator
            self.orchestrator = WorldOrchestrator(
                self.initializer.services,
                self.initializer.agents
            )
            
            # Start orchestrator
            await self.orchestrator.start()
            
            self.running = True
            print("✅ World AI Agent System is running!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start World system: {e}")
            return False
    
    async def stop(self):
        """Stop the World system"""
        if self.orchestrator:
            await self.orchestrator.stop()
        
        self.running = False
        print("🛑 World AI Agent System stopped")
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command"""
        if not self.orchestrator:
            return {"error": "System not initialized"}
        
        return await self.orchestrator.execute_command(command)
    
    async def interactive_mode(self):
        """Run in interactive mode"""
        print("\n🌍 World AI Agent System - Interactive Mode")
        print("Type 'help' for available commands or 'exit' to quit")
        print("-" * 60)
        
        while self.running:
            try:
                command = input("World> ").strip()
                
                if command.lower() in ['exit', 'quit']:
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower() == 'status':
                    status = await self.orchestrator.get_system_status()
                    print(f"System Status: {status}")
                elif command:
                    result = await self.execute_command(command)
                    print(f"Result: {result}")
                    print()
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        await self.stop()
    
    def show_help(self):
        """Show available commands"""
        help_text = """
🌍 World AI Agent System - Available Commands:

Core Commands:
  help                    - Show this help message
  status                  - Show system status
  exit/quit              - Exit the system

Project Commands:
  create project <name>   - Create a new project
  list projects          - List all projects
  build <description>    - Build something

Data Commands:
  scrape <url>           - Scrape data from URL
  analyze <data>         - Analyze data
  generate report        - Generate analytics report

AI Commands:
  chat <message>         - Chat with the system
  generate <content>     - Generate content
  code <description>     - Generate code

Business Commands:
  find leads <keywords>  - Find business leads
  analyze market <topic> - Analyze market trends
  create campaign        - Create marketing campaign

Examples:
  create project my-web-app
  scrape https://example.com
  generate Python web scraper
  find leads AI startups
  analyze market fintech trends

Type any natural language command and the system will understand!
        """
        print(help_text)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="World AI Agent System")
    parser.add_argument("--start-all", action="store_true", help="Start all services")
    parser.add_argument("--start-api", action="store_true", help="Start API service")
    parser.add_argument("--start-agents", action="store_true", help="Start agents")
    parser.add_argument("--start-scrapers", action="store_true", help="Start scrapers")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--command", type=str, help="Execute a single command")
    parser.add_argument("--config", type=str, help="Configuration file path")
    
    args = parser.parse_args()
    
    # Check for Gemini API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   Some features may not work properly")
        print("   Set it with: export GEMINI_API_KEY='your-api-key'")
        print()
    
    # Create and start World system
    world = WorldSystem()
    
    try:
        success = await world.start(args.config)
        
        if not success:
            sys.exit(1)
        
        if args.command:
            # Execute single command
            result = await world.execute_command(args.command)
            print(f"Command Result: {result}")
        elif args.interactive or not any([args.start_all, args.start_api, args.start_agents, args.start_scrapers]):
            # Default to interactive mode
            await world.interactive_mode()
        else:
            # Start specific services
            if args.start_all:
                print("🚀 Starting all services...")
                # Keep running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\nShutting down...")
            
            if args.start_api:
                print("🌐 Starting API service...")
                # Start API server
                from api.main import start_api_server
                await start_api_server(world.orchestrator)
            
            if args.start_agents:
                print("🤖 Starting agents...")
                # Agents are already started with orchestrator
            
            if args.start_scrapers:
                print("🕷️  Starting scrapers...")
                # Start scraper services
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await world.stop()

if __name__ == "__main__":
    asyncio.run(main())

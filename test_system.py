#!/usr/bin/env python3
"""
World AI Agent System - Test Script
Test the complete World system functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add World to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.system_init import SystemInitializer
from core.orchestrator import WorldOrchestrator

async def test_system():
    """Test the World system"""
    print("🧪 Testing World AI Agent System...")
    
    try:
        # Initialize system
        print("1. Initializing system...")
        initializer = SystemInitializer()
        success = await initializer.initialize()
        
        if not success:
            print("❌ System initialization failed!")
            return False
        
        print("✅ System initialized successfully!")
        
        # Create orchestrator
        print("2. Creating orchestrator...")
        orchestrator = WorldOrchestrator(
            initializer.services,
            initializer.agents
        )
        
        await orchestrator.start()
        print("✅ Orchestrator started!")
        
        # Test basic commands
        print("3. Testing basic commands...")
        
        # Test project creation
        print("   - Testing project creation...")
        result = await orchestrator.execute_command("create a Python web scraper project")
        print(f"   Result: {result.get('success', False)}")
        
        # Test data scraping
        print("   - Testing data scraping...")
        result = await orchestrator.execute_command("scrape data from https://example.com")
        print(f"   Result: {result.get('success', False)}")
        
        # Test content generation
        print("   - Testing content generation...")
        result = await orchestrator.execute_command("generate a marketing email about AI technology")
        print(f"   Result: {result.get('success', False)}")
        
        # Test business tasks
        print("   - Testing business tasks...")
        result = await orchestrator.execute_command("find leads for AI startups")
        print(f"   Result: {result.get('success', False)}")
        
        # Test analytics
        print("   - Testing analytics...")
        result = await orchestrator.execute_command("analyze the collected data and generate insights")
        print(f"   Result: {result.get('success', False)}")
        
        # Get system status
        print("4. Getting system status...")
        status = await orchestrator.get_system_status()
        print(f"   System status: {status['orchestrator']['status']}")
        print(f"   Active agents: {len(status['agents'])}")
        print(f"   Active services: {len(status['services'])}")
        
        # Stop orchestrator
        print("5. Stopping orchestrator...")
        await orchestrator.stop()
        print("✅ Orchestrator stopped!")
        
        print("🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🌍 World AI Agent System - Test Suite")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not set")
        print("   Some features may not work properly")
        print("   Set it with: export GEMINI_API_KEY='your-api-key'")
        print()
    
    success = await test_system()
    
    if success:
        print("\n✅ All tests passed! World system is ready to use.")
        print("\n🚀 To start the system:")
        print("   python main.py --interactive")
        print("\n📖 For more options:")
        print("   python main.py --help")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

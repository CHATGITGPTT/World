# 🌍 World - Universal AI Agent System

## 🚀 Overview

World is a comprehensive, professional-grade AI agent system that integrates all the tools and capabilities from your workspace into a unified, powerful platform. It combines:

- **AI Coding Agent System** - Advanced software development capabilities
- **Smolagents Framework** - Multi-agent coordination and tool usage
- **Web Scraping Engine** - Advanced data collection and processing
- **Chatbot System** - Conversational AI with NLU and context management
- **Lead Qualification System** - Business intelligence and lead scoring
- **Analytics Engine** - Data analysis and business insights
- **Content Generation** - AI-powered content creation
- **Sales Automation** - Lead generation and email automation

## 🏗️ Architecture

```
World/
├── core/           # Core system components
├── agents/         # AI agents and orchestrators
├── tools/          # Specialized tools and utilities
├── services/       # Microservices and APIs
├── data/           # Data storage and management
├── config/         # Configuration and environment
├── api/            # REST API endpoints
├── web/            # Web interfaces and dashboards
├── ai/             # AI models and processing
├── scrapers/       # Web scraping engines
├── analytics/      # Analytics and reporting
├── storage/        # File and database management
├── logs/           # System logs and monitoring
└── backups/        # Backup and recovery
```

## 🎯 Key Features

### 🤖 Multi-Agent System
- **Orchestrator Agent** - Coordinates all other agents
- **Coding Agent** - Software development and automation
- **Data Agent** - Data collection, processing, and analysis
- **Communication Agent** - Chat, email, and social media
- **Business Agent** - Sales, marketing, and lead management
- **Analytics Agent** - Insights, reporting, and optimization

### 🛠️ Integrated Tools
- **Web Scraping** - Advanced data collection with Playwright
- **AI Processing** - Gemini AI integration for all tasks
- **Code Execution** - Safe Python/JavaScript execution
- **File Management** - Comprehensive file operations
- **Database Operations** - SQL and NoSQL support
- **API Integration** - REST and GraphQL endpoints

### 📊 Analytics & Intelligence
- **Real-time Analytics** - Live system monitoring
- **Business Intelligence** - Lead scoring and market analysis
- **Performance Metrics** - System and agent performance
- **Predictive Analytics** - Trend analysis and forecasting

### 🔒 Security & Reliability
- **Rate Limiting** - API protection and resource management
- **Authentication** - Secure access control
- **Data Encryption** - Secure data storage and transmission
- **Backup & Recovery** - Automated backup systems
- **Error Handling** - Comprehensive error management

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# Install dependencies
pip install -r requirements.txt
npm install
```

### 2. Initialize System
```bash
python core/system_init.py
```

### 3. Start Services
```bash
# Start all services
python main.py --start-all

# Or start individual services
python main.py --start-api
python main.py --start-agents
python main.py --start-scrapers
```

### 4. Access Interfaces
- **API**: http://localhost:8000
- **Web Dashboard**: http://localhost:3000
- **Agent Console**: http://localhost:8080

## 📖 Usage Examples

### Basic Agent Interaction
```python
from core.orchestrator import WorldOrchestrator

# Initialize the system
world = WorldOrchestrator()

# Create a new project
result = world.execute_command("create a Python web scraper for e-commerce sites")

# Analyze data
analysis = world.execute_command("analyze the scraped data and generate insights")

# Generate content
content = world.execute_command("create a marketing email based on the analysis")
```

### API Usage
```bash
# Chat with the system
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Build a lead generation system", "user_id": "user123"}'

# Scrape data
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "selectors": ["h1", "p"]}'

# Get analytics
curl http://localhost:8000/api/analytics/dashboard
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
GEMINI_API_KEY=your-api-key
SYSTEM_MODE=production
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///world.db
REDIS_URL=redis://localhost:6379

# Services
API_PORT=8000
WEB_PORT=3000
AGENT_PORT=8080

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Agent Configuration
```json
{
  "agents": {
    "orchestrator": {
      "enabled": true,
      "max_concurrent_tasks": 10
    },
    "coding": {
      "enabled": true,
      "languages": ["python", "javascript", "html", "css"]
    },
    "data": {
      "enabled": true,
      "max_scrape_depth": 3,
      "rate_limit": 1000
    }
  }
}
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Test Individual Components
```bash
# Test agents
python tests/test_agents.py

# Test API
python tests/test_api.py

# Test scrapers
python tests/test_scrapers.py
```

## 📈 Monitoring

### System Health
```bash
# Check system status
curl http://localhost:8000/health

# Get performance metrics
curl http://localhost:8000/api/metrics
```

### Logs
```bash
# View system logs
tail -f logs/system.log

# View agent logs
tail -f logs/agents.log
```

## 🔮 Advanced Features

### Custom Agent Development
```python
from core.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent")
    
    def process_task(self, task):
        # Your custom logic here
        return self.execute_task(task)
```

### Plugin System
```python
from core.plugin_manager import PluginManager

# Load custom plugins
plugin_manager = PluginManager()
plugin_manager.load_plugin("custom_plugin.py")
```

### Workflow Automation
```python
from core.workflow_engine import WorkflowEngine

# Define automated workflows
workflow = WorkflowEngine()
workflow.add_step("scrape_data", {"url": "https://example.com"})
workflow.add_step("analyze_data", {"model": "gemini"})
workflow.add_step("generate_report", {"format": "pdf"})
workflow.execute()
```

## 🛡️ Security

### Authentication
- JWT-based authentication
- Role-based access control
- API key management
- Rate limiting

### Data Protection
- Encryption at rest and in transit
- Secure file handling
- Privacy-compliant data processing
- Audit logging

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Development Guide](docs/agents.md)
- [Configuration Reference](docs/config.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the docs/ folder
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: support@world-ai.com

---

**🌍 Welcome to World - Where AI Agents Unite! 🚀**

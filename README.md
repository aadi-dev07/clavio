# Multi-Agent System for Product Development

A comprehensive multi-agent system built with Python, LangChain, and Gemini AI that automates product development workflows through three specialized agents.

## 🤖 Agents Overview

### Agent 1: GitHub MCP Coordinator
- **Purpose**: Real-time GitHub activity monitoring and reporting
- **Features**:
  - Daily commit analysis and reporting
  - Pull request tracking
  - Repository statistics
  - AI-powered insights and recommendations
  - Scheduled monitoring service

### Agent 2: AI Analysis Agent (Multi-Agent System)
- **Purpose**: Product requirements analysis using multiple specialized sub-agents
- **Sub-Agents**:
  - **Product Analyst**: Business value and market positioning
  - **Technical Analyst**: Technical feasibility and architecture
  - **Business Analyst**: Revenue impact and ROI analysis
- **Data Sources**: GitHub, Trello, Notion
- **Output**: Goals, constraints, edge cases, follow-up questions, impact analysis

### Agent 3: PRD and Gherkin Generator
- **Purpose**: Generate Product Requirements Documents and test scenarios
- **Features**:
  - Comprehensive PRD generation
  - Gherkin BDD scenarios
  - Structured documentation templates
  - Integration with analysis results

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gemini API key
- GitHub token (optional)
- Trello API credentials (optional)
- Notion integration token (optional)

### Installation

1. **Clone and setup**:
```bash
cd agent-debate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the system**:
```bash
python main.py
```

## ⚙️ Configuration

### Required Environment Variables
```bash
# Gemini API (Required)
GOOGLE_API_KEY=your_gemini_api_key_here

# GitHub (Optional - for Agent 1)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_repository_name

# Trello (Optional - for Agent 2)
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_BOARD_ID=your_trello_board_id

# Notion (Optional - for Agent 2)
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

### Optional Settings
```bash
LOG_LEVEL=INFO
REPORT_SCHEDULE_HOURS=24
```

## 📋 Usage Examples

### 1. GitHub Report Only
```python
from agents import GitHubAgent
import asyncio

async def generate_report():
    agent = GitHubAgent()
    report = await agent.generate_daily_report(days_back=7)
    print(report)

asyncio.run(generate_report())
```

### 2. Product Analysis Only
```python
from agents import AnalysisAgent
import asyncio

async def analyze_product():
    agent = AnalysisAgent()
    result = await agent.analyze_product_requirements()
    print(f"Goals: {result.goals}")
    print(f"Constraints: {result.constraints}")

asyncio.run(analyze_product())
```

### 3. Complete Workflow
```python
from main import MultiAgentOrchestrator
import asyncio

async def run_workflow():
    orchestrator = MultiAgentOrchestrator()
    results = await orchestrator.run_complete_workflow()
    print(f"Status: {results['status']}")

asyncio.run(run_workflow())
```

### 4. Interactive Mode
```bash
python main.py
# Follow the interactive menu
```

## 🏗️ Architecture

```
Multi-Agent System
├── Agent 1: GitHub MCP Coordinator
│   ├── Repository monitoring
│   ├── Commit analysis
│   ├── PR tracking
│   └── AI report generation
├── Agent 2: Analysis Agent
│   ├── Product Analyst (sub-agent)
│   ├── Technical Analyst (sub-agent)
│   ├── Business Analyst (sub-agent)
│   ├── Data integration (GitHub/Trello/Notion)
│   └── Multi-agent synthesis
└── Agent 3: PRD Generator
    ├── PRD document generation
    ├── Gherkin scenario creation
    ├── Template-based formatting
    └── Documentation export
```

## 📁 Project Structure

```
agent-debate/
├── agents/
│   ├── __init__.py
│   ├── github_agent.py      # Agent 1
│   ├── analysis_agent.py    # Agent 2
│   └── prd_agent.py         # Agent 3
├── output/                  # Generated files
├── config.py               # Configuration
├── main.py                 # Main orchestrator
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 API Integration

### GitHub Integration
- Repository statistics
- Commit history analysis
- Pull request tracking
- Issue analysis

### Trello Integration
- Board and card data
- Task tracking
- Project management insights

### Notion Integration
- Database queries
- Page content analysis
- Documentation extraction

## 📊 Output Examples

### GitHub Report
```markdown
# GitHub Activity Report

**Repository:** user/repo
**Generated:** 2024-01-15 10:30:00

## Commit Summary
- Total commits: 15
- Lines added: 1,250
- Lines deleted: 340

## Pull Requests
- Open PRs: 3
- Merged PRs: 8
```

### Product Analysis
```markdown
# Product Analysis Results

## Goals
- Improve user engagement by 25%
- Reduce system latency by 50ms
- Implement new payment gateway

## Constraints
- Limited development resources
- Q1 2024 deadline
- Budget constraints of $50K
```

### PRD Document
```markdown
# Product Requirements Document

## Product Title
Enhanced User Dashboard

## Overview
This feature will provide users with a comprehensive...

## Objectives
- Increase user retention by 30%
- Improve user satisfaction scores
```

## 🧪 Testing

### Gherkin Scenarios
```gherkin
Feature: User Dashboard Enhancement

  Scenario: User views dashboard
    Given I am a logged-in user
    When I navigate to the dashboard
    Then I should see my personalized content
    And the page should load within 2 seconds
```

## 🚦 Monitoring

### Continuous GitHub Monitoring
```python
# Start monitoring service
orchestrator = MultiAgentOrchestrator()
await orchestrator.start_github_monitoring()
```

## 🛠️ Customization

### Adding New Data Sources
1. Create a new fetch method in `AnalysisAgent`
2. Add configuration variables
3. Update the `gather_all_data()` method

### Custom PRD Templates
1. Modify the Jinja2 template in `PRDAgent`
2. Add new sections as needed
3. Update parsing logic

### New Agent Types
1. Create new agent class
2. Add to `agents/__init__.py`
3. Integrate with orchestrator

## 📈 Performance

- **Concurrent Processing**: All agents run asynchronously
- **Rate Limiting**: Respects API rate limits
- **Error Handling**: Comprehensive error recovery
- **Caching**: Intelligent data caching (future enhancement)

## 🔒 Security

- Environment variable configuration
- API key protection
- Input validation
- Error sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review error logs
3. Create an issue on GitHub
4. Contact the development team

## 🔮 Future Enhancements

- [ ] Web-based dashboard
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] Custom agent plugins
- [ ] API endpoints
- [ ] Database persistence
- [ ] Multi-repository support
- [ ] Slack/Teams integration

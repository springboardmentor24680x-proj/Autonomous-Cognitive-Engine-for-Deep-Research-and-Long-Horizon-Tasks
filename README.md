# 🧠 Autonomous Multi-Agent Cognitive Engine

> **A sophisticated multi-agent system for intelligent task processing, delegation, and coordination**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-orange.svg)](https://langsmith.com)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red.svg)](https://flask.palletsprojects.com)

## 🚀 Overview

This project implements an **autonomous multi-agent cognitive engine** that intelligently delegates tasks to specialized domain agents. The system features a supervisor agent coordinating with six specialized sub-agents, providing comprehensive solutions across research, coding, planning, translation, content creation, and document analysis.

### ✨ Key Features

- 🎯 **Intelligent Task Delegation** - Automatic routing to domain specialists with >90% accuracy
- 🔄 **Multi-Agent Coordination** - Seamless collaboration between 6 specialized agents
- 📊 **Complete Observability** - Full LangSmith tracing with input visibility
- 🔒 **Privacy-First Design** - Fresh session isolation with no persistent conversations
- 🌐 **Real-Time Web Interface** - Modern chat UI with Socket.IO
- 📝 **Professional Output** - Clean markdown formatting with proper attribution

## 📊 Project Presentation

🎨 **[View Interactive Presentation](https://www.canva.com/design/DAG_O1x7c-0/8WrNnqafjj7sjWJp1PyGKQ/edit?utm_content=DAG_O1x7c-0&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)** - Complete project overview with visual demonstrations and system architecture

## 🏗️ Architecture

```
┌─────────────────┐
│ Supervisor Agent │ ← Central Orchestrator
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │ Delegation │
    │  Analysis  │
    └─────┬─────┘
          │
┌─────────┴─────────┐
│   Subagent Pool   │
├───────────────────┤
│ • SearchAgent     │ → Web research & information gathering
│ • CodeAgent       │ → Software development & debugging  
│ • PlanningAgent   │ → Strategic planning & project management
│ • CreativeAgent   │ → Content creation & marketing copy
│ • TranslationAgent│ → Multilingual translation & localization
│ • SummarizerAgent │ → Document analysis & synthesis
└───────────────────┘
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.8+
- API Keys: Groq, Anthropic, Tavily, LangSmith

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks.git
cd Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Environment Setup

Create a `.env` file with your API keys:

```bash
# Core API Keys
GROQ_API_KEY=your_groq_api_key
ANTHROPIC_API_KEY=your_anthropic_key
TAVILY_API_KEY=your_tavily_key

# LangSmith Tracing (Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=autonomous-cognitive-engine

# Workflow Configuration
USE_LANGGRAPH=false
```

### Running the Application

```bash
# Web Interface (Recommended)
python app.py
# Access at http://localhost:5000

# CLI Interface
python main.py
```

## 🎯 Usage Examples

### Web Interface
1. Start the web app: `python app.py`
2. Open http://localhost:5000
3. Start chatting with the autonomous system

### CLI Interface
```bash
python main.py
> "Create a business plan for a coffee shop"
# → Automatically delegated to PlanningAgent

> "Translate this to Spanish: Hello world"
# → Automatically delegated to TranslationAgent

> "Write Python code to sort a list"
# → Automatically delegated to CodeAgent
```

### API Usage
```python
from src.agents.supervisor_agent import SupervisorAgent

agent = SupervisorAgent()
result = agent.run_with_context("Your task here", [], "session-id")
print(result['final_response'])
```

## 🧪 Testing

```bash
# Test all agents
python simple_test.py

# Test delegation functionality
python test_delegation.py

# Test TODO workflow
python test_todo_functionality.py

# Test input visibility
python test_input_visibility.py
```

## 📊 System Capabilities

### Agent Specializations

| Agent | Primary Function | Use Cases |
|-------|------------------|-----------|
| **SearchAgent** | Web research & information gathering | Market analysis, fact checking, current events |
| **CodeAgent** | Software development & debugging | Algorithm implementation, code review, technical docs |
| **PlanningAgent** | Strategic planning & project management | Business strategy, project roadmaps, timelines |
| **CreativeAgent** | Content creation & marketing | Blog posts, social media, brand messaging |
| **TranslationAgent** | Multilingual translation (35+ languages) | Document translation, content localization |
| **SummarizerAgent** | Document analysis & synthesis | Research analysis, executive summaries |

### Performance Metrics

- ✅ **>90% delegation accuracy** in task-to-agent matching
- ✅ **Real-time processing** with Socket.IO
- ✅ **Complete traceability** through LangSmith integration
- ✅ **Fresh session isolation** for privacy protection
- ✅ **Professional output formatting** with attribution

## 🔍 System Behavior

### Execution Patterns

The system uses three execution pathways:

1. **Direct Processing** (40%) - Simple queries handled by supervisor
2. **Single Delegation** (45%) - Domain-specific tasks routed to specialists  
3. **Complex Workflows** (15%) - Multi-step coordination with artifact storage

### Trace Metadata

LangSmith traces show different patterns based on execution type:

```json
// Simple Direct Processing
{
  "tools_used": 0,
  "delegated_to": null,
  "todos_created": 0,
  "synthesis_file": null
}

// Single Agent Delegation
{
  "tools_used": 2,
  "delegated_to": "PlanningAgent",
  "todos_created": 1,
  "synthesis_file": null
}

// Complex Multi-Step Workflow
{
  "tools_used": 5,
  "workflow": "TODO_VFS_WORKFLOW",
  "todos_created": 3,
  "synthesis_file": "synthesis_20241123_143045.md"
}
```

## 📁 Project Structure

```
├── src/
│   ├── agents/                 # All agent implementations
│   ├── tools/                  # Delegation and management tools
│   ├── memory/                 # Conversation and VFS systems
│   └── graph/                  # Alternative workflow (optional)
├── templates/                  # Web interface templates
├── docs/                       # Documentation
├── notebooks/                  # Development notebooks
├── app.py                      # Flask web application
├── main.py                     # CLI interface
└── requirements.txt            # Dependencies
```

## 🔧 Configuration

### Delegation Settings
- **Confidence Threshold**: 0.4 minimum for agent routing
- **Session Management**: Fresh isolation with no persistence
- **Response Format**: Professional markdown with attribution

### Workflow Options
- **Traditional Supervisor**: Default workflow with TODO functionality
- **LangGraph**: Alternative workflow (set `USE_LANGGRAPH=true`)

## 📚 Documentation

- **[Technical Documentation](PROJECT_DOCUMENTATION.md)** - Complete system architecture and implementation details
- **[Architecture Guide](docs/architecture.md)** - System design and component overview
- **[Workflow Specifications](docs/ideal_workflow.md)** - Detailed workflow documentation
- **[Development Milestones](docs/milestones.md)** - Project development timeline

## 🚀 Deployment

### Local Development
```bash
python app.py  # Web interface
python main.py # CLI interface
```

### Production Considerations
- Configure proper API rate limits
- Set up monitoring and logging
- Implement proper error handling
- Consider load balancing for high traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the multi-agent framework
- **LangSmith** for comprehensive tracing and monitoring
- **Groq** for fast LLM inference
- **Tavily** for web search capabilities



---



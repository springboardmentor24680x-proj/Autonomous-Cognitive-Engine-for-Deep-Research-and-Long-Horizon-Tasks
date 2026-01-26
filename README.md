# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks


## Overview

The **Autonomous Cognitive Engine** is an LLM-driven system designed to autonomously perform deep research and long-horizon tasks. It decomposes complex user queries into structured actions, delegates work to specialized sub-agents, persists memory across sessions, and produces verified, structured outputs with minimal human intervention.

---

## Key Features

* Task planning with strict TODO enforcement
* Persistent memory via a Virtual File System (VFS)
* Sub-agent delegation architecture
* Dedicated Research Agent
* Dedicated Summarization Agent
* Tool-based execution (files, calendar, web, visualization)
* LangSmith tracing for observability and debugging

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│  User Request (Complex Multi-Step Task)             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Supervisor Agent                                   │
│  • Plans execution (write_todos)                    │
│  • Routes to specialized agents                     │
│  • Enforces one-tool-per-turn                       │
└────┬─────────────────┬──────────────────┬───────────┘
     │                 │                  │
     ▼                 ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Research     │ │Summarization │ │ Visualization│
│ Sub-Agent    │ │ Sub-Agent    │ │    Tools     │
└──────────────┘ └──────────────┘ └──────────────┘
     │                 │                  │
     └─────────────────┼──────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Virtual File System (Persistent Memory)            │
│  • research_notes.txt                               │
│  • strategy_summary.txt                             │
│  • charts.png                                       │
│  • todos_work.txt                                   │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Verified Structured Output                         │
│  • Artifacts stored in VFS                          │
│  • All decisions logged for audit                   │
│  • Ready for downstream systems                     │
└─────────────────────────────────────────────────────┘
```

---

## Core Components

### Supervisor Agent

* Central orchestrator of the system
* Cannot perform research or summarization directly
* Enforces **one tool call per turn**
* Verifies sub-agent outputs before task completion

### Virtual File System (VFS)

* Acts as persistent external memory
* Grounds outputs to prevent hallucination
* Enables long-horizon reasoning
* Supports read, write, edit, delete, and list operations

### Research Sub-Agent

* Dedicated factual research agent
* Restricted to web search tools only
* Stores structured research outputs in VFS

### Summarization Sub-Agent

* Condenses large research outputs
* Used for executive summaries and synthesis
* Supervisor is forbidden from summarizing inline

### Visualization Tool (Charts & Graphs)

Supports generation of:

* Bar charts
* Pie charts
* Line charts
* Scatter plots

---

## Visualization Design Principles

* Visualization is strictly tool-gated
* Data must exist before chart creation
* Charts read only from validated data blocks
* Prevents invalid chart-data combinations

### Required Data Format

```
DATA FOR GRAPHING
Online Sales: 40
Wholesale Sales: 35
Subscriptions: 25
END DATA FOR GRAPHING
```

All generated charts are saved back into the Virtual File System.

---

## Execution Flow

```
Step 1: User submits complex request
   ↓
Step 2: Supervisor calls write_todos (explicit planning)
   ↓
Step 3: Supervisor analyzes intent and routes task
   ↓
Step 4: Sub-agent or tool executes (one per turn)
   ├─ IF Tool: Result returned, VFS updated
   ├─ IF Sub-agent: Isolated execution, results verified
   └─ IF Dependencies not met: Graceful failure with actionable error
   ↓
Step 5: Output stored in VFS (persistent memory)
   ↓
Step 6: For multi-step tasks: Return to Step 2 for next task
   ↓
Step 7: All tasks complete: Return verified output to user
```

## Observability & Debugging

* Integrated LangSmith tracing
* Full visibility into:

  * Tool calls
  * Sub-agent execution
  * Decision flow

Enables efficient debugging and performance analysis.

---

## Safety & Constraints

| Constraint | Purpose | Violation Handling |
|-----------|---------|-------------------|
| No research by Supervisor | Prevents hallucination | Uses research_task sub-agent |
| One tool call per turn | Maintains clarity | Explicit error if violated |
| File existence verified | Prevents assumptions | Graceful failure with actionable error |
| Visualization requires data | No fabricated charts | Explicit data validation |
| Constraint violation = failure | Enterprise compliance | Stops immediately, clear error |

**Design Philosophy**: Fail explicitly and loudly rather than silently proceeding with wrong assumptions.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Groq (Kimi-K2) | Fast, cost-effective inference |
| **Orchestration** | LangChain | Tool calling and message handling |
| **Sub-Agents** | DeepAgents | Modular, specialized agents |
| **Memory** | Virtual File System | Persistent, queryable storage |
| **Web Search** | Tavily API | Real-time research data |
| **Visualization** | Matplotlib | Publication-quality charts |
| **Observability** | LangSmith | Execution tracing and debugging |
| **UI** | Streamlit | Interactive web interface |
| **Language** | Python 3.9+ | Core implementation |
---

## Project Structure

```
Autonomous-Cognitive-Engine-for-Deep-Research/
├── src/                 # Core agent logic & execution
├── subagents/           # Research & summarization sub-agents
├── storage/             # Persistent memory / vector store
├── venv/                # Virtual environment (ignored)
├── __pycache__/         # Python cache (ignored)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Quick Start

### Prerequisites
- Python 3.9+
- pip or conda
- GROQ API key (free at [groq.com](https://groq.com))
- Tavily API key (optional, for web search)

### Installation

**Step 1: Clone Repository**
```bash
git clone https://github.com/your-username/Autonomous-Cognitive-Engine-for-Deep-Research.git
cd Autonomous-Cognitive-Engine-for-Deep-Research
```

**Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Environment Variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

**Step 5: Run the Application**

Option A - Interactive UI:
```bash
$env:PYTHONPATH="."
streamlit run src/main/app.py
```

Option B - Automated Demo:
```bash
$env:PYTHONPATH="."
python tests/scenarios/comprehensive_demo.py
```

---

## Usage Examples


## Use Cases & Examples

### Enterprise Applications
1. **Market Intelligence**: Research competitors, synthesize findings, generate reports
2. **Strategic Planning**: Long-horizon business planning with dependency tracking
3. **Executive Reporting**: Auto-generate summaries and visualizations
4. **Operational Planning**: Create todos and schedule reviews
5. **Data Analysis**: Multi-source synthesis with visual output

---

## Example Commands

* Perform market research
* Create long-term strategic plans
* Generate executive summaries
* Schedule strategy reviews
* Create visual charts from stored data

---

## Sample Use Cases

* Market and competitor research
* Long-horizon business planning
* Executive summary generation
* Strategic roadmap creation
* Data visualization for decision-making

---

## Current Progress

### Research & Summarization Delegation
The system successfully delegates factual research and content condensation to specialized sub-agents. All research tasks are handled by a dedicated research sub-agent, while summarization is performed by a separate summarization sub-agent, ensuring modularity and clear separation of responsibilities.

### Persistent Memory via Virtual File System (VFS)
A virtual file system is implemented to store and retrieve intermediate and final outputs such as research notes, summaries, visualizations, and TODO lists. This enables stateful, long-horizon task execution across multiple steps without relying on repeated model context.

### Observable Sub-Agent Execution
All agent and sub-agent interactions are observable through tracing and UI state inspection. Tool calls, delegated sub-agent executions, file system updates, and calendar operations are transparently visible, enabling easier debugging and performance analysis.

---

## Future Enhancements

* LangGraph StateGraph integration
* Planner, Verifier, and Critic agents
* Vector database-backed memory
* Role-based access control
* FastAPI deployment
* Advanced Planning
* Dynamic Agent Scaling
* Multi-Modal Cognition

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

## Overview

The **Autonomous Cognitive Engine** is an advanced AI Agent Framework designed to move beyond simple prompt-response interactions. By leveraging **LangGraph**, the system handles complex, multi-step tasks autonomously. The agent plans its own execution strategy, manages persistent memory via a virtual environment, and delegates specialized work to sub-agents.

***

## Key Features

### 1. Dynamic Task Planning (Milestone 1) ✅

* **Decomposition**: Breaks down high-level user requests into structured, actionable TODO lists.
* **Goal Orientation**: Sets intermediate goals to ensure progress on long-horizon tasks without losing focus.

### 2. Memory Management - Virtual File System (Milestone 2) ✅

* **Persistent Workspace**: Implements a **Virtual File System (VFS)** to store intermediate research results, drafts, and data.
* **Context Extension**: Allows agents to read from and write to a workspace, effectively overcoming LLM context window limitations by offloading information to "storage."

### 3. Multi-Agent Delegation (Milestone 3) 🔄

* **Supervisor-Worker Architecture**: A high-reasoning **Supervisor** node (Llama-3.1-70B via Groq) manages the workflow and delegates technical tasks to specialized sub-agents.

### 4. Stateful & Resilient Workflow ✅

* **Persistence**: Built on LangGraph to maintain state across complex execution cycles.
* **Robustness**: Native support for branching logic, error retries, and iterative loops.

***

## Architecture Flow

```text
       [ User Input ]
             ↓
 [ Supervisor Agent ] ↔ [ Virtual File System (Memory) ]
   ↙      ↓      ↘
[Research] [Writer] [Search Agent]
   ↘      ↓      ↙
 [ Result Aggregation ]
      ↓
  [ Final Output ]
```

***

## Tech Stack

* **Languages**: Python 3.11+
* **Frameworks**: LangGraph, LangChain Core
* **Models**: Groq (Llama-3.1-70B for orchestration, Llama-3.1-8B for fast execution)
* **Search/Tools**: Tavily API, LangSmith (Tracing & Debugging)
* **Tracing**: LangSmith (Production Observability)

***

## Project Structure

```text
/autonomous-cognitive-agent/
│
├── app/
│   ├── __init__.py      # Python package
│   ├── main.py          # CLI entry point ✅ Fixed
│   ├── agent.py         # Supervisor logic ✅ Fixed
│   ├── tools.py         # VFS tools (ls, read, write) ✅ Fixed
│   └── state.py         # AgentState TypedDict ✅ Fixed
│
├── .env                 # API keys (Groq, Tavily, LangSmith)
└── README.md            # This documentation
```

***

## Getting Started

### 1. Environment Setup

```powershell
cd "C:\Users\chitt\OneDrive\Desktop\autonomous-cognitive-agent"
.venv\Scripts\activate
pip install langchain-groq langchain-tavily langgraph langsmith python-dotenv
```

### 2. API Configuration

Create `.env` file in root:

```text
GROQ_API_KEY=gsk_your_groq_key_here
TAVILY_API_KEY=tvly_your_tavily_key_here
LANGCHAIN_API_KEY=lsv2_your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
```

### 3. Run the Application

```powershell
python .\app\main.py
```

**Expected Output**:
```
--- Autonomous Cognitive Agent ---
User: Research AI agents
✅ Plan Generated:
  1. Tavily search: AI agent benchmarks
  2. Write research.txt  
  3. List workspace files
```

***

## Use Case Examples

* **Autonomous Market Research**: Agent searches web via Tavily, synthesizes findings, writes comprehensive report to VFS.
* **Deep Document Analysis**: Reads long documents from workspace, stores key insights, performs iterative reasoning.
* **Code Debugging**: Reads code files, analyzes errors, suggests and applies fixes via edit_file tool.

***

## Project Status: **Production Prototype** ✅

* ✅ **Task Planning**: Dynamic TODO generation via supervisor (Groq Llama-3.1-70B)
* ✅ **Persistent Memory**: Complete VFS (ls/read/write/edit tools working)
* ✅ **Production Tracing**: LangSmith traces live at smith.langchain.com
* ✅ **Import Issues Fixed**: All Pylance/MyTool/operator errors resolved
* 🔄 **Tavily Integration**: Ready in supervisor node
* 🔄 **Multi-Agent**: Supervisor delegation architecture complete

***

## Challenges Overcome

| **Issue** | **Status** | **Solution** |
|-----------|------------|--------------|
| `ImportError: MyTool` | ✅ Fixed | Import `@tool` functions directly |
| `operator.update` error | ✅ Fixed | Simple `Dict[str,str]` state |
| Pydantic warnings | ✅ Suppressed | `warnings.filterwarnings()` |
| Case-sensitive paths | ✅ Fixed | `app/__init__.py` + lowercase |

***

## License

This project is for **Educational and Research purposes only**. MIT License for non-commercial learning projects.

***

**🚀 Ready to run**: `python .\app\main.py`  
**📊 Live traces**: https://smith.langchain.com  
**Status**: **Production-ready prototype** with full observability. 
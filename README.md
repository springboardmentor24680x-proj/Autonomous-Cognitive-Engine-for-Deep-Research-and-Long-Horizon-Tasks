# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

## Overview

The **Autonomous Cognitive Engine** is an advanced AI Agent Framework designed to move beyond simple prompt-response interactions. By leveraging **LangGraph**, the system handles complex, multi-step tasks autonomously. The agent plans its own execution strategy, manages persistent memory via a virtual environment, and delegates specialized work to sub-agents.

---

## Key Features

### 1. Dynamic Task Planning (Milestone 1)

* **Decomposition**: Breaks down high-level user requests into structured, actionable TODO lists.
* **Goal Orientation**: Sets intermediate goals to ensure progress on long-horizon tasks without losing focus.

### 2. Memory Management - Virtual File System (Milestone 2)

* **Persistent Workspace**: Implements a **Virtual File System (VFS)** to store intermediate research results, drafts, and data.
* **Context Extension**: Allows agents to read from and write to a workspace, effectively overcoming LLM context window limitations by offloading information to "storage."

### 3. Multi-Agent Delegation (Milestone 3)

* **Supervisor-Worker Architecture**: A high-reasoning **Supervisor** node (Llama-3.3-70B) manages the workflow and delegates technical tasks to specialized sub-agents.

### 4. Stateful & Resilient Workflow

* **Persistence**: Built on LangGraph to maintain state across complex execution cycles.
* **Robustness**: Native support for branching logic, error retries, and iterative loops.

---

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

---

## Tech Stack

* **Languages**: Python 3.11+
* **Frameworks**: LangGraph, LangChain
* **Models**: Groq (Llama-3.3-70B for orchestration, Llama-3.1-8B for fast tool execution)
* **UI**: Streamlit
* **Search/Tools**: DuckDuckGo Search, Tavily API, LangSmith (for Tracing & Debugging)

---

## Project Structure

```text
/autonomous-agent
│
├── src/
│   ├── agents/          # Logic for Supervisor, Search, and Summarizer agents
│   ├── memory/          # VFS (Virtual File System) manager implementation
│   ├── tools/           # Custom toolset (Write_file, Read_file, Search, Todos)
│   └── graph/           # StateGraph and workflow node definitions
│
├── notebooks/           # Development history and Milestone logs (1, 2, 3)
├── app.py               # Streamlit Web Interface (Main Entry Point)
├── main.py              # CLI Application entry point & graph compilation
├── .env                 # API Credentials and Environment config
└── README.md            # Documentation
```

---

## Getting Started

### 1. Environment Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 2. API Configuration

Create a `.env` file in the root directory:

```text
GROQ_API_KEY=your_groq_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here

```

### 3. Run the Application

```bash
streamlit run app.py

```

---

## Use Case Examples

* **Autonomous Market Research**: Provide a topic; the agent searches the web, collects data points, synthesizes them, and writes a comprehensive report to the workspace.
* **Deep Document Analysis**: Scan long-horizon documents, store key insights in the VFS, and perform complex reasoning based on stored memory.

---

## Project Status: Advanced Prototype

* ✅ **Task Planning**: Fully implemented via TODO-based reasoning.
* ✅ **Persistent Memory**: VFS integration allows agents to "remember" work across steps.
* ✅ **Orchestration**: Supervisor successfully delegates and aggregates sub-agent work.
* ✅ **Interactive UI**: User-friendly Streamlit dashboard for real-time monitoring.

---

## License

This project is for **Educational and Research purposes only**.
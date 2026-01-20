#  Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks

This project implements a **multi-agent research system** using **LangGraph**, **LangChain**, **LangSmith tracing**, and **Streamlit UI**. The system is designed to clearly separate **planning**, **research**, **search**, and **summarization** responsibilities, while keeping **all reasoning and execution traces inside LangSmith** and **only final outputs + files visible in the UI**.

---

##  Key Features

*  **Planner Agent** – Breaks a user query into structured TODOs
*  **Search Agent** – Executes web searches using Tavily
*  **Research Agent** – Coordinates tools and prepares content
*  **Summarizer Agent** – Produces concise summaries
*  **Virtual File System (VFS)** – Shared memory across agents
*  **LangSmith Tracing** – Full internal visibility (planner → tools → agents)
*  **Streamlit UI** – Clean UI with sidebar files only (no internal thoughts)

---

##  Project Structure

```
src/
├── app.py                     # Streamlit UI entry point
│
├── agents/
│   └── agents/
│       ├── planner_agent.py   # Task planning agent (TODO generator)
│       ├── research_agent.py  # Orchestrates research flow
│       ├── search_agent.py    # Calls web search tool
│       └── summarizer_agent.py# Summarization agent
│
├── graph/
│   ├── state.py               # AgentState definition
│   ├── state_graph.py         # Main LangGraph construction
│   └── research_graph.py      # Research execution flow
│
├── memory/
│   └── vfs.py                 # Virtual File System (shared memory)
│
├── tools/
│   ├── llm_factory.py         # Centralized LLM creation (OpenRouter)
│   ├── web_search.py          # Tavily web search tool (traceable)
│   ├── summarizer_tool.py     # Summarizer tool (traceable)
│   ├── write_todos.py         # Writes planner TODOs into VFS
│   └── shared_resources.py    # Shared constants / helpers
│
└── __pycache__/               # Python cache files
```

---

##  Environment Variables

Create a `.env` file at the project root:

```env
# LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=deep-agent-system

# LLM (OpenRouter)
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxx

# Web Search
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
```

**Important**: OpenRouter keys **must NOT** be used with `ChatOpenAI`. All LLMs are created via `llm_factory.py`.

---

##  Agent Responsibilities

###  Planner Agent (`planner_agent.py`)

* Converts user query into structured TODOs
* Writes TODOs to VFS
* Appears in LangSmith as `planner_agent`

### 🔍 Search Agent (`search_agent.py`)

* Calls the `web_search` tool
* No reasoning leakage to UI
* Fully traceable

###  Research Agent (`research_agent.py`)

* Decides which tools to call
* Aggregates search results
* Passes content to summarizer

###  Summarizer Agent (`summarizer_agent.py`)

* Produces final summary
* Uses LLM directly
* Appears as `summarizer_agent` in traces

---

##  Tools

###  Web Search Tool (`tools/web_search.py`)

* Uses Tavily API
* Decorated with `@traceable`
* Appears as a tool node in LangSmith

###  Summarizer Tool (`tools/summarizer_tool.py`)

* Standalone summarization tool
* Traceable
* Can be reused independently if needed

---

##  Virtual File System (VFS)

* Implemented in `memory/vfs.py`
* Acts as shared memory between agents
* Displayed **only in Streamlit sidebar**
* Examples:

  * `todos.json`
  * `research.txt`
  * `summary.md`

---

##  LangSmith Tracing (Critical Design)

**What goes into tracing**

* Planner decisions
* Tool calls
* LLM calls
* Agent transitions
 **What does NOT go into UI**

* Chain-of-thought
* Intermediate reasoning
* Tool internals

This ensures mentor-level observability **without leaking reasoning**.

---

##  Running the App

```bash
# Activate venv
source venv/bin/activate  # or venv\\Scripts\\activate

# Run Streamlit
streamlit run src/app.py
```

---

##  UI Behavior

* **Main Chat**: User query → planned tasks → final summary
* **Sidebar**:

  * Virtual files only
  * No agent thoughts
* **Tracing**: View everything in LangSmith dashboard

---

## 🧪 Typical Flow

1. User enters a query
2. Planner creates TODOs
3. Research agent invokes search
4. Search agent calls web tool
5. Summarizer agent produces summary
6. Files written to VFS
7. UI shows summary + files

---

##  Design Philosophy

> **UI is for results. Tracing is for thinking.**

This architecture is built to be:

* Mentor-review friendly
* Debuggable
* Extensible (code agent, math agent, etc.)
* Production-aligned

---

##  Future Extensions

* Code Agent
* PDF ingestion
* Vector store memory
* Multi-session persistence

---
 **This README matches your current folder structure and tracing-first architecture.**

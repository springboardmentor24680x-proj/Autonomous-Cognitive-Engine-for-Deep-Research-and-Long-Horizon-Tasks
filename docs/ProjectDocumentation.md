# LangGraph-Based Autonomous Research Agent  
## Project Report & Technical Documentation

---

## 1. Project Introduction

This project implements an **Autonomous Research Agent** using **LangGraph**, **LangChain**, and **LangSmith tracing**.  
The system is designed to handle multi-step research workflows by decomposing a user query into planning, research, and summarization phases.

Unlike simple chatbots, this agent:

- Uses explicit state management  
- Separates responsibilities across specialized agents  
- Executes tasks in a deterministic, traceable pipeline  
- Provides full observability using LangSmith  

The application exposes a **Streamlit-based UI** while keeping all reasoning, planning, and execution details **outside the UI and inside LangSmith traces**.

---

## 2. Overall Architecture

The system follows a **linear LangGraph execution pipeline**:

User Query
↓
Planner Agent
↓
Research Agent → Web Search Tool
↓
Summarizer Agent → Summarizer Tool
↓
Final Output

yaml
Copy code

### Key Architectural Principles

- Planner does not execute  
- Research agent is the only agent with web access  
- Summarization is delegated to a tool  
- All state transitions are explicit  
- All execution steps are traceable  

---

## 3. Project Folder Structure

src/
├── agents/
│ ├── planner_agent.py
│ └── agents/
│ ├── research_agent.py
│ ├── search_agent.py
│ └── summarizer_agent.py
│
├── graph/
│ ├── state.py
│ ├── state_graph.py
│ ├── research_graph.py
│
├── memory/
│ └── vfs.py
│
├── tools/
│ ├── llm_factory.py
│ ├── web_search.py
│ ├── summarizer_tool.py
│ ├── write_todos.py
│ └── shared_resources.py
│
└── app.py

markdown
Copy code

---

## 4. Core Components

### 4.1 Streamlit Application (`app.py`)

#### Purpose

- Acts as the **UI layer only**
- Sends user input to LangGraph
- Displays final outputs
- Does **not** handle reasoning or tool calls

#### Responsibilities

- Load environment variables  
- Initialize LangGraph  
- Render chat interface  
- Display Virtual File System contents  
- Invoke the graph with a state object  

#### Key Concept

LangGraph expects **state**, not messages:

```python
result = graph.invoke({"query": user_input})
## 4.2 Agent State Definition (graph/state.py)
Purpose
Defines the shared state schema passed between agents.

Typical State Fields
query

todos

research

summary

This ensures:

Predictable execution

Clear data flow

Debuggable failures

4.3 LangGraph Orchestration (graph/state_graph.py)
Purpose
Defines how agents are connected and executed.

Execution Order
powershell
Copy code
planner → research → summarizer → END
Key Properties
Single entry point (planner)

Explicit edges

No hidden branching

Fully traceable DAG

4.4 Planner Agent (agents/planner_agent.py)
Role
Responsible for:

Understanding user intent

Generating a structured TODO list

Deciding what should happen, not doing it

Rules Enforced
Always outputs TODOs

Never performs research

Never calls tools

Never summarizes

Output Example
json
Copy code
{
  "todos": [
    {
      "id": "todo-1",
      "action": "web_search",
      "description": "Research AI in healthcare",
      "depends_on": []
    },
    {
      "id": "todo-2",
      "action": "summarizer",
      "description": "Summarize research findings",
      "depends_on": ["todo-1"]
    }
  ]
}
4.5 Research Agent (agents/agents/research_agent.py)
Role
Responsible for factual data collection.

Capabilities
Receives query from state

Calls the web_search tool at most once

Produces structured research output

Writes results back to state

Restrictions
No file writing

No summarization

No planning

4.6 Web Search Tool (tools/web_search.py)
Purpose
Provides controlled and traceable web access.

Properties
Uses Tavily API

Returns clean textual results

Fully traceable in LangSmith

python
Copy code
@tool
@traceable(name="web_search")
def web_search(query: str) -> str:
    ...
Benefits
No hallucinated browsing

Tool usage is auditable

Exact timing and tokens are visible

4.7 Summarizer Agent (agents/agents/summarizer_agent.py)
Role
Acts as a controller, not an executor.

Responsibilities
Select content from state

Delegate summarization to the tool

Store final summary in state

python
Copy code
state["summary"] = summarizer.invoke(content)
4.8 Summarizer Tool (tools/summarizer_tool.py)
Purpose
Performs the actual summarization.

Why a Tool?
Clear separation of concerns

Independent tracing

Cleaner observability

python
Copy code
@tool
@traceable(name="summarizer")
def summarizer(text: str) -> str:
    ...
LangSmith Trace View
nginx
Copy code
summarizer_agent
 └─ summarizer
     └─ ChatOpenAI
4.9 Virtual File System (memory/vfs.py)
Purpose
Acts as in-memory persistent storage.

Usage
Store intermediate artifacts

Display files in the sidebar

Enable future long-horizon reasoning

Benefits
Deterministic memory

No reliance on implicit LLM recall

Debuggable state inspection

5. LangSmith Tracing
LangSmith provides full execution observability.

What Is Traced
LangGraph root run

Each agent invocation

Each tool call

Each LLM request

Trace Hierarchy
markdown
Copy code
LangGraph
 ├─ planner_agent
 │   └─ ChatOpenAI
 ├─ research_agent
 │   ├─ web_search
 │   └─ ChatOpenAI
 └─ summarizer_agent
     ├─ summarizer
     └─ ChatOpenAI
Why This Matters
Debugging becomes trivial

Latency bottlenecks are visible

Token usage is transparent

Reasoning is auditable

6. Execution Workflow
User submits a query in the UI

Planner generates TODOs

Research agent fetches data

Summarizer agent compresses content

Final output is displayed

Full trace is stored in LangSmith

7. Key Advantages
Deterministic execution

Strict role separation

Tool-governed reasoning

Production-grade observability

Clean UI / logic separation

8. Challenges
Higher architectural complexity

Increased token usage

Multi-step latency

9. Future Enhancements
Conditional branching in LangGraph

Retry and failure recovery nodes

Long-term persistent storage

Multi-agent parallel execution

Evaluation and feedback loops

10. Conclusion
This project demonstrates a modern, production-aligned agent architecture using LangGraph and LangSmith.

By separating planning, research, and summarization into independent agents and tools—and by enforcing explicit state transitions—the system eliminates hidden reasoning and uncontrolled behavior.

The result is a transparent, debuggable, and scalable autonomous research agent suitable for real-world analytical workflows.

markdown
Copy code

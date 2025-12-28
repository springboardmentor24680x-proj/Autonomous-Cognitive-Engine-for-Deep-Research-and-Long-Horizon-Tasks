OB# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks  
**Springboard – Infosys Internship Project**

---

## Overview
The **Autonomous Cognitive Engine** is an LLM-driven multi-agent system designed to perform **deep research and long-horizon tasks** with minimal human intervention.

The system decomposes complex user queries into structured TODOs, delegates execution to specialized sub-agents, persists memory across runs, and produces traceable, well-structured outputs.

## Key Features

-  **Supervisor-driven Task Planning & TODO Enforcement**
-  **Persistent Memory using Virtual File System (VFS)**
-  **Sub-Agent Delegation Architecture**
-  **Research Agent for information gathering**
-  **Summarization Agent for condensed insights**
-  **Tool-based Execution** (file tools implemented, extensible)
-  **LangSmith Tracing for Observability**
-  **LangGraph-based StateGraph orchestration (in progress)**

---

## System Architecture

User  
↓  
Supervisor Agent  
↓  
Persistent Memory (VFS)  
↓  
Sub-Agents  
├── Research Agent  
└── Summarization Agent  
↓  
Tool Execution  
↓  
Final Structured Output

---

## 🛠 Tech Stack

- **Python**  
- **LangChain**  
- **LangGraph**  
- **Groq LLM**  
- **LangSmith** (Tracing & Observability)

---

## Project Structure

```text
Autonomous-Cognitive-Engine-for-Deep-Research/
├── src/graph/state_graph.py        # Supervisor & graph entry point
├── src/app.py                      # Streamlit UI
├── src/graph/research_graph.py     # Research sub-agent graph
├── src/graph/summarizer_graph.py   # Summarization sub-agent graph
├── src/graph/web_search_graph.py   # Web search delegation
├── src/tools/llm_factory.py        # Centralized LLM configuration
├── src/memory/vfs.py               # Persistent Virtual File System
├── src/graph/state.py              # Shared agent state
├── src/tools/shared_resources.py   # Shared tools and utilities
├── venv/                            # Virtual environment (ignored)
├── __pycache__/                     # Python cache (ignored)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
Current Progress
✔ Multi-agent delegation (Supervisor → Sub-agents)
✔ Persistent memory across executions
✔ Research and summarization workflows
✔ Structured task planning and TODO enforcement
✔ LangSmith-traced execution flow

Future Work
Dedicated Planner Agent

Verification / Critic Agent

Advanced LangGraph StateGraph routing

Long-term vector-based memory

Additional tool integrations (calendar, APIs)

Internship Outcome
This project demonstrates:

Autonomous reasoning

Multi-agent coordination

Long-horizon task execution

Observable and debuggable AI systems

Designed and implemented as part of the Infosys Springboard Internship Program.




# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

### A Springboard – Infosys Internship Project

## Overview
The **Autonomous Cognitive Engine** is an LLM-powered system designed to autonomously execute deep research and long-horizon tasks.  
It decomposes complex user queries into structured plans, delegates execution to specialized sub-agents, maintains persistent memory, and produces reliable, traceable outputs with minimal human intervention.

The project emphasizes **agent orchestration, memory management, observability, and research automation**.

---

## Key Features
- Task Planning and TODO Enforcement
- Persistent Memory using Virtual File System (VFS)
- Supervisor–Sub-Agent Architecture
- Research Agent for factual data collection
- Summarization Agent for structured output generation
- Tool-based execution (files, memory, task tracking)
- LangSmith Tracing for agent observability and debugging

---

## Architecture
```
User
↓
Supervisor Agent
↓
Persistent Memory (VFS)
↓
Sub-Agents (Research Agent / Summarization Agent)
↓
Tools (File System, TODO Manager, Tracing)
↓
Final Structured Output

```

---

## Tech Stack
- **Programming Language:** Python
- **LLM Provider:** Groq
- **Frameworks:** LangChain, DeepAgents
- **Observability:** LangSmith Tracing
- **Frontend (Optional):** Streamlit
- **Environment:** Virtualenv

---

## Project Structure
```
Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks/
├── src/ # Core supervisor agent and execution logic
├── subagents/ # Research and summarization agents
├── storage/ # Persistent memory and VFS files
├── utils/ # Helper utilities (TODO, tracing, helpers)
├── app.py # Main application entry point
├── requirements.txt # Project dependencies
├── README.md # Project documentation
├── LICENSE
├── .gitignore
└── venv/ # Virtual environment (ignored)
```
---

## Current Progress
- ✔ Supervisor and sub-agent delegation implemented  
- ✔ Research and summarization agents functional  
- ✔ Persistent memory using VFS  
- ✔ TODO-based task enforcement  
- ✔ Partial LangSmith tracing integration  
- ✔ Streamlit-based execution interface  

---


Future Enhancements

Integration with LangGraph StateGraph

Planner and verification agents

Vector-based long-term memory

Multi-tool reasoning and validation

Improved fault tolerance and recovery

Full LangSmith tracing stabilization
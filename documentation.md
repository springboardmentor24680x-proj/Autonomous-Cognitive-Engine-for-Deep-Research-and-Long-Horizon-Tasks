# Autonomous Cognitive Agent System

## Introduction

This project implements an **Autonomous Cognitive Agent System** designed to perform intelligent, long-horizon tasks through structured planning, reasoning, tool usage, and memory management.

The system is built using **Python**, **LangGraph**, **LangChain**, and **Groq-hosted Large Language Models (LLMs)**, with support for both command-line and Streamlit-based user interfaces.

The core idea is to move beyond single-prompt LLM usage and instead build an **agentic workflow** where tasks are planned, executed step by step, and stored in memory for future reference. The architecture is modular, extensible, and suitable for both research and real-world automation.

---

## Objectives

- **Build an autonomous AI agent** capable of reasoning and execution  
- **Implement structured task planning** using TODO decomposition  
- **Overcome LLM context limitations** through persistent memory  
- **Separate reasoning from execution** using tool abstractions  
- **Enable supervisor–worker coordination**  
- **Provide an interactive user interface**

---

## Technology Stack

### Programming Language
- Python

### Agent & Workflow Frameworks
- **LangGraph** – Stateful agent execution  
- **LangChain** – Tool abstraction and LLM utilities  

### Large Language Model
- **Groq LLM** (`llama-3.1-8b-instant`)

### Utilities
- **python-dotenv** – Environment variable management  
- **LangSmith** – Tracing and observability  

### User Interface
- **Streamlit**

---

## System Architecture Overview

The system follows a **Supervisor–Worker architecture** implemented using LangGraph. Each agent operates on a shared state, enabling controlled execution and persistent context across interactions.

### Architectural Principles

- Explicit planning before execution  
- Clear separation between reasoning and actions  
- Tool-driven interaction with memory  
- Stateful and explainable workflows  

---

## Environment Setup and LLM Initialization

The Groq LLM client is initialized using environment variables stored in a `.env` file.

```python
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")
client = Groq(api_key=API_KEY)
```
---

## Reusable LLM Call Wrapper
```python
def llm_call(messages):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content
```
---
## Task Planning Using TODO Decomposition
User requests are converted into structured TODO steps to ensure deterministic and controlled execution.

```python
from langchain.tools import tool

@tool
def write_todos(request: str):
    """Break a user request into small, clear TODO steps."""
    system = "You are a task planner. Break the request into small, clear TODO steps."
    msg = [
        {"role": "system", "content": system},
        {"role": "user", "content": request}
    ]
    result = llm_call(msg)
    todos = [
        {"task": t.strip().lstrip("0123456789.- ")}
        for t in result.split("\n") if t.strip()
    ]
    return todos or []
```
---
## Supervisor Agent
The Supervisor Agent interprets user intent, generates TODO plans, and manages the overall execution state.

```python
def supervisor_node(state):
    if not state.get("todos"):
        todos = write_todos.invoke(state["user_query"])
        state["todos"] = todos or []
        state["current_step"] = 0
    return state
```
---

## Worker Agent
The Worker Agent executes individual TODO tasks sequentially and stores intermediate results.

```python
def worker_node(state):
    if state["current_step"] >= len(state.get("todos", [])):
        return state

    task = state["todos"][state["current_step"]]["task"]

    messages = [
        {"role": "system", "content": "You are a helpful worker agent."},
        {"role": "user", "content": task}
    ]

    result = llm_call(messages)
    state["todos"][state["current_step"]]["result"] = result
    state["current_step"] += 1
    return state
```
---
## Workflow Orchestration with LangGraph
LangGraph is used to define and control the agent workflow using a state graph.

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(dict)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("worker", worker_node)
workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "worker")
workflow.add_conditional_edges(
    "worker",
    lambda state: END if state["current_step"] >= len(state.get("todos", [])) else "worker",
    {"worker": "worker", END: END}
)

graph = workflow.compile()
```
---
## Persistent Memory – Virtual File System (VFS)
The Virtual File System (VFS) enables agents to store and retrieve information beyond the LLM context window.

```python
from langchain_core.tools import tool

@tool
def write_file(filename: str, content: str, vfs: dict) -> str:
    vfs[filename] = content
    return f"File '{filename}' written successfully."

@tool
def read_file(filename: str, vfs: dict) -> str:
    return vfs.get(filename, "File not found.")

@tool
def list_files(vfs: dict) -> str:
    if not vfs:
        return "No files present."
    return "\n".join(vfs.keys())
```
---
## Streamlit User Interface
The Streamlit UI provides an interactive chat-based interface for the autonomous agent.

```python
import streamlit as st
from agent import graph

st.set_page_config(page_title="AI Agent", layout="centered")
st.title("🧠 Intelligent AI Agent")
```
---
### UI Features
- Real-time chat interaction  
- Persistent session state  
- Clear visualization of agent responses
---
## End-to-End Execution Flow
1. User submits a query  
2. Supervisor agent generates a TODO-based plan  
3. Worker agent executes tasks sequentially  
4. Memory is updated when required  
5. Final response is generated  
6. Output is displayed to the user
---
## Setup and Usage

### Prerequisites
- Python 3.10 or above  
- Valid Groq API key  
- Internet connectivity  

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### Create a .env file in the project root
```env
GROQ_API_KEY=your_api_key_here
```
### Running the Agent (CLI Mode)
```bash
python agent.py
```
### Running the Streamlit Application
```bash
streamlit run app.py
```
---
## Challenges Faced
- Managing long-term context within LLM limitations  
- Inconsistent responses without structured planning  
- State recursion errors in LangGraph workflows  
- Coordinating shared state across multiple agents  
---

## Limitations
- Dependent on external LLM availability and API limits  
- Sequential task execution without parallelism  
- Memory is local and not distributed  
- Limited real-world tool integrations  
---

## Troubleshooting
- **GROQ_API_KEY not found** → Ensure the `.env` file exists and the variable name is correct  
- **GraphRecursionError** → Increase recursion limit during graph invocation  
- **Incomplete or vague responses** → Improve system prompts and add explicit planning constraints  
- **Streamlit UI not updating** → Clear session state and restart the Streamlit server  
---

## Conclusion
This project demonstrates a scalable and explainable autonomous agent architecture that integrates planning, reasoning, persistent memory, and execution.  
The modular design allows easy extension with additional agents, tools, and workflows, making it a strong foundation for advanced AI research and practical automation use cases.

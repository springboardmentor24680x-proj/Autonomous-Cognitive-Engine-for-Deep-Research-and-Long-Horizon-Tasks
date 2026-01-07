# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

## Overview

This project focuses on building an **autonomous AI agent framework** using **LangGraph** that can handle **complex, long-horizon tasks**. The agent is designed to plan tasks, manage memory, and delegate work to sub-agents instead of relying on simple prompt–response interactions.

The goal is to simulate advanced AI agent behavior such as planning, reasoning, memory management, and modular task execution.

---

## Key Features

### Task Planning
- Breaks complex user requests into structured TODO lists
- Enables long-horizon execution with clear intermediate goals

### Memory Management (Virtual File System)
- Uses a virtual file system (VFS) to store intermediate results
- Allows agents to read/write context across multiple steps

### Sub-Agent Delegation
- Main agent can delegate subtasks to specialized sub-agents
- Improves modularity and separation of concerns

### Stateful Workflow
- Built with **LangGraph** to maintain state across execution steps
- Supports branching, retries, and multi-step reasoning

---

## System Workflow

1. **User Input**  
   User provides a complex or multi-step request

2. **Task Planning**  
   Agent decomposes the request into a structured TODO list

3. **Task Execution**
   - Uses tools (LLMs, search, code execution)
   - Stores intermediate data in the virtual file system
   - Delegates tasks to sub-agents when required

4. **Result Aggregation**  
   Agent gathers outputs from all steps and sub-agents

5. **Final Output**  
   Consolidated and coherent final response is generated

---
## Architecture Diagram
```python
 Input(User prompt / request)
  ↓
Supervisor Agent(Main Cognitive Agent)
  ↓
Search(Tavily API / Search Tools)
  ↓
Reasoning(LangGraph execution)
  ↓
Summarization(Final synthesis step)
  ↓
Memory(VFS)
  ↓
Output(Final agent response)
```

## Tech Stack

* Python 3.11+
* LangGraph
* LangChain
* LLM API (Claude / Groq)
* LangSmith (Tracing & Debugging)
* Tavily API (Search)

---

## Use Case Example

* Autonomous research report generation
* Multi-step code analysis or refactoring
* Long-horizon reasoning tasks
* Knowledge synthesis from multiple sources

---

## Running the Project

This guide explains how to run the **Autonomous Cognitive Engine** locally using Streamlit.

---

### 1. Clone the Repository

```python
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
### 2. Create a Virtual Environment (Recommended)
```python
python -m venv venv
```
### 3. Activate the Virtual Environment
* On Windows:

```python
venv\Scripts\activate
```
* On macOS/Linux:

```python
source venv/bin/activate
```
### 4. Install Dependencies
```python
pip install -r requirements.txt
```

Make sure the requirements.txt includes all necessary packages such as streamlit, langgraph, langchain-groq, etc.

### 5. Run the Streamlit App
```python
streamlit run src/app.py
```

### 6. Open the App in Your Browser

```python
Streamlit will automatically open your default web browser at:

http://localhost:8501
```

You can now interact with the Autonomous Cognitive Agent.

### 7. Clear Chat History

Use the sidebar “Clear Chat” button to reset the conversation memory when needed.

## Project Status

Work in progress — milestone-based development.

---

## License

This project is intended for educational and research purposes only.

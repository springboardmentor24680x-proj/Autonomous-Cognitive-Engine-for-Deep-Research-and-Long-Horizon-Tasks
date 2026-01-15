# Autonomous Cognitive Engine

The **Autonomous Cognitive Engine** is an AI system designed to perform **deep research** and **long-horizon tasks** using a structured, multi-agent workflow. Unlike traditional chat-based systems, this project focuses on **explicit reasoning, controlled tool usage, persistent memory, and testable execution**.

It uses a **graph-based agent architecture** where different agents handle tasks like web search, research, summarization, and task management.

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Objectives](#objectives)  
3. [Technologies Used](#technologies-used)  
4. [Project Architecture](#project-architecture)  
5. [Folder Structure](#folder-structure)  
6. [Module Description](#module-description)  
7. [Testing Strategy](#testing-strategy)  
8. [Setup Instructions](#setup-instructions)  
9. [Running the Application](#running-the-application)  
10. [Current Status](#current-status)  
11. [Challenges Faced](#challenges-faced)  
12. [Future Enhancements](#future-enhancements)  
13. [Conclusion](#conclusion)  

---

## Project Overview
The system uses a **Supervisor–Sub Agent architecture**, implemented via LangGraph. Agents have specialized roles: **research, search, summarization, and task management**, while the graph controls execution and routing.

---

## Objectives
- Modular AI system with clear separation of responsibilities  
- Long-horizon reasoning using persistent memory  
- Controlled tool usage to prevent hallucinations  
- Testable and verifiable execution  
- Simple user interface for interaction  

---

## Technologies Used
- Python  
- LangGraph  
- LangChain  
- OpenRouter API (LLM provider)  
- Streamlit (UI)  
- Pytest (testing)  
- Virtual File System (VFS) for memory  

---

## Project Architecture
- **Agents**: Specialized logic for research, search, summarization  
- **Graphs**: Control execution flow and routing  
- **State Management**: Shared `AgentState` across nodes  
- **Memory (VFS)**: Persistent storage  
- **Tools**: LLM access, web search, todo writing  
- **Tests**: Validate each module independently  

---

## Folder Structure
```
src/
├── agents/
│ ├── code_agent.py
│ ├── research_agent.py
│ ├── search_agent.py
│ └── summarizer_agent.py
├── graph/
│ ├── state.py
│ ├── state_graph.py
│ ├── research_graph.py
│ ├── web_search_graph.py
│ └── summarizer_graph.py
├── memory/
│ └── vfs.py
├── tools/
│ ├── llm_factory.py
│ ├── shared_resources.py
│ └── write_todos.py
├── app.py

tests/
├── test_routing.py
├── test_summarizer.py
├── test_todo.py
├── test_vfs.py
└── test_web_search.py

markdown
Copy code

---

## Module Description

### Supervisor & Routing (Graph)
- Controls the flow between agents  
- Decides if input requires search, summarization, or direct response  
- Implemented using LangGraph state transitions  

### Research Agent
- Performs factual research  
- Uses controlled web search  
- Returns structured content to the graph  

### Web Search Module
- Executes external searches  
- Restricted to research-related tasks  
- Returns results to the graph  

### Summarizer Agent
- Converts large research outputs into concise summaries  
- Produces readable, structured content  

### Virtual File System (VFS)
- Persistent memory storage  
- Supports `read`, `write`, and `list` operations  
- Stores files like `search.txt`, `summary.txt`, and `todos.txt`  

### Todo Generator
- Extracts action items from user input or summaries  
- Stores tasks in `todos.txt` via VFS  

---

## Testing Strategy
Testing is done using **pytest** to ensure correctness and reliability.

**Test Coverage**:  
- Routing logic  
- Summarizer output  
- Web search execution  
- VFS read/write operations  
- Todo generation  

All tests are isolated and independently verifiable.

---

## Setup Instructions

### **1. Clone Repository**
```bash
git clone <repository-url>
cd Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
2. Create Virtual Environment
bash
Copy code
python -m venv venv
# Activate environment:
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
4. Set Environment Variables
Create a .env file in the project root with the following content:

ini
Copy code
OPENROUTER_API_KEY=your_api_key_here
5. Run the Application
bash
Copy code
streamlit run src/app.py
6. Current Status
Core agent workflow implemented

Persistent memory via VFS working

All major modules tested

Streamlit UI integrated

7. Challenges Faced
Managing shared state across agents

Preventing incorrect routing

Handling long outputs safely

Designing testable agent logic

8. Future Enhancements
Multi-modal inputs (PDFs, images)

Advanced planning workflows

Improved visualization support

Agent self-evaluation and feedback loops
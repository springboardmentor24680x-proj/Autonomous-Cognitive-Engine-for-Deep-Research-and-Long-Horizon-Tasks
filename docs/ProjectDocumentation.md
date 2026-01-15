# Autonomous Cognitive Engine – Project Documentation

## 1. Project Overview
The Autonomous Cognitive Engine is an AI-based system designed to perform deep research and long-horizon tasks using a structured, multi-agent workflow.  
Unlike traditional chat-based systems, this project focuses on **explicit reasoning, controlled tool usage, persistent memory, and testable execution**.

The system uses a **graph-based agent architecture** where different agents handle specific responsibilities such as web search, research, summarization, and task management.

---

## 2. Objectives
- Build a modular AI system with clear separation of responsibilities
- Enable long-horizon reasoning using persistent memory
- Prevent uncontrolled tool usage and hallucinations
- Ensure correctness using automated tests
- Provide a simple UI for user interaction

---

## 3. Technologies Used
- **Python**
- **LangGraph**
- **LangChain**
- **OpenRouter API (LLM provider)**
- **Streamlit** (UI)
- **Pytest** (testing)
- **Virtual File System (VFS)** for memory

---

## 4. Project Architecture
The project follows a **Supervisor–Sub Agent architecture** implemented using LangGraph.

### Key Components
- **Agents**: Specialized logic for research, search, summarization
- **Graphs**: Control execution flow and routing
- **State Management**: Shared `AgentState` passed across nodes
- **Memory (VFS)**: File-based persistent storage
- **Tools**: LLM access, web search, todo writing
- **Tests**: Validate each module independently

---

## 5. Folder Structure
src/
│
├── agents/
│ ├── code_agent.py
│ ├── research_agent.py
│ ├── search_agent.py
│ └── summarizer_agent.py
│
├── graph/
│ ├── state.py
│ ├── state_graph.py
│ ├── research_graph.py
│ ├── web_search_graph.py
│ └── summarizer_graph.py
│
├── memory/
│ └── vfs.py
│
├── tools/
│ ├── llm_factory.py
│ ├── shared_resources.py
│ └── write_todos.py
│
├── app.py
│
tests/
│
├── test_routing.py
├── test_summarizer.py
├── test_todo.py
├── test_vfs.py
└── test_web_search.py


---

## 6. Module Description

### 6.1 Supervisor & Routing (Graph)
- Controls the flow between agents
- Decides whether input needs search, summarization, or direct response
- Implemented using LangGraph state transitions

---

### 6.2 Research Agent
- Performs factual research
- Uses controlled web search
- Returns structured content to the graph

---

### 6.3 Web Search Module
- Executes external searches
- Restricted to research-related tasks
- Results are passed back through the graph

---

### 6.4 Summarizer Agent
- Converts large research outputs into concise summaries
- Produces readable and structured content

---

### 6.5 Virtual File System (VFS)
- Acts as persistent memory
- Stores files like:
  - `search.txt`
  - `summary.txt`
  - `todos.txt`
- Supports write, read, and list operations

---

### 6.6 Todo Generator
- Extracts action items from user input or summaries
- Stores tasks in `todos.txt` using VFS

---

## 7. Testing Strategy
Testing is done using **pytest** to ensure correctness and reliability.

### Test Coverage
- Routing logic
- Summarizer output
- Web search execution
- VFS read/write operations
- Todo generation

All tests are isolated and independently verifiable.

---

## 8. Setup Instructions

### Clone Repository
```bash
git clone <repository-url>
cd Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks

Create Virtual Environment
python -m venv venv
source venv/Scripts/activate

Install Dependencies
pip install -r requirements.txt

Environment Variables

Create a .env file:

OPENROUTER_API_KEY=your_api_key_here

9. Running the Application
streamlit run src/app.py

10. Current Status

Core agent workflow implemented

Persistent memory via VFS working

All major modules tested

Streamlit UI integrated

11. Challenges Faced

Managing shared state across agents

Preventing incorrect routing

Handling long outputs safely

Designing testable agent logic

12. Future Enhancements

Multi-modal inputs (PDFs, images)

Advanced planning workflows

Improved visualization support

Agent self-evaluation and feedback loops

13. Conclusion

This project demonstrates a structured approach to building autonomous AI systems using agent graphs, persistent memory, and controlled tool usage.
It avoids implicit reasoning and focuses on clarity, correctness, and maintainability, making it suitable for real-world research and planning tasks.
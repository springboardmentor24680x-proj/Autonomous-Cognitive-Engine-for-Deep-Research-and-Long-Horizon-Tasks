 A Springboard – Infosys Internship Project
 Overview
 The Autonomous Cognitive Engine is an AI system designed to perform deep research and long-horizon tasks autonomously.  
It can:  
- Break complex tasks into smaller subtasks  
- Delegate work to specialized sub-agents  
- Store results and instructions in a Virtual File System (VFS)  
- Produce structured outputs with minimal human input
Key Features
- Task Planning & TODO Management  
- Persistent Memory using VFS  
- Sub-Agent Delegation to:
  - Research Agent  
  - Summarization Agent  
  - Code Agent  
  - Search Agent  
- Tool Integration for file operations  
- Chat Interface via CLI or Streamlit UI
Architecture
User → Supervisor Agent → Memory (VFS) → Sub-Agents → Tools → Output
Tech Stack
- Python  
- LangChain  
- LangGraph  
- Streamlit  
- OpenRouter API / ChatOpenAI
Project Structure
Autonomous-Cognitive-Engine/
│
├── main.py # Supervisor agent & StateGraph
├── ui.py # Streamlit interface
├── vfs_tools.py # Virtual File System
├── agents/ # Sub-agent modules
├── storage/ # Persistent memory
├── docs/ # Notes and documentation
├── README.md
└── .gitignore
Current Status
- Sub-agent delegation working  
- Persistent memory implemented  
- TODO management working  
- CLI and Streamlit UI functional 
Future work
- Add Planner & Verification Agents  
- Integrate Vector Memory for semantic retrieval  
- Enhance task automation and observability 

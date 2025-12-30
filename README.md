Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks
1. Overview
The Autonomous Cognitive Engine is an AI system designed to assist researchers in automating complex tasks, managing information, and generating insights over extended workflows. It integrates multiple specialized agents to handle summarization, search, memory management, and task execution, enabling efficient exploration and decision-making across large datasets and documents.
2. Approach
The system uses a modular architecture with the following approach:
Agent-based Architecture: Different agents are responsible for specific tasks such as information retrieval, summarization, and task management.
State Management: A state graph tracks execution and memory of tasks to ensure consistency across operations.
Virtual File System (VFS): Structured reading, writing, and editing of files, enabling smooth data handling without cluttering the workspace.
Pipeline-driven Processing: Milestone workflows are implemented in structured pipelines to allow sequential task execution, experimentation, and evaluation.
3. Key Features
Supervisory Agent: Orchestrates multiple sub-agents and ensures task prioritization and execution order.
Summarization Agent: Automatically summarizes documents or notes to generate concise insights.
Search Agent: Performs intelligent searches across local and external resources.
Memory Management: Maintains state and historical context for long-horizon tasks.
Task Management: Tracks milestones and subtasks through a to-do list agent.
Extensible Tools: Supports VFS tools for file read/write/edit and other utilities for custom extensions.
4. Tech Stack
Programming Language: Python 3.10+
Libraries & Frameworks:
LangChain & LangGraph for agent orchestration
Groq for AI model integration
Dotenv for environment variable management
Standard Python libraries (os, datetime)
Git/GitHub: Branch-based development workflow for team collaboration
5. Setup
Clone the repository:git clone https://github.com/springboardmentor24680x-proj/Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks.git
cd Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
git checkout intern-divyadharshini
Create virtual environment:python -m venv .venv
Activate environment:
Windows:.venv\Scripts\activate
Install dependencies:pip install -r requirements.txt
Configure environment variables:
Create a .env file with required API keys and paths.
6. Usage
Run Agents:
Copy code
Bash
python agents/agent.py
Add Tasks:
Tasks can be added via the todolist.py agent.
File Operations:
Use VFS tools (read_file.py, write_file.py) for reading, writing, and editing project files.
7. Troubleshooting
Large Files: Avoid pushing large audio or dataset files to GitHub; use external storage if needed.
Branch Workflow: Always work on your assigned branch (intern-yourname) and do not push to main.
Dependencies: Ensure all libraries in requirements.txt are installed in the virtual environment.
Debugging: Check console logs for errors and verify that .env variables are correctly configured.
Performance: Some AI tasks may require high memory or processing power; consider limiting batch sizes during experiments.

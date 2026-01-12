# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

## 1. Overview
The Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks is an AI-based system developed to support complex research workflows that require sustained reasoning over extended periods of time. The system is designed to automate research-oriented tasks such as information retrieval, summarization, task tracking, and structured data handling.

By combining multiple specialized agents under a unified control mechanism, the project aims to improve productivity, reduce manual effort, and maintain contextual continuity across long-running tasks.

---

## 2. Approach
The project follows a modular and agent-driven architecture. Each agent is designed with a specific responsibility and operates under the coordination of a supervisory mechanism. This ensures that tasks are executed in a controlled, sequential, and context-aware manner.

The approach focuses on maintaining clear boundaries between components while allowing seamless interaction through shared state and tools. A state-driven execution flow ensures that progress and context are preserved across multiple steps of a task.

---

## 3. Key Features
- Modular multi-agent architecture
- Supervisory agent for task coordination
- Summarization agent for content condensation
- Search agent for information retrieval
- Task management using a structured to-do system
- Virtual File System (VFS) tools for controlled file operations
- Clean and extensible project structure

---

## 4. Tech Stack
- Programming Language: Python 3.10+
- Agent Frameworks:
  - LangChain
  - LangGraph
- Model Integration:
  - Groq API
- Environment Configuration:
  - python-dotenv
- Version Control:
  - Git and GitHub (branch-based workflow)

---

## 5. Setup (Windows Only)

### Step 1: Clone the Repository
```bash
git clone https://github.com/springboardmentor24680x-proj/Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks.git
cd Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
git checkout intern-Divyadharshini
```
### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```
### Step 3: Activate the Virtual Environment

```bash
.venv\Scripts\activate
```
### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```
### Step 5: Configure Environment Variables

Create a `.env` file in the root directory and add the required API keys and configuration values.



---

## 6. Usage
1. Execute the main agent script to start the system:  
   python agents/agent.py  
2. Add and manage tasks using the task management module.  
3. Perform file operations such as reading, writing, and editing using VFS tools.  
4. Extend the system by adding new agents or tools following the existing modular structure.

---

## 7. Troubleshooting
1. Large files or datasets should not be pushed to GitHub.
2. Always ensure work is done on the assigned branch and not on the main branch.
3. Missing or incorrect environment variables may cause execution failures.
4. Dependency issues can be resolved by reinstalling packages from requirements.txt.
5. Performance may vary based on system resources and API usage limits.
6. Review terminal logs and error messages for debugging issues.
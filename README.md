# Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
An advanced AI-powered engine designed to autonomously conduct deep research, handle complex workflows, and execute long-horizon tasks with minimal supervision. Powered by LangGraph, LangSmith, Groq, and Tavily APIs, it can plan tasks, delegate subtasks, and summarize results effectively.

# Features:

-Autonomous task management and delegation

-Multi-step reasoning for long-horizon tasks

-Web search integration using Tavily API

-Text summarization using Groq LLM

-In-memory virtual file system (VFS) for persistent state

-Streamlit-based web UI for interactive chats

-CLI interface for quick experimentation



## Architecture

```text

User Input
    │
    ▼
+---------------------+
|    Task Manager     |  <- Writes TODOs to VFS
+---------------------+
    │
    ▼
+---------------------+
|  Delegation Engine  |  <- Web search + summarizer
+---------------------+
    │
    ▼
+---------------------+
|   Assistant LLM     |  <- Generates final responses
+---------------------+
    │
    ▼
Output (CLI / Streamlit)


Components:

-Task Manager (write_todos) – Maintains an internal TODO list for multi-step instructions

-Delegation Engine (delegate_task) – Performs web searches and summarizes results

-Assistant (assistant_response) – Combines delegated results and user input to generate final replies

-VFS (src/vfs.py) – In-memory file system for storing tasks and outputs

-Web & Summarizer Agents – Sub-agents for web search and summarization

-Streamlit UI (streamlit_app.py) – Interactive web interface with multi-threaded chat support


1.Create a virtual environment and activate:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

2.Install dependencies:
using pip install <package name>

3.Set environment variables in a .env file

Usage:

CLI:
-python agent.py

Type your queries directly.

Type exit to quit.

The agent maintains an internal TODO list and delegates web search/summarization as needed.


Streamlit Web UI:

-streamlit run streamlit_app.py

Open the URL provided by Streamlit in your browser.

Start new chats, switch threads, and interact with the agent in real-time.
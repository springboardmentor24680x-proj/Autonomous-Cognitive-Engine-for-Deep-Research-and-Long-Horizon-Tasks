# Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
> A powerful, stateful, fully autonomous AI agent built with LangGraph, FastAPI, and Google Gemini.

## 🚀 Overview

This project implements a **fully autonomous cognitive agent** that can understand natural language, reason step-by-step, plan actions, and execute multiple tools — all while maintaining memory and context across conversations.

It acts as your personal AI assistant for productivity, planning, research, and organization.

Built using modern agent orchestration patterns with **LangGraph** and powered by **Google Gemini 1.5 Flash**.

Perfect for:
- Personal productivity
- Research assistance
- Demonstrating advanced AI agent architectures
- Learning how autonomous agents work under the hood

## ✨ Features

- **Natural Language Control** — Just talk to it like a real assistant
- **Task Management** — Create, update, complete, and delete tasks
- **Calendar Integration** — Schedule events with smart date/time parsing ("tomorrow", "next Monday", etc.)
- **Virtual File System** — Save notes, export task lists, read saved files
- **Persistent Memory** — Session-based state preserved across page reloads
- **Rich Narration** — Detailed, friendly explanations of every action taken
- **Professional UI** — Clean sidebar showing tasks, files, events, and live stats

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Agent Framework**: LangGraph (by LangChain)
- **LLM**: Google Gemini 1.5 Flash (`gemini-1.5-flash-002`)
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript
- **State Management**: In-memory sessions 


## 📦 Project Structure

```
autonomous-cognitive-agent/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI server, endpoints, and session handling
│       ├── agent.py             # LangGraph workflow, reasoning node, and agent logic
│       ├── tools.py             # All tool implementations (todos, calendar, files, etc.)
│       ├── utils.py             # State management, prompts, Gemini client, and helpers
│      
├── frontend/
│   ├── index.html               # Main chat interface and UI
│   ├── script.js                # Frontend JavaScript logic (chat, state sync, UI updates)
│   └── styles.css               # Custom styling for the frontend
├── .env                         # Environment variables (e.g., GEMINI_API_KEY)
├── requirements.txt             # Python dependencies

```

## ⚙️ Setup & Installation
1. Clone the repository
Bashgit clone https://github.com/yourusername/autonomous-cognitive-agent.git
cd autonomous-cognitive-agent

2. Create virtual environment
Bashpython -m venv venv
venv\Scripts\activate       # Windows

3. Install dependencies
Bashpip install -r requirements.txt

4. Get your Gemini API Key

Go to: https://aistudio.google.com/app/apikey
Create a new API key
Add it to .env file:

5. Run the backend server
Bashcd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

6. Open the frontend
Open frontend/index.html in your browser
(or serve it with any static server)

## 🎯 Usage Examples
Try saying:

"Plan a trip to Goa next week"
"Schedule a team meeting tomorrow at 3 PM with Alex and Sara"
"Create tasks: buy groceries, call mom, finish report"
"Save my notes on machine learning"
"Export all tasks to a file"
"Show me all my events"

The agent will reason, use tools, and narrate exactly what it did!

# Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
A powerful, stateful AI agent built with LangGraph, FastAPI, and Google Gemini
🚀 Overview
This is a fully autonomous cognitive agent capable of:

Understanding natural language requests
Planning and executing multiple tools autonomously
Managing tasks (todos)
Scheduling calendar events
Saving and reading files in a virtual filesystem
Maintaining long-term memory and context across conversations
Providing rich, narrated feedback after every action

Built using modern AI orchestration patterns with LangGraph for agent workflow control and Google Gemini 1.5 Flash as the reasoning engine.
Perfect for personal productivity, research assistance, or demonstrating advanced agent architectures.
✨ Features

Natural Language Control – Just talk to it like a human
Task Management – Create, update, complete, delete tasks
Calendar Integration – Schedule meetings with date/time parsing (including "tomorrow", "next Monday")
Virtual File System – Save notes, export tasks, read files
Persistent Sessions – Memory preserved across page reloads (via session ID)
Rich Narration – Detailed, friendly responses explaining what was done
Professional UI – Clean sidebar with tasks, files, events, and stats

🛠️ Tech Stack

Backend: FastAPI + Python
Agent Framework: LangGraph (by LangChain)
LLM: Google Gemini 1.5 Flash (gemini-1.5-flash-002)
Frontend: HTML + Tailwind CSS + Vanilla JS
State Management: In-memory sessions (easy to swap with Redis)

📦 Project Structure
text.
├── backend/
│   └── app/
│       ├── main.py          # FastAPI server & endpoints
│       ├── agent.py         # LangGraph workflow & reasoning
│       ├── tools.py         # All tool implementations
│       ├── utils.py         # State, prompts, Gemini client
│       └── styles.css       # Optional custom styles
├── frontend/
│   ├── index.html           # Main UI
│   ├── script.js            # Frontend logic
│   └── styles.css           # Custom styling
├── .env                     # Environment variables
└── requirements.txt
⚙️ Setup & Installation
1. Clone the repository
Bashgit clone https://github.com/yourusername/autonomous-cognitive-agent.git
cd autonomous-cognitive-agent
2. Create virtual environment
Bashpython -m venv venv
source venv/bin/activate    # Linux/Mac
# or
venv\Scripts\activate       # Windows
3. Install dependencies
Bashpip install -r requirements.txt
4. Get your Gemini API Key

Go to: https://aistudio.google.com/app/apikey
Create a new API key
Add it to .env file:

envGEMINI_API_KEY=your_api_key_here
5. Run the backend server
Bashcd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
6. Open the frontend
Open frontend/index.html in your browser
(or serve it with any static server)
🎯 Usage Examples
Try saying:

"Plan a trip to Goa next week"
"Schedule a team meeting tomorrow at 3 PM with Alex and Sara"
"Create tasks: buy groceries, call mom, finish report"
"Save my notes on machine learning"
"Export all tasks to a file"
"Show me all my events"

The agent will reason, use tools, and narrate exactly what it did!

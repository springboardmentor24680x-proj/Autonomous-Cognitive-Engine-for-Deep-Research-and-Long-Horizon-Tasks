# Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks

**A Springboard – Infosys Internship Project**

---

## Overview

The **Autonomous Cognitive Engine** is an LLM-driven system designed to autonomously perform deep research and long-horizon tasks. It decomposes complex user queries into structured actions, delegates work to specialized sub-agents, persists memory across sessions, and produces verified, structured outputs with minimal human intervention.

---

## Key Features

* Task planning with strict TODO enforcement
* Persistent memory via a Virtual File System (VFS)
* Sub-agent delegation architecture
* Dedicated Research Agent
* Dedicated Summarization Agent
* Tool-based execution (files, calendar, web, visualization)
* LangSmith tracing for observability and debugging

---

## Architecture

```
User
  ↓
Supervisor Agent
  ↓
Virtual File System (Persistent Memory)
  ↓
Sub-Agents (Research / Summarization)
  ↓
Tools (Web / Files / Calendar / Visualization)
  ↓
Verified Structured Output
```

---

## Core Components

### Supervisor Agent

* Central orchestrator of the system
* Cannot perform research or summarization directly
* Enforces **one tool call per turn**
* Verifies sub-agent outputs before task completion

### Virtual File System (VFS)

* Acts as persistent external memory
* Grounds outputs to prevent hallucination
* Enables long-horizon reasoning
* Supports read, write, edit, delete, and list operations

### Research Sub-Agent

* Dedicated factual research agent
* Restricted to web search tools only
* Stores structured research outputs in VFS

### Summarization Sub-Agent

* Condenses large research outputs
* Used for executive summaries and synthesis
* Supervisor is forbidden from summarizing inline

### Visualization Tool (Charts & Graphs)

Supports generation of:

* Bar charts
* Pie charts
* Line charts
* Scatter plots

---

## Visualization Design Principles

* Visualization is strictly tool-gated
* Data must exist before chart creation
* Charts read only from validated data blocks
* Prevents invalid chart-data combinations

### Required Data Format

```
DATA FOR GRAPHING
Online Sales: 40
Wholesale Sales: 35
Subscriptions: 25
END DATA FOR GRAPHING
```

All generated charts are saved back into the Virtual File System.

---

## Execution Flow

1. User submits a complex request
2. Supervisor analyzes intent
3. Tasks are delegated to tools or sub-agents
4. Sub-agents perform isolated work
5. Outputs are stored in the VFS
6. Supervisor verifies results
7. Final response is returned

---

## Observability & Debugging

* Integrated LangSmith tracing
* Full visibility into:

  * Tool calls
  * Sub-agent execution
  * Decision flow

Enables efficient debugging and performance analysis.

---

## Safety & Constraints

* Supervisor cannot perform research or summarization
* Only one tool call allowed per turn
* All file operations require verification
* No assumptions about file existence
* Visualization allowed only from validated data blocks
* Any constraint violation is treated as a system failure

---

## Tech Stack

* Python
* LangChain
* DeepAgents
* Groq LLM
* Matplotlib (Visualization)
* LangSmith (Tracing)

---

## Project Structure

```
Autonomous-Cognitive-Engine-for-Deep-Research/
├── src/                 # Core agent logic & execution
├── subagents/           # Research & summarization sub-agents
├── storage/             # Persistent memory / vector store
├── venv/                # Virtual environment (ignored)
├── __pycache__/         # Python cache (ignored)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Setup (Project Initialization)

### 1. Clone the Repository

```
git clone https://github.com/your-username/Autonomous-Cognitive-Engine-for-Deep-Research.git
cd Autonomous-Cognitive-Engine-for-Deep-Research
```

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Usage

### Start the Agent

```
python src/main/app.py
```

---

## Example Commands

* Perform market research
* Create long-term strategic plans
* Generate executive summaries
* Schedule strategy reviews
* Create visual charts from stored data

---

## Sample Use Cases

* Market and competitor research
* Long-horizon business planning
* Executive summary generation
* Strategic roadmap creation
* Data visualization for decision-making

---

## Current Progress

### Research & Summarization Delegation
The system successfully delegates factual research and content condensation to specialized sub-agents. All research tasks are handled by a dedicated research sub-agent, while summarization is performed by a separate summarization sub-agent, ensuring modularity and clear separation of responsibilities.

### Persistent Memory via Virtual File System (VFS)
A virtual file system is implemented to store and retrieve intermediate and final outputs such as research notes, summaries, visualizations, and TODO lists. This enables stateful, long-horizon task execution across multiple steps without relying on repeated model context.

### Observable Sub-Agent Execution
All agent and sub-agent interactions are observable through tracing and UI state inspection. Tool calls, delegated sub-agent executions, file system updates, and calendar operations are transparently visible, enabling easier debugging and performance analysis.

---

## Future Enhancements

* LangGraph StateGraph integration
* Planner, Verifier, and Critic agents
* Vector database-backed memory
* Role-based access control
* FastAPI deployment
* Advanced Planning
* Dynamic Agent Scaling
* Multi-Modal Cognition

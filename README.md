# Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks
Springboard Internship Project – Infosys
# Overview

The Autonomous Cognitive Engine (ACE) is an LLM-driven system designed to autonomously perform deep research and long-horizon tasks. It breaks complex user goals into actionable plans, delegates work to specialized sub-agents, maintains persistent memory, and produces structured outputs with minimal human intervention.

Key Features

1.Task Planning & TODO Enforcement – Structured task decomposition and execution tracking

2. Persistent Memory (VFS) – Long-term storage of research artifacts and context

3. Sub-Agent Delegation

4. Research Agent

5. Summarization Agent

Tool-Based Execution – File system and extensible tool support

Observability – LangSmith tracing for agent execution transparency

# Architecture:
User → Supervisor Agent → Memory (VFS)
                     ↓
           Sub-Agents (Research / Summary)
                     ↓
                   Tools
                     ↓
                Final Output


# Tech Stack:

Python

LangChain & DeepAgents

Groq LLM

LangSmith (Tracing)

# Project Structure:
Autonomous-Cognitive-Engine-for-Deep-Research/

├── src/ # Core agent logic
├── subagents/    # Research & summary agents
├── storage/      # Persistent memory
├── README.md
└── requirements.txt

# Current Progress:

✅ Research & summarization delegation

✅ Persistent memory

✅ Strict TODO management

✅ Observable sub-agent execution

# Future Work:

LangGraph StateGraph

Planner & verification agents

Vector-based semantic memory

# License:

MIT License

# Autonomous-Cognitive-Engine-for-Deep-Research-and-Long-Horizon-Tasks

A Springboard – Infosys Internship Project

Overview

The Autonomous Cognitive Engine is an LLM-driven system designed to perform deep research and long-horizon tasks autonomously. It breaks complex queries into actions, delegates work to sub-agents, stores memory persistently, and produces structured outputs with minimal human input.

key Features

    * Task Planning & TODO Enforcement

    * Persistent Memory using Virtual File System (VFS)

    * Sub-Agent Delegation

    * Research Agent

    * Summarization Agent

    * Tool-based Execution (files, calendar)

    * LangSmith Tracing for observability

Architecture

User → Supervisor Agent
        ↓
   Memory (VFS)
        ↓
 Sub-Agents (Research / Summary)
        ↓
   Tools → Final Output

Tech Stack

    * Python

    * LangChain & DeepAgents

    * Groq LLM

LangSmith (Tracing)

Project Structure

Autonomous-Cognitive-Engine-for-Deep-Research/
├── src/                 # Core agent logic & execution
├── subagents/           # Research & summarization sub-agents
├── storage/             # Persistent memory / vector store
├── venv/                # Virtual environment (ignored)
├── __pychche__/         # Python cache (ignored)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt



    ✔ Research & summarization delegation
    ✔ Persistent memory
    ✔ Strict TODO management
    ✔ Observable sub-agent execution

Future Work

    * LangGraph StateGraph

    * Planner & verification agents

    * Vector memory
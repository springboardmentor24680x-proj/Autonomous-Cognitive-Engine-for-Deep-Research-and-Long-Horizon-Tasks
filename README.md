Autonomous Cognitive Engine for Deep Research and Long-Horizon Tasks
Project Overview

The Autonomous Cognitive Engine is a stateful, Large Language Model (LLM)–driven system designed to autonomously handle complex, long-horizon tasks such as deep research, multi-step reasoning, structured planning, and problem solving with minimal human intervention.

Unlike traditional chat-based assistants that operate in single-step interactions, this system is designed to plan, remember, reason, and act over extended workflows. It leverages structured task planning, persistent memory, and multi-agent collaboration to maintain continuity and focus across multiple execution steps.

The system functions as a supervisor-driven cognitive agent capable of:

Understanding complex user requests

Decomposing high-level goals into actionable sub-tasks

Maintaining memory across multiple steps using an external store

Using tools and external resources effectively

Delegating work to specialized sub-agents

Producing coherent final outputs after long execution cycles

This project focuses on building a core cognitive architecture using LangGraph, LangChain, and Large Language Models (LLMs), following modern agentic AI design patterns.

System Capabilities

Structured Task Planning using dynamic TODO lists

Persistent Memory through a custom Virtual File System (VFS)

Stateful Execution with LangGraph-based workflows

Multi-Agent Delegation, including:

Summarization Agent

Code Generation Agent

Web Search Agent

Event Scheduling using a built-in calendar system

Interactive Web UI using Streamlit

Observability & Tracing with LangSmith

Automated Testing using Pytest

Tech Stack
Core Technologies

Python 3.10+

LangGraph – Stateful agent orchestration

LangChain – LLM integration and tool abstractions

Groq API – High-performance LLM inference backend

Tools & Utilities

Custom Virtual File System (VFS) for persistent memory

File operation tools (read, write, edit, delete)

Calendar & TODO planning tools

LangSmith – Tracing, debugging, and observability (optional)

Streamlit – Web-based user interface

python-dotenv – Environment variable management

Pytest – Automated testing framework

User Interface

The system includes a Streamlit-based chat interface that allows users to interact with the agent conversationally. The UI provides:

Guided instructions for using TODOs, Calendar, and VFS commands

A chat panel for natural language interaction

A sidebar to view stored files, TODO lists, calendar events, and clear chat history

This interface ensures transparency by allowing users to inspect the agent’s internal memory and planning state while executing long-horizon tasks.

Current Project Status

The following components have been successfully implemented and tested:

 Task planning and decomposition using TODO lists

 External memory management via Virtual File System

 Stateful execution using LangGraph

 Sub-agent delegation:

Summarization Agent

Code Agent

Web Search Agent

 Streamlit-based user interface

 Automated testing with Pytest (15/15 tests passed)



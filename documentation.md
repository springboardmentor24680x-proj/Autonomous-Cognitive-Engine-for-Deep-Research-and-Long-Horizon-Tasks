\# Autonomous Cognitive Agent System



\## Introduction



This project implements an \*\*Autonomous Cognitive Agent System\*\* designed to perform intelligent, long-horizon tasks through structured planning, reasoning, tool usage, and memory management.



The system is built using \*\*Python\*\*, \*\*LangGraph\*\*, \*\*LangChain\*\*, and \*\*Groq-hosted Large Language Models (LLMs)\*\*, with support for both command-line and Streamlit-based user interfaces.



The core idea is to move beyond single-prompt LLM usage and instead build an \*\*agentic workflow\*\* where tasks are planned, executed step by step, and stored in memory for future reference. The architecture is modular, extensible, and suitable for both research and real-world automation.



---



\## Objectives



\- \*\*Build an autonomous AI agent\*\* capable of reasoning and execution  

\- \*\*Implement structured task planning\*\* using TODO decomposition  

\- \*\*Overcome LLM context limitations\*\* through persistent memory  

\- \*\*Separate reasoning from execution\*\* using tool abstractions  

\- \*\*Enable supervisor–worker coordination\*\*  

\- \*\*Provide an interactive user interface\*\*



---



\## Technology Stack



\### Programming Language

\- Python



\### Agent \& Workflow Frameworks

\- \*\*LangGraph\*\* – Stateful agent execution  

\- \*\*LangChain\*\* – Tool abstraction and LLM utilities  



\### Large Language Model

\- \*\*Groq LLM\*\* (`llama-3.1-8b-instant`)



\### Utilities

\- \*\*python-dotenv\*\* – Environment variable management  

\- \*\*LangSmith\*\* – Tracing and observability  



\### User Interface

\- \*\*Streamlit\*\*



---



\## System Architecture Overview



The system follows a \*\*Supervisor–Worker architecture\*\* implemented using LangGraph. Each agent operates on a shared state, enabling controlled execution and persistent context across interactions.



\### Architectural Principles



\- Explicit planning before execution  

\- Clear separation between reasoning and actions  

\- Tool-driven interaction with memory  

\- Stateful and explainable workflows  



---



\## Environment Setup and LLM Initialization



The Groq LLM client is initialized using environment variables stored in a `.env` file.



```python

import os

from dotenv import load\_dotenv

from groq import Groq



load\_dotenv()



API\_KEY = os.getenv("GROQ\_API\_KEY")

if not API\_KEY:

&nbsp;   raise ValueError("GROQ\_API\_KEY not found. Please check your .env file.")



client = Groq(api\_key=API\_KEY)


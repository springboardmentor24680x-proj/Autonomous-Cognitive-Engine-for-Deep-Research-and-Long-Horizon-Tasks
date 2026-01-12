\# Autonomous Cognitive Agent System



\## 1. Introduction



This project implements an \*\*Autonomous Cognitive Agent System\*\* designed to perform intelligent, long-horizon tasks through structured planning, reasoning, tool usage, and memory management. The system is built using \*\*Python\*\*, \*\*LangGraph\*\*, \*\*LangChain\*\*, and \*\*Groq-hosted Large Language Models (LLMs)\*\*, with both command-line and Streamlit-based user interfaces.



The core idea is to move beyond single-prompt LLM usage and instead build an \*\*agentic workflow\*\* where tasks are planned, executed step by step, and stored in memory for future reference. The architecture is modular, extensible, and suitable for research as well as real-world automation.



---



\## 2. Objectives



\- Build an autonomous AI agent capable of reasoning and execution  

\- Implement structured task planning using TODO decomposition  

\- Overcome LLM context limitations using persistent memory  

\- Separate reasoning from execution using tools  

\- Enable supervisor–worker style coordination  

\- Provide an interactive user interface  



---



\## 3. Technology Stack



\### Programming Language

\- \*\*Python\*\*



\### Agent \& Workflow Frameworks

\- \*\*LangGraph\*\* – Stateful agent execution  

\- \*\*LangChain\*\* – Tool abstraction and LLM utilities  



\### Large Language Model

\- \*\*Groq LLM\*\* (`llama-3.1-8b-instant`)



\### Utilities

\- \*\*python-dotenv\*\* – Environment management  

\- \*\*LangSmith\*\* – Tracing and observability  



\### User Interface

\- \*\*Streamlit\*\*



---



\## 4. System Architecture Overview



The system follows a \*\*Supervisor–Worker architecture\*\* implemented using LangGraph. Each agent operates on a shared state, enabling controlled execution and persistent context.



\### Key Principles



\- Explicit planning before execution  

\- Clear separation of reasoning and actions  

\- Tool-driven interaction with memory  

\- Stateful, explainable workflows  



---



\## 5. Environment Setup and LLM Initialization



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


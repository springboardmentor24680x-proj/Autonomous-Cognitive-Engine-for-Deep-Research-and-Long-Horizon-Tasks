# ==============================
# research_agent.py
# ==============================

import os
import json
from groq import Groq
from langsmith import traceable
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# ---- VERY IMPORTANT: init tracing FIRST ----
from src.tracing.langsmith import init_tracing
init_tracing()

# ---- Local imports ----
from src.memory.vfs import append_file
from src.tools.calendar_tools import add_event
from src.main.fact_extractor import extract_facts
from src.main.event_extractor import extract_event

# ---- Groq Client ----
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---- System Prompt ----
SYSTEM_PROMPT = """
You are a research and task execution agent.

Capabilities:
- Reason step by step
- Store long-term user facts
- Schedule calendar events automatically

Rules:
- Be concise
- Be factual
- Do not hallucinate
"""

# ==============================
# Groq Reasoning (TRACED)
# ==============================
@traceable(name="groq_reasoning")
def groq_reason(messages):
    """
    Converts LangChain messages to Groq format
    and performs reasoning.
    """
    groq_messages = []

    for m in messages:
        if m.type == "system":
            role = "system"
        elif m.type == "human":
            role = "user"
        elif m.type == "ai":
            role = "assistant"
        else:
            continue

        groq_messages.append({
            "role": role,
            "content": m.content
        })

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=groq_messages,
        temperature=0.3,
    )

    return completion.choices[0].message.content


# ==============================
# Agent Wrapper (TRACED)
# ==============================
class AgentWrapper:

    @traceable(name="agent_invoke")
    def invoke(self, messages):
        """
        Main agent entrypoint.
        Handles:
        - Fact extraction → VFS
        - Event extraction → Calendar
        - Final Groq response
        """

        # ---- Get latest user message ----
        user_text = messages[-1].content

        # =========================
        # FACT EXTRACTION (MEMORY)
        # =========================
        try:
            facts = extract_facts(user_text)
            if facts and facts != "NONE":
                append_file("facts.md", facts)
        except Exception:
            pass  # never crash agent on memory failure

        # =========================
        # EVENT EXTRACTION (CALENDAR)
        # =========================
        try:
            event_json = extract_event(user_text)

            if event_json and event_json != "NONE":
                data = json.loads(event_json)
                add_event(
                    title=data.get("title", "Event"),
                    date=data.get("date", "Unknown"),
                    time=data.get("time", "Unknown")
                )
        except Exception:
            pass  # safe failure

        # =========================
        # GROQ RESPONSE
        # =========================
        reply = groq_reason(
            [SystemMessage(content=SYSTEM_PROMPT)] + messages
        )

        return {
            "messages": messages + [AIMessage(content=reply)]
        }


# ==============================
# Setup Function (USED BY UI)
# ==============================
def setup_agent():
    return AgentWrapper()

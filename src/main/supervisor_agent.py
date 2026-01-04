
from langsmith import traceable
from langchain_core.messages import AIMessage
import json

from src.main.research_agent import run_research
from src.main.summarization_agent import run_summary
from src.main.fact_extractor import extract_facts
from src.main.event_extractor import extract_event
from src.memory.vfs import append_file
from src.tools.calendar_tools import add_event
from src.main.agent_router import route_task
from src.main.chat_agent import run_chat


class SupervisorAgent:
    """
    Central controller that coordinates all sub-agents.
    """

    # -------------------------------
    # ROOT TRACE ENTRY
    # -------------------------------
    @traceable(name="supervisor_run", run_type="chain")
    def run(self, messages):
        """
        Entry point for the supervisor agent.
        """
        return self.invoke(messages)

    # -------------------------------
    # MAIN ORCHESTRATION LOGIC
    # -------------------------------
    @traceable(name="invoke", run_type="chain")
    def invoke(self, messages):
        """
        Extracts facts/events, routes tasks, and returns final response.
        """

        # Get latest user message
        user_text = messages[-1].content

        # ---------- FACT EXTRACTION ----------
        # Extract long-term user facts and store them
        try:
            facts = extract_facts(user_text)
            if facts and facts != "NONE":
                append_file("facts.md", facts)
        except:
            pass  # Ignore extraction errors

        # ---------- EVENT EXTRACTION ----------
        # Extract calendar event and schedule it
        event_msg = None
        try:
            ev = extract_event(user_text)
            if ev and ev != "NONE":
                data = json.loads(ev)
                event_msg = add_event(
                    data["title"], data["date"], data["time"]
                )
        except:
            pass  # Ignore extraction or parsing errors

        # ---------- TASK ROUTING ----------
        # Decide which sub-agent to use
        task = route_task(user_text)

        if task == "research":
            output = run_research(user_text)

        elif task == "summary":
            output = run_summary()

        elif task == "calendar" and event_msg:
            output = event_msg

        else:
            # Default conversational response
            output = run_chat(user_text)

        # Return updated conversation
        return {
            "messages": messages + [AIMessage(content=output)]
        }


def setup_agent():
    """
    Initializes and returns the supervisor agent.
    """
    return SupervisorAgent()

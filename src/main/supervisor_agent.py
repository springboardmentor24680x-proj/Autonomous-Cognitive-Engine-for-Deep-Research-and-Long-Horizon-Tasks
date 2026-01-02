




import json
from langsmith import traceable
from langchain_core.messages import AIMessage

from src.tracing.langsmith import init_tracing
from src.main.agent_router import route_task
from src.main.research_agent import run_research
from src.main.summarization_agent import run_summary
from src.main.fact_extractor import extract_facts
from src.main.event_extractor import extract_event
from src.memory.vfs import append_file
from src.tools.calendar_tools import add_event

init_tracing()

@traceable(name="supervisor_agent")
class SupervisorAgent:

    @traceable(name="invoke")
    def invoke(self, messages):
        user_text = messages[-1].content

        # ---- FACT MEMORY ----
        try:
            facts = extract_facts(user_text)
            if facts and facts != "NONE":
                append_file("facts.md", facts)
        except:
            pass

        # ---- EVENT EXTRACTION ----
        event_msg = None
        try:
            ev = extract_event(user_text)
            if ev and ev != "NONE":
                data = json.loads(ev)
                event_msg = add_event(
                    data["title"], data["date"], data["time"]
                )
        except:
            pass

        # ---- ROUTING ----
        task = route_task(user_text)

        if task == "research":
            output = run_research(user_text)

        elif task == "summary":
            output = run_summary()

        elif task == "calendar" and event_msg:
            output = event_msg

        else:
            output = "Task completed."

        return {
            "messages": messages + [AIMessage(content=output)]
        }

def setup_agent():
    return SupervisorAgent()

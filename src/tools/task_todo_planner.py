from langsmith import traceable
from langchain_groq import ChatGroq

class TaskToDoPlannerTool:

    @traceable(name="Central Task Planner", run_type="tool")
    def run(self, query: str) -> str:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        return llm.invoke(
            f"Create a step-by-step execution plan for: {query}"
        ).content

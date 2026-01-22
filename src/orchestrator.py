from langsmith import traceable
from agents.researcher import ResearcherAgent
from agents.creative import CreativeAgent
from agents.coder import CoderAgent
from tools.task_todo_planner import TaskToDoPlannerTool


class MainAgent:
    def __init__(self):
        # Tools
        self.planner = TaskToDoPlannerTool()

        # Agents
        self.researcher = ResearcherAgent()
        self.creative = CreativeAgent()
        self.coder = CoderAgent()

    @traceable(name="Main Agent Execution")
    def run(self, query: str) -> str:
        """
        Routes the user query to one or more agents based on intent.
        A single query can trigger multiple agents.
        """

        q = query.lower()
        outputs = []

        # -------------------------------------------------
        # Step 1: Planning (trace only, no UI output)
        # -------------------------------------------------
        self.planner.run(query)

        # -------------------------------------------------
        # Step 2: Intent detection
        # -------------------------------------------------
        wants_research = any(word in q for word in [
            "concept", "concepts", "explain", "explanation",
            "what is", "definition", "key", "overview"
        ])

        wants_creative = any(word in q for word in [
            "clearly", "elaborate", "describe", "detailed",
            "article", "blog", "write"
        ])

        wants_code = any(word in q for word in [
            "code", "program", "implement", "implementation",
            "sample code", "example", "java", "python", "c++"
        ])

        # -------------------------------------------------
        # Step 3: Agent execution
        # -------------------------------------------------
        if wants_research:
            outputs.append(self.researcher.run(query))

        if wants_creative:
            outputs.append(self.creative.run(query))

        if wants_code:
            outputs.append(self.coder.run(query))

        # -------------------------------------------------
        # Step 4: Return combined output
        # -------------------------------------------------
        return "\n\n".join(outputs)

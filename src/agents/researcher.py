from langsmith import traceable
from agents.base_agent import BaseAgent

class ResearcherAgent(BaseAgent):

    @traceable(name="Researcher Agent")
    def run(self, query: str) -> str:
        research = self.web_search.run(query)

        res = self.llm.invoke(
            f"Explain factually using this info:\n{research}\nDo NOT include any code."
        )
        return f"<h3 style='font-size:20px; font-weight:bold; color:#1f4e78;'>🔍 Researcher Output</h3>\n{res.content}"

from langsmith import traceable
from agents.base_agent import BaseAgent

class CreativeAgent(BaseAgent):

    @traceable(name="Creative Agent")
    def run(self, query: str) -> str:
        # Step 1: Use WebSearch tool for factual info
        research = self.web_search.run(query)

        # Step 2: Generate creative article using ChatGroq
        res = self.llm.invoke(
            f"Write a creative, engaging article based on this info:\n{research}\nDo NOT include any code."
        )

        # Return with bigger heading
        return f"<h3 style='font-size:20px; font-weight:bold; color:#9c27b0;'>✍️ Creative Output</h3>\n{res.content}"

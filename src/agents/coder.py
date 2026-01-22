from langsmith import traceable
from agents.base_agent import BaseAgent
from tools.code_generator import CodeGenerationTool

class CoderAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.code_gen = CodeGenerationTool()  # ✅ only here

    @traceable(name="Coder Agent")
    def run(self, query: str) -> str:
        code = self.code_gen.run(
            f"Write clean, optimized code for:\n{query}"
        )

        refined = self.llm.invoke(
            f"Refine and optimize this code:\n{code}"
        )

        return (
            "<h3 style='font-size:20px; font-weight:bold; color:#00796b;'>"
            "💻 Coder Output</h3>\n"
            f"<pre>{refined.content}</pre>"
        )

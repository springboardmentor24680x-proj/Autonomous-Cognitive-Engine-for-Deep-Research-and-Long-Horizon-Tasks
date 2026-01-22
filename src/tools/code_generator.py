from langsmith import traceable
from langchain_groq import ChatGroq

class CodeGenerationTool:
    def __init__(self):
        #  DO NOT TRACE INIT
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )

    @traceable(name="Code Generator Tool", run_type="tool")
    def run(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content

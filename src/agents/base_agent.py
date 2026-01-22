from langchain_groq import ChatGroq
from tools.web_search import WebSearchTool

class BaseAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )
        self.web_search = WebSearchTool()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import Optional

class SummarizeTool:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    def summarize(self, text: str, context: Optional[str] = None) -> str:
        """
        Summarizes the provided text, optionally receiving context.
        """
        prompt = f"Please summarize the following text:\n\n{text}"
        if context:
            prompt += f"\n\nContext to keep in mind: {context}"
        
        prompt += "\n\nProvide a concise and informative summary."

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Summarization Error: {str(e)}"

summarize_tool = SummarizeTool()

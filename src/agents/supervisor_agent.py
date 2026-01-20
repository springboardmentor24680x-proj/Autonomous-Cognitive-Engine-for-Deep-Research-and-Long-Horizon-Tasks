from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langsmith import traceable

@traceable(name="supervisor_agent")
class SupervisorAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            temperature=0,
            # LangSmith automatic tracing
        )
    
    def node(self, state):
        query = state["messages"][-1].content
        prompt = f"""
        SUPERVISOR: Plan research for "{query}"
        
        Return concise 3-step plan:
        1. Research objectives
        2. Key questions  
        3. Expected insights
        
        100 words max.
        """
        
        response = self.llm.invoke(prompt)
        return {
            "messages": [AIMessage(content=response.content)]
        }

supervisor_node = SupervisorAgent().node

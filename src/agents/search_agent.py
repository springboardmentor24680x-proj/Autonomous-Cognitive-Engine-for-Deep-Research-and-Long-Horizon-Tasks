from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langsmith import traceable

@traceable(name="research_agent")
class SearchAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        # Tavily disabled for production stability
        # self.tavily = TavilySearchResults(max_results=5) 
    
    def run(self, state):
        query = state["messages"][-1].content
        prompt = f"""
        RESEARCH AGENT: Analyze "{query}"
        
        Deliver:
        • 3 **Key Findings**
        • **Technical Details**
        • **2026 Trends**
        
        Precise, technical. 150 words max.
        """
        
        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

research_node = SearchAgent().run

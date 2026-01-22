from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langsmith import traceable
from src.tools.search_tool import tavily_tool

@traceable(name="research_agent")
class SearchAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    def run(self, state):
        query = state["messages"][0].content
        
        # ACTUALLY SEARCH THE WEB
        print(f"  ... Searching web for: {query}")
        search_results = tavily_tool.search(query)
        
        prompt = (
            f"RESEARCH AGENT: Analyze the following search results and provide 3 key findings for: {query}.\n"
            f"Search Results: {search_results}\n\n"
            "Format: 3 clear, distinct bullet points. Max 150 words total."
        )
        
        response = self.llm.invoke(prompt)
        
        # RECTIFICATION: Mark 'research' as done in the state
        current_todos = state.get("todos", [])
        updated_todos = [
            {**t, "done": True} if t['agent'] == 'research' else t 
            for t in current_todos
        ]
        
        return {
            "messages": [AIMessage(content=response.content)],
            "todos": updated_todos, # Pass the updated list back
            "next": "supervisor"
        }

research_node = SearchAgent().run
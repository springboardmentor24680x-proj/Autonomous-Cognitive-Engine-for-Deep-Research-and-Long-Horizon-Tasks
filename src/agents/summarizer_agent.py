from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from src.memory.vfs import vfs
from langsmith import traceable
from src.tools.summarize_tool import summarize_tool

@traceable(name="summarizer_agent")
class SummarizerAgent:
    def __init__(self):
        # We might not need direct LLM here anymore if using the tool,
        # but let's keep it if we need any other logic later.
        pass
    
    def node(self, state):
        query = state["messages"][0].content
        research_data = state["messages"][-1].content # Get research results
        
        # USE THE TOOL
        summary_content = summarize_tool.summarize(
            text=research_data, 
            context=f"The user original query was: {query}. Create a final report."
        )
        
        # Save to VFS
        filename = f"{query.replace(' ', '_')}_report.txt"
        vfs.write_report(filename, summary_content)
        
        # RECTIFICATION: Mark 'summarize' as done
        current_todos = state.get("todos", [])
        updated_todos = [
            {**t, "done": True} if t['agent'] == 'summarize' else t 
            for t in current_todos
        ]
        
        return {
            "messages": [AIMessage(content=f"Report saved to {filename}")],
            "todos": updated_todos,
            "next": "supervisor"
        }

summarizer_node = SummarizerAgent().node
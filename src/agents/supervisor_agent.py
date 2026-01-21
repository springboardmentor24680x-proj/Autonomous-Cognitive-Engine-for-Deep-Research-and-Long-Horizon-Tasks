from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langsmith import traceable
from src.tools import delegate_task  # M3 Tool
from src.memory.vfs import vfs      # Your M2 VFS

@traceable(name="supervisor_agent")
class SupervisorAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            temperature=0,
        )
    
    def node(self, state):
        query = state["messages"][-1].content
        files = vfs.ls()  # Your M2 VFS
        
        prompt = f"""
        SUPERVISOR: Complete research workflow for "{query}"
        
        Workspace: {files}
        Available tools: delegate_task('research'|'summarize'), vfs.write_report()
        
        CREATE EXECUTABLE 3-STEP PLAN:
        1. delegate_task('research', 'research topic')
        2. delegate_task('summarize', 'analyze findings') 
        3. vfs.write_report('final_report.md', 'final content')
        
        EXACT FORMAT - numbered list only:
        """
        
        response = self.llm.invoke(prompt)
        todos = response.content.split('\n')[:3]  # Extract first 3 steps
        
        return {
            "messages": [AIMessage(content="\n".join(todos))],
            "todos": todos  # M4: Pass todos to state
        }

supervisor_node = SupervisorAgent().node

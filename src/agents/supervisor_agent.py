from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langsmith import traceable

@traceable(name="supervisor_agent")
class SupervisorAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    def node(self, state):
        messages = state.get("messages", [])
        query = messages[0].content if messages else "No Query"
        todos = state.get("todos", [])
        
        # 1. INITIALIZE: Todo list okkasari mathrame create avthundi
        if not todos:
            todos = [
                {"id": 1, "task": f"Research {query}", "done": False, "agent": "research"},
                {"id": 2, "task": f"Summarize findings", "done": False, "agent": "summarize"}
            ]
            return {
                "todos": todos,
                "next": "research",
                "messages": [AIMessage(content="Plan created. Routing to Research.")]
            }
        
        # 2. ROUTE: Next unfinished task emundo chusi akkadiki pampisthundi
        next_todo = next((t for t in todos if not t.get('done')), None)
        
        if next_todo:
            return {
                "next": next_todo['agent'],
                "messages": [AIMessage(content=f"Proceeding to {next_todo['agent']}.")]
            }
        
        # 3. FINISH: Anni tasks ayipothe flow end chestundi
        return {"next": "__end__", "messages": [AIMessage(content="Workflow complete.")]}

supervisor_node = SupervisorAgent().node
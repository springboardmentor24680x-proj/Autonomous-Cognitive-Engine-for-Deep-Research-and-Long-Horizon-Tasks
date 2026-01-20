import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import warnings

warnings.filterwarnings("ignore")
load_dotenv()
# Change this line in main.py:
#from src.graph.state_graph import state_graph  # Now works correctly

print("Autonomous Cognitive Engine")
print("Deep Research & Long-Horizon Task Framework")
print("--- Engine Active ---")

try:
    from src.agents.supervisor_agent import supervisor_node
    from src.agents.search_agent import research_node  
    from src.agents.summarizer_agent import summarizer_node
    from src.graph.state_graph import state_graph
    print("All agents and graph loaded successfully")
except ImportError as e:
    print(f"Import error: {e}")
    print("Run: pip install -U langchain-groq langchain-tavily python-dotenv")
    exit(1)

def run_interactive_agent():
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    while True:
        try:
            query = input("\nWhat complex task should I perform? ").strip()
            if not query or query.lower() in ['exit', 'quit', 'bye']:
                print("Engine shutdown complete.")
                break
            
            print(f"Processing: {query}")
            
            inputs = {
                "messages": [HumanMessage(content=query)],
                "todos": [],
                "next": "supervisor"
            }
            
            print("Agent Execution")
            for step_num, event in enumerate(state_graph.stream(inputs, {"recursion_limit": 25})):
                node_name = list(event.keys())[0]
                step_data = event[node_name]
                
                print(f"Step {step_num+1}: {node_name.upper()}")
                if "messages" in step_data:
                    last_msg = step_data["messages"][-1]
                    print(f"  Output: {last_msg.content[:100]}...")
                
                if "todos" in step_data:
                    todos = step_data["todos"]
                    remaining = len([t for t in todos if not t.get('done', False)])
                    print(f"  TODOs: {remaining} remaining")
            
            print("Task execution complete.")
            print("Ready for next task")
            
        except KeyboardInterrupt:
            print("Interrupted by user.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Engine remains active for next attempt...")

if __name__ == "__main__":
    run_interactive_agent()

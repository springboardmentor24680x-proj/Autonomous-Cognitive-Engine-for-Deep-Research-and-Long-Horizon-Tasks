from typing import Dict, List
from langchain_core.messages import AIMessage

class VFSManager:
    @staticmethod
    def process_tool_calls(state: dict) -> dict:
        """Process tool calls and ensures clean data storage."""
        new_vfs = dict(state.get("vfs", {}))
        new_todos = list(state.get("todos", []))
        
        if not state["messages"]:
            return {"vfs": new_vfs, "todos": new_todos}
            
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]
                
                # Logic for Milestone 2: Context Offloading
                if name == "write_file":
                    fname = str(args.get("filename", "untitled.txt"))
                    fcontent = str(args.get("content", ""))
                    # Clean out any list brackets that the LLM might have sent
                    new_vfs[fname] = fcontent.strip("[]'\"")
                
                # Logic for Milestone 1: Planning
                elif name == "write_todos":
                    tasks = args.get("tasks", [])
                    # Flatten list and remove markdown bullets
                    new_todos = [str(t).strip("- ") for t in tasks]
                    
        return {"vfs": new_vfs, "todos": new_todos}
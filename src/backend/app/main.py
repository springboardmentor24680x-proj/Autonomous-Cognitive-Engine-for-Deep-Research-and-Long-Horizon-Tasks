from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .utils import get_or_create_session, sessions
from .agent import agent

app = FastAPI(title="Autonomous AI Agent", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    messages: list
    todos: list
    files: dict
    calendar: list
    visualizations: list  

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with visualization support"""
    try:
        # Get or create session
        state = get_or_create_session(request.session_id)
       
        # Add user message to state
        from langchain_core.messages import HumanMessage
        state["messages"].append(HumanMessage(content=request.message))
       
        # Run the agent 
        result = agent.invoke(state)
       
        # Update session with result
        sessions[request.session_id] = result
       
        # Format messages for response
        formatted_messages = []
        for msg in result["messages"]:
            formatted_messages.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
       
        # Get last assistant response
        last_assistant_response = ""
        for msg in reversed(result["messages"]):
            if msg.type == "ai":
                last_assistant_response = msg.content
                break
       
        return ChatResponse(
            response=last_assistant_response, 
            messages=formatted_messages,
            todos=result["todos"],
            files=result["files"],
            calendar=result["calendar"],
            visualizations=result.get("visualizations", [])  # Include visualizations
        )
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state including visualizations"""
    state = get_or_create_session(session_id)
    return {
        "todos": state["todos"],
        "files": state["files"],
        "calendar": state["calendar"],
        "visualizations": state.get("visualizations", []),
        "context": state["context"]
    }

@app.get("/visualizations/{session_id}")
async def get_visualizations(session_id: str):
    """Get all visualizations for a session"""
    state = get_or_create_session(session_id)
    return {
        "visualizations": state.get("visualizations", []),
        "count": len(state.get("visualizations", []))
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "autonomous-ai-agent-v3",
        "version": "3.1.0",
        "features": ["tasks", "calendar", "files", "visualizations", "sub-agents"]
    }

# ═══════════════════════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
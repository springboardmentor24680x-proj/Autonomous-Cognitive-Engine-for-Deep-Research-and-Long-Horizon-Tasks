from fastapi import FastAPI
from pydantic import BaseModel
import requests

XAI_API_KEY = "xai-zqu43jubJnQs0yWEpVOuFL6knfzBT8WCmRcLTTtSOGp9oO0WDhO1IYQEbjmjJAYfwULmQwtyZbOu37Hr"

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list

@app.post("/chat")
def chat(req: ChatRequest):
    response = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "grok-beta",
            "messages": req.messages,
            "temperature": 0.7
        }
    )
    return response.json()

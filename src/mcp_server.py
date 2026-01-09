from fastapi import FastAPI
from pydantic import BaseModel

from agents.summarization_agent import summarization_agent
from agents.web_search_agent import web_search_agent
from agents.code_agent import code_agent

app = FastAPI(title="MCP Tool Server")

# ---------- Schemas ----------

class TextInput(BaseModel):
    text: str

class QueryInput(BaseModel):
    query: str

# ---------- Tools ----------

@app.post("/summarize")
def summarize(input: TextInput):
    return {"result": summarization_agent(input.text)}

@app.post("/web_search")
def web_search(input: QueryInput):
    return {"result": web_search_agent(input.query)}

@app.post("/code")
def code(input: TextInput):
    return {"result": code_agent(input.text)}

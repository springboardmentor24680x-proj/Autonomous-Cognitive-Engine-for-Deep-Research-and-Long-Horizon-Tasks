import json
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import logging
# Import tools
from tools.web_search import web_search
from tools.vfs import vfs_write, vfs_read, vfs_ls
from tools.visualization import create_visualization
from tools.calendar import add_event, list_events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, "mcp_server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MCP_Server")
logger.info("Logger initialized successfully")

load_dotenv()
mcp = FastMCP("autonomous-cognitive-engine")

# Initialize LLM
llm = ChatGroq(model="moonshotai/kimi-k2-instruct-0905", temperature=0)

# --- IMPROVED SUPERVISOR PROMPT ---
SUPERVISOR_PROMPT = """
You are an Autonomous Supervisor. Your job is to lead a research project.
You must use tools in a logical sequence:
1. 'research_agent': To get data from the web.
2. 'vfs_write': To save the research to a file (use .txt or .md).
3. 'create_visualization': To make a chart from the saved file.
4. 'add_event': To schedule a follow-up.

NEVER output a tool call as a 'final_answer'. 
If you need to write a file, you MUST output: {"action": "vfs_write", "args": {...}}.
Only use 'final_answer' when you have NO MORE tools to run.

CRITICAL: Review the 'Tool output' in the context. If you just received research results, your NEXT action should be 'vfs_write'.
Output ONLY JSON: {"action": "tool_name", "args": {"arg_name": "value"}}
"""

@mcp.tool()
def supervisor(query: str) -> str:
    """Decides the next step in the research workflow."""
    logger.info(f"Supervisor received query: {query[:100]}...")
    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=query)
    ])
    text = response.content.strip()
    logger.debug(f"Raw LLM Response: {text}")
    # Clean JSON
    clean = text.replace("```json", "").replace("```", "").strip()
    
    try:
        json.loads(clean) 
        logger.info(f"Supervisor decision: {clean}")
        return clean       
    except Exception:
        # If LLM failed JSON, force a final answer so the app doesn't hang
        logger.error(f"JSON Parsing failed: {str(e)}")
        return json.dumps({
            "action": "final_answer", 
            "args": {"response": text}
        })

@mcp.tool()
def research_agent(query: str) -> str:
    """Performs web research and formats data for graphing."""
    logger.info(f"Researching: {query}")
    raw_results = web_search(query)
    
    # Use LLM to structure the messy web results
    struct_prompt = f"""
    Summarize these results for: {query}
    Results: {raw_results}
    
    You MUST include a section:
    DATA FOR GRAPHING
    Brand: Number
    """
    
    res = llm.invoke([
        SystemMessage(content="You are a data researcher. Be precise."),
        HumanMessage(content=struct_prompt)
    ])
    
    # Return as string so app.py can easily append it to context
    logger.info("Research completed and structured.")
    return res.content

# Register tools
mcp.tool()(vfs_write)
mcp.tool()(vfs_read)
mcp.tool()(vfs_ls)
mcp.tool()(create_visualization)
mcp.tool()(add_event)
mcp.tool()(list_events)

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")
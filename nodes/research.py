from src.tools.web_search import web_search
from src.memory.vfs import write_file
from subagents.research_subagent import build_research_agent
import datetime
import os
from langchain_groq import ChatGroq

def research_node():
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )

    agent = build_research_agent(llm)

    def node(state):
        query = state["messages"][-1].content

        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        text = result["messages"][-1].content

        filename = "research_notes.txt"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        write_file(
            filename,
            f"\n---\nTime: {timestamp}\n{text}"
        )

        return {
            **state,
            "final_response": f"Research completed and saved to {filename}"
        }

    return node

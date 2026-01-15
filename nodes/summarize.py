from src.memory.vfs import read_file, write_file
from subagents.summarization_subagent import build_summarization_agent
import os
from langchain_groq import ChatGroq

def summarize_node():
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )
    summarizer = build_summarization_agent(llm)

    def node(state):
        filename = state["source_file"] or "research_notes.txt"
        content = read_file(filename)

        summary = summarizer.invoke({"input": content})
        out_file = filename.replace(".txt", "_summary.txt")
        write_file(out_file, summary)

        return {
            **state,
            "final_response": f"Summary saved to {out_file}"
        }

    return node

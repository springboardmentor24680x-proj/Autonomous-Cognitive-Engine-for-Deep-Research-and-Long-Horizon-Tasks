from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from state import AgentState
from llm_factory import make_llm
from vfs_tools import VirtualFileSystem
from shared_resources import vfs


vfs = VirtualFileSystem()

def summarizer_node(state: AgentState) -> AgentState:
    llm = make_llm()

    prompt = HumanMessage(
        content=f"Summarize the following:\n\n{state['search_results']}"
    )

    response = llm.invoke([prompt])

    vfs.write_file("summary.txt", prompt.content, response.content)
    state["messages"].append(response)

    return state

graph = StateGraph(AgentState)
graph.add_node("summarize", summarizer_node)
graph.set_entry_point("summarize")
graph.add_edge("summarize", END)

SummarizationAgent = graph.compile()

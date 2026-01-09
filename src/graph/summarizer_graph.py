from langchain_core.messages import HumanMessage
from langsmith import traceable

from graph.state import AgentState
from tools.llm_factory import make_llm
from memory.vfs import vfs   # ✅ singleton VFS

@traceable(name="summarizer_node")
def summarizer_node(state: AgentState) -> AgentState:
    llm = make_llm()

    content = state.get("search_results", "")

    # 🔹 Remove links / sources
    if "Sources:" in content:
        content = content.split("Sources:")[0].strip()

    prompt = HumanMessage(
        content=(
            "Summarize the following clearly.\n"
            "- No links\n"
            "- No sources\n\n"
            f"{content}"
        )
    )

    response = llm.invoke([prompt])

    vfs.write_file(
        file_name="summary.txt",
        prompt=prompt.content,
        response=response.content
    )

    state["messages"].append(response)
    return state

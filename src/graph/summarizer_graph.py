from langchain_core.messages import HumanMessage, AIMessage
from graph.state import AgentState
from tools.llm_factory import make_llm
from memory.vfs import vfs

def summary_node(state: AgentState) -> AgentState:
    content = state.get("search_results")
    if not content:
        return state

    llm = make_llm()

    prompt = HumanMessage(
        content=(
            "You are a professional research analyst.\n\n"
            "TASK:\n"
            "1. Identify TOP 3 REAL case studies.\n"
            "2. For EACH case study provide:\n"
            "   - Organization\n"
            "   - Use case\n"
            "   - Impact / outcome\n"
            "   - Source link\n"
            "3. Extract lessons for SMALL BUSINESSES.\n\n"
            "FORMAT:\n"
            "- Headings\n"
            "- Bullet points\n"
            "- Clear explanations\n\n"
            f"CONTENT:\n{content}"
        )
    )

    response = llm.invoke([prompt])

    state["summary"] = response.content
    state.setdefault("messages", []).append(AIMessage(content=response.content))

    vfs.write_file("summary.txt", prompt.content, response.content)
    return state

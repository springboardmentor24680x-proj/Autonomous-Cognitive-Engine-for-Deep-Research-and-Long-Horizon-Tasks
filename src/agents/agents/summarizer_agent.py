from langsmith import traceable
from tools.summarizer_tool import summarizer
from memory.vfs import write_file


@traceable(name="summarizer_agent")
def summarizer_node(state: dict) -> dict:
    """
    Summarizer agent node.
    Calls the summarizer TOOL so it appears in tracing.
    """

    content = (
        state.get("research")
        or state.get("search_results")
        or ""
    )

    if not content:
        state["summary"] = "No content available to summarize."
        return state

    summary = summarizer.invoke({"text": content})

    state["summary"] = summary

    write_file.invoke({
        "filename": "summary.txt",
        "content": summary
    })

    return state

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

def summarizer_node(state: dict) -> dict:
    content = state["files"]["research.txt"]

    summary = llm.invoke(
        f"Summarize the following content clearly:\n{content}"
    ).content

    state["files"]["summary.txt"] = summary
    state["output"] = summary
    return state

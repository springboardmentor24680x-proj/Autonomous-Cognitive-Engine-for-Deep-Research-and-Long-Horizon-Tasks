from langchain_core.messages import SystemMessage

def supervisor_node(llm):
    def node(state):
        user_text = state["messages"][-1].content.lower()

        if "research" in user_text:
            return {**state, "intent": "research"}
        if "summarize" in user_text:
            return {**state, "intent": "summarize"}
        if any(k in user_text for k in ["chart", "graph", "visualize"]):
            return {**state, "intent": "visualize"}
        if any(k in user_text for k in ["meeting", "event", "calendar"]):
            return {**state, "intent": "calendar"}

        return {**state, "intent": "respond"}

    return node

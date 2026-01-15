from src.tools.calendar_tools import add_event

def calendar_node():
    def node(state):
        text = state["messages"][-1].content
        # simple demo parsing
        return {**state, "final_response": "Calendar action completed."}

    return node

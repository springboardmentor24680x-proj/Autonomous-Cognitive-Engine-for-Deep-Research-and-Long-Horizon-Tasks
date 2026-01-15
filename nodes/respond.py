from langchain_core.messages import AIMessage

def respond_node():
    def node(state):
        return {
            "messages": state["messages"] + [
                AIMessage(content=state.get("final_response", "Done."))
            ]
        }

    return node

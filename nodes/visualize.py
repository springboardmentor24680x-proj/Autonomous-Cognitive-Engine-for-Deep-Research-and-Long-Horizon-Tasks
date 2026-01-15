from src.tools.visualization import create_visualization

def visualize_node():
    def node(state):
        result = create_visualization(
            source_file=state["source_file"],
            chart_type=state["chart_type"],
            title=state.get("chart_title", "")
        )

        return {**state, "final_response": result}

    return node

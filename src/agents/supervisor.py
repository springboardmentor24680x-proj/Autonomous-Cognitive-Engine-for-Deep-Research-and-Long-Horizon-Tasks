from agents.web_search import web_search

def supervisor(state: dict) -> dict:
    user_goal = state["input"]

    research = web_search(user_goal)
    state["files"]["research.txt"] = research

    # DO NOT summarize here
    return state

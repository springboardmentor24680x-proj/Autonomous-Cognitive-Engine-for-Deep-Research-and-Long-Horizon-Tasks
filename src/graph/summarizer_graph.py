# graph/summarizer_graph.py
from graph.state import AgentState
from tools.llm_factory import make_llm

def summary_node(state: AgentState) -> AgentState:
    content = state.get("search_results", "")
    if not content:
        state["summary"] = "No content to summarize."
        return state

    # Get configured client
    openai_client = make_llm(provider="openrouter")

    prompt = [
        {"role": "system", "content": "You are a helpful assistant that summarizes text."},
        {"role": "user", "content": content}
    ]

    # Use Chat Completions
    response = openai_client.ChatCompletion.create(
        model="gpt-4o-mini",  # you can change to any valid OpenRouter model
        messages=prompt,
        max_tokens=300,
    )

    summary_text = response.choices[0].message["content"]

    state["summary"] = summary_text
    return state

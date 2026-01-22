from agents.summarizer import run as summarize
from agents.analyzer import run as analyze
from agents.planner import run as plan

def route(prompt: str):
    p = prompt.lower()

    if "summarize" in p or "summary" in p:
        return "summary", summarize(prompt)

    elif "analyze" in p or "analysis" in p:
        return "analysis", analyze(prompt)

    elif "plan" in p or "prepare" in p:
        return "plan", plan(prompt)

    else:
        # default fallback
        return "analysis", analyze(prompt)

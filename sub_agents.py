from llm.groq_llm import call_llm


# 🔍 Research Agent
def research_agent(task: str):
    print("🤖 Research Agent working...")

    prompt = f"""
You are a research agent.

Task:
{task}

Collect detailed, factual information.
"""

    return call_llm(prompt)


# ✍️ Summarizer Agent
def summarizer_agent(content: str):
    print("🤖 Summarizer Agent working...")

    prompt = f"""
You are a summarization agent.

Summarize and structure this:

{content}
"""

    return call_llm(prompt)
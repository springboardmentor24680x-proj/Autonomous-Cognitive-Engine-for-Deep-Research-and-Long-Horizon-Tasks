from langchain_groq import ChatGroq

llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0
)

def summarization_agent(text: str) -> str:
    res = llm.invoke(
        f"Summarize the following in exactly 2 sentences:\n{text}"
    )
    return res.content

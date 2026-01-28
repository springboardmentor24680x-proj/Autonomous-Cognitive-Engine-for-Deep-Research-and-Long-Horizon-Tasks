from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

def web_search(task: str) -> str:
    prompt = f"Perform deep research and return structured notes:\n{task}"
    return llm.invoke(prompt).content

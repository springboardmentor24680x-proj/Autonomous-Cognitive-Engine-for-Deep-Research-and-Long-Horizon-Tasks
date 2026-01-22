from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant",
     temperature=0
)

def run(prompt: str) -> str:
    response = llm.invoke(
        f"Create a step-by-step plan for:\n{prompt}"
    )
    return response.content

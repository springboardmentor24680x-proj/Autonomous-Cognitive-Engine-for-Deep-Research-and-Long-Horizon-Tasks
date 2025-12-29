from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# LLM
llm = ChatOpenAI(temperature=0)

# Prompt template (important for tracing clarity)
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent task planning agent."),
    ("human", "Create a clear, actionable TODO list for the following request:\n{user_input}")
])

def generate_todo(user_input: str):
    chain = prompt_template | llm
    response = chain.invoke({"user_input": user_input})
    return response.content


def run_agent():
    print("\n🧠 TODO Planner Agent (LangSmith Tracing Enabled)")
    print("Type 'exit' to stop\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Agent stopped.")
            break

        todo = generate_todo(user_input)

        print("\n📋 Generated TODO List:\n")
        print(todo)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    run_agent()

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(temperature=0)

def generate_todo(prompt: str) -> str:
    """
    Uses LLM to generate a TODO list for ANY user prompt
    """
    planner_prompt = f"""
You are an intelligent task planning agent.

Given a user request, generate a clear, actionable TODO list.
Do NOT explain anything.
Return only a numbered list of tasks.

User request:
{prompt}
"""
    response = llm.invoke(planner_prompt)
    return response.content


def run_agent():
    print("\n TODO Agent Started")
    print("Type 'exit' to stop\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Agent stopped.")
            break

        todo = generate_todo(user_input)

        print("\n Generated TODO List:\n")
        print(todo)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    run_agent()


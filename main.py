import os
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------
# Load API Key from .env
# -------------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API Key not found! Check your .env file.")
    exit()

client = OpenAI(api_key=api_key)

# -------------------------------------------------
# To-Do List System
# -------------------------------------------------
todo_list = []

def add_task(task):
    todo_list.append(task)
    return f"Task added: {task}"

def view_tasks():
    if not todo_list:
        return "No tasks added yet."
    return "\n".join(f"- {t}" for t in todo_list)

# -------------------------------------------------
# AI Assistant Function
# -------------------------------------------------
def ask_ai(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------
# Menu System
# -------------------------------------------------
def main():
    print("\n--- AI + To-Do List Assistant ---")
    print("Commands:")
    print(" add <task>      → Add new task")
    print(" view            → View tasks")
    print(" ask <question>  → Ask AI anything")
    print(" exit            → Quit")

    while True:
        user_input = input("\nWhat do you want to do? ")

        if user_input.startswith("add "):
            print(add_task(user_input[4:]))

        elif user_input == "view":
            print(view_tasks())

        elif user_input.startswith("ask "):
            print("\nAI:", ask_ai(user_input[4:]))

        elif user_input == "exit":
            print("Goodbye!")
            break

        else:
            print("Invalid command. Try again.")

main()
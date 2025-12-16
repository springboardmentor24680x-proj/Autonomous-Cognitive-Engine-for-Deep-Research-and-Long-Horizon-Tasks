import os
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from langchain_core.tools import Tool
# Import the tool functions from your VFS file
# NOTE: The imported functions will now use the VFS-only logic above.
from vfs import write_file, read_file, ls, edit_file,clear_vfs 
# Import functions from calendar_service.py
from calendar_service import add_event, list_events, delete_event

def setup_agent():
    """Sets up the Groq client, system prompt, and initializes the agent."""
    load_dotenv()
    clear_vfs()
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")

    groq_client = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )
    
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # ----------------------------
    # System Prompt
    # ----------------------------
    system_prompt = f"""
You are a versatile and intelligent AI Assistant specializing in organization, file management, and scheduling.
Your goal is to execute the appropriate tool action precisely.

TODAY'S DATE: {current_date}

AVAILABLE TOOLS:
- File Management: write_file, read_file, edit_file, ls
- Scheduling: add_event, list_events, delete_event

---
TODO MANAGEMENT RULES (STRICT):
---

1. CREATE NEW TODO FILE (Only for the very first todo list in a category):
- If the user asks to CREATE or MAKE a todo list, and you confirm the file is new:
  • You MUST call write_file to create the file.
  • You MUST use the correct category filename (todos_personal.txt, todos_work.txt, etc.).
  • Final response MUST be ONLY: "Todo saved successfully to <filename>"

2. ADD / EDIT / UPDATE / DELETE TODOS (For existing files):
- If the user asks to ADD, MODIFY, UPDATE, or DELETE a todo, you are manipulating an existing file.
  • **SEQUENCE:** You MUST use the sequence: **read_file -> LLM Reasoning/Update -> edit_file**
  • First, call read_file("<category file>") to get current contents.
  • Then, update the entire content string.
  • Finally, call edit_file("<category file>", "new, updated content").
- Final response MUST be ONLY: "Todo updated successfully"

3. READ / SHOW TODOS:
- If the user asks to SHOW, READ, VIEW, or LIST todos:
  • Use the rules for reading (read_file for specific, or multiple reads for general).
  • DO NOT call write_file or edit_file.

4. FILE QUERIES & CALENDAR RULES:
- (Keep your existing Rules 4 and 5 as they are robust)
"""



    # Pass the functions directly to the 'tools' list.
    agent = create_deep_agent(
        tools=[
            write_file,
            read_file,
            ls,
            edit_file,
            add_event,
            list_events,
            delete_event        ],
        system_prompt=system_prompt,
        model=groq_client,
    )
    
    return agent

def main():
    """Main function to initialize and run the interactive agent loop."""
    agent = setup_agent()
    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Check for empty input to prevent errors
        if not user_input.strip():
            continue

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })

        print("\nAgent:\n")
        # Print the model's final response, which MUST be the tool output
        print(result["messages"][-1].content)

# Standard Python entry point
if __name__ == "__main__":
    main()
import os
import datetime
from dotenv import load_dotenv

# 1. Load environment variables IMMEDIATELY so sub-agents can see the API key
load_dotenv()

from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from langchain_core.tools import tool

# VFS tools
from src.memory.vfs import write_file, read_file, ls, edit_file, clear_vfs

# Calendar tools
from src.tools.calendar_tools import add_event, list_events, delete_event

# Research sub-agent
from subagents.research_subagent import build_research_agent

#Summarization sub-agent
from subagents.summarization_subagent import build_summarization_agent

VFS = {}
EVENTS = []
def setup_agent():
    # Clear the virtual file system on startup
    clear_vfs()

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not found in environment variables. Check your .env file.")

    # Keeping your specific model name as requested
    groq_client = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="meta-llama/llama-4-scout-17b-16e-instruct"
    )

    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # SYSTEM PROMPT 
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
    If the user asks a question about their plans, people, or data that you don't recall, ALWAYS use the ls and read_file tools to check your VFS files before answering 'I don't know'.
"""

    # Build research sub-agent
    research_agent = build_research_agent(groq_client)
    #Build summarize sub_agent
    summarization_agent = build_summarization_agent(groq_client)

    # TASK DELEGATION TOOL
    @tool
    def research_task(description: str, subagent_type: str) -> str:
        """
        Delegate a task to a specialized sub-agent.
        Allowed subagent_type: 'research' (for lookups and reports).
        """
        print(f"\n--- DEBUG: Main Agent is calling subagent_type: '{subagent_type}' ---")
        print(f"--- DEBUG: Description sent: '{description}' ---")
        normalized = subagent_type.lower()
    
        if "research" in normalized:
            # Invoking the research sub-agent
            result = research_agent.invoke({"messages": [{"role": "user", "content": description}]},config={"run_name": "ResearchSubAgent"})
            
            research_output = result["messages"][-1].content
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            entry = (
                f"\n---\n"
                f"Research Topic: {description}\n"
                f"Time: {timestamp}\n\n"
                f"{research_output}\n"
            )

            # Check if file exists and append/edit, otherwise create new
            existing = read_file("research_notes.txt")
            if isinstance(existing, str) and not existing.startswith("File"):
                edit_file("research_notes.txt", existing + entry)
            else:
                write_file("research_notes.txt", entry)

            return "Research completed and saved to research_notes.txt"
    #Summarization Sub-Agent
    @tool
    def summarization_task(description: str) -> str:
        """
        Delegate summarization to the summarization sub-agent.
        """
        result = summarization_agent.invoke(
            {"messages": [{"role": "user", "content": description}]},
            config={
                "run_name": "SummarizationSubAgent",
                "tags": ["subagent", "summarization"]
            }
        )
        return result["messages"][-1].content


    # Create main agent
    agent = create_deep_agent(
        tools=[
            write_file,
            read_file,
            ls,
            edit_file,
            add_event,
            list_events,
            delete_event,
            research_task, 
            summarization_task
        ],
        system_prompt=system_prompt,
        model=groq_client,
    )

    return agent

def main():
    # Initialize the agent
    agent = setup_agent()

    print("AI Assistant initialized. Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        try:
            # Execute agent logic
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            print("\nAgent:\n")
            print(result["messages"][-1].content)
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
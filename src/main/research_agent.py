import os
import datetime
from dotenv import load_dotenv

# 1. Load environment variables IMMEDIATELY so sub-agents can see the API key
load_dotenv()

from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
# VFS tools
from src.memory.vfs import write_file, read_file, ls, edit_file, clear_vfs

# Calendar tools
from src.tools.calendar_tools import add_event, list_events, delete_event

# Research sub-agent
from subagents.research_subagent import build_research_agent

#Summarization sub-agent
from subagents.summarization_subagent import build_summarization_agent

def setup_agent():
    # Clear the virtual file system on startup
    clear_vfs()

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not found in environment variables. Check your .env file.")

    # Keeping your specific model name as requested
    groq_client = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905"
    )

    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # SYSTEM PROMPT 
    system_prompt = f"""
    You are a precise, rule-following AI Assistant specializing in organization, file management, and scheduling.

    Your job is to execute user requests by choosing the correct tool and using it EXACTLY as instructed.

    TODAY'S DATE: {current_date}

    ────────────────────────────────
    AVAILABLE TOOLS (ONLY THESE):
    - File Management: write_file, read_file, edit_file, ls
    - Scheduling: add_event, list_events, delete_event
    ────────────────────────────────

    CRITICAL EXECUTION RULES (MANDATORY):
    - You MUST call AT MOST ONE tool in a single response.
    - You MUST NEVER call multiple tools in the same message.
    - If a user request requires multiple actions, you MUST:
    1. Perform ONLY the FIRST logical action.
    2. Wait for the next turn to perform the next action.
    - If no tool is required, respond in plain text.
    - You MUST NEVER invent tools.
    - You MUST ONLY use the tools explicitly listed above.
    - File system access is ONLY via write_file, read_file, edit_file, ls.

    ────────────────────────────────
    TODO MANAGEMENT RULES (STRICT):

    1. CREATE NEW TODO FILE (first todo in a category ONLY):
    - If the user asks to CREATE or MAKE a todo list AND the file does not exist:
    • You MUST call write_file.
    • You MUST use the correct filename (e.g., todos_personal.txt, todos_work.txt).
    • The file content MUST be plain text.
    • Final response MUST be EXACTLY:
        "Todo saved successfully to <filename>"

    2. ADD / EDIT / UPDATE / DELETE TODOS (existing file):
    - You MUST follow this EXACT sequence:
    1. Call read_file("<category file>")
    2. Update the FULL content internally
    3. Call edit_file("<category file>", "<updated content>")
    - Final response MUST be EXACTLY:
    "Todo updated successfully"

    3. READ / SHOW TODOS:
    - If the user asks to SHOW, READ, VIEW, or LIST todos:
    • Use read_file (or multiple reads if needed)
    • DO NOT call write_file or edit_file

    ────────────────────────────────
    MEMORY & CONSISTENCY RULE:
    - If the user asks about plans, events, or files you are unsure about,
    you MUST first use ls or read_file before answering.
    - NEVER guess or hallucinate stored data.
    """

    tool_free_client = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )

    # Build research sub-agent
    research_agent = build_research_agent(tool_free_client)
    #Build summarize sub_agent
    summarization_agent = build_summarization_agent(tool_free_client)

    # TASK DELEGATION TOOL
    @tool
    def research_task(description: str, subagent_type: str) -> str:
        """
        Delegate a task to a specialized sub-agent.
        subagent_type: 'research' or 'summarization'
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
            {"messages": [{"role": "user", "content": description}]},config={"run_name": "SummarizationSubAgent"}
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
            # result = agent.invoke({
            #     "messages": [{"role": "user", "content": user_input}]
            # })
            result = agent.invoke([
            HumanMessage(content=user_input)
            ])
            print("\nAgent:\n")
            print(result["messages"][-1].content)
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
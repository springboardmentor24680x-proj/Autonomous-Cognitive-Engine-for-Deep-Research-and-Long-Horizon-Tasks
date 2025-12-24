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
    You are a precise, rule-following Supervisor Agent in a multi-agent system.
    Your primary objective is to manage high-level orchestration across research, summarization, and file-based memory.

    TODAY'S DATE: {current_date}
    TOOLS AVAILABLE:
    - Files: write_file, read_file, edit_file, ls
    - Calendar: add_event, list_events, delete_event
    - Sub-agents: research_task, summarization_task

    RULES:
    1. Use tools for ALL research, summarization, file access, and scheduling.
    2. Never summarize or research inline.
    3. One tool call per turn.
    4. Always check files with ls/read_file before using them.
    5. Do not assume data or file existence.

    SUB-AGENT RULES:
    - Use research_task for any market, competitor, or risk research.
    - Use summarization_task for any summarization or document combining.
    - Always pass config when invoking sub-agents.

    SUMMARIZATION FLOW (MANDATORY):
    - read_file all required files
    - call summarization_task on combined text
    - write_file to save output

    Failure to follow these rules is an error.
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
    def research_task(description: str) -> str:
        """
        Perform research using the research sub-agent and store results.
        """
        print("\n--- DEBUG: Research sub-agent invoked ---")
        print(f"--- Topic: {description} ---")

        result = research_agent.invoke(
            {"messages": [{"role": "user", "content": description}]},
            config=RunnableConfig(
                run_name="ResearchSubAgent",
                tags=["subagent", "research"]
            )
        )

        research_output = result["messages"][-1].content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = (
            f"\n---\n"
            f"Research Topic: {description}\n"
            f"Time: {timestamp}\n\n"
            f"{research_output}\n"
        )

        existing = read_file("research_notes.txt")
        if isinstance(existing, str) and not existing.startswith("File"):
            edit_file("research_notes.txt", existing + entry)
        else:
            write_file("research_notes.txt", entry)

        return "Research completed and saved to research_notes.txt"

        
    @tool
    def summarization_task(text: str, config: RunnableConfig) -> str: 
        """
        Summarize text using the summarization sub-agent.
        """
        # config is automatically injected by the main agent.
        # Passing it here links the sub-agent run to the parent trace.
        result = summarization_agent.invoke(
            {"input": text},
            config=config
        )
        
        # If using StrOutputParser, 'result' is already a string.
        # If not, use 'result.content'.
        return result

    @tool
    def summarize_file(filename: str, config: RunnableConfig) -> str: # Add config here
        """
        Read a file, delegate summarization, and save result.
        """
        # Sanitize filename (remove leading slashes for VFS)
        clean_filename = filename.lstrip('/')
        content = read_file(clean_filename)
        
        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # Delegate to the other tool using the same config
        summary = summarization_task.invoke(
            {"text": content},
            config=config
        )

        summary_file = clean_filename.replace(".txt", "_summary.txt")
        write_file(summary_file, summary)

        return f"Summary saved successfully to {summary_file}"

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
            summarization_task,
            summarize_file
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
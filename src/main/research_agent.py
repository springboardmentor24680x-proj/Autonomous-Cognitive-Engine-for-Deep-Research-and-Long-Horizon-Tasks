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

    ────────────────────────────────
    AVAILABLE TOOLS (ONLY THESE):
    - File Management: write_file, read_file, edit_file, ls
    - Scheduling: add_event, list_events, delete_event
    - Specialized Sub-Agents: research_task, summarization_task
    ────────────────────────────────

    CRITICAL EXECUTION RULES (MANDATORY):
    1. ONE TOOL PER TURN: You MUST call AT MOST ONE tool in a single response.
    2. ATOMIC ACTIONS: If a request requires multiple actions (e.g., Research -> Summarize -> Save), you MUST perform them one by one, waiting for the user to prompt the next step.
    3. SEARCH BEFORE GUESSING: If a user asks about previously stored data, you MUST use 'ls' or 'read_file' before responding. Never guess file contents.
    4. CONTEXT MANAGEMENT: To avoid token limit errors (10k TPM), be concise in your responses. If a tool output is too large, summarize it immediately.
    5. NO HALLUCINATIONS: Never invent tool names or assume a file exists without checking the VFS.

    ────────────────────────────────
    SUB-AGENT DELEGATION RULES:
    - RESEARCH: Use 'research_task' for market lookups, competitor analysis, or gathering new data.
    - SUMMARIZATION: Use 'summarization_task' for condensing long reports, file contents, or research notes.
    - ALWAYS pass the 'config' parameter when calling sub-agents to ensure LangSmith tracing visibility.

    ────────────────────────────────
    TODO MANAGEMENT RULES (STRICT):
    - CREATE: If creating a new list, use write_file (filename: todos_<category>.txt). 
      Response: "Todo saved successfully to <filename>"
    - UPDATE: read_file -> modify internally -> edit_file. 
      Response: "Todo updated successfully"
    - VIEW: Use read_file only. Do not call write/edit.

    ────────────────────────────────
    CHAINING PROTOCOL (Example):
    User: "Research coffee risks and save a summary."
    Turn 1: Call research_task.
    User: (System Result)
    Turn 2: Call summarization_task.
    User: (System Result)
    Turn 3: Call write_file.
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

        
    #Summarization Sub-Agent
    @tool
    def summarize_file(filename: str, config: RunnableConfig) -> str: # 1. Accept parent config
        """
        Summarize a file and store the summary.
        """
        content = read_file(filename)
        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # 2. Pass 'input' key to match your ChatPromptTemplate("{input}")
        # 3. Pass the 'config' directly to link the trace to the Supervisor
        result = summarization_agent.invoke(
            {"input": content}, 
            config=config 
        )

        # 4. Extract content (result is a BaseMessage from the Groq client)
        summary = result.content 
        
        summary_file = filename.replace(".txt", "_summary.txt")
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
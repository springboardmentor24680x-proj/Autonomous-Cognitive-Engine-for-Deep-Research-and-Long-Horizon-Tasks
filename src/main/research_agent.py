import os
import datetime
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import re
import io
from src.tools.web_search import web_search
# 1. Load environment variables IMMEDIATELY so sub-agents can see the API key
load_dotenv()

from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
# VFS tools
from src.memory.vfs import write_file, read_file, ls, edit_file,clear_vfs,delete_file,VFS

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

    TODO MANAGEMENT (STRICT - TOOL ONLY):

    - If the user asks to create or add a WORK todo:
    → You MUST call create_work_todo
    → You MUST NOT explain or summarize
    → You MUST NOT call write_file directly
    → The task text must be passed exactly

    - After create_work_todo succeeds:
    → Respond ONLY with confirmation

    SUB-AGENT RULES:
    - Use research_task for any market, competitor, or risk research.
    - Use summarization_task for any summarization or document combining.
    - Always pass config when invoking sub-agents.

    SUMMARIZATION FLOW (MANDATORY):
    - read_file all required files
    - call summarization_task on combined text
    - write_file to save output

    STRICT EXECUTION PROTOCOL:
    - You are a Manager. Managers do not do work; they DELEGATE.
    - NEVER respond with "Done", "I've summarized it", or "Task complete" unless you have JUST received a successful result from a tool.
    - If a user asks to summarize a file, your ONLY valid response is a call to 'summarize_file'.
    - Providing a text response instead of a tool call is a CRITICAL FAILURE.
    
    - VISUALIZATION: If the user mentions "trends", "shares", "comparison", or "graph", 
      first call 'research_task', then call 'create_market_share_chart' using the research file as source.
      
      VISUALIZATION FEEDBACK: When you create a chart, inform the user that it is now visible in the 'Virtual Files' sidebar. Do not offer to 'show' the image in the chat, as it is already displayed in the UI

      WEB RESEARCH PROTOCOL:
    - For any query requiring current events (2024-2025), pricing, or market shares, 
      always use 'research_task' which now has live web access via Tavily.
    - If the user asks a direct question about a recent event, you may use 'web_search' directly.

    Failure to use a tool when an action is requested is a system violation.
    """


    tool_free_client = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="moonshotai/kimi-k2-instruct-0905",
        temperature=0.3
    )

    # Build research sub-agent
    # research_agent = build_research_agent(tool_free_client)
    research_agent = build_research_agent(tool_free_client, tools=[web_search])
    #Build summarize sub_agent
    summarization_agent = build_summarization_agent(tool_free_client)

    # TASK DELEGATION TOOL
    @tool
    def research_task(description: str, config: RunnableConfig) -> str:

        """Perform research and store results. Returns a BRIEF summary to keep context small."""

        print("\n--- DEBUG: Research sub-agent invoked ---")
        print(f"--- Topic: {description} ---")

        result = research_agent.invoke(
            {"messages": [{"role": "user", "content": description}]},
            config=config
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

        #Condensed version for the Supervisor's chat history
        summary_text = (research_output[:500] + "...") if len(research_output) > 500 else research_output
        return f"Research completed. Highlights: {summary_text} [Full data saved to research_notes.txt]"        
    
    @tool
    def summarization_task(text: str, config: RunnableConfig) -> str: 
        
        """Summarize text using the summarization sub-agent."""
        # Use the sub-agent directly
        result = summarization_agent.invoke(
            {"input": text},
            config=config
        )
        # Handle both String and Message return types
        return result if isinstance(result, str) else result.content

    @tool
    def summarize_file(filename: str, config: RunnableConfig) -> str:
        """Read a file, delegate summarization, and save result."""
        print(f"\n--- DEBUG: summarize_file called for {filename} ---")
        clean_filename = filename.lstrip('/')
        content = read_file(clean_filename)
        
        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # FIX: Call the logic directly or ensure result is a string
        # If you call summarization_task.invoke(), LangChain might wrap the output
        summary = summarization_agent.invoke(
            {"input": content},
            config=config
        )
        
        summary_text = summary if isinstance(summary, str) else summary.content

        summary_file = clean_filename.replace(".txt", "_summary.txt")
        write_file(summary_file, summary_text)

        return f"Summary saved successfully to {summary_file}"

    @tool
    def create_work_todo(task_text: str) -> str:
        """
        Creates or appends a task to the work todo list (todos_work.txt).
        Use this ONLY for work-related tasks.
        """
        filename = "todos_work.txt"
        existing_content = read_file(filename)
        
        # Check if file exists or is empty
        if isinstance(existing_content, str) and "not found" in existing_content:
            write_file(filename, f"WORK TODO LIST:\n- {task_text}")
        else:
            edit_file(filename, f"{existing_content}\n- {task_text}")
            
        return f"Successfully added '{task_text}' to {filename}"
    
    @tool
    def create_market_share_chart(source_file: str) -> str:
        """
        Parses a research file specifically for the 'DATA FOR GRAPHING' section
        to avoid plotting timestamps and metadata.
        """
        content = read_file(source_file)
        
        # 1. ONLY extract data from the designated block
        if "DATA FOR GRAPHING" in content:
            relevant_text = content.split("DATA FOR GRAPHING")[-1]
        elif "DATA BLOCK" in content:
            relevant_text = content.split("DATA BLOCK")[-1]
        else:
            relevant_text = content

        # 2. Extract Label: Value pairs
        matches = re.findall(r"([a-zA-Z\s]+):\s*(\d+(?:\.\d+)?)", relevant_text)
        
        if not matches:
            return "No valid data found in the Graphing section."

        labels = [m[0].strip() for m in matches]
        values = [float(m[1]) for m in matches]

        # 3. Create a Bar Chart (Much cleaner for brand names than a Pie Chart)
        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, values, color='skyblue')
        
        # Add values on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{int(yval)}', ha='center', va='bottom')

        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Store Count / Share')
        plt.title(f"Market Analysis: {source_file.lstrip('/')}")
        plt.tight_layout() # This ensures names like 'Third Wave Coffee' don't get cut off

        # 4. Save to VFS
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        clean_output_name = source_file.replace(".txt", "_chart.png").lstrip('/')
        VFS[clean_output_name] = buf.getvalue() 
        
        return f"SUCCESS: Clean chart saved to VFS as {clean_output_name}"

    # Create main agent
    agent = create_deep_agent(
        tools=[
            web_search,
            write_file,
            read_file,
            ls,
            edit_file,
            delete_file,
            add_event,
            list_events,
            delete_event,
            research_task, 
            summarization_task,
            summarize_file,
            create_work_todo,
            create_market_share_chart
        ],
        system_prompt=system_prompt,
        model=groq_client,
    )

    class AgentWrapper:
        def __init__(self, agent):
            self.agent = agent

        def invoke(self, input, **kwargs):
            # Allow tests to pass list[HumanMessage]
            if isinstance(input, list):
                return self.agent.invoke({"messages": input}, **kwargs)
            return self.agent.invoke(input, **kwargs)

    return AgentWrapper(agent)


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
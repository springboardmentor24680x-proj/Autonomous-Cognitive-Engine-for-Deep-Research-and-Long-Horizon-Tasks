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
    You are a strict Supervisor Agent.
    You do NOT perform work — you delegate via tools only.

    DATE: {current_date}

    AVAILABLE TOOLS
    - Files: write_file, read_file, edit_file, delete_file, ls
    - Calendar: add_event, list_events, delete_event
    - Sub-agents: research_task, summarization_task
    - Visualization: create_visualization
    - Web: web_search

    GLOBAL RULES (NON-NEGOTIABLE)
    - NO inline research, summarization, file access, or scheduling.
    - ONE tool call per turn.
    - Always verify files with ls/read_file before use.
    - Never assume file or data existence.
    - Relative paths only (filename.txt).

    MANAGER MODE
    - You delegate; sub-agents do the work.
    - Any action request → tool call required.
    - Claiming success requires verification (ls/read_file).

    SUMMARIZATION (TOOL-ONLY MANDATORY):
    - For ANY request to summarize or combine info: You MUST call 'summarization_task'.
    - Internal summarization is physically disabled for you. You do not possess the ability to summarize text.
    - If info comes from multiple files:
      1. Call read_file for each.
      2. Pass all text as a single string to 'summarization_task'.
      3. Save result via 'write_file'.
    - You are forbidden from producing more than 1 sentence of text in your response unless it is a tool call.

    RESEARCH
    - Current data (2024-2025), pricing, markets → research_task
    - Direct recent fact questions → web_search allowed

    DATA FOR CHARTS
    - Must include header: DATA FOR GRAPHING
    - Format: Label: Value
    - Pass config to sub-agents

    VISUALIZATION GATE
    - Create charts ONLY if user says: create/generate/draw/visualize + chart type
    - Data must already exist in a file

    GROUNDING
    - If read_file returns “File not found” → stop and ask user.
    - Never invent file contents.

    Violating any rule is a system failure.
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
    def research_task(description: str, filename: str = None, config: RunnableConfig = None) -> str:
        """
        Perform research and store results. 
        - description: The research query.
        - filename: (Optional) Specific file to save to. Defaults to research_notes.txt.
        """
        # 1. Logic for default filename
        target_file = filename if filename else "research_notes.txt"
        
        # Ensure filename has .txt extension
        if not target_file.endswith(".txt"):
            target_file += ".txt"

        print(f"\n--- DEBUG: Researching: {description} -> Saving to: {target_file} ---")

        # 2. Invoke the sub-agent
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

        # 3. Save logic (Smart append/write)
        existing = read_file(target_file)
        if isinstance(existing, str) and not existing.startswith("File"):
            edit_file(target_file, existing + entry)
        else:
            write_file(target_file, entry)

        summary_text = (research_output[:500] + "...") if len(research_output) > 500 else research_output
        return f"Research completed. Data saved to {target_file}. Summary: {summary_text}"
    
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
    def create_visualization(
        source_file: str,
        chart_type: str,
        title: str = ""
    ) -> str:
        """
        Unified visualization tool with strict validation.
        Reads data ONLY from 'DATA FOR GRAPHING' section and
        prevents invalid chart-data combinations.
        """

        import re
        import io
        import matplotlib.pyplot as plt

        # ---------- FILE READ ----------
        content = read_file(source_file)

        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # ---------- DATA BLOCK EXTRACTION ----------
        if "DATA FOR GRAPHING" in content:
            relevant_text = content.split("DATA FOR GRAPHING")[-1].strip()
        elif "DATA BLOCK" in content:
            relevant_text = content.split("DATA BLOCK")[-1].strip()
        else:
            return (
                "Visualization failed: No 'DATA FOR GRAPHING' section found. "
                "Ensure the research output includes a dedicated graphing block."
            )

        if not relevant_text:
            return "Visualization failed: Graphing data section is empty."

        chart_type = chart_type.lower()

        # ---------- LINE / AREA ----------
        if chart_type in {"line", "area"}:
            matches = re.findall(r"(\d{4})\s*:\s*(\d+(?:\.\d+)?)", relevant_text)

            if not matches:
                return (
                    "Invalid data for line/area chart. "
                    "Expected format: Year: Value (e.g., 2023: 120)"
                )

            x = [int(m[0]) for m in matches]
            y = [float(m[1]) for m in matches]
            x, y = zip(*sorted(zip(x, y)))

            plt.figure(figsize=(10, 6))
            if chart_type == "line":
                plt.plot(x, y, marker="o", linewidth=2)
            else:
                plt.fill_between(x, y, alpha=0.6)

            plt.xlabel("Year")
            plt.ylabel("Value")

        # ---------- BAR / HORIZONTAL BAR / PIE ----------
        elif chart_type in {"bar", "horizontal_bar", "pie"}:
            matches = re.findall(r"([a-zA-Z\s]+):\s*(\d+(?:\.\d+)?)", relevant_text)

            if not matches:
                return (
                    "Invalid data for bar/pie chart. "
                    "Expected format: Label: Value (e.g., Online: 40)"
                )

            labels = [m[0].strip() for m in matches]
            values = [float(m[1]) for m in matches]

            plt.figure(figsize=(10, 6))

            if chart_type == "bar":
                plt.bar(labels, values)
                plt.xticks(rotation=45, ha="right")

            elif chart_type == "horizontal_bar":
                plt.barh(labels, values)

            else:  # pie
                plt.pie(values, labels=labels, autopct="%1.1f%%")

            plt.ylabel("Value")

        # ---------- SCATTER ----------
        elif chart_type == "scatter":
            # Guard against categorical data misuse
            if ":" in relevant_text:
                return (
                    "Invalid chart choice: Scatter plots require numeric X,Y pairs. "
                    "Use 'pie' or 'bar' for category-value data."
                )

            matches = re.findall(r"([\d\.]+)\s*,\s*([\d\.]+)", relevant_text)

            if not matches:
                return (
                    "Invalid data for scatter plot. "
                    "Expected format: X, Y (numeric pairs)."
                )

            x = [float(m[0]) for m in matches]
            y = [float(m[1]) for m in matches]

            plt.figure(figsize=(8, 6))
            plt.scatter(x, y)
            plt.xlabel("X")
            plt.ylabel("Y")

        # ---------- UNSUPPORTED ----------
        else:
            return (
                f"Unsupported chart type: '{chart_type}'. "
                "Supported types: line, area, bar, horizontal_bar, pie, scatter."
            )

        # ---------- FINALIZE ----------
        final_title = title if title else f"{chart_type.title()} Visualization"
        plt.title(final_title)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()

        output_name = source_file.replace(".txt", f"_{chart_type}.png").lstrip("/")
        VFS[output_name] = buf.getvalue()

        return f"SUCCESS: {chart_type} chart saved to VFS as {output_name}"


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
            create_visualization
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
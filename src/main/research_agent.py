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
   You are a STRICT SUPERVISOR AGENT.
    CORE RULE:
    For EVERY user request, ALWAYS create a TODO list using the built-in todo system.
    Return TODOS only. Never return normal text.
    
    You DO NOT perform research, summarization, visualization, file edits, or scheduling yourself.
    You ONLY delegate work via tools.

    DATE: {current_date}

    ────────────────────────
    AVAILABLE TOOLS
    ────────────────────────
    FILES:
    - write_file
    - read_file
    - edit_file
    - delete_file
    - ls

    CALENDAR:
    - add_event
    - list_events
    - delete_event

    SUB-AGENTS:
    - research_task
    - summarization_task

    VISUALIZATION:
    - create_visualization

    WEB:
    - web_search

    ────────────────────────
    GLOBAL EXECUTION RULES (NON-NEGOTIABLE)
    ────────────────────────
    1. NEVER call 'create_visualization' unless the user EXPLICITLY names a chart type (e.g., bar, pie) and uses a verb like 'create'.
    2. ONE TOOL CALL PER TURN — NO EXCEPTIONS.
    3. You MUST NEVER call multiple tools in the same response.
    4. You MUST NEVER perform inline reasoning, research, or summarization.
    5. Every action (read, write, summarize, visualize, schedule) REQUIRES a tool call.
    6. Never assume files, data, or events exist — always verify with ls or read_file.
    7. Relative filenames only (example: report.txt).

    ────────────────────────
    PLANNING VS EXECUTION
    ────────────────────────
    • If a request requires multiple steps:
    - Execute ONLY the NEXT logical step.
    - Wait for the user or next turn to continue.

    • You are NOT allowed to batch actions in a single turn.

    ────────────────────────
    RESEARCH RULES
    ────────────────────────
    • Market data, competitors, pricing, trends → research_task
    • research_task is the ONLY way to generate factual content.
    • research_task MUST save results to a file.
    ────────────────────
    SUMMARIZATION PROTOCOL (CRITICAL)
    ────────────────────────
    - You are FORBIDDEN from generating summary text yourself.
    - If a user asks to summarize, combine, or condense:
      1. First, call 'read_file' to retrieve the content.
      2. In the NEXT turn, call 'summarization_task' with that content.
      3. In the FINAL turn, call 'write_file' to save it.
    - If you provide a summary in natural language without calling 'summarization_task', it is a SYSTEM FAILURE.

    ────────────────────────
    VISUALIZATION RULES
    ────────────────────────
    • Only create charts if the user explicitly asks.
    • Chart data MUST already exist in a file.
    • File MUST contain a "DATA FOR GRAPHING" section.
    • Invalid data → stop and ask user.

    ────────────────────────
    GROUNDING & SAFETY
    ────────────────────────
    • If read_file returns "File not found" → STOP and ask the user.
    • Never invent file contents.
    • Never invent calendar events.
    • Never claim success without verification.

    COMMIT RULE (MANDATORY):
    - If a request requires a state change (file write/edit/delete, calendar change),
    you MUST call the corresponding tool.
    - You are FORBIDDEN from claiming success in text unless a tool was executed.
    - No “created successfully” messages without a tool call.

    If a request implies writing a file → write_file OR edit_file MUST be called.

    MULTI-FILE RULE:
    - If a request requires reading multiple files,
    STOP after reading ONE file and wait for the next turn.
    - Never attempt to simulate multiple reads.

    ────────────────────────
    DATA STRUCTURE RULES (FIX)
    ────────────────────────
    • BAR/PIE CHARTS: Use 'Label: Value' (e.g., Strategy: 10).
    • SCATTER CHARTS: Use 'X, Y' numeric pairs ONLY. (e.g., 7, 9). 
    • WARNING: Do not include any text, hashtags, or descriptions inside the 'DATA FOR GRAPHING' block, or the visualization tool will fail.
    ────────────────────────
    RESPONSE FORMAT
    ────────────────────────
    • If calling a tool → ONLY return the tool call.
    • If no tool is required → respond in ONE short sentence.
    • Errors must be explicit and actionable.

    Violating ANY rule is a SYSTEM FAILURE.

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
    def summarization_task(text: str, config: RunnableConfig = None) -> str: 
        """
        Summarize a block of text. 
        Use this tool whenever a summary, condensation, or combination of text is required.
        """
        # The agent often forgets to pass config, so we make it optional in the signature
        result = summarization_agent.invoke(
            {"input": text},
            config=config
        )
        return result if isinstance(result, str) else result.content

    @tool
    def summarize_file(filename: str, config: RunnableConfig = None) -> str:
        """
        Automatic workflow: Reads a specific file, delegates to the summarization sub-agent, 
        and saves the output to a new file.
        """
        clean_filename = filename.lstrip('/')
        content = read_file(clean_filename)
        
        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # Directly use the logic to ensure trace visibility
        summary_result = summarization_agent.invoke(
            {"input": content},
            config=config
        )
        
        summary = summary_result if isinstance(summary_result, str) else summary_result.content
        summary_file = clean_filename.replace(".txt", "_summary.txt")
        write_file(summary_file, summary)

        return f"SUCCESS: Summary of {clean_filename} saved to {summary_file}"

    @tool
    def create_work_todo(task_text: str, status: str = "PENDING") -> str:
        """
        Creates or updates todos.
        status = PENDING | COMPLETED
        """

        filename = "todos_work.txt"
        existing = read_file(filename)

        if status == "PENDING":
            content = existing if isinstance(existing, str) and not existing.startswith("File") else "WORK TODO LIST\n\n"
            content += f"- {task_text} [PENDING]\n"
            write_file(filename, content)
            return "Todo created (PENDING)."

        if status == "COMPLETED":
            if isinstance(existing, str):
                updated = existing.replace("[PENDING]", "[COMPLETED]")
                write_file(filename, updated)
                return "Todos marked COMPLETED."

            return "Todo update skipped."

    @tool
    def create_visualization(
        source_file: str,
        chart_type: str,
        title: str = ""
    ) -> str:
        """
        Enhanced visualization tool with robust data parsing.
        Cleans data blocks and extracts numeric values even if extra text or hashtags are present.
        """
        import re
        import io
        import matplotlib.pyplot as plt

        # ---------- FILE READ ----------
        content = read_file(source_file)

        if isinstance(content, str) and content.startswith("File"):
            return f"Error: {content}"

        # ---------- DATA BLOCK EXTRACTION ----------
        # Try multiple common headers
        data_headers = ["DATA FOR GRAPHING", "DATA BLOCK", "GRAPH DATA"]
        relevant_text = ""
        for header in data_headers:
            if header in content:
                relevant_text = content.split(header)[-1].strip()
                # Stop if we find a common footer or separator
                relevant_text = re.split(r"END DATA|END GRAPHING|#|---", relevant_text)[0].strip()
                break

        if not relevant_text:
            return "Visualization failed: No valid data block found in file."

        chart_type = chart_type.lower()
        plt.figure(figsize=(10, 6))

        try:
            # ---------- SCATTER (Numeric Pairs) ----------
            if chart_type == "scatter":
                # Logic: Split into lines and find any two numbers on each line.
                # This ignores labels like "Priority 1" or hashtags.
                lines = [l for l in relevant_text.split('\n') if l.strip()]
                x, y = [], []
                for line in lines:
                    nums = re.findall(r"(\d+(?:\.\d+)?)", line)
                    if len(nums) >= 2:
                        x.append(float(nums[0]))
                        y.append(float(nums[1]))
                
                if not x:
                    return "Invalid data for scatter: No numeric pairs found (e.g., 7, 9)."
                
                plt.scatter(x, y, s=120, alpha=0.7, edgecolors='k', color='royalblue')
                plt.xlabel("X Axis")
                plt.ylabel("Y Axis")

            # ---------- BAR / PIE / HORIZONTAL BAR (Categorical) ----------
            elif chart_type in {"bar", "horizontal_bar", "pie"}:
                # Logic: Find 'Category: Number' even with bullet points or dashes
                matches = re.findall(r"([a-zA-Z\s\d]+):\s*(\d+(?:\.\d+)?)", relevant_text)
                if not matches:
                    return "Invalid data for bar/pie: Expected 'Label: Value' pairs."
                
                labels = [m[0].strip().replace("- ", "").replace("* ", "") for m in matches]
                values = [float(m[1]) for m in matches]

                if chart_type == "bar":
                    plt.bar(labels, values, color='skyblue')
                    plt.xticks(rotation=45, ha="right")
                elif chart_type == "horizontal_bar":
                    plt.barh(labels, values, color='lightgreen')
                else: # pie
                    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)

            # ---------- LINE / AREA (Time/Series) ----------
            elif chart_type in {"line", "area"}:
                matches = re.findall(r"(\d+(?:\.\d+)?)\s*[:,\s]\s*(\d+(?:\.\d+)?)", relevant_text)
                if not matches:
                    return "Invalid data for line/area chart."
                
                x = [float(m[0]) for m in matches]
                y = [float(m[1]) for m in matches]
                # Sort by X to ensure lines don't zig-zag
                x, y = zip(*sorted(zip(x, y)))

                if chart_type == "line":
                    plt.plot(x, y, marker='o', linewidth=2, color='coral')
                else:
                    plt.fill_between(x, y, alpha=0.4, color='teal')
                    plt.plot(x, y, marker='.', alpha=0.8)

            else:
                plt.close()
                return f"Unsupported chart type: {chart_type}"

            # ---------- FINALIZE ----------
            final_title = title if title else f"{chart_type.replace('_', ' ').title()} Analysis"
            plt.title(final_title, fontsize=14, pad=20)
            plt.grid(True, linestyle='--', alpha=0.6) if chart_type != "pie" else None
            plt.tight_layout()

            # Save to VFS
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close()

            output_name = source_file.replace(".txt", f"_{chart_type}.png").lstrip("/")
            VFS[output_name] = buf.getvalue()

            return f"SUCCESS: {chart_type} chart saved as {output_name}"

        except Exception as e:
            plt.close()
            return f"Visualization logic error: {str(e)}"

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

        def invoke(self, input_messages, **kwargs):
            user_text = input_messages[-1].content.lower()
            
            # Logic Gate: Is a chart actually requested?
            trigger_verbs = ["create", "generate", "draw", "visualize"]
            chart_types = ["bar", "pie", "line", "scatter", "area"]
            is_requested = any(v in user_text for v in trigger_verbs) and any(c in user_text for c in chart_types)

            # If not requested, we tell the agent the tool is currently locked
            if not is_requested and "create_visualization" in user_text:
                return {"messages": [HumanMessage(content="System: Visualization tool is locked unless explicitly requested with chart type.")]}

            return self.agent.invoke({"messages": input_messages}, **kwargs)

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


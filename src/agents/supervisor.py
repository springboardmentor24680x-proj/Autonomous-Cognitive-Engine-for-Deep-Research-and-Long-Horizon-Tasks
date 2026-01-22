# supervisor.py

import os
from datetime import datetime

from planner import run as planner_run
from analyzer import run as analyzer_run
from summarizer import run as summarizer_run


MEMORY_DIR = "memory"
PLAN_FILE = os.path.join(MEMORY_DIR, "plan.txt")
RESULTS_FILE = os.path.join(MEMORY_DIR, "results.txt")


def save_to_memory(filename: str, content: str):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def append_to_memory(filename: str, content: str):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(filename, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")


def read_from_memory(filename: str) -> str:
    if not os.path.exists(filename):
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def supervisor(task: str) -> str:
    """
    Deep Agent (Orchestrator / Supervisor)
    Implements the exact flow from the diagram.
    """

    print("=== [1] User submitted complex task ===")
    print(task)

    # -------------------------------------------------
    # [2] Create plan (Planning Tool)
    # -------------------------------------------------
    print("\n=== [2] Calling Planning Tool ===")
    plan = planner_run(task)

    print("\n=== [3] Returned Task Plan ===")
    print(plan)

    # -------------------------------------------------
    # [4] Save plan to filesystem (memory)
    # -------------------------------------------------
    print("\n=== [4] Saving plan to memory ===")
    save_to_memory(PLAN_FILE, plan)

    print("Plan stored in:", PLAN_FILE)

    # -------------------------------------------------
    # [5] Loop over each subtask
    # -------------------------------------------------
    steps = [s.strip() for s in plan.split("\n") if s.strip()]

    # Clear old results
    save_to_memory(RESULTS_FILE, "")

    for idx, step in enumerate(steps, start=1):
        print(f"\n=== [6] Launch sub-agent for subtask {idx} ===")
        print("Subtask:", step)

        lower_step = step.lower()

        # -------------------------------------------------
        # [7] Sub-agent performs reasoning + tool calls
        # -------------------------------------------------
        if "summar" in lower_step:
            print("Using Summarizer Agent")
            result = summarizer_run(step)
            agent_used = "Summarizer Agent"

        elif "analy" in lower_step or "analyze" in lower_step:
            print("Using Analyzer Agent")
            result = analyzer_run(step)
            agent_used = "Analyzer Agent"

        else:
            # Default reasoning agent
            print("Using Analyzer Agent (default)")
            result = analyzer_run(step)
            agent_used = "Analyzer Agent (default)"

        print("\n--- Tool Result ---")
        print(result)

        # -------------------------------------------------
        # [9] Write results to memory (filesystem)
        # -------------------------------------------------
        timestamp = datetime.now().isoformat()
        memory_block = (
            f"Step {idx}: {step}\n"
            f"Agent: {agent_used}\n"
            f"Time: {timestamp}\n"
            f"Result:\n{result}\n"
            f"{'-'*50}"
        )

        append_to_memory(RESULTS_FILE, memory_block)

        print("Result written to memory.")

        # -------------------------------------------------
        # [10] Acknowledged (implicit)
        # -------------------------------------------------
        print("Acknowledged by filesystem.")

        # -------------------------------------------------
        # [11] Return subtask results to supervisor (implicit)
        # -------------------------------------------------

    # -------------------------------------------------
    # [12] Read stored context from memory
    # -------------------------------------------------
    print("\n=== [12] Reading stored context from memory ===")
    all_results = read_from_memory(RESULTS_FILE)

    # -------------------------------------------------
    # [13] Provide context to orchestrator
    # -------------------------------------------------
    print("\n=== [13] Providing context to orchestrator ===")

    # -------------------------------------------------
    # [14] Compose final response from memory & results
    # -------------------------------------------------
    print("\n=== [14] Composing final response ===")

    final_prompt = (
        "Using the following execution results, produce a clear final response:\n\n"
        f"{all_results}"
    )

    final_output = summarizer_run(final_prompt)

    return final_output


if __name__ == "__main__":
    user_task = input("Enter complex task: ")
    final_answer = supervisor(user_task)

    print("\n========== FINAL RESPONSE TO USER ==========\n")
    print(final_answer)

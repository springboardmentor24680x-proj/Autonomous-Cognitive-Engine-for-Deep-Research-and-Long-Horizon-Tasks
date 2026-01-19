import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
# This enables GROQ_API_KEY and LANGSMITH_TRACING
load_dotenv()

# Ensure the root directory is in the python path for modular imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph.state_graph import create_graph

# --- 1. CONFIGURATION CHECK ---
def check_environment():
    """Verify that essential API keys are present before starting."""
    required_keys = ["GROQ_API_KEY"]
    missing = [key for key in required_keys if not os.getenv(key)]
    
    if missing:
        print(f"CRITICAL ERROR: Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        return False
    
    if os.getenv("LANGSMITH_TRACING") == "true":
        print("LangSmith Tracing: ENABLED")
    return True

# --- 2. GRAPH INITIALIZATION ---
# We initialize the graph here so it can be imported by app.py
# or the Jupyter notebooks.
if check_environment():
    # create_graph() builds the LangGraph workflow with Supervisor, 
    # Sub-Agents, and the Virtual File System (VFS).
    graph = create_graph()
else:
    graph = None

# --- 3. CLI EXECUTION (Optional) ---
if __name__ == "__main__":
    """
    If you run 'python main.py' directly, it performs a system check.
    To start the UI, run 'streamlit run app.py'.
    """
    if graph:
        print("\n[✔] Autonomous Agent Graph Compiled Successfully.")
        print("[✔] Modular structure detected (src.agents, src.tools, src.memory).")
        print("\nTo launch the dashboard, run:")
        print(">>> streamlit run app.py")
    else:
        print("\n[✘] Graph initialization failed. Check your .env configuration.")
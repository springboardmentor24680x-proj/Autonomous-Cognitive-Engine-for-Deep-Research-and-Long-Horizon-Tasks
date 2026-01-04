import sys
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Ensure project root is in Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS
from src.main.supervisor_agent import setup_agent

# Streamlit page configuration
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")

@st.cache_resource
def load_agent():
    """
    Initializes and caches the supervisor agent.
    """
    return setup_agent()

# Load agent once
agent = load_agent()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header(" Virtual File System")

    # Display stored memory files
    if not VFS:
        st.info("No files stored.")
    else:
        for name, content in VFS.items():
            with st.expander(name):
                st.code(content)

    st.divider()
    st.header("Calendar Events")

    # Display scheduled calendar events
    if not EVENTS:
        st.info("No scheduled events.")
    else:
        for e in EVENTS:
            st.markdown(f"**{e['title']}**")
            st.caption(f"{e['date']} | {e['time']}")

# ---------------- CHAT UI ----------------
st.title(" Autonomous Cognitive Engine")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="I am an autonomous agent with memory and sub-agents.")
    ]

# Render chat messages
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Handle new user input
if user_input := st.chat_input("Enter a task..."):
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Run agent and show response
    with st.spinner("Thinking..."):
        result = agent.run(st.session_state.messages[-6:])  # Use recent context only
        reply = result["messages"][-1].content
        st.session_state.messages.append(AIMessage(content=reply))
        st.rerun()

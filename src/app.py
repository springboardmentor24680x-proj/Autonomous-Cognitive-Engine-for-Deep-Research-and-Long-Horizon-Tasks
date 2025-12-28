import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import traceable

from src.graph.state_graph import app          # compiled LangGraph
from src.graph.state import AgentState
from src.memory.vfs import VirtualFileSystem

# ----------------- Shared VFS -----------------
# IMPORTANT: must match the one used in graph
vfs = VirtualFileSystem()

# ----------------- Agent Runner -----------------
@traceable(name="chat_turn")
def run_agent(state: AgentState):
    return app.invoke(state)

# ----------------- Streamlit Page Config -----------------
st.set_page_config(
    page_title="LangGraph AI Chatbot",
    layout="wide"
)

st.title("LangGraph Multi-Agent Chatbot")

# ----------------- Initialize Session State -----------------
if "state" not in st.session_state:
    st.session_state.state = AgentState(
        messages=[],
        search_results=None,
        needs_web=None,
    )

if "displayed_ai" not in st.session_state:
    st.session_state.displayed_ai = []

if "vfs_files" not in st.session_state:
    st.session_state.vfs_files = vfs.ls()

# ----------------- Main Chat Display -----------------
for msg in st.session_state.state["messages"]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# ----------------- Sidebar: Virtual File System -----------------
with st.sidebar:
    st.title("Virtual File System")

    if st.button("Refresh Files"):
        st.session_state.vfs_files = vfs.ls()

    files = st.session_state.vfs_files
    if files:
        selected_file = st.selectbox("Files", files)
        if st.button("Read File"):
            content = vfs.read_file(selected_file)
            st.text_area("File Content", content, height=300)
    else:
        st.info("No files created yet.")

# ----------------- Chat Input -----------------
user_input = st.chat_input("Type your query here...")

if user_input:
    # Append user message
    st.session_state.state["messages"].append(
        HumanMessage(content=user_input)
    )

    st.chat_message("user").write(user_input)

    # Run agent
    st.session_state.state = run_agent(st.session_state.state)

    # Display only new AI messages
    for msg in st.session_state.state["messages"]:
        if isinstance(msg, AIMessage) and msg not in st.session_state.displayed_ai:
            st.chat_message("assistant").write(msg.content)

    # Track displayed AI messages
    st.session_state.displayed_ai = [
        m for m in st.session_state.state["messages"] if isinstance(m, AIMessage)
    ]

    # Refresh VFS
    st.session_state.vfs_files = vfs.ls()

    st.rerun()

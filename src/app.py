# src/app.py
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from core_app import create_initial_state, invoke_chat, vfs

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="LangGraph AI Chatbot",
    layout="wide"
)

st.title("LangGraph Multi-Agent Chatbot")

# ---------------- Session State ----------------
if "state" not in st.session_state:
    st.session_state.state = create_initial_state()

if "displayed_ai" not in st.session_state:
    st.session_state.displayed_ai = []

if "vfs_files" not in st.session_state:
    st.session_state.vfs_files = vfs.ls()

# ---------------- Display Chat ----------------
for msg in st.session_state.state["messages"]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# ---------------- Sidebar: VFS ----------------
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

# ---------------- Chat Input ----------------
user_input = st.chat_input("Type your query here...")

if user_input:
    st.chat_message("user").write(user_input)

    st.session_state.state = invoke_chat(
        st.session_state.state,
        user_input
    )

    for msg in st.session_state.state["messages"]:
        if isinstance(msg, AIMessage) and msg not in st.session_state.displayed_ai:
            st.chat_message("assistant").write(msg.content)

    st.session_state.displayed_ai = [
        m for m in st.session_state.state["messages"]
        if isinstance(m, AIMessage)
    ]

    st.session_state.vfs_files = vfs.ls()
    st.rerun()

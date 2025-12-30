import streamlit as st
from langchain.messages import AIMessage

# Import your existing agent functions
from Vfs_tools import run_agent  # make sure this path is correct

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="ChatAI", layout="centered")
st.title("ChatAI")
st.caption("Welcome to this chat!")

# -------------------------------
# Session State (INIT ONCE)
# -------------------------------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# IMPORTANT: prevents duplicate AI messages
if "last_ai_msg_id" not in st.session_state:
    st.session_state.last_ai_msg_id = None

# -------------------------------
# Sidebar Controls
# -------------------------------
with st.sidebar:
    if st.button("🧹 Clear chat"):
        st.session_state.chat_history = []
        st.session_state.agent_state = None
        st.session_state.last_ai_msg_id = None
        st.rerun()

# -------------------------------
# Input Box
# -------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Append user message ONCE
    st.session_state.chat_history.append(("user", user_input))

    # Run agent
    st.session_state.agent_state = run_agent(user_input, st.session_state.agent_state)

    # Get last AI message (ignore tool calls)
    for msg in reversed(st.session_state.agent_state["messages"]):
        if (
            isinstance(msg, AIMessage)
            and msg.content
            and not msg.tool_calls
            and msg.id != st.session_state.last_ai_msg_id
        ):
            ai_text = msg.content.strip()
            st.session_state.chat_history.append(("assistant", ai_text))
            st.session_state.last_ai_msg_id = msg.id
            break

# -------------------------------
# Chat Display (render AFTER messages appended)
# -------------------------------
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)

# -------------------------------
# UX polish
# -------------------------------
with st.spinner("Thinking..."):
    pass

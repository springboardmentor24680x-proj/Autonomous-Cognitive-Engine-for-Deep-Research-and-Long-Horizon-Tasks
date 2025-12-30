import streamlit as st
from agent import run_agent, initial_state

st.set_page_config("AI Multi-Agent Chatbot", layout="wide")
st.title("🤖 AI Multi-Agent Chatbot")

# ---- SESSION STATE ----
if "state" not in st.session_state:
    st.session_state.state = initial_state()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---- CHAT INPUT ----
user_input = st.chat_input("Ask something...")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.tasks.append(user_input)

    # Run agent
    st.session_state.state = run_agent(user_input, st.session_state.state)

    # Save assistant message
    st.session_state.chat_history.append(
        ("assistant", st.session_state.state["final_answer"])
    )

# ---- DISPLAY CHAT ----
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# ---- SIDEBAR ----
with st.sidebar:
    st.subheader("🕘 Previous Tasks")
    for i, task in enumerate(st.session_state.tasks, 1):
        st.write(f"{i}. {task}")

    st.divider()
    st.subheader("⚡ Current Task")
    st.write(st.session_state.state["current_task"] or "Waiting...")
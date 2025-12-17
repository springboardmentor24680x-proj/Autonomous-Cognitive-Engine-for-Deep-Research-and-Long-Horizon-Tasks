import streamlit as st
from agents.chat_agent import handle_message

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Chat Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Chat Agent")
st.caption("With VFS, TODO Planner & Calendar")

# ================= HOW TO USE (INTRO) =================
st.markdown("## 📘 How to Use This Assistant")

st.info("""
This assistant helps you **plan tasks**, **store information**, and **manage events**
using simple commands.

Follow the guide below before chatting 👇

---

## 📝 TODO Commands (Task Planning)
command for adding todo start with todo.plan

Use TODOs to break any task into clear steps.

**Create a TODO plan**

---
## 📅 calender Commands(Event Planning)

Add event in calender


command for adding event start with calendar.add <event title> | YYYY-MM-DD HH:MM this format

---
## 📂 VFS Commands (Virtual File System)

Use VFS to store and manage files inside the agent.

**List all files**

---

## 💬 Chat

After using TODO, Calendar, or VFS commands,
you can chat normally and ask questions.
""")

st.markdown("---")

# ================= SESSION STATE =================
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {}

if "chat_ui" not in st.session_state:
    st.session_state.chat_ui = []

# ================= CHAT UI =================
st.markdown("## 💬 Chat")

for msg in st.session_state.chat_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state.chat_ui.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call agent
    with st.spinner("Thinking..."):
        st.session_state.agent_state, reply = handle_message(
            st.session_state.agent_state,
            user_input
        )

    # Show agent reply
    st.session_state.chat_ui.append({
        "role": "assistant",
        "content": reply
    })
    with st.chat_message("assistant"):
        st.markdown(reply)

# ================= SIDEBAR =================
with st.sidebar:
    st.header("📂 Agent Memory")

    if st.button("📁 List Files"):
        files = st.session_state.agent_state.get("files", {})
        st.json(files if files else "No files yet")

    st.markdown("---")

    if st.button("📝 View TODOs"):
        todos = st.session_state.agent_state.get("files", {}).get(
            "todos.json", "No TODOs"
        )
        st.code(todos, language="json")

    st.markdown("---")

    if st.button("📅 View Calendar"):
        calendar = st.session_state.agent_state.get("files", {}).get(
            "calendar.json", "No events"
        )
        st.code(calendar, language="json")

    st.markdown("---")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_ui = []
        st.rerun()

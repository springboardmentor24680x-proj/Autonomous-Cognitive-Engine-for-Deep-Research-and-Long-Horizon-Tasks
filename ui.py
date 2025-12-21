import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import ONLY runtime objects from main
from main import app, SYSTEM_PROMPT, vfs

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(
    page_title="LangGraph AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 LangGraph Multi-Agent Chatbot")

# ------------------------------------------
# SESSION STATE INIT
# ------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [SystemMessage(content=SYSTEM_PROMPT)],
        "todos": [],
        "vfs": {}
    }

# ------------------------------------------
# DISPLAY CHAT HISTORY
# ------------------------------------------
for msg in st.session_state.state["messages"]:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# ------------------------------------------
# USER INPUT
# ------------------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.chat_message("user").write(user_input)

    # Add user message
    st.session_state.state["messages"].append(
        HumanMessage(content=user_input)
    )

    # Invoke LangGraph Supervisor
    st.session_state.state = app.invoke(st.session_state.state)

    # Display last AI message
    last_msg = st.session_state.state["messages"][-1]
    if isinstance(last_msg, AIMessage):
        st.chat_message("assistant").write(last_msg.content)

# ------------------------------------------
# SIDEBAR — VIRTUAL FILE SYSTEM
# ------------------------------------------
st.sidebar.title("📁 Virtual File System")

files = vfs.ls()
if files:
    selected_file = st.sidebar.selectbox("Files", files)

    if st.sidebar.button("Read File"):
        content = vfs.read_file(selected_file)
        st.sidebar.text_area(
            "File Content",
            content,
            height=300
        )
else:
    st.sidebar.info("No files created yet.")

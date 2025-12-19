import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# IMPORT FROM YOUR MAIN FILE
from main import app, AgentState, SYSTEM_PROMPT, vfs

# ------------------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------------------
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 LangGraph AI Chatbot")

# ------------------------------------------
# SESSION STATE INIT
# ------------------------------------------
if "state" not in st.session_state:
    st.session_state.state: AgentState = {
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

    # Add user message to state
    st.session_state.state["messages"].append(
        HumanMessage(content=user_input)
    )

    # Invoke LangGraph app
    st.session_state.state = app.invoke(st.session_state.state)

    # Get last AI message
    last_msg = st.session_state.state["messages"][-1]

    if isinstance(last_msg, AIMessage):
        st.chat_message("assistant").write(last_msg.content)

# ------------------------------------------
# SIDEBAR: VFS FILE VIEWER
# ------------------------------------------
st.sidebar.title("📁 Virtual File System")

files = vfs.ls()
if files:
    selected = st.sidebar.selectbox("Files", files)
    if st.sidebar.button("Read File"):
        content = vfs.read_file(selected)
        st.sidebar.text_area("File Content", content, height=300)
else:
    st.sidebar.write("No files yet.")

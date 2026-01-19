# app.py
import streamlit as st
from main import graph # This will now be found correctly
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from main import graph # Import the compiled LangGraph from your main logic file

# 1. Setup Environment and Tracing
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "autonomous-agent-ui"

st.set_page_config(page_title="Autonomous Agent Lab", layout="wide")

# 2. Initialize Session State
# We store the 'vfs' and 'todos' separately to display them in the sidebar
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vfs" not in st.session_state:
    st.session_state.vfs = {}
if "todos" not in st.session_state:
    st.session_state.todos = []

# 3. Sidebar for Agent "Memory" Visualization
with st.sidebar:
    st.header("📋 Project TODOs")
    if not st.session_state.todos:
        st.info("No tasks planned yet.")
    for todo in st.session_state.todos:
        status_icon = "✅" if todo["status"] == "completed" else "⏳"
        st.write(f"{status_icon} {todo['task']}")
    
    st.divider()
    st.header("📂 Virtual File System")
    if not st.session_state.vfs:
        st.info("No files saved yet.")
    for filename, content in st.session_state.vfs.items():
        with st.expander(f"📄 {filename}"):
            st.text(content)

# 4. Main Chat Interface
st.title("🤖 Deep Agent: Autonomous Researcher")

# Display historical messages
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Handle new user input
if prompt := st.chat_input("Enter your research goal..."):
    # Add user message to state
    new_user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(new_user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Execute LangGraph
    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning and executing tools..."):
            # We pass the current chat history, todos, and vfs into the graph
            inputs = {
                "messages": st.session_state.messages,
                "todos": st.session_state.todos,
                "vfs": st.session_state.vfs
            }
            
            # LangGraph execution (Traced automatically to LangSmith)
            final_state = graph.invoke(inputs)
            
            # Update Streamlit session state from Graph's final state
            st.session_state.messages = final_state["messages"]
            st.session_state.vfs = final_state.get("vfs", {})
            st.session_state.todos = final_state.get("todos", [])
            
            # Show the final reasoning output
            final_response = final_state["messages"][-1].content
            st.markdown(final_response)
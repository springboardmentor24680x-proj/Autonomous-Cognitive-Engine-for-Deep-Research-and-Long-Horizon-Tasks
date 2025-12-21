import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS
from src.main import research_agent as ra
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(page_title="Deep Agent UI", layout="wide")

# --------------------------------------------------
# Initialize Agent (Cached)
# --------------------------------------------------
@st.cache_resource
def load_agent():
    return ra.setup_agent()

agent = load_agent()

# --------------------------------------------------
# Sidebar: Live Agent Storage (VFS & Calendar)
# --------------------------------------------------
with st.sidebar:
    st.title("Agent State")
    
    # --- VFS Display ---
    st.header("Virtual Files")
    if not VFS:
        st.info("No files in memory.")
    else:
        for filename, content in VFS.items():
            with st.expander(f"{filename}"):
                st.code(content, language="text")

    st.divider()

    # --- Calendar Display ---
    st.header("Scheduled Events")
    if not EVENTS:
        st.info("No events found.")
    else:
        for i, event in enumerate(EVENTS):
            st.markdown(f"**{i}. {event['title']}**")
            st.caption(f"{event['date']} | {event['time']}")
            st.divider()

# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.title("Deep Agent: Todo & Calendar")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="Hello! I'm ready to manage your files and schedule.")
    ]

# Display Chat History
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# User Input
if user_input := st.chat_input("What should I do?"):
    # Add user message to UI
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Processing..."):
        try:
            # Run the agent
            result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
            ans = result["messages"][-1].content
            
            # Save and display AI response
            st.session_state.messages.append(AIMessage(content=ans))
            with st.chat_message("assistant"):
                st.markdown(ans)
            
            # Force refresh to show new files/events in the sidebar immediately
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS
from src.main import research_agent as ra
from src.main.research_agent import setup_agent
from src.logging_config import get_logger

logger = get_logger(__name__)
import io
import base64
from pathlib import Path

# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(page_title="Deep Agent UI", layout="wide")

# --------------------------------------------------
# Initialize Agent (Cached)
# --------------------------------------------------
@st.cache_resource
def load_agent():
    logger.info("load_agent: initializing agent (cached)")
    return ra.setup_agent()

agent = load_agent()

# --------------------------------------------------
# Sidebar: Live Agent Storage (VFS & Calendar)
# --------------------------------------------------
with st.sidebar:
    st.title("Agent State")

    # ---------------------------
    # Virtual File PREVIEW ONLY
    # ---------------------------
    st.header("Virtual File System")

    if not VFS:
        st.info("No files in memory.")
    else:
        for filename, content in VFS.items():
            if filename.endswith(".png"):
                st.image(content, caption=filename)
            else:
                with st.expander(f"{filename}"):
                    if isinstance(content, bytes):
                        st.warning("Binary file (preview not available)")
                    else:
                        st.code(str(content), language="text")

    st.divider()

    # ---------------------------
    # Calendar PREVIEW
    # ---------------------------
    st.header("Scheduled Events")
    if not EVENTS:
        st.info("No events found.")
    else:
        for i, event in enumerate(EVENTS):
            st.markdown(f"**{i+1}. {event['title']}**")
            st.caption(f"{event['date']} | {event['time']}")


# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.title("Autonomous Cognitive Agent – Planning, Memory & Tools")

# --- Download Center ---
with st.expander("Download Files & Images", expanded=False):
    st.subheader("Available Downloads (Click to Download)")
    if VFS:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Files:**")
            for filename, content in VFS.items():
                if not filename.endswith(".png"):
                    st.download_button(
                        label=f"File: {filename}",
                        data=content,
                        file_name=filename,
                        mime="text/plain",
                        key=f"download_center_file_{filename}"
                    )
        with col2:
            st.write("**Images:**")
            for filename, content in VFS.items():
                if filename.endswith(".png"):
                    st.download_button(
                        label=f"Image: {filename}",
                        data=content,
                        file_name=filename,
                        mime="image/png",
                        key=f"download_center_img_{filename}"
                    )
    else:
        st.info("No files available for download yet.")

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
    st.session_state.messages.append(HumanMessage(content=user_input))
    logger.info("User input received via Streamlit UI")

    with st.spinner("Processing..."):
        try:
            #  1. FORCE TODO CREATION FIRST
            # res=agent.agent.invoke({
            #     "messages": [
            #         HumanMessage(
            #             content=f"Create todo: {user_input}",
            #         )
            #     ]
            # })

            #  2. RUN ACTUAL AGENT LOGIC
            history = st.session_state.messages[-5:]
            logger.debug("Invoking agent with history length=%d", len(history))
            result = agent.invoke(history)

            ans = result["messages"][-1].content
            st.session_state.messages.append(AIMessage(content=ans))
            st.rerun()
            
        except Exception as e:
            logger.exception("Exception while processing user input")
            st.error(f"Error: {e}")

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS

#  LangGraph import (NEW)
from src.main.graph import build_graph


# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(page_title="Deep Agent UI", layout="wide")


# --------------------------------------------------
# Initialize LangGraph (Cached)
# --------------------------------------------------
@st.cache_resource
def load_graph():
    return build_graph()

graph = load_graph()


# --------------------------------------------------
# Sidebar: Live Agent Storage (VFS & Calendar)
# --------------------------------------------------
with st.sidebar:
    st.title("Agent State")

    # ---- Virtual Files ----
    st.header("Virtual Files")
    if not VFS:
        st.info("No files in memory.")
    else:
        for filename, content in VFS.items():
            if filename.endswith(".png"):
                st.image(content, caption=filename)
            else:
                with st.expander(f"📄 {filename}"):
                    st.code(content, language="text")

    st.divider()

    # ---- Calendar ----
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


# ---- Display Chat History ----
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)


# --------------------------------------------------
# User Input
# --------------------------------------------------
if user_input := st.chat_input("What should I do?"):
    st.session_state.messages.append(HumanMessage(content=user_input))

    with st.spinner("Processing..."):
        try:
            # 🔹 Trim history to avoid token explosion
            history = st.session_state.messages[-5:]

            # 🔹 LangGraph invocation
            result = graph.invoke(
                {"messages": history}
            )

            # 🔹 Extract final assistant message
            final_messages = result.get("messages", [])
            if final_messages:
                ans = final_messages[-1].content
            else:
                ans = "Done."

            st.session_state.messages.append(
                AIMessage(content=ans)
            )

            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

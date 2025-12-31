import sys
import os
from dotenv import load_dotenv
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.memory.vfs import append_file

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS
from src.main.research_agent import setup_agent

st.set_page_config(page_title="Deep Agent UI", layout="wide")

@st.cache_resource
def load_agent():
    return setup_agent()

agent = load_agent()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("Agent State")

    st.header("Virtual Files")
    if not VFS:
        st.info("No files in memory.")
    else:
        for name, content in VFS.items():
            with st.expander(name):
                st.code(content)

    st.divider()
    st.header("Scheduled Events")
    if not EVENTS:
        st.info("No events found.")
    else:
        for e in EVENTS:
            st.markdown(f"**{e['title']}**")
            st.caption(f"{e['date']} | {e['time']}")

# ---------------- Chat ----------------
st.title("Deep Agent: Todo & Calendar")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="Hello! I'm ready to manage your files and schedule.")
    ]

for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

if user_input := st.chat_input("What should I do?"):
    st.session_state.messages.append(HumanMessage(content=user_input))

    with st.spinner("Processing..."):
        result = agent.invoke(st.session_state.messages[-5:])
        ans = result["messages"][-1].content
        st.session_state.messages.append(AIMessage(content=ans))
        st.rerun()

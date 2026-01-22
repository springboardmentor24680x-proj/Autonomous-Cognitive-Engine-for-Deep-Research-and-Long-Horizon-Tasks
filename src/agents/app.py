import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from vfs import VirtualFileSystem
from router import route

st.set_page_config(layout="wide")
st.title(" Multi-Agent Cognitive Engine")

# ---- SESSION STATE INIT ----
if "vfs" not in st.session_state:
    st.session_state.vfs = VirtualFileSystem()

if "chat" not in st.session_state:
    st.session_state.chat = []

vfs = st.session_state.vfs

# ---- SINGLE CHAT INPUT (ONLY ONE) ----
prompt = st.chat_input(
    "Ask me to summarize, analyze, or plan...",
    key="main_chat_input"
)

# ---- HANDLE USER INPUT ----
if prompt:
    agent, response = route(prompt)

    vfs.save(agent, prompt, response)

    st.session_state.chat.append(("user", prompt))
    st.session_state.chat.append(("assistant", response))

# ---- DISPLAY CHAT HISTORY ----
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.write(msg)

# ---- SIDEBAR MEMORY VIEW ----
st.sidebar.title(" Agent Memory (VFS)")
files = vfs.list_files()

if not files:
    st.sidebar.write("No memory yet")
else:
    for f in files:
        st.sidebar.write(f)

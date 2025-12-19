import streamlit as st
from agent import run_turn

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Cognibot",
    layout="wide"
)

# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown("""
<style>
body { background-color: #0e0e0e; }
.sidebar { background-color: #111; }
.thread {
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
}
.thread:hover {
    background-color: #1f1f1f;
}
.user {
    background: #2b5876;
    color: white;
    padding: 12px;
    border-radius: 14px;
    margin-bottom: 8px;
}
.assistant {
    background: #1c1c1c;
    color: #e5e5e5;
    padding: 12px;
    border-radius: 14px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Init Session State
# --------------------------------------------------
if "threads" not in st.session_state:
    st.session_state.threads = {"chat_1": []}
    st.session_state.active_thread = "chat_1"

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "input": "",
        "messages": [],
        "vfs": {},
        "delegated_result": ""
    }

# --------------------------------------------------
# Sidebar — Chat Threads
# --------------------------------------------------
with st.sidebar:
    st.title("Chats")

    if st.button("+ New Chat"):
        new_id = f"chat_{len(st.session_state.threads) + 1}"
        st.session_state.threads[new_id] = []
        st.session_state.active_thread = new_id
        st.session_state.agent_state = {
            "input": "",
            "messages": [],
            "vfs": {},
            "delegated_result": ""
        }
        st.rerun()

    st.divider()

    for chat_id in st.session_state.threads:
        if st.button(chat_id, use_container_width=True):
            st.session_state.active_thread = chat_id
            st.session_state.agent_state["messages"] = (
                st.session_state.threads[chat_id].copy()
            )
            st.rerun()

# --------------------------------------------------
# Main Chat Area
# --------------------------------------------------
st.title("Cognibot")

messages = st.session_state.agent_state["messages"]

for msg in messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user'><b>You</b><br>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='assistant'><b>Cognibot</b><br>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# --------------------------------------------------
# Input
# --------------------------------------------------
user_input = st.chat_input("Message Cognibot…")

if user_input:
    with st.spinner("Thinking..."):
        # IMPORTANT: run_turn RETURNS UPDATED STATE
        updated_state = run_turn(
            st.session_state.agent_state,
            user_input
        )

    # Sync updated agent state
    st.session_state.agent_state = updated_state
    st.session_state.threads[
        st.session_state.active_thread
    ] = updated_state["messages"]

    st.rerun()

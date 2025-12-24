import streamlit as st
from agent import app as agent_app
from langsmith import get_current_run_tree

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
    margin-bottom: 6px;
}

.tokens {
    font-size: 12px;
    color: #9a9a9a;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Session State Init
# --------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = {
        "input": "",
        "messages": [],
        "vfs": {},
        "delegated_result": ""
    }

if "threads" not in st.session_state:
    st.session_state.threads = {"chat_1": []}
    st.session_state.active_thread = "chat_1"

if "_awaiting_response" not in st.session_state:
    st.session_state._awaiting_response = False

# --------------------------------------------------
# Sidebar — Threads
# --------------------------------------------------
with st.sidebar:
    st.title("Chats")

    if st.button("+ New Chat"):
        cid = f"chat_{len(st.session_state.threads) + 1}"
        st.session_state.threads[cid] = []
        st.session_state.active_thread = cid
        st.session_state.state = {
            "input": "",
            "messages": [],
            "vfs": {},
            "delegated_result": ""
        }
        st.session_state._awaiting_response = False
        st.rerun()

    st.divider()

    for cid in st.session_state.threads:
        if st.button(cid, use_container_width=True):
            st.session_state.active_thread = cid
            st.session_state.state["messages"] = (
                st.session_state.threads[cid].copy()
            )
            st.session_state._awaiting_response = False
            st.rerun()

# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.title("Cognibot")

for msg in st.session_state.state["messages"]:
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

# --------------------------------------------------
# STEP 1 — Capture user input ONLY
# --------------------------------------------------
if user_input and not st.session_state._awaiting_response:
    st.session_state.state["messages"].append(
        {"role": "user", "content": user_input}
    )

    st.session_state.state["input"] = user_input
    st.session_state.threads[
        st.session_state.active_thread
    ] = st.session_state.state["messages"]

    st.session_state._awaiting_response = True
    st.rerun()

# --------------------------------------------------
# STEP 2 — Run agent ONCE
# --------------------------------------------------
if st.session_state._awaiting_response:
    with st.spinner("Thinking..."):
        st.session_state.state = agent_app.invoke(
            st.session_state.state,
            config={"configurable": {"thread_id": st.session_state.active_thread}}
        )

    st.session_state.threads[
        st.session_state.active_thread
    ] = st.session_state.state["messages"]

    st.session_state._awaiting_response = False

    # ---------------- Token Display ----------------
    run = get_current_run_tree()
    if run and run.outputs and "usage" in run.outputs:
        usage = run.outputs["usage"]

        st.markdown(
            f"""
            <div class='tokens'>
            Tokens — Input: {usage.get('input_tokens', 0)},
            Output: {usage.get('output_tokens', 0)},
            Total: {usage.get('total_tokens', 0)}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.rerun()

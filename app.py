# import sys
# import os
# sys.path.append(os.path.abspath("."))

# import streamlit as st
# from dotenv import load_dotenv
# from src.graph.state_graph import build_graph


# load_dotenv()

# st.set_page_config("Autonomous Cognitive Engine", layout="wide")

# # -------- INIT STATE --------
# if "agent_state" not in st.session_state:
#     st.session_state.agent_state = {
#         "messages": [
#             {
#                 "role": "assistant",
#                 "content": "Hello! I automatically remember important things.",
#             }
#         ],
#         "todos": [],
#         "files": {},
#     }

# state = st.session_state.agent_state

# # -------- SIDEBAR --------
# with st.sidebar:
#     st.title("📝 TODOS")
#     for t in state["todos"]:
#         st.write(("✅" if t["done"] else "⬜"), t["task"])

#     st.divider()
#     st.title("🧠 VFS Memory")
#     for f in state["files"]:
#         st.write(f)

# # -------- CHAT --------
# st.title("Autonomous Cognitive Engine")

# for msg in state["messages"]:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# if user_input := st.chat_input("What should I do?"):
#     state["messages"].append({"role": "user", "content": user_input})

#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.spinner("Thinking..."):
#         st.session_state.agent_state = agent_step(user_input, state)
#         st.rerun()
import sys
import os

# Ensure src is importable
sys.path.append(os.path.abspath("."))

import streamlit as st
from dotenv import load_dotenv

from src.graph.state_graph import build_graph

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Autonomous Cognitive Engine",
    layout="wide"
)

# -------------------------------------------------
# INIT GRAPH
# -------------------------------------------------
graph = build_graph()

# -------------------------------------------------
# INIT STATE
# -------------------------------------------------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [
            {
                "role": "assistant",
                "content": "Hello! I automatically remember important things and complete tasks autonomously."
            }
        ],
        "todos": [],
        "files": {},
        "current_task": ""
    }

state = st.session_state.agent_state

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.title("📝 TODO LIST")

    if state["todos"]:
        for t in state["todos"]:
            st.write(("✅" if t["done"] else "⬜"), t["task"])
    else:
        st.caption("No tasks yet")

    st.divider()

    st.title("🧠 VFS MEMORY")
    if state["files"]:
        for f in state["files"]:
            st.write(f)
    else:
        st.caption("Memory empty")

# -------------------------------------------------
# MAIN CHAT UI
# -------------------------------------------------
st.title("Autonomous Cognitive Engine")

for msg in state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
if user_input := st.chat_input("What should I do?"):
    # Add user message
    state["messages"].append({
        "role": "user",
        "content": user_input
    })

    state["current_task"] = user_input

    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------------------------------
    # EXECUTE AUTONOMOUS GRAPH
    # -------------------------------------------------
    with st.spinner("Thinking autonomously..."):
        final_state = graph.invoke(state)
        st.session_state.agent_state = final_state
        st.rerun()

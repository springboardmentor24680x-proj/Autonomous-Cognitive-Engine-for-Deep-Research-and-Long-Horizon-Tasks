
# import streamlit as st
# from dotenv import load_dotenv
# from agent import agent_step
# import sys
# import os
# sys.path.append(os.path.dirname(__file__))
# load_dotenv()
# st.set_page_config("Autonomous Cognitive Engine", layout="wide")

# # -------- INIT AGENT STATE --------
# if "agent_state" not in st.session_state:
#     st.session_state.agent_state = {
#         "messages": [
#             {"role": "assistant", "content": "Hello! I can plan tasks and manage files."}
#         ],
#         "todos": [],
#         "files": {}
#     }

# state = st.session_state.agent_state

# # -------- SIDEBAR --------
# with st.sidebar:
#     st.title("📝 TODOS")
#     for t in state["todos"]:
#         st.write(("✅" if t["done"] else "⬜"), t["task"])

#     st.divider()
#     st.title("📁 VFS")
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
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv
from agent import agent_step

load_dotenv()
st.set_page_config("Autonomous Cognitive Engine", layout="wide")

# -------- INIT STATE --------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [
            {
                "role": "assistant",
                "content": "Hello! I automatically remember important things.",
            }
        ],
        "todos": [],
        "files": {},
    }

state = st.session_state.agent_state

# -------- SIDEBAR --------
with st.sidebar:
    st.title("TODOS")
    for t in state["todos"]:
        st.write(("✅" if t["done"] else "⬜"), t["task"])

    st.divider()
    st.title(" VFS Memory")
    for f in state["files"]:
        st.write(f)

# -------- CHAT --------
st.title("Autonomous Cognitive Engine")

for msg in state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("What should I do?"):
    state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        st.session_state.agent_state = agent_step(user_input, state)
        st.rerun()

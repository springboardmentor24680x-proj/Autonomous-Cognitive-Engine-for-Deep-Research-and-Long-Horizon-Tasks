
# import streamlit as st
# from new.agent import agent_step
# from todo import todo_manager

# st.set_page_config("Autonomous Cognitive Engine", layout="wide")

# if "chat" not in st.session_state:
#     st.session_state.chat = [
#         {"role": "assistant", "content": "Hello! I can manage TODOs and files."}
#     ]

# # -------- Sidebar --------
# with st.sidebar:
#     st.title("TODOS")
#     for t in todo_manager.list():
#         st.write(("✅" if t["done"] else "⬜"), t["task"])

# # -------- Chat --------
# st.title(" Autonomous Agent")

# for msg in st.session_state.chat:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# if user_input := st.chat_input("What should I do?"):
#     st.session_state.chat.append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.spinner("Thinking..."):
#         st.session_state.chat = agent_step(user_input, st.session_state.chat)
#         st.rerun()
import streamlit as st
from agent import agent_step
from todo import todo_manager
from dotenv import load_dotenv
load_dotenv()
st.set_page_config("Autonomous Cognitive Engine", layout="wide")

if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "assistant", "content": "Hello! I can manage TODOs and files."}
    ]

# -------- Sidebar --------
with st.sidebar:
    st.title("TODOS")
    for t in todo_manager.list():
        st.write(("✅" if t["done"] else "⬜"), t["task"])

# -------- Chat --------
st.title("Autonomous Agent")

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("What should I do?"):
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        st.session_state.chat = agent_step(user_input, st.session_state.chat)
        st.rerun()

# import streamlit as st
# from agents.supervisor_agent import SupervisorAgent
# from memory.vfs import load_memory, clear_memory
# from utils.logger import setup_logger

# logger = setup_logger("Streamlit-App")

# st.set_page_config(page_title="Autonomous Cognitive Agent", layout="wide")
# st.title("Autonomous Cognitive Agent")

# logger.info("Streamlit app started")

# # ---------- SIDEBAR ----------
# with st.sidebar:
#     st.header("Chat History")
#     history = load_memory()

#     if not history:
#         st.info("No chat history yet.")
#     else:
#         q = 1
#         for msg in history:
#             if msg["role"] == "user":
#                 st.markdown(f"**Q{q}:** {msg['content'][:40]}...")
#                 q += 1

#     if st.button("Clear Chat", use_container_width=True):
#         clear_memory()
#         logger.info("Chat history cleared")
#         st.rerun()

# # ---------- MAIN CHAT ----------
# for msg in load_memory():
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ---------- INPUT ----------
# if user_input := st.chat_input("Ask something..."):
#     logger.info(f"User input received: {user_input}")

#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             result = SupervisorAgent.invoke({"input": user_input})

#             st.markdown(result["output"])
#             st.divider()
#             st.markdown("**Summary**")
#             st.markdown(result["summary"])

#             logger.info("Response delivered to user")


import streamlit as st

from agents.supervisor_agent import SupervisorAgent
from memory.vfs import load_memory, clear_memory
from utils.logger import setup_logger


# ---------------- SETUP ----------------

logger = setup_logger("Streamlit-App")

st.set_page_config(
    page_title="Autonomous Cognitive Agent",
    layout="wide"
)

st.title("Autonomous Cognitive Agent")

logger.info("Streamlit app started")


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("Chat History")

    history = load_memory()

    if not history:
        st.info("No chat history yet.")
    else:
        q = 1
        for msg in history:
            if msg["role"] == "user":
                st.markdown(f"**Q{q}:** {msg['content'][:40]}...")
                q += 1

    if st.button("Clear Chat", use_container_width=True):
        clear_memory()
        logger.info("Chat history cleared")
        st.rerun()


# ---------------- MAIN CHAT WINDOW ----------------

for msg in load_memory():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- USER INPUT ----------------

if user_input := st.chat_input("Ask something..."):
    logger.info(f"User input received: {user_input}")

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run supervisor agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = SupervisorAgent.invoke({"input": user_input})

            # Main answer
            st.markdown(result["output"])

            # Summary
            st.divider()
            st.markdown("**Summary**")
            st.markdown(result["summary"])

            logger.info("Response delivered to user")

import streamlit as st
from agents.supervisor_agent import SupervisorAgent
from memory.vfs import load_memory, clear_memory

st.set_page_config(page_title="Autonomous Cognitive Agent", layout="wide")
st.title("Autonomous Cognitive Agent")

# ---------- SIDEBAR ----------
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

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        clear_memory()
        st.experimental_rerun()

# ---------- MAIN CHAT ----------
for msg in load_memory():
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])

    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

            if "summary" in msg:
                st.divider()
                st.markdown("**Summary**")
                st.markdown(msg["summary"])

# ---------- INPUT ----------
if user_input := st.chat_input("Ask something..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = SupervisorAgent.invoke({"input": user_input})
            st.markdown(result["output"])
            st.divider()
            st.markdown("**Summary**")
            st.markdown(result["summary"])

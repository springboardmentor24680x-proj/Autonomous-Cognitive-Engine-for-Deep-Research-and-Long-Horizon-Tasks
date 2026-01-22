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
        for i, msg in enumerate(history):
            if msg["role"] == "user":
                st.markdown(f"**Q{i//3 + 1}:** {msg['content'][:40]}...")

    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        clear_memory()
        st.rerun()

# ---------- MAIN CHAT ----------
for msg in load_memory():
    role = msg["role"]
    content = msg["content"]
    if role in ["user", "assistant"]:
        with st.chat_message(role):
            st.markdown(content)
    elif role == "summary":
        with st.chat_message("assistant"):
            st.markdown(f"#### Summary\n{content}")


# ---------- INPUT ----------
if user_input := st.chat_input("Ask something..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call SupervisorAgent
                result = SupervisorAgent.invoke({"input": user_input})

                # Use the correct key: "output"
                full_output = result.get("output", "No output returned.")

                # Handle long outputs by splitting into chunks
                for paragraph in full_output.split("\n\n"):  # split by paragraph
                 st.markdown(paragraph)

            except Exception as e:
                st.error(f"Error: {e}")

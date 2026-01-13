import streamlit as st
from agents.supervisor_agent import SupervisorAgent
from utils.logger import setup_logger

logger = setup_logger("Streamlit-App")
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
                st.markdown(f"**Q{i//2 + 1}:** {msg['content'][:40]}...")

    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        clear_memory()
        st.experimental_rerun()

# ---------- MAIN CHAT ----------
# Display full chat history
for msg in load_memory():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
                MAX_CHARS = 2000
                chunks = [full_output[i:i + MAX_CHARS] for i in range(0, len(full_output), MAX_CHARS)]
                for chunk in chunks:
                    st.markdown(chunk)

            except Exception as e:
                st.error(f"Error: {e}")

            logger.info("Response delivered to user")

import streamlit as st
from agents.main_agent import MainAgent

st.set_page_config(page_title="🤖 Real AI Chat", layout="wide")

# --- 1. Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. Sidebar Navigation & History ---
with st.sidebar:
    st.header("📜 Chat History")
    
    # Display a list of past questions
    if not st.session_state.messages:
        st.info("No history yet. Start chatting!")
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                # Create a small preview of the question
                st.text(f"Q{i//2 + 1}: {msg['content'][:30]}...")

    st.divider()
    
    # The "Clear" button to wipe memory
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 3. Main Chat Interface ---
st.title("🤖 Real AI Chat")
st.caption("Welcome to the Real AI Chat interface.Ask anything!")

# Display message history in the main window
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. Chat Input & Delegation Logic ---
if user_input := st.chat_input("Message the AI..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Delegating to sub-agents..."):
            # Construct the history list for the LangGraph agent
            # This is the "Memory" that keeps the conversation 'Real'
            chat_context = [f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]]
            
            # Invoke the MainAgent (The Orchestrator)
            result = MainAgent.invoke({
                "input": user_input,
                "history": chat_context
            })
            
            # Extract the final synthesized output
            full_reply = result.get("output", "I'm sorry, I couldn't process that.")
            
            st.markdown(full_reply)
            
            # Save the response to session memory
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
import streamlit as st
import os
from dotenv import load_dotenv
from orchestrator import MainAgent

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = MainAgent(api_key=GROQ_API_KEY)

st.title("🏛️ Main Agent System")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter multi-task prompt..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 4. Get results as a dictionary
    results_dict = st.session_state.agent.route_request(prompt, history=st.session_state.messages)

    # 5. Display and Store each sub-agent response separately
    for agent_name, content in results_dict.items():
        if "Skipped" not in content: # Only show and save active responses
            with st.chat_message("assistant"):
                st.markdown(f"**{agent_name}**:\n{content}")
            
            # Save individually so the filter can distinguish them
            st.session_state.messages.append({
                "role": "assistant", 
                "content": content, 
                "agent_name": agent_name 
            })
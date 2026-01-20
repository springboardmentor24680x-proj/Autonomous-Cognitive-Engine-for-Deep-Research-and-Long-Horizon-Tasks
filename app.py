import streamlit as st
import time
import uuid
from langchain_core.messages import HumanMessage
from src.graph.state_graph import state_graph
from src.memory.vfs import vfs

st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")
st.title("Autonomous Cognitive Engine")
st.markdown("Production Single-Pass Multi-Agent Framework")

with st.sidebar:
    st.header("Agent Status")
    st.info("Production Ready\n\nArchitecture:\n• 3 LLM Agents\n• Linear Flow\n• Internal VFS")
    
    files = vfs.list_reports()
    if files:
        st.subheader("Generated Reports")
        for file in files:
            filepath = f"data/{file}"
            with open(filepath, 'r') as f:
                st.download_button(
                    label=f"Download {file}",
                    data=f.read(),
                    file_name=file,
                    mime="text/plain"
                )
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter research query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    inputs = {"messages": [HumanMessage(content=prompt)]}

    with st.chat_message("assistant"):
        status = st.status("Executing workflow...", expanded=True)
        thoughts = st.container()
        
        full_response = ""
        try:
            with status:
                for event in state_graph.stream(inputs):
                    for node, state in event.items():
                        if "messages" in state and state["messages"]:
                            content = state["messages"][-1].content[:1000]
                            full_response += f"{node.upper()}:\n{content}\n\n"
                            with thoughts.container():
                                st.markdown(full_response)
            
            st.success("Execution Complete")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
    st.rerun()

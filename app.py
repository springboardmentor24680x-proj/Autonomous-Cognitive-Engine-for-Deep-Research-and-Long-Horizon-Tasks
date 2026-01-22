import streamlit as st
import time
from langchain_core.messages import HumanMessage
from src.graph.state_graph import state_graph
from src.memory.vfs import vfs

st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")
st.title(" Autonomous Cognitive Engine")
st.markdown("**Production Multi-Agent TODO-Driven Framework**")

# ===== SIDEBAR: AGENT STATUS + VFS DOWNLOADS =====
with st.sidebar:
    st.header(" Agent Status")
    st.info("""
    **Production Ready**
    
    Architecture:
    • Supervisor (M1: Planning)
    • Research + Summarizer (M3: Sub-Agents)  
    • VFS Memory (M2: Persistence)
    • LangGraph Routing (M4: Orchestration)
    """)
    
    # VFS Files Download
    st.subheader(" Generated Reports")
    files = vfs.ls()
    if files:
        for file in files:
            try:
                with open(f"data/{file}", 'r') as f:
                    st.download_button(
                        label=f" {file}",
                        data=f.read(),
                        file_name=file,
                        mime="text/markdown"
                    )
            except:
                st.warning(f" {file} (read error)")
    else:
        st.info("No reports yet. Run a research task!")
    
    if st.button(" Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ===== CHAT HISTORY =====
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== RESEARCH INPUT =====
if prompt := st.chat_input(" Enter research query (e.g., 'EV market 2026')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ===== FULL STATE INPUT (Todos + VFS) =====
    inputs = {
        "messages": [HumanMessage(content=prompt)],
        "todos": st.session_state.get("todos", []),
        "next": "supervisor"
    }

    # ===== LIVE EXECUTION VISUALIZATION =====
    with st.chat_message("assistant"):
        status = st.status(" Executing TODO-Driven Workflow...", expanded=True)
        progress_container = st.container()
        todo_tracker = st.container()
        
        full_response = ""
        todos_display = []
        
        with status:
            for step_num, event in enumerate(state_graph.stream(inputs, {"recursion_limit": 25})):
                for node_name, state in event.items():
                    # Extract TODO progress
                    todos = state.get("todos", [])
                    next_action = state.get("next", "unknown")
                    
                    # Live TODO visualization
                    todos_remaining = [t for t in todos if not t.get('done', False)]
                    todos_status = []
                    
                    for todo in todos:
                        status_icon = "" if todo.get('done', True) else ""
                        todos_status.append(f"{status_icon} {todo.get('task', 'N/A')}")
                    
                    # Node output
                    if "messages" in state and state["messages"]:
                        content = state["messages"][-1].content[:800]
                        full_response += f"**{node_name.upper()}**: {content}\n\n"
                    
                    # Live UI updates
                    with progress_container.container():
                        st.markdown(f"### Step {step_num+1}: **{node_name.upper()}**")
                        st.markdown(f"**Next Agent**: `{next_action}`")
                        st.markdown("**TODO Progress:**")
                        for status_line in todos_status:
                            st.markdown(f"• {status_line}")
                        st.markdown("---")
                    
                    # Update session state for persistence
                    st.session_state.todos = todos
                    st.session_state.next = next_action
        
        # Final summary
        st.success(" **Workflow Complete!**")
        st.markdown("**Final Output:**")
        st.markdown(full_response)
        
        # Save to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response.strip()
        })
    
    st.rerun()

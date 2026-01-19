import streamlit as st
from main import graph
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Deep Agent OS", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []
if "vfs" not in st.session_state: st.session_state.vfs = {}
if "todos" not in st.session_state: st.session_state.todos = []

# --- RECTIFIED SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Workspace")
    
    st.header("📋 Task Plan")
    for t in st.session_state.todos:
        st.info(str(t))
    
    st.divider()

    st.header("📂 Virtual Files")
    # This loop ensures we see files individually, not as a raw list
    if st.session_state.vfs:
        for filename, content in st.session_state.vfs.items():
            with st.expander(f"📄 {filename}"):
                st.markdown(content)
                st.download_button("Download", content, filename, key=filename)
    else:
        st.caption("No files in VFS.")

# --- CHAT INTERFACE ---
st.title("🤖 Autonomous Agent Lab")

for m in st.session_state.messages:
    if m.content and isinstance(m.content, str):
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(m.content)

if prompt := st.chat_input("Enter your request..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Executing..."):
        try:
            # High recursion limit to allow deep research
            config = {"recursion_limit": 50}
            final = graph.invoke({
                "messages": st.session_state.messages, 
                "vfs": st.session_state.vfs,
                "todos": st.session_state.todos
            }, config=config)
            
            st.session_state.messages = final["messages"]
            st.session_state.vfs = final["vfs"]
            st.session_state.todos = final["todos"]
            st.rerun()
        except Exception as e:
            st.error(f"System Error: {str(e)}")
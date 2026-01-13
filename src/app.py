import streamlit as st
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph.state_graph import build_state_graph
from memory.vfs import vfs

load_dotenv()

st.set_page_config(page_title="AI Research Agent", layout="wide")
st.title("AI Research Agent")

if "graph" not in st.session_state:
    st.session_state.graph = build_state_graph()

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input(
    "Ask anything (search / summary / both):",
    placeholder="Research real-world case studies with sources and insights"
)

if st.button("Send") and query.strip():
    state = {"messages": [HumanMessage(content=query)]}
    result = st.session_state.graph.invoke(state)

    st.session_state.history.append({
        "question": query,
        "search": result.get("search_results"),
        "summary": result.get("summary"),
    })

st.divider()

for h in reversed(st.session_state.history):
    st.markdown("### Question")
    st.write(h["question"])

    if h.get("summary"):
        st.markdown("### Answer")
        st.write(h["summary"])
    elif h.get("search"):
        st.markdown("### Search Result")
        st.write(h["search"])

    st.divider()

with st.sidebar:
    st.header("Memory (VFS)")
    files = vfs.ls()
    if files:
        f = st.selectbox("Files", files)
        st.text_area("Content", vfs.read_file(f), height=300)
    else:
        st.write("No files yet")

    if st.session_state.history:
        st.download_button(
            "Export JSON",
            json.dumps(st.session_state.history, indent=2),
            file_name="research.json",
            mime="application/json",
        )

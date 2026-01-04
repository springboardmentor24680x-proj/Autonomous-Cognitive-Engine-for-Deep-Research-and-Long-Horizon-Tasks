import streamlit as st
from my_mcp.client import MCPClient

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")

# --------------------------------------------------
# MCP Client (Cached)
# --------------------------------------------------
@st.cache_resource
def load_client():
    return MCPClient("http://localhost:3333")

client = load_client()

# --------------------------------------------------
# Sidebar: Server State
# --------------------------------------------------
with st.sidebar:
    st.title("Agent State")

    st.header("Virtual Files")
    files = client.call("vfs_ls")

    if not files or "No files" in str(files):
        st.info("No files in memory.")
    else:
        for fname in files["files"].split(","):
            fname = fname.strip()
            content = client.call("vfs_read", {"filename": fname})["content"]

            if fname.endswith(".png"):
                st.image(content, caption=fname)
            else:
                with st.expander(fname):
                    st.code(content, language="text")

# --------------------------------------------------
# Chat UI
# --------------------------------------------------
st.title("Deep Agent (MCP Powered)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for role, text in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(text)

# Input
if user_input := st.chat_input("What should I do?"):
    st.session_state.messages.append(("user", user_input))

    with st.spinner("Thinking..."):
        try:
            # MCP: send as research OR summary request
            if "research" in user_input.lower():
                result = client.call(
                    "research_task",
                    {"query": user_input}
                )
                response = f"Research completed → {result['file_written']}"

            elif "summarize" in user_input.lower():
                response = client.call(
                    "summarize_file",
                    {"filename": "research_notes.txt"}
                )
                response = f"Summary saved → {response['summary_file']}"

            else:
                response = "Please request research or summarization."

            st.session_state.messages.append(("assistant", response))
            st.rerun()

        except Exception as e:
            st.error(str(e))

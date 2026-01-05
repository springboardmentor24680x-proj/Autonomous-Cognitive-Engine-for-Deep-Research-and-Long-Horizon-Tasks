# my_mcp/mcp_app.py
import streamlit as st
from my_mcp.client import MCPClient
import base64
from io import BytesIO
from PIL import Image
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")

@st.cache_resource
def load_client():
    return MCPClient("http://localhost:3333")

client = load_client()

# --- Sidebar: Fixed File List Parsing ---
with st.sidebar:
    st.title("Agent State")
    st.header("Virtual Files")
    
    # Get the files from the server
    vfs_data = client.call("vfs_ls")
    file_list = vfs_data.get("files", [])

    # Defensive check
    if isinstance(file_list, str):
        file_list = [file_list]
    elif not isinstance(file_list, list):
        file_list = []


    if not file_list:
        st.info("No files in memory.")
    else:
        for fname in file_list:
            # Cleanly read each file
            res = client.call("vfs_read", {"filename": fname})
            content = res.get("content", "Empty")

            with st.expander(f"{fname}"):
                if fname.endswith(".png"):
                    st.image(content)
                else:
                    st.code(content, language="text")

# --- Chat UI: Support for Complex Prompts ---
st.title("Deep Agent (MCP Powered)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for role, text in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(text)

if user_input := st.chat_input("Enter your complex research task..."):
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Executing multi-step task..."):
        try:
            # Use research_task as the entry point for your agentic workflow
            # Your agent should be smart enough to call vfs_write, visualize, etc.
            result = client.call("research_task", {"query": user_input})
            
            response = f"Task Complete!\n\n**Result:** {result.get('status', 'Done')}\n**File:** {result.get('file_written', 'N/A')}"
            
            st.session_state.messages.append(("assistant", response))
            st.rerun()

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")

import streamlit as st
from my_mcp.client import MCPClient
import base64
from io import BytesIO
from PIL import Image

# --- Page configuration ---
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")

# --- MCP Client Initialization ---
@st.cache_resource
def load_client():
    # Ensure the URL matches your server's address
    return MCPClient("http://localhost:3333")

client = load_client()

# --- Utility: Display Logic for Files ---
def display_vfs_file(fname, content):
    """Handles different file types for the sidebar display."""
    if fname.endswith(".png"):
        try:
            # If content is a base64 string, decode it
            if isinstance(content, str) and (content.startswith("data:image") or len(content) > 100):
                # Clean prefix if exists
                if "," in content:
                    content = content.split(",")[1]
                img_bytes = base64.b64decode(content)
                st.image(img_bytes, caption=fname, use_container_width=True)
            else:
                st.warning(f"Could not parse image data for {fname}")
        except Exception as e:
            st.error(f"Error rendering {fname}: {e}")
    else:
        st.code(content, language="text")

# --- Sidebar: File Explorer ---
with st.sidebar:
    st.title("Agent State")
    st.header("Virtual Files")
    
    # Refresh button to manually trigger VFS check
    if st.button(" Refresh Files"):
        st.rerun()

    try:
        vfs_data = client.call("vfs_ls")
        # Ensure we always treat file_list as a list
        file_list = vfs_data.get("files", [])
        if isinstance(file_list, str):
            file_list = [file_list]
        
        if not file_list:
            st.info("No files in memory.")
        else:
            for fname in file_list:
                # Read content for each file to show in expander
                res = client.call("vfs_read", {"filename": fname})
                content = res.get("content", "Empty")
                
                with st.expander(f" {fname}"):
                    display_vfs_file(fname, content)
    except Exception as e:
        st.error(f"Could not connect to VFS: {e}")

# --- Chat UI ---
st.title("Deep Agent (MCP Powered)")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if user_input := st.chat_input("Enter your complex research task..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Executing task via MCP..."):
        try:
            # Multi-step agentic execution
            # Note: For real agentic behavior, you might call a 'supervisor' or 
            # a tool that chains these actions on the server side.
            result = client.call("research_task", {"query": user_input})
            
            # Construct assistant response
            status = result.get('status', 'Done')
            filename = result.get('file_written', 'N/A')
            response_text = f"**Task Complete!**\n\n**Result:** {status}\n**File:** {filename}"
            
            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response_text)
                
            # Rerun to update the sidebar with new files
            st.rerun()

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")

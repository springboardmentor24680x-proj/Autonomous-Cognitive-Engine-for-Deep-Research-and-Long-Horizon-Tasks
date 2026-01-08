import streamlit as st
from my_mcp.client import MCPClient
import base64
import json
import time

# --- Page configuration ---
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")

# --- MCP Client Initialization ---
@st.cache_resource
def load_client():
    return MCPClient("http://localhost:3333")

client = load_client()

# --- Utility: Display Logic for Files ---
def display_vfs_file(fname, content):
    """Handles different file types for the sidebar display."""
    if fname.endswith(".png"):
        try:
            if isinstance(content, str) and "," in content:
                content = content.split(",")[1]
            img_bytes = base64.b64decode(content)
            st.image(img_bytes, caption=fname, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering {fname}: {e}")
    else:
        st.code(content, language="text")

# --- Sidebar: File Explorer ---
with st.sidebar:
    st.title("Agent State")
    st.header("Virtual Files")
    
    if st.button("🔄 Refresh Files"):
        st.rerun()

    try:
        vfs_data = client.call("vfs_ls")
        file_list = vfs_data.get("files", [])
        if isinstance(file_list, str):
            file_list = [file_list]
        
        if not file_list:
            st.info("No files in memory.")
        else:
            for fname in file_list:
                res = client.call("vfs_read", {"filename": fname})
                content = res.get("content", "Empty")
                with st.expander(f"📄 {fname}"):
                    display_vfs_file(fname, content)
    except Exception as e:
        st.error(f"VFS Error: {e}")

# --- Chat UI ---
st.title("Deep Agent (MCP Trace Mode)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Agentic Execution Loop ---
if user_input := st.chat_input("Enter your complex research task..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Use st.status to show the "Thinking Trace"
    with st.status("Agent is working...", expanded=True) as status_box:
        current_query = user_input
        final_response = ""
        
        # Limit to 5 steps to prevent infinite loops
        for step in range(5):
            st.write(f"🧠 **Step {step+1}:** Consulting Supervisor...")
            
            # 1. Ask Supervisor for the next action
            decision = client.call("supervisor", {"query": current_query})
            
            action = decision.get("action")
            args = decision.get("args", {})

            # 2. Check if we reached a final answer
            if action == "final_answer" or not action:
                final_response = args.get("response", "I have completed all tasks.")
                break

            # 3. TRACE: Show the tool call details
            st.write(f"🛠️ **Action:** Calling tool `{action}`")
            st.json(args) # This shows the parameters in the trace

            # 4. Execute the tool
            try:
                tool_result = client.call(action, args)
                st.write(f"✅ **Result:** Success")
                
                # Update query with tool output so supervisor knows what happened
                current_query = f"Tool '{action}' result: {json.dumps(tool_result)}. Task context: {user_input}"
            except Exception as e:
                st.error(f"Tool Error: {e}")
                current_query = f"Tool '{action}' failed with error: {str(e)}"
            
            time.sleep(1) # Brief pause for UI readability

        status_box.update(label="Tasks Finished!", state="complete", expanded=False)

    # Save and display final response
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    with st.chat_message("assistant"):
        st.markdown(final_response)
    
    # Rerun to refresh the VFS sidebar automatically
    st.rerun()
import streamlit as st
from my_mcp.client import MCPClient
import base64
import json
import time
import logging
import os

# --------------------
# Logging Setup
# --------------------
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("STREAMLIT_APP")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler("logs/mcp_app.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
# --------------------
# Page configuration
# --------------------
st.set_page_config(page_title="Autonomous Cognitive Engine", layout="wide")
logger.info("Streamlit app started")

# --------------------
# MCP Client Initialization
# --------------------
@st.cache_resource
def load_client():
    logger.info("Initializing MCP Client")
    return MCPClient("http://localhost:3333")

client = load_client()

# --------------------
# Utility: Display Logic for Files
# --------------------
def display_vfs_file(fname, content):
    if fname.endswith(".png"):
        try:
            if isinstance(content, str) and "," in content:
                content = content.split(",")[1]
            img_bytes = base64.b64decode(content)
            st.image(img_bytes, caption=fname, use_container_width=True)
        except Exception as e:
            logger.exception(f"Failed to render image {fname}")
            st.error(f"Error rendering {fname}: {e}")
    else:
        st.code(content, language="text")

# --------------------
# Sidebar: File Explorer
# --------------------
with st.sidebar:
    st.title("Agent State")
    st.header("Virtual Files")

    if st.button(" Refresh Files"):
        logger.info("User refreshed VFS")
        st.rerun()

    try:
        logger.info("Requesting VFS file list")
        vfs_data = client.call("vfs_ls")
        file_list = vfs_data.get("files", [])
        logger.info(f"VFS files: {file_list}")

        if not file_list:
            st.info("No files in memory.")
        else:
            for fname in file_list:
                res = client.call("vfs_read", {"filename": fname})
                file_content = res.get("content", "Empty")
                with st.expander(f" {fname}"):
                    display_vfs_file(fname, file_content)

    except Exception as e:
        logger.exception("VFS Connection Error")
        st.error(f"VFS Connection Error: {e}")

# --------------------
# Chat UI
# --------------------
st.title("Deep Agent (MCP Trace Mode)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------
# Agentic Execution Loop
# --------------------
if user_input := st.chat_input("Enter your complex research task..."):
    logger.info(f"User input: {user_input}")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.status("Agent is working...", expanded=True) as status_box:
        current_query = user_input
        final_response = ""

        for step in range(5):
            logger.info(f"Step {step+1} - Supervisor call")
            st.write(f"**Step {step+1}:** Consulting Supervisor...")

            decision_resp = client.call("supervisor", {"query": current_query})
            logger.info(f"Supervisor response: {decision_resp}")

            try:
                decision = decision_resp
                action = decision.get("action")
                args = decision.get("args", {})
            except Exception as e:
                logger.exception("Supervisor response parsing failed")
                final_response = str(decision_resp)
                break

            if action == "final_answer" or not action:
                final_response = args.get("response", "Task completed.")
                logger.info("Final answer reached")
                break

            st.write(f"**Action:** `{action}`")
            st.json(args)

            try:
                logger.info(f"Executing tool: {action} | args={args}")
                tool_result = client.call(action, args)
                logger.info(f"Tool result: {tool_result}")

                current_query = f"Tool '{action}' result: {json.dumps(tool_result)}. Next step?"
            except Exception as e:
                logger.exception("Tool execution failed")
                current_query = f"Tool '{action}' failed: {str(e)}"

            time.sleep(0.5)

        status_box.update(label="Tasks Finished!", state="complete", expanded=False)

    st.session_state.messages.append({"role": "assistant", "content": final_response})
    with st.chat_message("assistant"):
        st.markdown(final_response)

    logger.info("Agent loop finished")

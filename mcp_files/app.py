import streamlit as st
import json
import base64
import re
import os
import logging
from mcp_client import call_mcp_sync

# --- LOGGING SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, "app.log")
logger = logging.getLogger("Streamlit_App")

if not logger.handlers:
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

logger.info("Streamlit App logger initialized")

# --- PAGE CONFIG ---
st.set_page_config(page_title="Autonomous Agent", layout="wide")
st.title("🧠 Autonomous Cognitive Agent")

# --- SESSION STATE ---
for key, default in [("history", []), ("step", 0), ("context", ""), ("is_running", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- SIDEBAR: VFS VIEW ---
with st.sidebar:
    st.header("📂 File System")
    if st.button("Refresh Files"):
        st.rerun()

    try:
        files_json = call_mcp_sync("vfs_ls", {})
        files_data = json.loads(files_json.replace("'", '"'))
        file_list = files_data.get("files", []) if isinstance(files_data, dict) else files_data

        for f in file_list:
            with st.expander(f):
                content_res = call_mcp_sync("vfs_read", {"filename": f})
                if f.endswith(".png"):
                    try:
                        img_data = json.loads(content_res).get("content", content_res) if "{" in content_res else content_res
                        st.image(base64.b64decode(img_data))
                    except Exception as e:
                        logger.error(f"Failed to load image {f}: {str(e)}")
                        st.error(f"Failed to load image {f}")
                else:
                    st.text(content_res[:500])
    except Exception as e:
        logger.warning(f"VFS not ready: {str(e)}")
        st.info("Server standby.")

# --- MAIN CHAT DISPLAY ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
if user_input := st.chat_input("Ask something..."):
    logger.info(f"User Input: {user_input}")
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.context = f"User Request: {user_input}"
    st.session_state.step = 0
    st.session_state.is_running = True
    st.rerun()

# --- AGENT STEP PROCESS ---
if st.session_state.is_running:
    if st.session_state.step < 10:
        step = st.session_state.step
        logger.info(f"--- Processing Step {step + 1} ---")
        with st.chat_message("assistant"):
            with st.status(f"Step {step+1}: Agent Working...", expanded=True) as status:
                st.write("Consulting Supervisor...")
                decision_raw = call_mcp_sync("supervisor", {"query": st.session_state.context})

                # Robust JSON Parsing
                action, args = None, {}
                try:
                    clean_text = re.sub(r'```json\s*|\s*```', '', decision_raw).strip()
                    decision = json.loads(clean_text)
                    action = decision.get("action")
                    args = decision.get("args", {})
                except Exception:
                    json_match = re.search(r'\{.*\}', decision_raw, re.DOTALL)
                    if json_match:
                        try:
                            decision = json.loads(json_match.group())
                            action = decision.get("action")
                            args = decision.get("args", {})
                        except Exception as e:
                            logger.error(f"JSON parsing failed: {str(e)}")

                if action == "final_answer" or not action:
                    res = args.get("response", decision_raw) if isinstance(args, dict) else decision_raw
                    logger.info("Final answer reached.")
                    st.markdown(res)
                    st.session_state.history.append({"role": "assistant", "content": res})
                    st.session_state.is_running = False
                    status.update(label="Task Complete!", state="complete")
                    st.rerun()
                else:
                    logger.info(f"Executing: {action}")
                    st.write(f"Running: `{action}`")
                    try:
                        tool_result = call_mcp_sync(action, args)
                        st.session_state.context += f"\n\n[Observation from {action}]:\n{tool_result}"
                    except Exception as e:
                        logger.error(f"Tool execution failed: {str(e)}")
                        st.session_state.context += f"\n\n[Error executing {action}]: {str(e)}"
                    st.session_state.step += 1
                    status.update(label=f"Finished {action}", state="complete")
                    st.rerun()
    else:
        logger.warning("Step limit reached.")
        st.error("Step Limit Reached.")
        st.session_state.is_running = False

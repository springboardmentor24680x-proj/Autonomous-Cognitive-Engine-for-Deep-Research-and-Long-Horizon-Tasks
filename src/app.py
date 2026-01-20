# --------------------------------------------------
# 🔴 MUST BE FIRST: Load .env for LangSmith Tracing
# --------------------------------------------------
import os
from dotenv import load_dotenv

load_dotenv()  # REQUIRED for LANGCHAIN_TRACING_V2


# --------------------------------------------------
# Streamlit
# --------------------------------------------------
import streamlit as st

# LangChain message objects (ONLY for UI history)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Shared memory
from memory.vfs import VFS

# LangGraph
from graph.state_graph import build_graph


# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Deep Agent UI",
    layout="wide"
)


# --------------------------------------------------
# Initialize LangGraph (Cached)
# --------------------------------------------------
@st.cache_resource
def load_graph():
    return build_graph()

graph = load_graph()


# --------------------------------------------------
# Sidebar: Agent State (VFS only)
# --------------------------------------------------
with st.sidebar:
    st.title("Agent State")

    # ---------- Virtual Files ----------
    st.header("📁 Virtual Files")

    if not VFS:
        st.info("No files in memory.")
    else:
        for filename, content in VFS.items():
            with st.expander(f"📄 {filename}"):
                st.code(content, language="text")

    # ---- OPTIONAL: Debug tracing (remove later) ----
    st.divider()
    st.caption("🔍 Tracing Debug")
    st.write("Tracing:", os.getenv("LANGCHAIN_TRACING_V2"))
    st.write("Project:", os.getenv("LANGCHAIN_PROJECT"))


# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.title("Autonomous Cognitive Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content="Hello! I can plan tasks, research topics, and summarize results."
        )
    ]


# ---------- Display Chat History ----------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)


# --------------------------------------------------
# User Input
# --------------------------------------------------
if user_input := st.chat_input("What should I do?"):
    # Store user message (UI only)
    st.session_state.messages.append(
        HumanMessage(content=user_input)
    )

    with st.spinner("Thinking..."):
        try:
            # 🔹 LangGraph expects STATE, not messages
            result = graph.invoke(
                {"query": user_input}
            )

            # 🔹 Compose assistant response
            response_parts = []

            if "todos" in result:
                response_parts.append("### 📋 Planned Tasks")
                response_parts.append(f"```json\n{result['todos']}\n```")

            if "summary" in result:
                response_parts.append("### 📝 Summary")
                response_parts.append(result["summary"])

            final_answer = "\n\n".join(response_parts) or "Done."

            st.session_state.messages.append(
                AIMessage(content=final_answer)
            )

            st.rerun()

        except Exception as e:
            st.error(f"Execution error: {e}")

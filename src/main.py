import streamlit as st
from dotenv import load_dotenv
from orchestrator import MainAgent

load_dotenv()

st.set_page_config("Autonomous Cognitive Engine", layout="wide")
st.title("🤖 Autonomous Cognitive Engine")

agent = MainAgent()

# -------------------------------
# 🔹 Session State Initialization
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "prompts" not in st.session_state:
    st.session_state.prompts = []

# -------------------------------
# 🔹 Sidebar – Previous Prompts
# -------------------------------
st.sidebar.title("🕘 Prompt History")

if st.session_state.prompts:
    for i, p in enumerate(st.session_state.prompts, 1):
        st.sidebar.markdown(f"**{i}.** {p}")
else:
    st.sidebar.info("No prompts yet")

st.sidebar.markdown("---")
st.sidebar.info(
    "🔍 Researcher → Facts\n\n"
    "✍️ Creative → Article\n\n"
    "💻 Coder → Code"
)

# -------------------------------
# 🔹 Display Previous Chat
# -------------------------------
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content, unsafe_allow_html=True)

# -------------------------------
# 🔹 New User Input
# -------------------------------
if prompt := st.chat_input("Ask something..."):
    # Store prompt
    st.session_state.prompts.append(prompt)
    st.session_state.chat_history.append(("user", prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.run(prompt)
            st.markdown(response, unsafe_allow_html=True)

    # Store assistant response
    st.session_state.chat_history.append(("assistant", response))

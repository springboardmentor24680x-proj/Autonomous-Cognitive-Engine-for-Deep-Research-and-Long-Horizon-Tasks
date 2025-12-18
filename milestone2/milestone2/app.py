# app.py
import streamlit as st
from agent import graph

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Agent",
    page_icon="🧠",
    layout="centered"
)

# -------------------------------------------------
# CUSTOM CSS (UI POLISH)
# -------------------------------------------------
st.markdown("""
<style>
.chat-title {
    font-size: 38px;
    font-weight: 700;
}
.badge {
    display: inline-block;
    background-color: #f0f2f6;
    padding: 6px 12px;
    border-radius: 20px;
    margin-right: 6px;
    font-size: 14px;
}
.footer {
    text-align: center;
    color: gray;
    font-size: 13px;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("<div class='chat-title'>🧠 Intelligent AI Agent</div>", unsafe_allow_html=True)

st.markdown(
    """
An **AI Agent designed for natural, continuous conversation**  
that understands context, remembers earlier prompts, and responds intelligently —
similar to ChatGPT, but built from scratch using **LangGraph + Groq**.
"""
)

st.markdown(
    """
<span class="badge">🤖 Conversational AI</span>
<span class="badge">🧠 Prompt Continuity</span>
<span class="badge">📊 Reasoning</span>
<span class="badge">⚙️ Agent Architecture</span>
""",
unsafe_allow_html=True
)

st.divider()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "chat_history": [],
        "vfs": {},
        "final_answer": ""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------
# EXAMPLE PROMPTS (FIRST LOAD)
# -------------------------------------------------
if not st.session_state.messages:
    st.info(
        "💡 **Try prompts like:**\n\n"
        "- Plan a birthday party for a 12-year-old with ₹8,000\n"
        "- Modify the plan to include indoor games\n"
        "- Reduce the budget by ₹1,000\n"
        "- Create a checklist for the event day"
    )

# -------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
user_input = st.chat_input("Ask the AI Agent anything...")

if user_input:
    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Thinking indicator
    with st.chat_message("assistant"):
        with st.spinner("🧠 AI Agent is thinking..."):
            st.session_state.agent_state["user_query"] = user_input
            st.session_state.agent_state = graph.invoke(
                st.session_state.agent_state
            )

            agent_reply = st.session_state.agent_state.get(
                "final_answer",
                "I'm here to help! 😊"
            )

            st.markdown(agent_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": agent_reply
    })

# -------------------------------------------------
# SIDEBAR (CLEAN & IMPRESSIVE)
# -------------------------------------------------
with st.sidebar:
    st.header("🧠 About This AI Agent")

    st.markdown(
        """
This AI Agent demonstrates:

✔ Continuous conversation  
✔ Context awareness  
✔ Agent-style reasoning  
✔ Real-time response generation  

Built as part of an **AI internship project** using modern agent frameworks.
"""
    )

    st.divider()

    st.subheader("⚙️ Technology Stack")
    st.markdown(
        """
- **LangGraph** – Agent orchestration  
- **Groq LLM** – Fast inference  
- **Streamlit** – Interactive UI  
- **Python** – Core logic
"""
    )

    st.divider()

    st.subheader("🎯 How to Evaluate")
    st.markdown(
        """
- Ask follow-up questions  
- Modify earlier requests  
- Observe prompt continuity  
- Check reasoning consistency
"""
    )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    "<div class='footer'>🚀 AI Agent Project | Built for Internship Evaluation</div>",
    unsafe_allow_html=True
)
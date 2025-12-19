import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import ONLY the setup_agent function
from research_agent import setup_agent   # <-- rename your file to agent.py if needed
from src.memory.vfs import ls
from calendar_service import list_events

# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Deep Agent UI",
    layout="wide"
)

# --------------------------------------------------
# Initialize Agent (Cached)
# --------------------------------------------------
@st.cache_resource
def load_agent():
    return setup_agent()

agent = load_agent()


# --------------------------------------------------
# Session State: Chat History
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content="Hello! I can manage your todos, files, and calendar. What would you like to do?"
        )
    ]


# --------------------------------------------------
# Render Chat Messages
# --------------------------------------------------
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage) or isinstance(msg, SystemMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)


# --------------------------------------------------
# Chat Input
# --------------------------------------------------
user_input = st.chat_input(
    "Example: 'Create a todo to buy milk' or 'Schedule meeting tomorrow at 5 PM'"
)

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    with st.spinner("Agent is thinking..."):
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            final_response = result["messages"][-1].content

            st.chat_message("assistant").markdown(final_response)
            st.session_state.messages.append(AIMessage(content=final_response))

        except Exception as e:
            error_text = f"Error: {e}"
            st.error(error_text)
            st.session_state.messages.append(AIMessage(content=error_text))

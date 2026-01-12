import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.memory.vfs import VFS
from src.tools.calendar_tools import EVENTS
from src.main.research_agent import setup_agent

# 1. Page Config
st.set_page_config(page_title="Deep Agent UI", layout="wide")

# 2. Initialize Agent (Cached)
@st.cache_resource
def load_agent():
    return setup_agent()

agent = load_agent()

# 3. Sidebar: State Visualization
with st.sidebar:
    st.title("Agent State")
    st.header(" Virtual Files")
    if not VFS:
        st.info("VFS is empty.")
    else:
        for filename, content in VFS.items():
            if filename.endswith(".png"):
                st.image(content, caption=filename)
            else:
                with st.expander(f" {filename}"):
                    # Decode if it's bytes, else show as string
                    display_text = content.decode('utf-8') if isinstance(content, bytes) else content
                    st.code(display_text, language="text")
    
    st.divider()
    st.header(" Calendar")
    if not EVENTS:
        st.info("No events.")
    else:
        for i, event in enumerate(EVENTS):
            st.markdown(f"**{event['title']}**")
            st.caption(f"{event['date']} @ {event['time']}")
            st.divider()

# 4. Main Chat UI
st.title(" Deep Supervisor Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="System initialized. I am ready to manage your files and schedule.")
    ]

# Display Chat History
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# User Input Logic
if user_input := st.chat_input("What should I do?"):
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # First Invoke
            history = st.session_state.messages[-5:]
            result = agent.invoke(history)
            
            ans = result["messages"][-1].content
            st.session_state.messages.append(AIMessage(content=ans))
            st.markdown(ans)

            # --- THE MISSING LOOP ---
            # This handles the "__continue__" logic from your AgentWrapper
            while result.get("continue"):
                with st.status("Executing next step...", expanded=False):
                    result = agent.invoke([HumanMessage(content="__continue__")])
                    ans = result["messages"][-1].content
                    st.session_state.messages.append(AIMessage(content=ans))
                    st.write(ans) # Shows progress in the status expander
                
                # Update the main UI with the final result of that step
                st.markdown(ans)
            
            # Final refresh to update the sidebar VFS/Calendar
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from supervisor import AgentState

def summarizer_node(state: AgentState):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)
    
    # Find the most recent report in the VFS
    vfs = state.get("vfs", {})
    if not vfs:
        return {"messages": [HumanMessage(content="No files found to summarize.", name="summarizer")]}
    
    # Get the last added file content
    last_filename = list(vfs.keys())[-1]
    report_content = vfs[last_filename]
    
    prompt = f"Summarize the following report into 5 key bullet points for a busy executive:\n\n{report_content}"
    response = llm.invoke(prompt)
    
    # Save the summary as a new file in VFS
    summary_filename = f"SUMMARY_{last_filename}"
    vfs[summary_filename] = response.content
    
    return {
        "messages": [HumanMessage(content=f"Summary created: {summary_filename}", name="summarizer")],
        "vfs": vfs,
        "next_step": "end"
    }

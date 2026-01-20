from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from src.memory.vfs import vfs

class SummarizerAgent:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    def node(self, state):
        query = state["messages"][0].content.lower()
        filename = f"{query[:30].replace(' ', '_')}.txt"
        
        context = "\n".join([msg.content for msg in state["messages"][-3:]])
        prompt = f"""
        SUMMARIZER AGENT: Create final report for: {query}
        
        Context: {context}
        
        Format exactly:
        Executive Summary: [Topic] Project Report
        
        Key Insights:
        • Point 1
        • Point 2  
        • Point 3
        
        Actionable Recommendations:
        • Rec 1
        • Rec 2
        """
        
        response = self.llm.invoke(prompt)
        save_result = vfs.write_report(filename, response.content)
        
        final_output = f"{response.content}\n\n{save_result}"
        return {"messages": [AIMessage(content=final_output)]}

summarizer_node = SummarizerAgent().node

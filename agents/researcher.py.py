from groq import Groq
from langsmith import traceable

class ResearcherAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    @traceable(
        name="Researcher LLM Call", 
        metadata={"agent_type": "specialist", "capability": "web_research"} # Metadata entry
    ) 
    def run(self, user_query, history=None):
        messages = [{"role": "system", "content": "You are a Research Agent."}]
        if history: messages.extend(history)
        messages.append({"role": "user", "content": user_query})
        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
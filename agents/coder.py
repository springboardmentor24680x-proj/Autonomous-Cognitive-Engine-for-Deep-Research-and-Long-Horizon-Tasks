from groq import Groq
from langsmith import traceable

class CoderAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    @traceable(
        name="Coder LLM Call",
        metadata={"agent_type": "specialist", "capability": "code_generation", "language": "java/python"} # Metadata entry
    ) 
    def run(self, user_query, history=None):
        messages = [{"role": "system", "content": "You are a professional Coder."}]
        if history: messages.extend(history)
        messages.append({"role": "user", "content": user_query})
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return response.choices[0].message.content
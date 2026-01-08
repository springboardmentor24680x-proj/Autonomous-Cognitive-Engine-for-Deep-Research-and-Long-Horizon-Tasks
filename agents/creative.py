from groq import Groq
from langsmith import traceable

class CreativeAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    @traceable(name="Creative LLM Call") # Shows the "hidden" narrative generation
    def run(self, user_query, history=None):
        messages = [{"role": "system", "content": "You are a Creative Writer."}]
        if history: messages.extend(history)
        messages.append({"role": "user", "content": user_query})
        
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
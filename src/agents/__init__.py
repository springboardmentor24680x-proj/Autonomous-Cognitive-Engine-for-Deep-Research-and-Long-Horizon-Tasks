from dotenv import load_dotenv
load_dotenv(override=True)  # loads the .env file

import os
print("DEBUG GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))  # should print your actual key

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Get the API key from environment variable
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

client = Groq(api_key=API_KEY)

def ask_agent(query):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Groq Agent Ready!")
    while True:
        query = input("You: ")
        print("AI:", ask_agent(query))
        
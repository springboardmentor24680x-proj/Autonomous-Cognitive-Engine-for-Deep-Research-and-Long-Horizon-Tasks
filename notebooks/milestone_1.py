from groq import Groq
from dotenv import load_dotenv
import os


def chat_with_ai(user_input):
    """Handles calling the Groq API and returning the reply."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": user_input}]
    )

    return response.choices[0].message.content


def main():
    """Main function that runs the chatbot loop."""
    load_dotenv()

    print("AI Chatbot started! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Chatbot: Goodbye!")
            break

        reply = chat_with_ai(user_input)
        print("\nChatbot:", reply, "\n")


# This ensures main() runs only when this file is executed directly
if __name__ == "__main__":
    main()

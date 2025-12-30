def main():
    import os

    # Initialize OpenRouter client
    from langchain_groq import ChatGroq

    model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    groq_api_key=os.environ.get("GROQ_API_KEY", ""),
    max_tokens=1000
   )
    todo_list = []
    print("Welcome! Chat with your AI about your tasks. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Agent: Goodbye! I’ll remember your tasks for next time.")
            break

        # Build prompt for AI
        prompt = f"""
You are a friendly AI assistant helping the user manage their To-Do list.
Current tasks: {todo_list}
User says: "{user_input}"

Respond conversationally, acknowledge the tasks, update the list if necessary, 
and optionally summarize the current tasks. Return your message as text.
"""

        response = model.invoke(prompt)
        ai_message = response.content
        print(f"AI: {ai_message}")

        # Optional: extract updated tasks from AI response (simple parsing)
        if "Current tasks:" in ai_message:
            tasks_part = ai_message.split("Current tasks:")[-1]
            updated_tasks = [t.strip() for t in tasks_part.split(",") if t.strip()]
            todo_list = updated_tasks


if __name__ == "__main__":
    main()



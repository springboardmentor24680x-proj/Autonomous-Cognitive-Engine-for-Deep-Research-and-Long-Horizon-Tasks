import os
from dotenv import load_dotenv
from openai import OpenAI
from vfs import VFS

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1"   # 🔥 Grok endpoint
)

# ----------------------------
# Initialize VFS
# ----------------------------
vfs = VFS()

# ----------------------------
# AI Reply (Grok)
# ----------------------------
def ai_reply(message):
    response = client.responses.create(
        model="grok-2-latest",
        input=message
    )
    return response.output_text

# ----------------------------
# Agent Logic
# ----------------------------
def agent_handle(user_input):
    text = user_input.lower()

    # ----- Write file -----
    if text.startswith("write file"):
        try:
            _, _, rest = user_input.split(" ", 2)
            filename, content = rest.split(" ", 1)
            return vfs.write_file(filename, content)
        except:
            return "Usage: write file <filename> <content>"

    # ----- Read file -----
    if text.startswith("read file"):
        parts = user_input.split(" ")
        if len(parts) < 3:
            return "Usage: read file <filename>"
        return vfs.read_file(parts[2])

    # ----- List files -----
    if text == "list files":
        return vfs.list_files()

    # ----- Default: AI Chat -----
    return ai_reply(user_input)

# ----------------------------
# Main Loop
# ----------------------------
def main():
    print("\n✨ VFS Chat Agent (Grok) Started!")
    print("Commands:")
    print("  write file <filename> <content>")
    print("  read file <filename>")
    print("  list files")
    print("Type 'exit' to quit.\n")

    while True:
        user = input("You: ")

        if user.lower() == "exit":
            print("Agent: Goodbye! 👋")
            break

        reply = agent_handle(user)
        print("Agent:", reply, "\n")

if __name__ == "__main__":
    main()
from graph.graph import build_graph

print("🚀 Starting agent...")

app = build_graph()

state = {
    "messages": [
        {"role": "user", "content": "Write a report on AI in healthcare"}
    ],
    "todos": [],
    "current_task": "",
    "files": {},
    "final_output": ""
}

result = app.invoke(state)

print("✅ Execution finished")

print("\n🧠 FINAL OUTPUT:\n")
print(result.get("final_output"))
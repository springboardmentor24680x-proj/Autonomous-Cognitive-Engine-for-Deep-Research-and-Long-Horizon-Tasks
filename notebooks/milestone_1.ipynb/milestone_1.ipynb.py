# Cell 1: Setup
import os
from dotenv import load_dotenv
from main import graph
from langchain_core.messages import HumanMessage

load_dotenv()

# Cell 2: Test Task Decomposition
test_queries = [
    "Research the impact of 5G on healthcare and save a summary.",
    "Plan a trip to Tokyo including budget, sights, and flights.",
    "Analyze the stock performance of Nvidia in 2025."
]

for query in test_queries:
    print(f"\n--- Testing Query: {query} ---")
    inputs = {"messages": [HumanMessage(content=query)], "vfs": {}, "todos": []}
    
    # We only run the first step to see the planning
    for event in graph.stream(inputs):
        if "supervisor" in event:
            print("Supervisor is planning...")
        if "update" in event:
            state = event["update"]
            print(f"Generated TODOs: {state.get('todos', 'No tasks generated')}")
            break
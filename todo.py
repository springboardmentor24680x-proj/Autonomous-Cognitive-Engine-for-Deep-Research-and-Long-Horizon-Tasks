import json
from llm.groq_llm import call_llm

def generate_todos(user_query: str):

    prompt = f"""
Break this task into structured steps:

Return ONLY JSON list:
[
  {{"task": "..."}},
  {{"task": "..."}}
]

Task:
{user_query}
"""

    result = call_llm(prompt)

    try:
        return json.loads(result)
    except:
        return [{"task": "Fix parsing error in planner"}]
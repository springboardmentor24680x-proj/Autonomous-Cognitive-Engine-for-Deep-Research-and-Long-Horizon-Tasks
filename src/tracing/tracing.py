import os
from langsmith import Client

def init_tracing():
    if os.getenv("LANGCHAIN_TRACING_V2") == "true":
        return Client()
    return None

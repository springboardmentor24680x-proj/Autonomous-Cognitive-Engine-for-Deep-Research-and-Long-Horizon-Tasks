








import os

def init_tracing():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    return True

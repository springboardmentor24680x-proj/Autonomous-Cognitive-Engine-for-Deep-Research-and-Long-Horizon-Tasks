from fastapi import FastAPI

class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.app = FastAPI(title=name)

    def tool(self):
        def decorator(fn):
            self.app.post(f"/tool/{fn.__name__}")(fn)
            return fn
        return decorator

    def run(self, port=3333):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=port)

import requests

class MCPClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def call(self, tool: str, payload: dict):
        res = requests.post(f"{self.base_url}/{tool}", json=payload, timeout=30)
        res.raise_for_status()
        return res.json()["result"]

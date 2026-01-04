# my_mcp/client.py
import requests

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def call(self, tool_name: str, arguments: dict = None):
        url = f"{self.base_url}/tool/{tool_name}"
        response = requests.post(url, json=arguments or {})
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
import requests
import logging
import os

# --------------------
# Logger Setup (SAFE)
# --------------------
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("MCP_CLIENT")
logger.setLevel(logging.INFO)
logger.propagate = False  # IMPORTANT

if not logger.handlers:
    file_handler = logging.FileHandler("logs/client.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# --------------------
# MCP Client
# --------------------
class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        logger.info(f"Initialized MCPClient | base_url={self.base_url}")

    def call(self, tool_name: str, arguments: dict = None):
        url = f"{self.base_url}/tool/{tool_name}"
        payload = arguments or {}

        logger.info(f"POST {url} | payload={payload}")

        try:
            response = requests.post(url, json=payload)
            logger.info(f"HTTP {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(response.text)
                raise Exception(response.text)

        except Exception:
            logger.exception("MCPClient call failed")
            raise

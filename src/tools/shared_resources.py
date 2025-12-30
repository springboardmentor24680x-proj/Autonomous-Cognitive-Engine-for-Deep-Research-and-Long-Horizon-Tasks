from tavily import TavilyClient as _TavilyClient
from memory.vfs import VirtualFileSystem

# ---- Shared singletons ----
vfs = VirtualFileSystem()

class TavilyClient(_TavilyClient):
    """Thin wrapper so imports stay stable"""
    pass

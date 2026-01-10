import os
import base64

# Internal storage (Simple dictionary for Virtual File System)
VFS_STORAGE = {}

def write_file(filename, content):
    """Internal function to write to memory."""
    # content could be str (research) or bytes (charts)
    VFS_STORAGE[filename] = content
    return f"Success: {filename} written."

def read_file(filename):
    """Internal function to read from memory."""
    content = VFS_STORAGE.get(filename)
    if content is None:
        return {"error": f"File {filename} not found"}
    
    # Handle binary data (images) for SSE transport
    if isinstance(content, bytes):
        return {
            "content": base64.b64encode(content).decode('utf-8'),
            "type": "image"
        }
    
    return {"content": str(content), "type": "text"}

def ls():
    """List all files."""
    return list(VFS_STORAGE.keys())

# --- MCP Tool Wrappers (Used by server.py) ---
def vfs_write(filename: str, content: str):
    return write_file(filename, content)

def vfs_read(filename: str):
    # Returns the dict with type information
    return read_file(filename)

def vfs_ls():
    # Return a dict so the MCP client receives a clean JSON object
    return {"files": ls()}
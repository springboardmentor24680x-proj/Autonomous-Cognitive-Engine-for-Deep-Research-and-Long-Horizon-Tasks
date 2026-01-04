from my_mcp.server.fastapi import MCPServer
from src.memory.vfs import write_file, read_file, edit_file, delete_file, ls, clear_vfs

def register(server: MCPServer):

    @server.tool()
    def vfs_write(filename: str, content: str) -> dict:
        write_file(filename, content)
        return {"ok": True}

    @server.tool()
    def vfs_read(filename: str) -> dict:
        return {"content": read_file(filename)}

    @server.tool()
    def vfs_ls() -> dict:
        return {"files": ls()}

    @server.tool()
    def vfs_delete(filename: str) -> dict:
        return {"status": delete_file(filename)}

    @server.tool()
    def vfs_clear() -> dict:
        clear_vfs()
        return {"status": "cleared"}

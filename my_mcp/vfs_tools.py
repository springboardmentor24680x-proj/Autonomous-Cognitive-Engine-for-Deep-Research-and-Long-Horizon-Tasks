from pydantic import BaseModel
from my_mcp.server.fastapi import MCPServer
from src.memory.vfs import (
    write_file,
    read_file,
    delete_file,
    ls,
    clear_vfs,
)

# -------------------------------
# Input Schemas
# -------------------------------
class VFSWriteInput(BaseModel):
    filename: str
    content: str

class VFSReadInput(BaseModel):
    filename: str

class VFSDeleteInput(BaseModel):
    filename: str


def register(server: MCPServer):

    @server.tool()
    def vfs_write(input: VFSWriteInput) -> dict:
        write_file(input.filename, input.content)
        return {"ok": True}

    @server.tool()
    def vfs_read(input: VFSReadInput) -> dict:
        return {"content": read_file(input.filename)}

    @server.tool()
    def vfs_ls() -> dict:
        """
        List virtual files.
        """
        return {
            "files": ls()   # ✅ MUST be a list[str]
        }

    @server.tool()
    def vfs_delete(input: VFSDeleteInput) -> dict:
        delete_file(input.filename)
        return {"status": "deleted"}

    @server.tool()
    def vfs_clear() -> dict:
        clear_vfs()
        return {"status": "cleared"}

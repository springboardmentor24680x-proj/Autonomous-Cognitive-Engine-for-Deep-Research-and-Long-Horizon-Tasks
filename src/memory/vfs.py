# src/memory/vfs.py

VFS = {}

def write_file(filename: str, content: str):
    VFS[filename] = content

def append_file(filename: str, content: str):
    old = VFS.get(filename, "")
    if old:
        VFS[filename] = old + "\n" + content
    else:
        VFS[filename] = content

def read_file(filename: str):
    return VFS.get(filename, "")

def list_files():
    return list(VFS.keys())

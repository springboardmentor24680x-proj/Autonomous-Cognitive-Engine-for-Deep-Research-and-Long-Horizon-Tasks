class VirtualFileSystem:
    def __init__(self):
        self.files = {}

    def write(self, path: str, content: str):
        self.files[path] = content

    def read(self, path: str) -> str:
        return self.files.get(path, "")

    def list_files(self):
        return list(self.files.keys())

class VirtualFileSystem:
    def __init__(self):
        self.files = {}

    def write_file(self, filename, content):
        self.files[filename] = content
        return f"✅ File '{filename}' written."

    def read_file(self, filename):
        if filename not in self.files:
            return f"❌ File '{filename}' not found."
        return self.files[filename]

    def edit_file(self, filename, content):
        if filename not in self.files:
            return f"❌ File '{filename}' not found."
        self.files[filename] = content
        return f"✅ File '{filename}' updated."

    def ls(self):
        if not self.files:
            return "📂 No files in memory."
        return "\n".join(self.files.keys())

class VFS:
    def __init__(self):
        self.files = {}

    def write_file(self, filename, content):
        self.files[filename] = content
        return f"✅ File '{filename}' written successfully."

    def read_file(self, filename):
        if filename not in self.files:
            return "❌ File not found."
        return self.files[filename]

    def list_files(self):
        if not self.files:
            return "📂 No files available."
        return "\n".join(self.files.keys())
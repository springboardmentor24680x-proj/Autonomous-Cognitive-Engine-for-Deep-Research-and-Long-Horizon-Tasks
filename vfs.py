
class VFS:
    def __init__(self):
        self.files = {}

    def ls(self):
        return list(self.files.keys())

    def read(self, name):
        return self.files.get(name, "File not found")

    def write(self, name, content):
        self.files[name] = content
        return f"Written {name}"

    def edit(self, name, content):
        if name not in self.files:
            return "File not found"
        self.files[name] = content
        return f"Updated {name}"


vfs = VFS()

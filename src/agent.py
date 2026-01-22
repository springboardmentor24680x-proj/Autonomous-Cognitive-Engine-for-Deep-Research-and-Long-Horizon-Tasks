from vfs import VirtualFileSystem

def run_agent():
    vfs = VirtualFileSystem()

    print("\n Virtual File System Memory Agent (Running)")
    print("Available commands:")
    print("  write_file <filename>")
    print("  read_file <filename>")
    print("  edit_file <filename>")
    print("  ls")
    print("  exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input == "exit":
            print("Agent stopped.")
            break

        parts = user_input.split(maxsplit=1)
        command = parts[0]

        if command == "write_file" and len(parts) == 2:
            filename = parts[1]
            content = input("Enter content: ")
            print(vfs.write_file(filename, content))

        elif command == "read_file" and len(parts) == 2:
            filename = parts[1]
            print("\n" + vfs.read_file(filename))

        elif command == "edit_file" and len(parts) == 2:
            filename = parts[1]
            content = input("Enter new content: ")
            print(vfs.edit_file(filename, content))

        elif command == "ls":
            print("\nFiles in memory:")
            print(vfs.ls())

        else:
            print(" Invalid command or missing filename.")

if __name__ == "__main__":
    run_agent()


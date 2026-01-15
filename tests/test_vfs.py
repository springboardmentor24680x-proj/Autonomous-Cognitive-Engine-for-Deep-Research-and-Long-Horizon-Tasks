import pytest
from memory.vfs import vfs

def test_vfs_write_read():
    # Clear VFS using official API
    vfs.clear()  # Use method instead of direct attribute access

    # Write a file
    vfs.write_file("test.txt", "Prompt", "Response content")

    # Read back
    content = vfs.read_file("test.txt")

    # List files
    files = vfs.ls()

    # Assertions
    assert "Response content" in content
    assert "test.txt" in files

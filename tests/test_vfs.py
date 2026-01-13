# tests/test_vfs.py
import pytest
from memory.vfs import vfs

def test_vfs_write_read():
    vfs.files.clear()
    vfs.history.clear()

    vfs.write_file("test.txt", "Prompt", "Response content")
    content = vfs.read_file("test.txt")

    assert "Response content" in content
    assert "test.txt" in vfs.ls()

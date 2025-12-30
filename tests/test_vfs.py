# tests/test_vfs.py
import pytest
from memory.vfs import vfs, VirtualFileSystem

# -------------------
# Unit Tests for VFS
# -------------------

def test_vfs_write():
    # Clear VFS before test
    vfs.files.clear()
    vfs.history.clear()

    # Directly write a file
    vfs.write_file("ai_summary.txt", "Save a summary about AI agents", "AI agents are software entities...")
    
    # Assertions
    assert len(vfs.files) > 0
    assert "ai_summary.txt" in vfs.files
    assert "AI agents are software entities" in vfs.files["ai_summary.txt"]

def test_vfs_read():
    # Ensure there is at least one file
    if not vfs.files:
        vfs.write_file("ai_summary.txt", "Save a summary about AI agents", "AI agents are software entities...")

    file_name = list(vfs.files.keys())[0]
    content = vfs.read_file(file_name)
    
    assert isinstance(content, str)
    assert "AI agents" in content

def test_vfs_ls():
    # Ensure at least one file exists
    if not vfs.files:
        vfs.write_file("ai_summary.txt", "Prompt", "Response")
    
    files_list = vfs.ls()
    assert isinstance(files_list, list)
    assert len(files_list) > 0
    assert "ai_summary.txt" in files_list


# -----------------------------
# Optional: Simple Integration
# -----------------------------
# This requires your agent to accept a VFS parameter or global vfs usage
# For demonstration only
def test_integration_invoke_chat(monkeypatch):
    # Clear VFS
    vfs.files.clear()
    vfs.history.clear()

    # Dummy agent function that calls vfs.write_file
    def dummy_invoke_chat(chatbot_state, prompt):
        vfs.write_file("integration_test.txt", prompt, "Dummy response")

    chatbot_state = {}  # minimal state
    dummy_invoke_chat(chatbot_state, "Save something")
    
    assert "integration_test.txt" in vfs.files
    assert "Dummy response" in vfs.files["integration_test.txt"]

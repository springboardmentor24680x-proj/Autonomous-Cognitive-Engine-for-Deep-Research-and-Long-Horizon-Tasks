from src.memory.vfs import write_file, read_file, edit_file, ls, clear_vfs

def setup_function():
    clear_vfs()

def test_write_and_read_file():
    write_file("demo.txt", "hello")
    assert read_file("demo.txt") == "hello"

def test_edit_file():
    write_file("demo.txt", "hello")
    edit_file("demo.txt", "updated")
    assert read_file("demo.txt") == "updated"

def test_ls_lists_files():
    write_file("a.txt", "1")
    write_file("b.txt", "2")
    files = ls()
    assert "a.txt" in files
    assert "b.txt" in files
